"""
Stats Center — StarRocks SQL Runner
Implements the SQL runner interface for Vanna, connecting to StarRocks via MySQL protocol.
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import pymysql
from pymysql.cursors import DictCursor

from app.config import settings

logger = logging.getLogger(__name__)


class StarRocksRunner:
    """
    Executes SQL queries against StarRocks using the MySQL wire protocol.
    Compatible with Vanna's SqlRunner interface (returns pandas DataFrames).
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):
        self.host = host or settings.STARROCKS_HOST
        self.port = port or settings.STARROCKS_PORT
        self.user = user or settings.STARROCKS_USER
        self.password = password or settings.STARROCKS_PASSWORD
        self.database = database or settings.STARROCKS_DATABASE

    def _get_connection(self) -> pymysql.Connection:
        """Create a new connection to StarRocks."""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=DictCursor,
            connect_timeout=10,
            read_timeout=120,
            charset="utf8mb4",
        )

    def run_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a pandas DataFrame.

        This is the main interface method consumed by Vanna's RunSqlTool.
        """
        logger.info("Executing SQL against StarRocks:\n%s", sql)

        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                if not rows:
                    # Return empty DataFrame with column names from description
                    columns = (
                        [desc[0] for desc in cursor.description]
                        if cursor.description
                        else []
                    )
                    return pd.DataFrame(columns=columns)
                return pd.DataFrame(rows)
        except pymysql.MySQLError as exc:
            logger.error("StarRocks query error: %s", exc)
            raise RuntimeError(f"StarRocks query failed: {exc}") from exc
        finally:
            conn.close()

    def get_schema(self) -> str:
        """
        Retrieve the database schema (DDL) for training Vanna.
        Returns CREATE TABLE statements for all tables in the configured database.
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [list(row.values())[0] for row in cursor.fetchall()]

                ddl_statements = []
                for table in tables:
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    result = cursor.fetchone()
                    if result:
                        ddl = list(result.values())[1]
                        ddl_statements.append(ddl)

                return "\n\n".join(ddl_statements)
        finally:
            conn.close()

    def test_connection(self) -> bool:
        """Verify connectivity to StarRocks."""
        try:
            conn = self._get_connection()
            conn.cursor().execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False
