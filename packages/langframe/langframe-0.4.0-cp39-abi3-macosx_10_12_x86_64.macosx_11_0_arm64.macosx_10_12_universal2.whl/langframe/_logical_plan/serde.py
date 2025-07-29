import pickle  # nosec: B403

from langframe._backends.base.session_state import BaseSessionState
from langframe._logical_plan.plans.base import LogicalPlan


class LogicalPlanSerde:
    @staticmethod
    def serialize(plan: LogicalPlan) -> bytes:
        """
        Serialize a LogicalPlan to bytes using pickle.

        Removes any local execution refs from the plan (from FileSource).

        Args:
            plan: The LogicalPlan to serialize

        Returns:
            bytes: The serialized plan
        """

        def make_pure_logical_plan_copy(plan: LogicalPlan) -> LogicalPlan:
            new_children = []
            for child in plan.children():
                new_children.append(make_pure_logical_plan_copy(child))
            return plan.with_children_for_serde(new_children, None)

        return pickle.dumps(make_pure_logical_plan_copy(plan))

    @staticmethod
    def deserialize(data: bytes) -> LogicalPlan:
        """
        Deserialize bytes back into a LogicalPlan using pickle.

        Args:
            data: The serialized plan data

        Returns:
            The deserialized plan
        """
        return pickle.loads(data)  # nosec: B301

    @staticmethod
    def build_logical_plan_with_session_state(
        plan: LogicalPlan, session: BaseSessionState
    ) -> LogicalPlan:
        """
        Build a LogicalPlan with the session state. FileSources will be built with the session's execution ref
        and TableSources will be built with the session's catalog ref.

        Args:
            plan: The LogicalPlan to build
            session: The session state
        """
        # TODO(DY): replace pickle with substrait so we don't need this step
        new_children = []
        for child in plan.children():
            new_children.append(
                LogicalPlanSerde.build_logical_plan_with_session_state(child, session)
            )
        return plan.with_children_for_serde(new_children, session)
