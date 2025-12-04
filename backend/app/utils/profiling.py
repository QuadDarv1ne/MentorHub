"""
Database profiling и EXPLAIN ANALYZE утилита
Помогает анализировать производительность запросов к базе данных
"""

from sqlalchemy import text, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import Pool
import logging
import time
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryProfiler:
    """Профайлер для анализа SQL запросов"""

    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.total_time = 0.0
        self.slow_query_threshold = 0.5  # секунды

    def add_query(self, query: str, duration: float, params: Dict = None):
        """Добавить запрос в список профилированных"""
        self.queries.append({
            "query": query,
            "duration": duration,
            "params": params or {},
            "timestamp": datetime.now().isoformat(),
            "is_slow": duration > self.slow_query_threshold,
        })
        self.total_time += duration

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Получить все медленные запросы"""
        return [q for q in self.queries if q["is_slow"]]

    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку по запросам"""
        slow_queries = self.get_slow_queries()
        avg_time = self.total_time / len(self.queries) if self.queries else 0

        return {
            "total_queries": len(self.queries),
            "total_time": f"{self.total_time:.3f}s",
            "avg_time": f"{avg_time:.3f}s",
            "slow_queries_count": len(slow_queries),
            "slow_queries": slow_queries,
        }

    def reset(self):
        """Очистить статистику"""
        self.queries = []
        self.total_time = 0.0

    def print_summary(self):
        """Вывести сводку в логи"""
        summary = self.get_summary()
        logger.info(f"Query Profile Summary:")
        logger.info(f"  Total Queries: {summary['total_queries']}")
        logger.info(f"  Total Time: {summary['total_time']}")
        logger.info(f"  Avg Time: {summary['avg_time']}")
        logger.info(f"  Slow Queries: {summary['slow_queries_count']}")

        if summary["slow_queries"]:
            logger.warning("Slow Queries Detected:")
            for i, query in enumerate(summary["slow_queries"], 1):
                logger.warning(f"  {i}. {query['duration']:.3f}s - {query['query'][:100]}...")


# Глобальный профайлер
query_profiler = QueryProfiler()


def explain_query(db: Session, query_str: str) -> List[Dict[str, Any]]:
    """
    Анализ запроса с помощью EXPLAIN ANALYZE

    Пример:
        result = explain_query(db, "SELECT * FROM users WHERE email = 'test@example.com'")
        print(result)
    """
    try:
        # Используем EXPLAIN для PostgreSQL
        explain_query_str = f"EXPLAIN ANALYZE {query_str}"
        result = db.execute(text(explain_query_str))
        return [dict(row) for row in result.fetchall()]
    except Exception as e:
        logger.error(f"Error running EXPLAIN: {e}")
        return []


def setup_query_logging(db_engine):
    """
    Настройка логирования всех SQL запросов

    Пример:
        from app.database import engine
        setup_query_logging(engine)
    """

    @event.listens_for(db_engine, "before_cursor_execute")
    def receive_before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """Перед выполнением запроса"""
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(db_engine, "after_cursor_execute")
    def receive_after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """После выполнения запроса"""
        total_time = time.time() - conn.info["query_start_time"].pop(-1)

        # Логируем только медленные запросы по умолчанию
        if total_time > 0.1:  # 100ms
            logger.warning(
                f"Slow query ({total_time:.3f}s): {statement[:200]}... | Params: {parameters}"
            )

        # Добавляем в профайлер
        query_profiler.add_query(statement, total_time, parameters)


def find_n_plus_one_queries(db: Session, threshold: int = 10) -> Dict[str, int]:
    """
    Анализ N+1 проблем: находит повторяющиеся запросы

    Пример:
        n_plus_one = find_n_plus_one_queries(db)
        if n_plus_one:
            print("N+1 queries detected:", n_plus_one)
    """
    query_patterns = {}

    for query_info in query_profiler.queries:
        # Нормализуем запрос (убираем параметры и пробелы)
        normalized = " ".join(query_info["query"].split())

        if normalized not in query_patterns:
            query_patterns[normalized] = 0
        query_patterns[normalized] += 1

    # Возвращаем только повторяющиеся запросы
    return {q: count for q, count in query_patterns.items() if count > threshold}


def get_index_suggestions(db: Session) -> List[str]:
    """
    Получить рекомендации по индексам для PostgreSQL

    Пример:
        suggestions = get_index_suggestions(db)
        for suggestion in suggestions:
            print(suggestion)
    """
    suggestions = []

    try:
        # Анализируем медленные запросы
        slow_queries = query_profiler.get_slow_queries()

        if slow_queries:
            suggestions.append("Slow queries detected. Consider adding indexes on:")

            # Парсим WHERE условия для поиска часто фильтруемых полей
            for query in slow_queries[:5]:  # Берем топ 5 медленных
                query_str = query["query"].lower()

                if "where" in query_str:
                    suggestions.append(
                        f"  - Review query: {query_str[:100]}... (took {query['duration']:.3f}s)"
                    )

    except Exception as e:
        logger.error(f"Error generating index suggestions: {e}")

    return suggestions


class ProfileContext:
    """
    Context manager для профилирования блока кода

    Пример:
        with ProfileContext("Get mentors with users") as profile:
            mentors = db.query(Mentor).options(joinedload(Mentor.user)).all()
        profile.print_summary()
    """

    def __init__(self, label: str):
        self.label = label
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        query_profiler.reset()
        logger.info(f"Starting profile: {self.label}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        logger.info(f"\n{'='*60}")
        logger.info(f"Profile: {self.label}")
        logger.info(f"Total Duration: {duration:.3f}s")
        query_profiler.print_summary()
        logger.info(f"{'='*60}\n")

        return False

    def print_summary(self):
        """Вывести сводку профиля"""
        if self.start_time is None or self.end_time is None:
            logger.warning("Profile not completed")
            return

        duration = self.end_time - self.start_time
        logger.info(f"\nProfile '{self.label}' Duration: {duration:.3f}s")
        query_profiler.print_summary()
