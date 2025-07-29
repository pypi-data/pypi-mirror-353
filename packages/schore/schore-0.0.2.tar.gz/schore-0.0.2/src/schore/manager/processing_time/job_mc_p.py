from typing import Self, TextIO, Type, TypeVar

import pandas as pd

from ..base.table_2d_manager import Table2DManager

ProcessingTimeT = TypeVar("ProcessingTimeT", bound=int)


class JobMachineProcessingTimeManager(Table2DManager):
    """rows for jobs, columns for machines"""

    def __init__(self, name: str, df: pd.DataFrame) -> None:
        super().__init__(name, df)

    @classmethod
    def from_text_stream(
        cls,
        stream: TextIO,
        row_count: int,
        dtype: Type[ProcessingTimeT] | None = None,
        sep: str | None = None,
        name: str = "JobMachineProcessingTimeManager",
    ) -> Self:
        return super().from_text_stream(stream, row_count, dtype, sep, name)

    def machine_2_job_2_value_map(
        self, mc_id_list: list[str], job_id_list: list[str]
    ) -> dict[str, dict[str, ProcessingTimeT]]:
        """
        Create a mapping from machine ID to job ID and value.

        Args:
            mc_id_list (list[str]): List of machine IDs (columns).
            job_id_list (list[str]): List of job IDs (rows).

        Returns:
            dict[str, dict[str, ProcessingTimeT]]: Machine ID -> Job ID -> Value.
        """
        assert len(mc_id_list) == self.col_count(), "machine count mismatch"
        assert len(job_id_list) == self.row_count(), "job count mismatch"

        return {
            mc_id: {
                job_id: self.df.iat[row_idx, col_idx]
                for row_idx, job_id in enumerate(job_id_list)
            }
            for col_idx, mc_id in enumerate(mc_id_list)
        }

    def machine_job_2_value_map(
        self, mc_id_list: list[str], job_id_list: list[str]
    ) -> dict[tuple[str, str], ProcessingTimeT]:
        """
        Create a mapping from machine ID to job ID and value.

        Args:
            mc_id_list (list[str]): List of machine IDs (columns).
            job_id_list (list[str]): List of job IDs (rows).

        Returns:
            dict[tuple[str, str], ProcessingTimeT]: (Machine ID, Job ID) -> Value.
        """
        assert len(mc_id_list) == self.col_count(), "machine count mismatch"
        assert len(job_id_list) == self.row_count(), "job count mismatch"

        return {
            (mc_id, job_id): self.df.iat[row_idx, col_idx]
            for row_idx, job_id in enumerate(job_id_list)
            for col_idx, mc_id in enumerate(mc_id_list)
        }

    def job_2_eligible_mc_list_map(
        self, job_id_list: list[str], mc_id_list: list[str]
    ) -> dict[str, list[str]]:
        """
        Create a mapping from job ID to eligible machine IDs.

        Args:
            job_id_list (list[str]): List of job IDs (rows).
            mc_id_list (list[str]): List of machine IDs (columns).

        Returns:
            dict[str, list[str]]: Job ID -> List of eligible machine IDs.
        """
        assert len(mc_id_list) == self.col_count(), "machine count mismatch"
        assert len(job_id_list) == self.row_count(), "job count mismatch"

        return {
            job_id: [
                mc_id
                for col_idx, mc_id in enumerate(mc_id_list)
                if self.df.iat[row_idx, col_idx] > 0
            ]
            for row_idx, job_id in enumerate(job_id_list)
        }
