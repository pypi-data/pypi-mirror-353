from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Tuple

import polars as pl

from langframe.api.types.schema import Schema

if TYPE_CHECKING:
    from langframe._backends import BaseLineage
    from langframe._logical_plan import LogicalPlan
    from langframe.api.metrics import QueryMetrics


class BaseExecution(ABC):
    @abstractmethod
    def collect(
        self, plan: LogicalPlan, n: Optional[int] = None
    ) -> Tuple[pl.DataFrame, "QueryMetrics"]:
        """Execute a logical plan and return a Polars DataFrame and query metrics."""
        pass

    @abstractmethod
    def show(self, plan: LogicalPlan, n: int = 10) -> Tuple[str, QueryMetrics]:
        """Execute a logical plan and return a string representation of the sample rows of the DataFrame and query metrics."""
        pass

    @abstractmethod
    def count(self, plan: LogicalPlan) -> Tuple[int, QueryMetrics]:
        """Execute a logical plan and return the number of rows in the DataFrame and query metrics."""
        pass

    @abstractmethod
    def build_lineage(self, plan: LogicalPlan) -> BaseLineage:
        """Build a lineage graph from a logical plan."""
        pass

    @abstractmethod
    def save_as_table(
        self,
        logical_plan: LogicalPlan,
        table_name: str,
        mode: Literal["error", "append", "overwrite", "ignore"],
    ) -> QueryMetrics:
        """Execute the logical plan and save the result as a table in the current database."""
        pass

    @abstractmethod
    def save_to_file(
        self,
        logical_plan: LogicalPlan,
        file_path: str,
        mode: Literal["error", "overwrite", "ignore"] = "error",
    ) -> QueryMetrics:
        """Execute the logical plan and save the result to a file."""
        pass

    @abstractmethod
    def infer_schema_from_csv(
        self, paths: list[str], **options: Dict[str, Any]
    ) -> Schema:
        """Infer the schema of a CSV file"""
        pass

    @abstractmethod
    def infer_schema_from_parquet(
        self, paths: list[str], **options: Dict[str, Any]
    ) -> Schema:
        """Infer the schema of a Parquet file"""
        pass
