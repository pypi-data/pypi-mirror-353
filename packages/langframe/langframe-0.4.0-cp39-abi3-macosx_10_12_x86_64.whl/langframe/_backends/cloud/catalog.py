import asyncio
import logging
import threading
from dataclasses import dataclass
from typing import Any, Coroutine, Dict, List, Optional
from uuid import UUID

import polars as pl
import pyarrow as pa
from langframe_cloud.hasura_client.generated_graphql_client.client import (
    CatalogDispatchInput,
)
from langframe_cloud.hasura_client.generated_graphql_client.enums import (
    CatalogDatasetTypeReferenceEnum,
)
from langframe_cloud.hasura_client.generated_graphql_client.list_catalogs_for_organization import (
    ListCatalogsForOrganization,
)
from langframe_cloud.hasura_client.generated_graphql_client.load_table import (
    LoadTableSimpleCatalogLoadTable,
)

from langframe._backends import BaseCatalog
from langframe._backends.cloud.manager import CloudSessionManager
from langframe._backends.cloud.session_state import CloudSessionState
from langframe._backends.local.catalog import (
    DEFAULT_CATALOG_NAME,
    DEFAULT_DATABASE_NAME,
)
from langframe._backends.utils.catalog_utils import (
    DBIdentifier,
    TableIdentifier,
    compare_object_names,
)

#from langframe._backends.cloud.session_state import RemoteSessionState
from langframe._utils.schema import convert_polars_schema_to_custom_schema
from langframe.api.types import Schema

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CatalogKey:
    catalog_name: str
    catalog_id: UUID


class CloudCatalog(BaseCatalog):
    """
    A catalog for cloud execution mode. Implements the BaseCatalog -
    all table reads and writes should go through this class for unified table name canonicalization.
    """

    def __init__(self, session_state: CloudSessionState, cloud_session_manager: CloudSessionManager):
        """Initialize the remote catalog."""
        self.session_state = session_state
        self.lock = threading.Lock()
        self.current_catalog_id: UUID = UUID(session_state.ephemeral_catalog_id)
        self.current_catalog_name: str = DEFAULT_CATALOG_NAME
        self.current_database_name: str = DEFAULT_DATABASE_NAME
        self.user_id = cloud_session_manager.user_id
        self.organization_id = cloud_session_manager.organization_id
        self.user_client = cloud_session_manager.hasura_user_client

    def does_catalog_exist(self, catalog_name: str) -> bool:
        """Checks if a catalog with the specified name exists."""
        with self.lock:
            return self._does_catalog_exist(catalog_name)

    def get_current_catalog(self) -> str:
        """Get the name of the current catalog."""
        with self.lock:
            return self.current_catalog_name

    def set_current_catalog(self, catalog_name: str) -> None:
        """Set the current catalog."""
        if not catalog_name:
            raise ValueError("No catalog name provided")

        with self.lock:
            self._set_current_catalog(catalog_name)

    def list_catalogs(self) -> List[str]:
        """Get a list of all catalogs."""
        with self.lock:
            catalogs = self._get_catalogs_for_organization()
            # iterate over catalogs but exclude the ephemeral catalog name,
            # this will be added as the default catalog.
            remote_catalogs = [catalog.name for catalog in catalogs.values()]
            remote_catalogs.append(DEFAULT_CATALOG_NAME)
            return remote_catalogs

    # Database operations
    def does_database_exist(self, database_name: str) -> bool:
        """Checks if a database with the specified name exists in the current catalog."""
        with self.lock:
            db_identifier = DBIdentifier.from_string(database_name).enrich(
                self.current_catalog_name
            )
            return self._does_database_exist(db_identifier.catalog, db_identifier.db)

    def get_current_database(self) -> str:
        """Get the name of the current database in the current catalog."""
        with self.lock:
            return self.current_database_name

    def set_current_database(self, database_name: str) -> None:
        """Sets the current database.
        The database name can be fully qualified or not.
        If it is not fully qualified, the current catalog will be used to resolve the database.
        If it is fully qualified, we'll attempt to resolve it against the catalog provided in the db name.
        """
        with self.lock:
            if not database_name:
                raise ValueError("No database name provided")

            db_identifier = DBIdentifier.from_string(database_name).enrich(
                self.current_catalog_name
            )
            if not self._does_database_exist(db_identifier.catalog, db_identifier.db):
                raise ValueError(
                    f"Database {db_identifier.db} does not exist in catalog {db_identifier.catalog}"
                )

            self.current_database_name = db_identifier.db
            if not db_identifier.is_catalog_name_equal(self.current_catalog_name):
                self._set_current_catalog(db_identifier.catalog)

            logger.info(f"current catalog: {self.current_catalog_name}")
            logger.info(f"current database: {self.current_database_name}")

    def list_databases(self) -> List[str]:
        """Get a list of all databases in the current catalog."""
        with self.lock:
            return self._get_databases_for_catalog()

    def create_database(
        self, database_name: str, ignore_if_exists: bool = True
    ) -> bool:
        """Create a new database in the current catalog."""
        pass

    def drop_database(
        self,
        database_name: str,
        cascade: bool = False,
        ignore_if_not_exists: bool = True,
    ) -> bool:
        """Drop a database from the current catalog."""
        pass

    # Table operations
    def does_table_exist(self, table_name: str) -> bool:
        """Checks if a table with the specified name exists in the current database."""
        with self.lock:
            table_identifier = TableIdentifier.from_string(table_name).enrich(
                self.current_catalog_name, self.current_database_name
            )
            return self._does_table_exist(
                table_identifier.catalog, table_identifier.db, table_identifier.table
            )

    def list_tables(self) -> List[str]:
        """Get a list of all tables in the current database."""
        with self.lock:
            return self._get_tables_for_database(
                self.current_catalog_name,
                self.current_database_name,
            )

    def describe_table(self, table_name: str) -> Schema:
        """Get the schema of the specified table."""
        with self.lock:
            table_identifier = TableIdentifier.from_string(table_name).enrich(
                self.current_catalog_name,
                self.current_database_name,
            )

            if not self._does_table_exist(
                table_identifier.catalog, table_identifier.db, table_identifier.table
            ):
                raise ValueError(f"Table {table_name} does not exist")

            return self._get_table_details(
                table_identifier.catalog,
                table_identifier.db,
                table_identifier.table,
            )

    def drop_table(self, table_name: str, ignore_if_not_exists: bool = True) -> bool:
        """Drop a table from the current database."""
        pass

    def create_table(
        self, table_name: str, schema: Schema, ignore_if_exists: bool = True
    ) -> bool:
        """Create a new table in the current database."""
        pass

    def _does_table_exist(
        self, catalog_name: str, db_name: str, table_name: str
    ) -> bool:
        if not compare_object_names(self.current_catalog_name, catalog_name):
            if not self._does_catalog_exist(catalog_name):
                return False

        if not self._does_database_exist(catalog_name, db_name):
            return False

        tables = self._get_tables_for_database(catalog_name, db_name)
        return any(compare_object_names(table, table_name) for table in tables)

    def _set_current_catalog(self, catalog_name: str) -> None:
        if not catalog_name:
            raise ValueError("No catalog name provided")

        if compare_object_names(catalog_name, self.current_catalog_name):
            return

        if compare_object_names(catalog_name, DEFAULT_CATALOG_NAME):
            self.current_catalog_id = UUID(self.session_state.ephemeral_catalog_id)
            self.current_catalog_name = DEFAULT_CATALOG_NAME
            return

        catalog = self._get_catalog_by_name(catalog_name)
        if not catalog:
            raise ValueError(f"Catalog {catalog_name} does not exist")

        self.current_catalog_id = catalog.catalog_id
        self.current_catalog_name = catalog.catalog_name

    def _does_catalog_exist(self, catalog_name: str) -> bool:
        if compare_object_names(DEFAULT_CATALOG_NAME, catalog_name):
            return True

        if compare_object_names(self.current_catalog_name, catalog_name):
            return True

        catalog = self._get_catalog_by_name(catalog_name)
        return True if catalog else False

    def _get_catalogs_for_organization(self) -> Dict[str, ListCatalogsForOrganization]:
        result = self._execute_catalog_command(
            self.user_client.list_catalogs_for_organization(
                parent_organization_id=self.organization_id
            )
        )
        filtered_catalogs = [
            catalog for catalog in result.catalogs if not catalog.ephemeral
        ]
        return {catalog.name.casefold(): catalog for catalog in filtered_catalogs}

    def _does_database_exist(self, catalog_name: str, database_name: str) -> bool:
        """
        Checks if a database with the specified name exists in the specified catalog.
        """
        if not compare_object_names(self.current_catalog_name, catalog_name):
            if not self._does_catalog_exist(catalog_name):
                return False

        databases = self._get_databases_for_catalog(catalog_name)
        return any(
            compare_object_names(database, database_name) for database in databases
        )

    def _execute_catalog_command(self, command: Coroutine[Any, Any, Any]) -> Any:
        return asyncio.run_coroutine_threadsafe(
            command, self.session_state.asyncio_loop
        ).result()

    def _get_catalog_by_name(self, catalog_name: str) -> Optional[CatalogKey]:
        if compare_object_names(catalog_name, self.current_catalog_name):
            return (self.current_catalog_name, self.current_catalog_id)

        catalogs = self._get_catalogs_for_organization()
        catalog = catalogs.get(catalog_name.casefold(), None)
        if not catalog:
            return None
        return CatalogKey(catalog.name.casefold(), catalog.catalog_id)

    def _get_catalog_id(self, catalog_name: str) -> UUID:
        # this takes care of both the default catalog and the current catalog.
        if compare_object_names(catalog_name, self.current_catalog_name):
            return self.current_catalog_id

        catalog = self._get_catalog_by_name(catalog_name)
        if not catalog:
            raise ValueError(f"Catalog {catalog_name} does not exist")
        return catalog.catalog_id

    def _get_databases_for_catalog(
        self,
        catalog_name: Optional[str] = None,
    ) -> List[str]:
        if not catalog_name:
            catalog_name = self.current_catalog_name
        catalog_id = self._get_catalog_id(catalog_name)
        result = self._execute_catalog_command(
            self.user_client.list_namespaces(
                dispatch=self._get_catalog_dispatch_input(catalog_id)
            )
        )
        databases = [
            namespace.name for namespace in result.simple_catalog.list_namespaces
        ]

        # in case we are in the current catalog, always return the default database.
        if self.current_catalog_name == DEFAULT_CATALOG_NAME:
            databases.append(DEFAULT_DATABASE_NAME)

        return databases

    def _get_tables_for_database(
        self,
        catalog_name: str,
        db_name: str,
    ) -> List[str]:
        catalog_id = self._get_catalog_id(catalog_name)
        result = self._execute_catalog_command(
            self.user_client.get_dataset_names_for_catalog_namespace(
                catalog_id=catalog_id,
                namespace=db_name,
                dataset_type=CatalogDatasetTypeReferenceEnum.TABLE,
            )
        )
        return [dataset.name for dataset in result.catalog_dataset]

    def _get_table_details(
        self, catalog_name: str, db_name: str, table_name: str
    ) -> Schema:
        catalog_id = self._get_catalog_id(catalog_name)
        result = self._execute_catalog_command(
            self.user_client.load_table(
                dispatch=self._get_catalog_dispatch_input(catalog_id),
                namespace=db_name,
                name=table_name,
            )
        )
        return self._get_table_schema(result.simple_catalog.load_table)

    def _get_catalog_dispatch_input(
        self,
        catalog_id: Optional[UUID] = None,
    ) -> CatalogDispatchInput:
        """builds a CatalogDispatchInput object for the current catalog or the specified catalog."""
        return CatalogDispatchInput(
            catalog_id=catalog_id if catalog_id else self.current_catalog_id,
            parent_organization_id=self.organization_id,
            requested_by_user_id=self.user_id,
        )

    @staticmethod
    def _get_table_schema(table_details: LoadTableSimpleCatalogLoadTable) -> Schema:
        schema = table_details.schema_
        pa_fields = []
        for field in schema.fields:
            pa_fields.append(
                pa.field(
                    field.name,
                    CloudCatalog._get_schema_type_to_pyarrow(field.arrow_data_type),
                )
            )

        pa_schema = pa.schema(pa_fields)
        empty_table = pa.Table.from_batches([], schema=pa_schema)
        polars_schema = pl.from_arrow(empty_table).schema
        return convert_polars_schema_to_custom_schema(polars_schema)

    @staticmethod
    def _get_schema_type_to_pyarrow(schema_type: str):
        """
        Convert the schema type to a pyarrow type.
        """
        if schema_type.startswith("Decimal"):
            return pa.float64()
        else:
            return schema_type