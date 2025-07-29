"""
Logical plan module for query representation.

Note: These classes are not part of the public API and should not be used directly.
"""

from langframe._logical_plan.plans.aggregate import Aggregate, SemanticAggregate
from langframe._logical_plan.plans.base import CacheInfo, LogicalPlan
from langframe._logical_plan.plans.join import (
    Join,
    SemanticJoin,
    SemanticSimilarityJoin,
)
from langframe._logical_plan.plans.sink import FileSink, TableSink
from langframe._logical_plan.plans.source import FileSource, InMemorySource, TableSource
from langframe._logical_plan.plans.transform import (
    DropDuplicates,
    Explode,
    Filter,
    Limit,
    Projection,
    Sort,
    Union,
)
from langframe._logical_plan.plans.transform import Unnest as Unnest

__all__ = [
    "Aggregate",
    "SemanticAggregate",
    "CacheInfo",
    "LogicalPlan",
    "Join",
    "SemanticJoin",
    "SemanticSimilarityJoin",
    "FileSink",
    "TableSink",
    "FileSource",
    "InMemorySource",
    "TableSource",
    "DropDuplicates",
    "Explode",
    "Filter",
    "Limit",
    "Projection",
    "Sort",
    "Union",
    "Unnest",
]
