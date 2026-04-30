from src.infrastructure.connectors.impl.csv.factory import CsvConnectorFactory
from src.infrastructure.connectors.impl.jobs_api.factory import JobsApiConnectorFactory
from src.infrastructure.connectors.impl.memory.factory import MemoryConnectorFactory
from src.infrastructure.connectors.impl.postgres.factory import PostgresConnectorFactory
from src.infrastructure.connectors.impl.snowflake.factory import SnowflakeConnectorFactory


CONNECTOR_FACTORIES = {
    "csv": CsvConnectorFactory(),
    "file": CsvConnectorFactory(),
    "jobs_api": JobsApiConnectorFactory(),
    "memory": MemoryConnectorFactory(),
    "postgres": PostgresConnectorFactory(),
    "snowflake": SnowflakeConnectorFactory(),
}