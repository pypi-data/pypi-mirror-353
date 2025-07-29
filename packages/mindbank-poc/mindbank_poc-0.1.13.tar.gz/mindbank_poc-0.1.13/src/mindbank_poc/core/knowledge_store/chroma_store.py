"""
Реализация хранилища знаний на основе ChromaDB.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple, Union, Set
import uuid
import asyncio
import aiofiles

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings
from .base import BaseKnowledgeStore
from ..normalizer.models import NormalizedUnit
from ..enrichment.models import SegmentModel, ClusterModel

# Получаем логгер
logger = get_logger(__name__)


class ChromaKnowledgeStore(BaseKnowledgeStore):
    """
    Реализация хранилища знаний на основе ChromaDB.
    
    Использует ChromaDB для эффективного векторного поиска и хранения нормализованных юнитов.
    Преимущества по сравнению с JSONL:
    - Оптимизированный векторный поиск
    - Сохранение/загрузка данных без необходимости хранить все в памяти
    - Поддержка метаданных для фильтрации
    - Улучшенная масштабируемость
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация хранилища.
        
        Args:
            config: Конфигурация хранилища, может содержать:
                   - data_dir: путь к директории для хранения данных
                   - collection_name: имя коллекции в ChromaDB
        """
        super().__init__(config or {})
        
        # Директория для хранения данных
        self.data_dir = Path(self.config.get("data_dir", settings.storage.knowledge_dir))
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        # Имя коллекции
        self.collection_name = self.config.get("collection_name", "normalized_units")
        
        # Путь к ChromaDB
        self.chroma_path = self.data_dir / "chroma_db"
        self.chroma_path.mkdir(exist_ok=True, parents=True)
        
        # Логгирование инициализации
        logger.info(f"ChromaKnowledgeStore initialized. Data directory: {self.data_dir.resolve()}")
        logger.info(f"ChromaDB path: {self.chroma_path.resolve()}")
        logger.info(f"Collection name: {self.collection_name}")
        
        # Инициализация клиента ChromaDB (persistent)
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path.resolve()),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Получение или создание коллекции
        try:
            # Создаем функцию эмбеддингов None, чтобы отключить встроенную функцию эмбеддингов
            # Это важно, так как мы хотим использовать только наши собственные эмбеддинги от OpenAI
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Нормализованные единицы знаний"},
                embedding_function=None  # Отключаем встроенную функцию эмбеддингов
            )
            logger.info(f"ChromaKnowledgeStore: Collection '{self.collection_name}' ready")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {e}", exc_info=True)
            raise
    
    async def store(self, unit: NormalizedUnit) -> str:
        """
        Сохраняет нормализованную единицу в хранилище.
        
        Args:
            unit: Нормализованная единица для сохранения
            
        Returns:
            Идентификатор сохраненной единицы (unit.id)
        """
        try:
            # Идентификатор для ChromaDB (используем unit.id)
            doc_id = unit.id
            
            # Текстовое представление для поиска
            document = unit.text_repr
            
            # Векторное представление (если есть)
            embedding = unit.vector_repr
            
            # Метаданные для хранения и фильтрации
            metadata = {
                "unit_id": unit.id,
                "aggregate_id": unit.aggregate_id,
                "group_id": unit.group_id,
                "normalized_at": unit.normalized_at.isoformat(),
                # Копируем классификацию в метаданные для фильтрации
                **{f"class_{k}": str(v) for k, v in unit.classification.items()},
                # Копируем метаданные юнита для фильтрации (только строковые и числовые)
                **{k: str(v) if not isinstance(v, (int, float, bool, str)) else v 
                   for k, v in unit.metadata.items() 
                   if v is not None}
            }
            
            # Сохраняем полный объект как JSON в документе
            full_unit_json = unit.model_dump_json()
            
            # Проверяем, существует ли документ с таким ID
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing and existing['ids']:
                    # Если существует, обновляем
                    logger.info(f"Updating existing unit with ID {doc_id}")
                    self.collection.update(
                        ids=[doc_id],
                        embeddings=[embedding] if embedding else None,
                        metadatas=[metadata],
                        documents=[full_unit_json]
                    )
                else:
                    # Если не существует, добавляем
                    logger.info(f"Adding new unit with ID {doc_id}")
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding] if embedding else None,
                        metadatas=[metadata],
                        documents=[full_unit_json]
                    )
            except Exception as e:
                # Если произошла ошибка (например, коллекция пуста), добавляем
                logger.warning(f"Error checking existence, adding as new: {e}")
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding] if embedding else None,
                    metadatas=[metadata],
                    documents=[full_unit_json]
                )
            
            logger.info(f"Stored unit with ID {doc_id} in ChromaDB")
            return doc_id
        
        except Exception as e:
            logger.error(f"Error storing unit in ChromaDB: {e}", exc_info=True)
            raise
    
    async def get(self, unit_id: str) -> Optional[NormalizedUnit]:
        """
        Получает нормализованную единицу из хранилища по идентификатору.
        
        Args:
            unit_id: Идентификатор единицы (unit.id)
            
        Returns:
            Нормализованная единица или None, если единица не найдена
        """
        try:
            # Запрашиваем документ по ID
            result = self.collection.get(ids=[unit_id], include=["documents"])
            
            # Проверяем, найден ли документ
            if not result or not result['documents'] or not result['documents'][0]:
                logger.warning(f"Unit with ID {unit_id} not found in ChromaDB")
                return None
            
            # Десериализуем JSON в объект NormalizedUnit
            try:
                unit_json = result['documents'][0]
                unit = NormalizedUnit.model_validate_json(unit_json)
                return unit
            except Exception as e:
                logger.error(f"Error deserializing unit from ChromaDB: {e}", exc_info=True)
                return None
        
        except Exception as e:
            logger.error(f"Error retrieving unit from ChromaDB: {e}", exc_info=True)
            return None
    
    async def load_all(self) -> List[NormalizedUnit]:
        """
        Загружает все нормализованные юниты из хранилища.
        
        Returns:
            Список всех нормализованных юнитов
        """
        try:
            # Запрашиваем все документы из коллекции
            result = self.collection.get(include=["documents"])
            
            # Проверяем, есть ли результаты
            if not result or not result['documents']:
                logger.warning("No units found in ChromaDB")
                return []
            
            # Десериализуем каждый JSON в объект NormalizedUnit
            units = []
            for unit_json in result['documents']:
                try:
                    if unit_json:  # Проверяем, что JSON не пустой
                        unit = NormalizedUnit.model_validate_json(unit_json)
                        units.append(unit)
                except Exception as e:
                    logger.error(f"Error deserializing unit from ChromaDB: {e}", exc_info=True)
            
            logger.info(f"Loaded {len(units)} units from ChromaDB")
            return units
        
        except Exception as e:
            logger.error(f"Error loading all units from ChromaDB: {e}", exc_info=True)
            return []
    
    async def delete(self, unit_id: str) -> bool:
        """
        Удаляет нормализованную единицу из хранилища по идентификатору.
        
        Args:
            unit_id: Идентификатор единицы (unit.id)
            
        Returns:
            True, если удаление успешно, иначе False
        """
        try:
            # Удаляем документ по ID
            self.collection.delete(ids=[unit_id])
            logger.info(f"Deleted unit with ID {unit_id} from ChromaDB")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting unit from ChromaDB: {e}", exc_info=True)
            return False
    
    async def delete_all(self) -> bool:
        """
        Удаляет все нормализованные единицы из хранилища.
        
        Returns:
            True, если удаление успешно, иначе False
        """
        try:
            # Удаляем всю коллекцию и создаем заново
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Нормализованные единицы знаний"}
            )
            logger.info(f"Deleted all units from ChromaDB collection '{self.collection_name}'")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting all units from ChromaDB: {e}", exc_info=True)
            return False
    
    async def search(
        self, 
        # Убираем query_text, так как поиск будет только по вектору
        # query_text: Optional[str] = None,
        query_vector: Optional[List[float]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Tuple[NormalizedUnit, float]]:
        """
        Выполняет поиск в хранилище по вектору и/или метаданным.
        
        Args:
            query_vector: Вектор запроса для семантического поиска
            metadata_filters: Фильтры по метаданным
            limit: Максимальное количество результатов
            
        Returns:
            Список кортежей (unit, score) с найденными единицами и их релевантностью
        """
        try:
            # Проверяем, есть ли критерий поиска (вектор или фильтры)
            if not query_vector and not metadata_filters:
                logger.warning("Search requires either query_vector or metadata_filters")
                return []
            
            # Подготавливаем фильтры метаданных в формате ChromaDB
            chroma_filter = None
            if metadata_filters:
                # Конвертируем фильтры в формат ChromaDB
                chroma_filter = {"$and": []}
                for key, value in metadata_filters.items():
                    filter_key = f"class_{key}" if key in ["type", "topic", "category"] else key
                    chroma_filter["$and"].append({"$eq": {filter_key: value}})
            
            # Выполняем поиск
            if query_vector:
                # Семантический поиск по вектору
                result = self.collection.query(
                    query_embeddings=[query_vector],
                    where=chroma_filter,
                    n_results=limit,
                    include=["documents", "distances"] # Запрашиваем дистанции
                )
            elif metadata_filters: # Если вектора нет, но есть фильтры
                # Только фильтрация по метаданным
                result = self.collection.get(
                    where=chroma_filter,
                    limit=limit,
                    include=["documents"] # Дистанции не нужны/недоступны
                )
            else: # На случай, если контроль выше пропустит
                return []
            
            # Проверяем, есть ли результаты
            # Для query результат в result["documents"][0], для get в result["documents"]
            documents = result.get('documents')
            if not documents or (isinstance(documents, list) and not documents[0]):
                logger.warning("No results found in ChromaDB query")
                return []
            
            # Обработка результатов
            results_list = []
            docs_to_process = documents[0] if query_vector else documents
            distances_list = result.get('distances')[0] if query_vector and result.get('distances') else None
            
            for i, unit_json in enumerate(docs_to_process):
                try:
                    if unit_json:
                        unit = NormalizedUnit.model_validate_json(unit_json)
                        score = 0.99 # Скор по умолчанию для get()
                        
                        if distances_list:
                            distance = float(distances_list[i])
                            # Преобразуем косинусную дистанцию [0, 2] в скор [0.99, ~0]
                            # similarity = 1.0 - (distance / 2.0) # Сходство [0, 1]
                            # score = 0.99 * (similarity ** 0.8) # Нелинейное масштабирование
                            score = max(0.01, 0.99 * (1.0 - (distance / 2.0))) # Линейное масштабирование
                            score = round(score, 2)
                            
                        results_list.append((unit, score))
                except Exception as e:
                    logger.error(f"Error deserializing search result from ChromaDB: {e}", exc_info=True)
            
            logger.info(f"Found {len(results_list)} results in ChromaDB")
            # Сортируем по скору, если был векторный поиск
            if query_vector:
                results_list.sort(key=lambda item: item[1], reverse=True)
                
            return results_list
        
        except Exception as e:
            logger.error(f"Error searching in ChromaDB: {e}", exc_info=True)
            return []

    async def list_group_ids(self) -> Set[str]:
        """
        Возвращает множество всех group_id в хранилище.
        
        Returns:
            Set[str]: Множество уникальных group_id
        """
        group_ids = set()
        
        try:
            # Получаем все записи из коллекции
            result = self.collection.get(
                include=["metadatas"]
            )
            
            # Извлекаем group_id из метаданных
            if result and "metadatas" in result:
                for metadata in result["metadatas"]:
                    if metadata and "group_id" in metadata:
                        group_ids.add(metadata["group_id"])
            
            logger.debug(f"Found {len(group_ids)} unique group IDs in ChromaDB")
            return group_ids
            
        except Exception as e:
            logger.error(f"Failed to list group IDs from ChromaDB: {e}", exc_info=True)
            return set()
    
    async def list_by_group(self, group_id: str) -> List[NormalizedUnit]:
        """
        Возвращает список нормализованных единиц для указанной группы.
        
        Args:
            group_id: Идентификатор группы
            
        Returns:
            Список нормализованных единиц группы
        """
        try:
            # Запрашиваем все юниты группы
            results = self.collection.get(
                where={"group_id": group_id},
                include=["documents"]
            )
            
            units = []
            if results and results['documents']:
                for doc_json in results['documents']:
                    if doc_json:
                        try:
                            unit = NormalizedUnit.model_validate_json(doc_json)
                            units.append(unit)
                        except Exception as e:
                            logger.error(f"Error deserializing unit: {e}")
            
            logger.info(f"Found {len(units)} units for group {group_id} in ChromaDB")
            return units
            
        except Exception as e:
            logger.error(f"Error listing units by group from ChromaDB: {e}", exc_info=True)
            return []
    
    async def list_unprocessed_groups(self, min_units: int = 10) -> List[str]:
        """
        Возвращает список групп с необработанными юнитами (без сегментов).
        
        Args:
            min_units: Минимальное количество юнитов в группе для обработки
            
        Returns:
            Список идентификаторов групп
        """
        try:
            # Получаем все group_id и подсчитываем юниты
            group_ids = await self.list_group_ids()
            qualified_groups = []
            
            for group_id in group_ids:
                # Получаем количество юнитов в группе
                units = await self.list_by_group(group_id)
                if len(units) >= min_units:
                    # Проверяем, есть ли сегменты для этой группы
                    segments = await self.list_segments_by_group(group_id)
                    if not segments:
                        qualified_groups.append(group_id)
            
            logger.info(f"Found {len(qualified_groups)} groups with >= {min_units} units and no segments")
            return qualified_groups
            
        except Exception as e:
            logger.error(f"Failed to list unprocessed groups: {e}", exc_info=True)
            return []
    
    async def get_original_aggregate(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает оригинальный агрегат для нормализованной единицы.
        
        Args:
            unit_id: ID нормализованной единицы (unit.id)
            
        Returns:
            Агрегат или None, если не найден
        """
        try:
            # Сначала получаем нормализованную единицу
            unit = await self.get(unit_id)
            if not unit:
                logger.warning(f"Unit {unit_id} not found")
                return None
            
            # Для ChromaDB пытаемся загрузить через JSONL backend
            # В будущем здесь может быть реализация через отдельную коллекцию агрегатов
            from mindbank_poc.api.backends import jsonl_backend
            aggregate = await jsonl_backend.load_aggregate_by_id(unit.aggregate_id)
            
            if aggregate:
                # Преобразуем модель AggregateInput в словарь
                return aggregate.model_dump(mode="json")
            else:
                logger.warning(f"Original aggregate {unit.aggregate_id} not found for unit {unit_id}")
                return None
        except Exception as e:
            logger.error(f"Error loading original aggregate for unit {unit_id}: {e}")
            return None
    
    # Методы для работы с сегментами
    async def store_segment(self, segment: SegmentModel) -> str:
        """
        Сохраняет сегмент в хранилище.
        
        Args:
            segment: Сегмент для сохранения
            
        Returns:
            Идентификатор сохраненного сегмента
        """
        try:
            # Идентификатор для ChromaDB
            doc_id = f"segment_{segment.id}"
            
            # Текстовое представление для поиска (заголовок + резюме)
            document = f"{segment.title}\n\n{segment.summary}"
            
            # Векторное представление (если есть)
            embedding = segment.vector_repr
            
            # Метаданные для хранения и фильтрации
            metadata = {
                "doc_type": "segment",  # Тип документа
                "segment_id": segment.id,
                "group_id": segment.group_id,
                "created_at": segment.created_at.isoformat(),
                "entity_count": len(segment.entities),
                "unit_count": len(segment.raw_unit_ids),
                # Сохраняем первые 10 сущностей для фильтрации
                **{f"entity_{i}": entity for i, entity in enumerate(segment.entities[:10])}
            }
            
            # Сохраняем полный объект как JSON
            full_segment_json = segment.model_dump_json()
            
            # Добавляем в коллекцию
            if embedding:
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[full_segment_json],
                    metadatas=[metadata]
                )
            else:
                self.collection.add(
                    ids=[doc_id],
                    documents=[full_segment_json],
                    metadatas=[metadata]
                )
            
            logger.info(f"Stored segment {segment.id} in ChromaDB")
            return segment.id
            
        except Exception as e:
            logger.error(f"Error storing segment in ChromaDB: {e}", exc_info=True)
            raise
    
    async def get_segment(self, segment_id: str) -> Optional[SegmentModel]:
        """
        Получает сегмент из хранилища.
        
        Args:
            segment_id: Идентификатор сегмента
            
        Returns:
            Сегмент или None, если не найден
        """
        try:
            doc_id = f"segment_{segment_id}"
            result = self.collection.get(ids=[doc_id], include=["documents"])
            
            if not result or not result['documents'] or not result['documents'][0]:
                logger.warning(f"Segment with ID {segment_id} not found in ChromaDB")
                return None
            
            # Десериализуем JSON в объект SegmentModel
            try:
                segment_json = result['documents'][0]
                segment = SegmentModel.model_validate_json(segment_json)
                return segment
            except Exception as e:
                logger.error(f"Error deserializing segment from ChromaDB: {e}", exc_info=True)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving segment from ChromaDB: {e}", exc_info=True)
            return None
    
    async def list_segments_by_group(self, group_id: str) -> List[SegmentModel]:
        """
        Получает все сегменты для указанной группы.
        
        Args:
            group_id: Идентификатор группы
            
        Returns:
            Список сегментов группы
        """
        try:
            # Запрашиваем все сегменты группы
            results = self.collection.get(
                where={
                    "$and": [
                        {"doc_type": "segment"},
                        {"group_id": group_id}
                    ]
                },
                include=["documents"]
            )
            
            segments = []
            if results and results['documents']:
                for doc_json in results['documents']:
                    if doc_json:
                        try:
                            segment = SegmentModel.model_validate_json(doc_json)
                            segments.append(segment)
                        except Exception as e:
                            logger.error(f"Error deserializing segment: {e}")
            
            logger.info(f"Found {len(segments)} segments for group {group_id} in ChromaDB")
            return segments
            
        except Exception as e:
            logger.error(f"Error listing segments by group from ChromaDB: {e}", exc_info=True)
            return []
    
    async def get_segments_for_unit(self, unit_id: str) -> List[SegmentModel]:
        """
        Получает все сегменты, в которые входит указанный юнит.
        
        Args:
            unit_id: Идентификатор юнита (unit.id)
            
        Returns:
            Список сегментов, содержащих данный юнит
        """
        try:
            # В ChromaDB нет прямого способа искать по массиву raw_unit_ids,
            # поэтому загружаем все сегменты и фильтруем
            results = self.collection.get(
                where={"doc_type": "segment"},
                include=["documents"]
            )
            
            segments = []
            if results and results['documents']:
                for doc_json in results['documents']:
                    if doc_json:
                        try:
                            segment = SegmentModel.model_validate_json(doc_json)
                            # Проверяем, содержит ли сегмент данный юнит
                            if unit_id in segment.raw_unit_ids:
                                segments.append(segment)
                        except Exception as e:
                            logger.error(f"Error deserializing segment: {e}")
            
            logger.debug(f"Found {len(segments)} segments containing unit {unit_id}")
            return segments
            
        except Exception as e:
            logger.error(f"Error getting segments for unit from ChromaDB: {e}", exc_info=True)
            return []

    # Методы для работы с кластерами
    async def store_cluster(self, cluster: ClusterModel) -> str:
        """
        Сохраняет кластер в хранилище.
        
        Args:
            cluster: Кластер для сохранения
            
        Returns:
            Идентификатор сохраненного кластера
        """
        try:
            # Идентификатор для ChromaDB
            doc_id = f"cluster_{cluster.id}"
            
            # Текстовое представление для поиска (заголовок + резюме + ключевые слова)
            keywords_text = ", ".join(cluster.keywords) if cluster.keywords else ""
            document = f"{cluster.title}\n\n{cluster.summary}\n\nКлючевые слова: {keywords_text}"
            
            # Векторное представление (центроид кластера)
            embedding = cluster.centroid
            
            # Метаданные для хранения и фильтрации
            metadata = {
                "doc_type": "cluster",  # Тип документа
                "cluster_id": cluster.id,
                "cluster_size": cluster.cluster_size,
                "created_at": cluster.created_at.isoformat(),
                "keyword_count": len(cluster.keywords),
                # Сохраняем первые 10 ключевых слов для фильтрации
                **{f"keyword_{i}": keyword for i, keyword in enumerate(cluster.keywords[:10])}
            }
            
            # Сохраняем полный объект как JSON
            full_cluster_json = cluster.model_dump_json()
            
            # Добавляем в коллекцию
            if embedding:
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[full_cluster_json],
                    metadatas=[metadata]
                )
            else:
                self.collection.add(
                    ids=[doc_id],
                    documents=[full_cluster_json],
                    metadatas=[metadata]
                )
            
            logger.info(f"Stored cluster {cluster.id} with {cluster.cluster_size} segments in ChromaDB")
            return cluster.id
            
        except Exception as e:
            logger.error(f"Error storing cluster in ChromaDB: {e}", exc_info=True)
            raise
    
    async def get_cluster(self, cluster_id: str) -> Optional[ClusterModel]:
        """
        Получает кластер из хранилища.
        
        Args:
            cluster_id: Идентификатор кластера
            
        Returns:
            Кластер или None, если не найден
        """
        try:
            doc_id = f"cluster_{cluster_id}"
            result = self.collection.get(ids=[doc_id], include=["documents"])
            
            if not result or not result['documents'] or not result['documents'][0]:
                logger.warning(f"Cluster with ID {cluster_id} not found in ChromaDB")
                return None
            
            # Десериализуем JSON в объект ClusterModel
            try:
                cluster_json = result['documents'][0]
                cluster = ClusterModel.model_validate_json(cluster_json)
                return cluster
            except Exception as e:
                logger.error(f"Error deserializing cluster from ChromaDB: {e}", exc_info=True)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving cluster from ChromaDB: {e}", exc_info=True)
            return None
    
    async def list_clusters(self) -> List[ClusterModel]:
        """
        Получает все кластеры из хранилища.
        
        Returns:
            Список всех кластеров
        """
        try:
            # Запрашиваем все кластеры
            results = self.collection.get(
                where={"doc_type": "cluster"},
                include=["documents"]
            )
            
            clusters = []
            if results and results['documents']:
                for doc_json in results['documents']:
                    if doc_json:
                        try:
                            cluster = ClusterModel.model_validate_json(doc_json)
                            clusters.append(cluster)
                        except Exception as e:
                            logger.error(f"Error deserializing cluster: {e}")
            
            logger.info(f"Found {len(clusters)} clusters in ChromaDB")
            return clusters
            
        except Exception as e:
            logger.error(f"Error listing clusters from ChromaDB: {e}", exc_info=True)
            return []
    
    async def get_clusters_for_segment(self, segment_id: str) -> List[ClusterModel]:
        """
        Получает все кластеры, в которые входит указанный сегмент.
        
        Args:
            segment_id: Идентификатор сегмента
            
        Returns:
            Список кластеров, содержащих данный сегмент
        """
        try:
            # В ChromaDB нет прямого способа искать по массиву segment_ids,
            # поэтому загружаем все кластеры и фильтруем
            results = self.collection.get(
                where={"doc_type": "cluster"},
                include=["documents"]
            )
            
            clusters = []
            if results and results['documents']:
                for doc_json in results['documents']:
                    if doc_json:
                        try:
                            cluster = ClusterModel.model_validate_json(doc_json)
                            # Проверяем, содержит ли кластер данный сегмент
                            if segment_id in cluster.segment_ids:
                                clusters.append(cluster)
                        except Exception as e:
                            logger.error(f"Error deserializing cluster: {e}")
            
            logger.debug(f"Found {len(clusters)} clusters containing segment {segment_id}")
            return clusters
            
        except Exception as e:
            logger.error(f"Error getting clusters for segment from ChromaDB: {e}", exc_info=True)
            return []

    def _group_meta_file(self):
        return self.data_dir / "group_segmentation_meta.json"

    async def get_group_segmentation_meta(self, group_id: str) -> dict:
        """Возвращает метаинформацию по сегментации для группы (или пустой dict)."""
        meta_file = self._group_meta_file()
        if not meta_file.exists():
            return {}
        async with aiofiles.open(meta_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            if not content.strip():
                return {}
            try:
                meta = json.loads(content)
                return meta.get(group_id, {})
            except Exception:
                return {}

    async def set_group_segmentation_meta(self, group_id: str, last_segmented_at: str, last_segmented_unit_id: str):
        """Обновляет метаинформацию по сегментации для группы."""
        meta_file = self._group_meta_file()
        meta = {}
        if meta_file.exists():
            async with aiofiles.open(meta_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                if content.strip():
                    try:
                        meta = json.loads(content)
                    except Exception:
                        meta = {}
        meta[group_id] = {
            "last_segmented_at": last_segmented_at,
            "last_segmented_unit_id": last_segmented_unit_id
        }
        async with aiofiles.open(meta_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(meta, ensure_ascii=False, indent=2))

    async def get_groups_with_new_units_for_segmentation(self, min_units: int = 10) -> list:
        """Возвращает группы, где есть новые юниты после последней сегментации."""
        group_ids = await self.list_group_ids()
        result = []
        for group_id in group_ids:
            units = await self.list_by_group(group_id)
            if not units:
                continue
            units_sorted = sorted(units, key=lambda u: (u.normalized_at or getattr(u, 'stored_at', "")))
            last_unit = units_sorted[-1]
            meta = await self.get_group_segmentation_meta(group_id)
            last_segmented_unit_id = meta.get("last_segmented_unit_id")
            # Если сегментации не было или есть новые юниты
            if not last_segmented_unit_id or any(u.id > last_segmented_unit_id for u in units_sorted):
                if len(units) >= min_units:
                    result.append(group_id)
        return result 