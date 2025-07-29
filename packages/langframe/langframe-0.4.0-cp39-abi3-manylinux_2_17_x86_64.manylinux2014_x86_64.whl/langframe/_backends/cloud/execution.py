from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Literal, Optional, Tuple

import grpc
import polars as pl
import pyarrow as pa
import pyarrow.flight as flight  # noqa: F401 # Required to import flight.
from langframe_cloud.hasura_client.generated_graphql_client import (
    TypedefExecutionStatusReferenceEnum as QUERY_STATE,
)
from langframe_cloud.hasura_client.hasura_execution import (
    get_query_execution_by_id,
    query_execution_subscription,
)
from langframe_cloud.protos.engine.v1.engine_pb2 import (
    CollectExecutionRequest,
    CountExecutionRequest,
    GetExecutionResultRequest,
    GetExecutionResultResponse,
    ShowExecutionRequest,
    StartExecutionRequest,
)
from langframe_cloud.protos.engine.v1.engine_pb2_grpc import EngineServiceStub

from langframe._backends.base.execution import BaseExecution
from langframe._logical_plan.serde import LogicalPlanSerde
from langframe.api.metrics import LMMetrics, PhysicalPlanRepr, QueryMetrics, RMMetrics
from langframe.api.types import Schema

if TYPE_CHECKING:
    from langframe._backends.base.lineage import BaseLineage
    from langframe._backends.cloud.session_state import CloudSessionState
    from langframe._logical_plan.plans import LogicalPlan
    from langframe.api.metrics import QueryMetrics

import logging

logger = logging.getLogger(__name__)


class CloudExecution(BaseExecution):
    def __init__(self, session_state: CloudSessionState, engine_stub: EngineServiceStub):
        """Initialize the cloud execution client.

        Args:
            channel: A gRPC channel to communicate with the engine service.
        """
        self.session_state = session_state
        self._engine_stub = engine_stub
        logger.debug(
            f"Initialized enginestub with channel: {session_state.engine_channel}"
        )

    def collect(
        self, plan: LogicalPlan, n: Optional[int] = None
    ) -> Tuple[pl.DataFrame, QueryMetrics]:
        """Execute a logical plan and return a Polars DataFrame and query metrics."""

        request = StartExecutionRequest(
            collect=CollectExecutionRequest(
                serialized_plan=LogicalPlanSerde.serialize(plan)
            )
        )

        future = asyncio.run_coroutine_threadsafe(
            self._send_execution_request_and_wait(request),
            self.session_state.asyncio_loop,
        )
        execution_id = future.result()

        result_future = asyncio.run_coroutine_threadsafe(
            self._get_execution_result_from_arrow(execution_id),
            self.session_state.asyncio_loop,
        )
        df = result_future.result()

        return df, QueryMetrics(
            execution_time_ms=0.0,
            num_output_rows=0,
            total_lm_metrics=LMMetrics(),
            total_rm_metrics=RMMetrics(),
            _plan_repr=PhysicalPlanRepr(operator_id="empty"),
        )

    def show(self, plan: LogicalPlan, n: int = 10) -> Tuple[str, QueryMetrics]:
        """Execute a logical plan and return a string representation of the sample rows."""
        logger.debug(f"Sending show request: {plan}")
        request = StartExecutionRequest(
            show=ShowExecutionRequest(
                serialized_plan=LogicalPlanSerde.serialize(plan), row_limit=n
            )
        )
        future = asyncio.run_coroutine_threadsafe(
            self._send_execution_request_and_wait(request),
            self.session_state.asyncio_loop,
        )
        execution_id = future.result()

        result_future = asyncio.run_coroutine_threadsafe(
            self._get_execution_result(execution_id), self.session_state.asyncio_loop
        )
        result_response = result_future.result()

        if not result_response.HasField("show_result"):
            raise RuntimeError("Result of show execution did not include show string")

        # TODO: Get the metrics from hasura
        return result_response.show_result, QueryMetrics(
            execution_time_ms=0.0,
            num_output_rows=0,
            total_lm_metrics=LMMetrics(),
            total_rm_metrics=RMMetrics(),
            _plan_repr=PhysicalPlanRepr(operator_id="empty"),
        )

    def count(self, plan: LogicalPlan) -> Tuple[int, QueryMetrics]:
        """Execute a logical plan and return the number of rows."""
        request = StartExecutionRequest(
            count=CountExecutionRequest(
                serialized_plan=LogicalPlanSerde.serialize(plan)
            )
        )
        future = asyncio.run_coroutine_threadsafe(
            self._send_execution_request_and_wait(request),
            self.session_state.asyncio_loop,
        )
        execution_id = future.result()

        result_future = asyncio.run_coroutine_threadsafe(
            self._get_execution_result(execution_id), self.session_state.asyncio_loop
        )
        result_response = result_future.result()

        if not result_response.HasField("count_result"):
            raise RuntimeError("Result of count execution did not include count result")

        # TODO: Get the metrics from hasura
        return result_response.count_result, QueryMetrics(
            execution_time_ms=0.0,
            num_output_rows=0,
            total_lm_metrics=LMMetrics(),
            total_rm_metrics=RMMetrics(),
            _plan_repr=PhysicalPlanRepr(operator_id="empty"),
        )

    def build_lineage(self, plan: LogicalPlan) -> BaseLineage:
        """Build a lineage graph from a logical plan."""
        # TODO: Implement lineage building
        raise NotImplementedError(
            "Lineage building not implemented for cloud execution"
        )

    def save_as_table(
        self,
        logical_plan: LogicalPlan,
        table_name: str,
        mode: Literal["error", "append", "overwrite", "ignore"],
    ) -> QueryMetrics:
        """Execute the logical plan and save the result as a table."""
        # TODO: Implement table saving
        raise NotImplementedError("Table saving not implemented for cloud execution")

    def save_to_file(
        self,
        logical_plan: LogicalPlan,
        path: str,
        mode: Literal["error", "overwrite", "ignore"] = "error",
    ) -> QueryMetrics:
        """Execute the logical plan and save the result to a file."""
        # TODO: Implement file saving
        raise NotImplementedError("File saving not implemented")

    def save_as_csv(self, logical_plan: LogicalPlan, path: str) -> QueryMetrics:
        """Execute the logical plan and save the result as a CSV file."""
        # TODO: Implement CSV saving
        raise NotImplementedError("CSV saving not implemented for cloud execution")

    def save_as_parquet(self, logical_plan: LogicalPlan, path: str) -> QueryMetrics:
        """Execute the logical plan and save the result as a Parquet file."""
        # TODO: Implement Parquet saving
        raise NotImplementedError("Parquet saving not implemented for cloud execution")

    def infer_schema_from_csv(self, paths: list[str]) -> Schema:
        """Infer the schema of a CSV file."""
        # TODO: Implement CSV schema inference
        raise NotImplementedError(
            "CSV schema inference not implemented for cloud execution"
        )

    def infer_schema_from_parquet(self, paths: list[str]) -> Schema:
        """Infer the schema of a Parquet file."""
        # TODO: Implement Parquet schema inference
        raise NotImplementedError(
            "Parquet schema inference not implemented for cloud execution"
        )



    async def _send_execution_request_and_wait(
        self, request: StartExecutionRequest
    ) -> str:
        """Send a request to the engine service and return the execution id and query metrics."""
        logger.debug(f"Sending execution request: {request}")

        try:
            response = await self._engine_stub.StartExecution(
                request, metadata=self.session_state.get_engine_grpc_metadata()
            )
        except grpc.RpcError as e:
            raise RuntimeError(f"Failed to start execution: {e}") from e

        logger.debug(f"Execution response: {response}")
        execution_id = response.execution_id
        status = await query_execution_subscription(
            self.session_state.hasura_user_client,
            execution_id,
            [QUERY_STATE.READY, QUERY_STATE.FAILED],
        )
        if status == QUERY_STATE.FAILED:
            logger.error(f"Execution {execution_id} failed")
            execution_details = await get_query_execution_by_id(
                self.session_state.hasura_user_client, execution_id
            )
            raise RuntimeError(
                f"Execution {execution_id} failed: {execution_details.error_message}"
            )

        logger.info(f"Execution {execution_id} completed")
        return execution_id

    async def _get_execution_result(
        self, execution_id: str
    ) -> GetExecutionResultResponse:
        """Get the result of an execution."""
        result_request = GetExecutionResultRequest(execution_uuid=execution_id)
        try:
            result_response = await self._engine_stub.GetExecutionResult(
                result_request, metadata=self.session_state.get_engine_grpc_metadata()
            )
        except grpc.RpcError as e:
            raise RuntimeError(f"Failed to get execution result: {e}") from e
        return result_response

    async def _get_execution_result_from_arrow(self, execution_id: str) -> pl.DataFrame:
        """Get the result of an execution as a Polars DataFrame"""
        try:
            arrow_client = pa.flight.connect(
                f"grpc://{self.session_state.arrow_ipc_uri}"
            )
            reader = arrow_client.do_get(
                pa.flight.Ticket(str(execution_id).encode("utf-8"))
            )
            table = reader.read_all()
            return pl.DataFrame(table)
        except pa.flight.FlightServerError as e:
            raise RuntimeError(f"Failed to get execution result: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed while connecting to arrow IPC: {e}") from e
