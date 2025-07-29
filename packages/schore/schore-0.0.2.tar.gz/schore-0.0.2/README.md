# schore

Core classes for scheduling problems' definition

- `from schore import`
  - `DfManager`: A base class to manage a DataFrame.
  - `Table2DManager`: A class to manage a 2D table represented as a DataFrame.
  - `JobStageProcessingTimeManager`: A class to manage a 2D DataFrame with columns for stages & rows for jobs.
- `from schore.util import`
  - `TextDataParser`: A class to parse text data from a stream.
- `from schore.hybridflowshop import`
  - `HybridFlowShopProblem`: Hybrid flow shop problem instance with multiple jobs and stages, where each stage may have multiple parallel machines.
