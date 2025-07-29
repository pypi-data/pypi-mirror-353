import io

import pytest

from src.schore import JobStageProcessingTimeManager
from src.schore.hybridflowshop import HybridFlowShopProblem


@pytest.fixture
def pra_data_stream():
    """Fixture to provide a sample PRA data stream."""
    data = """\
6
3
2 3 2
2 3 4
6 4 8
9 1 5
4 6 3
1 5 10
4 8 12
"""
    return io.StringIO(data)


@pytest.fixture
def problem(pra_data_stream):
    """Fixture to parse the PRA data into a HybridFlowShopProblem."""
    return HybridFlowShopProblem.from_pra_data("from_pra_data", pra_data_stream)


def test_problem_structure(problem: HybridFlowShopProblem):
    """Test the overall structure of the parsed problem."""
    assert problem.job_count == 6
    assert problem.stage_count == 3
    assert problem.machine_count_per_stage == [2, 3, 2]
    assert isinstance(
        problem.p_manager, JobStageProcessingTimeManager
    )  # Ensure p_manager is initialized


def test_invalid_machine_line_length():
    """Test that invalid machine line length raises a ValueError."""
    bad_data = """\
6
3
2 2
2 3 4
6 4 8
9 1 5
4 6 3
1 5 10
4 8 12
"""
    with pytest.raises(
        ValueError,
        match=r"Stage count mismatch; stage_count=\d+; by machine_count_per_stage=\d+",
    ):
        HybridFlowShopProblem.from_pra_data("from_pra_data", io.StringIO(bad_data))


def test_invalid_processing_time_row():
    """Test that invalid processing time row raises a ValueError."""
    bad_data = """\
6
3
2 3 2
2 3 4
6 4
9 1 5
4 6 3
1 5 10
4 8 12
"""
    with pytest.raises(
        ValueError, match="Null value exists in the processing time data."
    ):
        HybridFlowShopProblem.from_pra_data("from_pra_data", io.StringIO(bad_data))


def test_job_id_list(problem: HybridFlowShopProblem):
    """Test the generation of job IDs."""
    expected_job_ids = ["j0", "j1", "j2", "j3", "j4", "j5"]
    assert problem.get_job_id_list() == expected_job_ids


def test_stage_id_list(problem: HybridFlowShopProblem):
    """Test the generation of stage IDs."""
    expected_stage_ids = ["i0", "i1", "i2"]
    assert problem.get_stage_id_list() == expected_stage_ids


def test_stage_to_machine_mapping(problem: HybridFlowShopProblem):
    """Test the mapping from stage IDs to machine IDs."""
    expected_mapping = {
        "i0": ["i0_0", "i0_1"],
        "i1": ["i1_0", "i1_1", "i1_2"],
        "i2": ["i2_0", "i2_1"],
    }
    assert problem.get_stage_2_machines_map() == expected_mapping


def test_repr(problem: HybridFlowShopProblem):
    """Test the __repr__ methods."""
    assert repr(problem) == "HybridFlowShopProblem(job_count=6, stage_count=3)"
