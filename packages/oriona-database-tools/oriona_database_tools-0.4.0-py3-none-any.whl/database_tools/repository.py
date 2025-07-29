"""Repository pattern for database operations."""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, Inspector
from sqlalchemy.pool import QueuePool

from .config import DatabaseConfig, TableFilterConfig
from .exceptions import ConnectionError, TableNotFoundError, TableAccessDeniedError
from .query_builder import QueryBuilder

logger = logging.getLogger(__name__)


class DatabaseRepository:
    """Repository for database operations."""
    
    def __init__(self, config: DatabaseConfig, table_filter: Optional[TableFilterConfig] = None):
        """Initialize repository with configuration."""
        self.config = config
        self.table_filter = table_filter or TableFilterConfig()
        self._engine: Optional[Engine] = None
        self._inspector: Optional[Inspector] = None
        self._bigquery_credentials_file: Optional[str] = None
    
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            try:
                # Setup BigQuery credentials if needed
                if self.config.is_bigquery and self.config.bigquery_config:
                    self._setup_bigquery_credentials()
                
                # Create engine with appropriate configuration
                if self.config.is_bigquery:
                    # BigQuery doesn't support traditional connection pooling
                    self._engine = create_engine(
                        self.config.url,
                        connect_args=self._get_connect_args()
                    )
                else:
                    # Traditional databases with connection pooling
                    self._engine = create_engine(
                        self.config.url,
                        poolclass=QueuePool,
                        pool_size=self.config.pool_size,
                        max_overflow=self.config.max_overflow,
                        pool_pre_ping=True,
                        pool_recycle=self.config.pool_recycle,
                        connect_args=self._get_connect_args()
                    )
                logger.info("Created database connection pool")
            except Exception as e:
                raise ConnectionError(f"Failed to create database engine: {str(e)}")
        return self._engine
    
    @property
    def inspector(self) -> Inspector:
        """Get or create database inspector."""
        if self._inspector is None:
            self._inspector = inspect(self.engine)
        return self._inspector
    
    def _setup_bigquery_credentials(self) -> None:
        """Setup BigQuery credentials environment."""
        if not self.config.bigquery_config:
            return
        
        # Try to get credentials file
        credentials_file = self.config.bigquery_config.get_credentials_path()
        if credentials_file:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
            self._bigquery_credentials_file = credentials_file
            logger.info("BigQuery credentials configured from base64 data")
        else:
            # Use default credentials (gcloud auth application-default login)
            logger.info("Using default BigQuery credentials")
    
    def _get_connect_args(self) -> dict:
        """Get database-specific connection arguments."""
        if self.config.is_postgresql:
            return {
                "connect_timeout": self.config.connect_timeout,
                "options": f"-c statement_timeout={self.config.statement_timeout}"
            }
        elif self.config.is_bigquery:
            # BigQuery-specific connection arguments
            args = {}
            if self.config.bigquery_config:
                if self.config.bigquery_config.location != "US":
                    args["location"] = self.config.bigquery_config.location
            return args
        return {}
    
    def _filter_tables(self, tables: List[str]) -> List[str]:
        """Filter tables based on whitelist/blacklist configuration."""
        return [table for table in tables if self.table_filter.is_table_allowed(table)]
    
    def get_tables(self) -> List[str]:
        """Get list of table names filtered by whitelist/blacklist."""
        try:

            if self.config.is_bigquery:
                return self._get_bigquery_tables()
            else:
                all_tables = self.inspector.get_table_names()
                return self._filter_tables(all_tables)

        except Exception as e:
            raise ConnectionError(f"Failed to retrieve tables: {str(e)}")
    
    def get_views(self) -> List[str]:
        """Get list of view names filtered by whitelist/blacklist."""
        try:

            if self.config.is_bigquery:
                return self._get_bigquery_views()
            else:
                all_views = self.inspector.get_view_names()
                return self._filter_tables(all_views)

        except Exception as e:
            raise ConnectionError(f"Failed to retrieve views: {str(e)}")
    
    def _get_bigquery_tables(self) -> List[str]:
        """Get BigQuery tables from all accessible datasets."""
        tables = []
        try:
            # If a specific dataset is configured, query only that dataset
            if self.config.bigquery_config and self.config.bigquery_config.dataset:
                dataset_id = self.config.bigquery_config.dataset
                query = f"""
                SELECT table_name
                FROM `{self.config.bigquery_config.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
                WHERE table_type = 'BASE TABLE'
                ORDER BY table_name
                """
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    tables = [row[0] for row in result]
            else:
                # Query all datasets
                query = f"""
                SELECT 
                    CONCAT(table_schema, '.', table_name) as full_table_name
                FROM `{self.config.bigquery_config.project_id}.INFORMATION_SCHEMA.TABLES`
                WHERE table_type = 'BASE TABLE'
                ORDER BY table_schema, table_name
                """
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    tables = [row[0] for row in result]
            
            return self._filter_tables(tables)
        except Exception as e:
            logger.warning(f"Failed to get BigQuery tables: {e}")
            return []
    
    def _get_bigquery_views(self) -> List[str]:
        """Get BigQuery views from all accessible datasets."""
        views = []
        try:
            # If a specific dataset is configured, query only that dataset
            if self.config.bigquery_config and self.config.bigquery_config.dataset:
                dataset_id = self.config.bigquery_config.dataset
                query = f"""
                SELECT table_name
                FROM `{self.config.bigquery_config.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
                WHERE table_type = 'VIEW'
                ORDER BY table_name
                """
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    views = [row[0] for row in result]
            else:
                # Query all datasets
                query = f"""
                SELECT 
                    CONCAT(table_schema, '.', table_name) as full_table_name
                FROM `{self.config.bigquery_config.project_id}.INFORMATION_SCHEMA.TABLES`
                WHERE table_type = 'VIEW'
                ORDER BY table_schema, table_name
                """
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    views = [row[0] for row in result]
            
            return self._filter_tables(views)
        except Exception as e:
            logger.warning(f"Failed to get BigQuery views: {e}")
            return []
    
    def get_database_type(self) -> str:
        """Get database dialect name."""
        return self.engine.dialect.name
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table or view exists and is allowed by filter."""
        # First check if the table is allowed by the filter
        if not self.table_filter.is_table_allowed(table_name):
            return False
        
        # Then check if it actually exists in the database
        all_tables = self.get_tables() + self.get_views()
        return table_name in all_tables
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        # Check if table is filtered
        if not self.table_filter.is_table_allowed(table_name):
            raise TableAccessDeniedError(table_name)
        
        # Check if table exists
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        columns = []
        for col in self.inspector.get_columns(table_name):
            columns.append({
                "name": col['name'],
                "type": str(col['type']),
                "nullable": col.get('nullable', True),
                "default": str(col.get('default', '')) if col.get('default') else None,
            })
        return columns
    
    def get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns for a table."""
        # Check if table is filtered
        if not self.table_filter.is_table_allowed(table_name):
            raise TableAccessDeniedError(table_name)
        
        # Check if table exists
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        return pk_constraint.get('constrained_columns', []) if pk_constraint else []
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        # Check if table is filtered
        if not self.table_filter.is_table_allowed(table_name):
            raise TableAccessDeniedError(table_name)
        
        # Check if table exists
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "columns": fk['constrained_columns'],
                "references": QueryBuilder.format_foreign_key_reference(
                    fk['referred_table'], 
                    fk['referred_columns']
                )
            })
        return foreign_keys
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for a table."""
        # Check if table is filtered
        if not self.table_filter.is_table_allowed(table_name):
            raise TableAccessDeniedError(table_name)
        
        # Check if table exists
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        query = QueryBuilder.count_query(table_name)
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.scalar()
    
    def get_sample_data(self, table_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        # Check if table is filtered
        if not self.table_filter.is_table_allowed(table_name):
            raise TableAccessDeniedError(table_name)
        
        # Check if table exists
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        
        if limit <= 0:
            return []
        
        query, params = QueryBuilder.sample_query(table_name, limit)
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            columns = list(result.keys())
            
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert non-primitive types to string
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    row_dict[col] = value
                rows.append(row_dict)
            
            return rows
    
    def execute_query(self, query: str, timeout: int) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Execute a query with timeout.
        
        Args:
            query: SQL query to execute
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (results, column_names)
        """
        with self.engine.connect() as conn:
            # Set statement timeout for PostgreSQL
            if self.config.is_postgresql:
                conn.execute(text(f"SET LOCAL statement_timeout = {timeout * 1000}"))
            
            result = conn.execute(text(query))
            columns = list(result.keys())
            
            # Convert results to list of dicts
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    row_dict[col] = value
                rows.append(row_dict)
            
            return rows, columns
    
    def close(self):
        """Close database connections and cleanup resources."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._inspector = None
        
        # Cleanup BigQuery credentials file
        if self._bigquery_credentials_file and self.config.bigquery_config:
            self.config.bigquery_config.cleanup_credentials_file(self._bigquery_credentials_file)
            self._bigquery_credentials_file = None