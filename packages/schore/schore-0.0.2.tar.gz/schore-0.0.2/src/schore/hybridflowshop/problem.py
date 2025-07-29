from typing import TextIO

from .. import JobStageProcessingTimeManager
from ..util import TextDataParser


class HybridFlowShopProblem:
    """
    Represents a hybrid flow shop problem instance with multiple jobs and stages,
    where each stage may have multiple parallel machines.

    This class assumes all machines at a given stage are eligible for any operation at that stage.
    """  # noqa: E501

    name: str
    """Name of the problem instance."""

    job_count: int
    """Number of jobs in the problem instance."""
    stage_count: int
    """Number of stages in the problem instance."""
    machine_count_per_stage: list[int]
    """List of the number of parallel machines at each stage."""
    p_manager: JobStageProcessingTimeManager
    """Manager for processing times of jobs at each stage."""

    def __init__(
        self,
        name: str,
        job_count: int,
        stage_count: int,
        machine_count_per_stage: list[int],
        p_manager: JobStageProcessingTimeManager,
    ):
        self.name = name
        self.job_count = job_count
        self.stage_count = stage_count
        self.machine_count_per_stage = machine_count_per_stage  # e.g., [2, 3, 2]
        self.p_manager = p_manager

    def __repr__(self):
        return (
            f"HybridFlowShopProblem(job_count={self.job_count},"
            f" stage_count={self.stage_count})"
        )

    @classmethod
    def from_pra_data(cls, name: str, stream: TextIO) -> "HybridFlowShopProblem":
        """
        Parse hybrid flow shop problem instance from a text stream in PRA-style format.

        Expected format:
            <job_count>
            <stage_count>
            <machine_count_per_stage>  # space-separated list
            <processing_time_row_0>
            <processing_time_row_1>
            ...
            <processing_time_row_n-1>

        Args:
            name (str): Name of the problem instance.
            stream (TextIO): Input stream (e.g., open file or StringIO) containing instance data.

        Returns:
            HybridFlowShopProblem: Parsed problem instance.
        """  # noqa: E501
        job_count = TextDataParser.strip_a_typed_value(stream, int)
        stage_count = TextDataParser.strip_a_typed_value(stream, int)
        machine_count_per_stage = TextDataParser.strip_a_typed_list(stream, int)

        cls._validate_pra_structure(stage_count, machine_count_per_stage)

        processing_times = JobStageProcessingTimeManager.from_text_stream(
            stream, job_count, dtype=int
        )

        cls._validate_processing_times(stage_count, processing_times)

        return cls(
            name=name,
            job_count=job_count,
            stage_count=stage_count,
            machine_count_per_stage=machine_count_per_stage,
            p_manager=processing_times,
        )

    @staticmethod
    def _validate_pra_structure(stage_count: int, machine_count_per_stage: list[int]):
        if len(machine_count_per_stage) != stage_count:
            raise ValueError(
                f"Stage count mismatch; stage_count={stage_count};"
                f" by machine_count_per_stage={len(machine_count_per_stage)}"
            )

    @staticmethod
    def _validate_processing_times(
        stage_count: int, processing_times: JobStageProcessingTimeManager
    ):
        if processing_times.col_count() != stage_count:
            raise ValueError(
                f"Expected {stage_count} processing times per job,"
                f" got {processing_times.col_count()}."
            )
        if processing_times.df.isnull().values.any():
            raise ValueError("Null value exists in the processing time data.")

    def get_job_id_list(self) -> list[str]:
        """Generate a list of job IDs with zero-padded numbers."""
        num_digits = len(str(self.job_count - 1))
        return [f"j{str(j).zfill(num_digits)}" for j in range(self.job_count)]

    def get_stage_id_list(self) -> list[str]:
        """Generate a list of stage IDs with zero-padded numbers."""
        num_digits = len(str(self.stage_count - 1))
        return [f"i{str(s).zfill(num_digits)}" for s in range(self.stage_count)]

    def get_stage_2_machines_map(self) -> dict[str, list[str]]:
        """Generate a mapping from stage IDs to lists of machine IDs."""
        result: dict[str, list[str]] = {}
        for stage_idx, stage_id in enumerate(self.get_stage_id_list()):
            num_digits = len(str(self.machine_count_per_stage[stage_idx] - 1))
            machine_ids = [
                f"{stage_id}_{str(m).zfill(num_digits)}"
                for m in range(self.machine_count_per_stage[stage_idx])
            ]
            result[stage_id] = machine_ids
        return result
