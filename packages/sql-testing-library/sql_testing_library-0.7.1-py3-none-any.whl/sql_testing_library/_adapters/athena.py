"""Amazon Athena adapter implementation."""

import logging
import time
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Type, Union, get_args


if TYPE_CHECKING:
    import boto3
    import pandas as pd

# Heavy import moved to function level for better performance
from .._mock_table import BaseMockTable
from .._types import BaseTypeConverter
from .base import DatabaseAdapter


try:
    import boto3

    has_boto3 = True
except ImportError:
    has_boto3 = False
    boto3 = None  # type: ignore


class AthenaTypeConverter(BaseTypeConverter):
    """Athena-specific type converter."""

    def convert(self, value: Any, target_type: Type) -> Any:
        """Convert Athena result value to target type."""
        # Handle Athena NULL values (returned as string "NULL")
        if value == "NULL":
            return None

        # Athena returns proper Python types in most cases, so use base converter
        return super().convert(value, target_type)


class AthenaAdapter(DatabaseAdapter):
    """Amazon Athena adapter for SQL testing."""

    def __init__(
        self,
        database: str,
        s3_output_location: str,
        region: str = "us-west-2",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ) -> None:
        if not has_boto3:
            raise ImportError(
                "Athena adapter requires boto3. "
                "Install with: pip install sql-testing-library[athena]"
            )

        assert boto3 is not None  # For type checker

        self.database = database
        self.s3_output_location = s3_output_location
        self.region = region

        # Initialize Athena client
        if aws_access_key_id and aws_secret_access_key:
            self.client = boto3.client(
                "athena",
                region_name=region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        else:
            # Use default credentials from ~/.aws/credentials or environment variables
            self.client = boto3.client("athena", region_name=region)

    def get_sqlglot_dialect(self) -> str:
        """Return Athena dialect for sqlglot."""
        return "athena"

    def execute_query(self, query: str) -> "pd.DataFrame":
        """Execute query and return results as DataFrame."""
        import pandas as pd

        # Start query execution
        response = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": self.database},
            ResultConfiguration={"OutputLocation": self.s3_output_location},
        )

        query_execution_id = response["QueryExecutionId"]

        # Wait for query to complete
        query_status, error_info = self._wait_for_query_with_error(query_execution_id)
        if query_status != "SUCCEEDED":
            error_message = f"Athena query failed with status: {query_status}"
            if error_info:
                error_message += f";Error details: {error_info}"
            raise Exception(error_message)

        # Get query results
        results = self.client.get_query_results(QueryExecutionId=query_execution_id)

        # Convert to DataFrame
        if "ResultSet" in results and "Rows" in results["ResultSet"]:
            rows = results["ResultSet"]["Rows"]
            if not rows:
                return pd.DataFrame()

            # First row is header
            header = [col["VarCharValue"] for col in rows[0]["Data"]]

            # Rest are data
            data = []
            for row in rows[1:]:
                data.append([col.get("VarCharValue") for col in row["Data"]])

            df = pd.DataFrame(data)
            df.columns = header
            return df
        else:
            return pd.DataFrame()

    def create_temp_table(self, mock_table: BaseMockTable) -> str:
        """Create a temporary table in Athena using CTAS."""
        timestamp = int(time.time() * 1000)
        temp_table_name = f"temp_{mock_table.get_table_name()}_{timestamp}"
        qualified_table_name = f"{self.database}.{temp_table_name}"

        # Generate CTAS statement (CREATE TABLE AS SELECT)
        ctas_sql = self._generate_ctas_sql(temp_table_name, mock_table)

        # Execute CTAS query
        self.execute_query(ctas_sql)

        return qualified_table_name

    def create_temp_table_with_sql(self, mock_table: BaseMockTable) -> Tuple[str, str]:
        """Create a temporary table and return both table name and SQL."""
        timestamp = int(time.time() * 1000)
        temp_table_name = f"temp_{mock_table.get_table_name()}_{timestamp}"
        qualified_table_name = f"{self.database}.{temp_table_name}"

        # Generate CTAS statement (CREATE TABLE AS SELECT)
        ctas_sql = self._generate_ctas_sql(temp_table_name, mock_table)

        # Execute CTAS query
        self.execute_query(ctas_sql)

        return qualified_table_name, ctas_sql

    def cleanup_temp_tables(self, table_names: List[str]) -> None:
        """Clean up temporary tables."""
        for full_table_name in table_names:
            try:
                # Extract just the table name, not the database.table format
                if "." in full_table_name:
                    table_name = full_table_name.split(".")[-1]
                else:
                    table_name = full_table_name

                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                self.execute_query(drop_query)
            except Exception as e:
                logging.warning(f"Warning: Failed to drop table {full_table_name}: {e}")

    def format_value_for_cte(self, value: Any, column_type: type) -> str:
        """Format value for Athena CTE VALUES clause."""
        from .._sql_utils import format_sql_value

        return format_sql_value(value, column_type, dialect="athena")

    def get_type_converter(self) -> BaseTypeConverter:
        """Get Athena-specific type converter."""
        return AthenaTypeConverter()

    def get_query_size_limit(self) -> Optional[int]:
        """Return query size limit in bytes for Athena."""
        # Athena has a 256KB limit for query strings
        return 256 * 1024  # 256KB

    def _wait_for_query(self, query_execution_id: str, max_retries: int = 60) -> str:
        """Wait for query to complete, returns final status."""
        status, _ = self._wait_for_query_with_error(query_execution_id, max_retries)
        return status

    def _wait_for_query_with_error(
        self, query_execution_id: str, max_retries: int = 60
    ) -> tuple[str, Optional[str]]:
        """Wait for query to complete, returns final status and error info if failed."""
        for _ in range(max_retries):
            response = self.client.get_query_execution(QueryExecutionId=query_execution_id)
            query_execution = response["QueryExecution"]
            status = query_execution["Status"]["State"]

            # Explicitly cast to string to satisfy type checker
            query_status: str = str(status)

            if query_status in ("SUCCEEDED", "FAILED", "CANCELLED"):
                error_info = None
                if query_status in ("FAILED", "CANCELLED"):
                    # Extract error information
                    status_info = query_execution["Status"]
                    if "StateChangeReason" in status_info:
                        error_info = status_info["StateChangeReason"]
                    elif "AthenaError" in status_info:
                        athena_error = status_info["AthenaError"]
                        error_type = athena_error.get("ErrorType", "Unknown")
                        error_message = athena_error.get("ErrorMessage", "No details available")
                        error_info = f"{error_type}: {error_message}"

                return query_status, error_info

            # Wait before checking again
            time.sleep(1)

        # If we reached here, we timed out
        return "TIMEOUT", "Query execution timed out after waiting for completion"

    def _build_s3_location(self, table_name: str) -> str:
        """Build proper S3 location path avoiding double slashes."""
        # Remove trailing slash from s3_output_location if present
        base_location = self.s3_output_location.rstrip("/")
        return f"{base_location}/{table_name}/"

    def _generate_ctas_sql(self, table_name: str, mock_table: BaseMockTable) -> str:
        """Generate CREATE TABLE AS SELECT (CTAS) statement for Athena."""
        df = mock_table.to_dataframe()
        column_types = mock_table.get_column_types()
        columns = list(df.columns)

        if df.empty:
            # For empty tables, create an empty table with correct schema
            # Type mapping from Python types to Athena types
            type_mapping = {
                str: "VARCHAR",
                int: "INTEGER",
                float: "DOUBLE",
                bool: "BOOLEAN",
                date: "DATE",
                datetime: "TIMESTAMP",
                Decimal: "DECIMAL(38,9)",
            }

            # Generate column definitions
            column_defs = []
            for col_name, col_type in column_types.items():
                # Handle Optional types
                if hasattr(col_type, "__origin__") and col_type.__origin__ is Union:
                    # Extract the non-None type from Optional[T]
                    non_none_types = [arg for arg in get_args(col_type) if arg is not type(None)]
                    if non_none_types:
                        col_type = non_none_types[0]

                athena_type = type_mapping.get(col_type, "VARCHAR")
                column_defs.append(f'"{col_name}" {athena_type}')

            columns_sql = ",\n  ".join(column_defs)

            # Create an empty external table with the correct schema
            return f"""
            CREATE EXTERNAL TABLE {table_name} (
              {columns_sql}
            )
            STORED AS PARQUET
            LOCATION '{self._build_s3_location(table_name)}'
            """
        else:
            # For tables with data, use CTAS with a VALUES clause
            # Build a SELECT statement with literal values
            select_expressions = []

            # Generate column expressions for the first row
            first_row = df.iloc[0]
            for col_name in columns:
                col_type = column_types.get(col_name, str)
                value = first_row[col_name]

                # Handle Optional types by extracting the non-None type for proper formatting
                actual_type = col_type
                if hasattr(col_type, "__origin__") and col_type.__origin__ is Union:
                    # Extract the non-None type from Optional[T]
                    non_none_types = [arg for arg in get_args(col_type) if arg is not type(None)]
                    if non_none_types:
                        actual_type = non_none_types[0]

                formatted_value = self.format_value_for_cte(value, actual_type)
                select_expressions.append(f'{formatted_value} AS "{col_name}"')

            # Start with the first row in the SELECT
            select_sql = f"SELECT {', '.join(select_expressions)}"

            # Add UNION ALL for each additional row
            for i in range(1, len(df)):
                row = df.iloc[i]
                row_values = []
                for col_name in columns:
                    col_type = column_types.get(col_name, str)
                    value = row[col_name]

                    # Handle Optional types by extracting the non-None type for proper formatting
                    actual_type = col_type
                    if hasattr(col_type, "__origin__") and col_type.__origin__ is Union:
                        # Extract the non-None type from Optional[T]
                        non_none_types = [
                            arg for arg in get_args(col_type) if arg is not type(None)
                        ]
                        if non_none_types:
                            actual_type = non_none_types[0]

                    formatted_value = self.format_value_for_cte(value, actual_type)
                    row_values.append(formatted_value)

                select_sql += f"\nUNION ALL SELECT {', '.join(row_values)}"

            # Create the CTAS statement for external table
            return f"""
            CREATE TABLE {table_name}
            WITH (
                format = 'PARQUET',
                external_location = '{self._build_s3_location(table_name)}'
            )
            AS {select_sql}
            """
