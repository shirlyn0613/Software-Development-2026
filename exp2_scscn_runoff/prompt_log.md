# Prompt Log - Experiment 2

Documentation of AI interactions

---

## Part 0: Initial

**prompt 1**

> read this document know the basic information, and generate empty file which are ought to be submitted

**answer 1**

> I read [Experiment2_SCSCN_Runoff.docx](Experiment2_SCSCN_Runoff.docx). It is a 2-hour lab handout for **Specialized Experiment 2: Hydrological Modeling: SCS-CN Runoff Calculation** in the **Smart Water Lab Series**.
>
> Main points:
>
> - **Goal:** implement the SCS-CN runoff method in Python, validate boundary conditions, and perform sensitivity analysis.
> - **Learning objectives:** translate formulas into code, handle physical boundary conditions, run tests, validate physical correctness, and document AI interactions.
> - **Core tasks:**
>   1. Implement `calculate_runoff(P, CN)`
>   2. Test boundary conditions such as `P < Ia`, `P = Ia`, and `CN = 100`
>   3. Analyze runoff sensitivity across multiple CN values
>   4. Validate `Q <= P` and document findings
> - **Deliverables:**
>   - `scscn_runoff.py`
>   - `test_scscn.py`
>   - `sensitivity_analysis.py`
>   - `runoff_comparison.png`
>   - `prompt_log.md`
> - **Expected behavior:** higher CN should produce higher runoff, and runoff should be zero when rainfall is below initial abstraction.
>
> I also created the empty submission files in this directory:
>
> - `scscn_runoff.py`
> - `test_scscn.py`
> - `sensitivity_analysis.py`
> - `runoff_comparison.png`
> - `prompt_log.md`

## Part 1: Formula Implementation

**prompt 1**

> I am implementing the SCS-CN runoff calculation method. Please write a Python function calculate_runoff(P, CN) that: 1. Calculates S using: S = (25400 / CN) - 254 2. Calculates Ia = 0.2 * S 3. Returns Q = 0 if P < Ia 4. Otherwise returns Q = (P - Ia)^2 / (P - Ia + S) 5. Ensures Q never exceeds P Include docstring and type hints.

**answer 1**

> Created `calculate_runoff(P, CN)` in `scscn_runoff.py` with type hints and a docstring.
>
> The function:
>
> - returns `0.0` for invalid or impervious-style edge inputs
> - computes `S = (25400 / CN) - 254`
> - computes `Ia = 0.2 * S`
> - returns `0.0` when `P < Ia`
> - otherwise computes runoff with the SCS-CN formula
> - clamps runoff so it never exceeds rainfall

## Part 2: Boundary Condition Testing

**prompt 1**

> Test Cases to Implement: 1. P = 0: Expected Q = 0 2. P < Ia: Expected Q = 0 3. P = Ia: Expected Q = 0 4. Normal case: P = 50mm, CN = 80 5. Maximum CN: CN = 100 6. Verify Q ≤ P for all cases

**answer 1**

> Created `test_scscn.py` with unit tests for:
>
> - zero rainfall
> - rainfall below initial abstraction
> - rainfall equal to initial abstraction
> - a normal case at `P = 50`, `CN = 80`
> - maximum curve number behavior
> - the physical constraint `Q <= P` across several rainfall and CN values

## Part 3: Sensitivity Analysis

**prompt 1**

> Sensitivity Analysis Requirements: 1. Fix P = 50mm 2. Calculate Q for CN = [60, 70, 80, 90, 95, 100] 3. Create a line plot: CN vs Q 4. Create a comparison plot: Rainfall vs Runoff for different CN values 5. Document observations about the relationship

**answer 1**

> Created `sensitivity_analysis.py` to:
>
> - compute runoff at `P = 50 mm` for `CN = [60, 70, 80, 90, 95, 100]`
> - draw a CN vs runoff line plot
> - draw a rainfall vs runoff comparison plot for multiple CN values
> - save the figure as `runoff_comparison.png`
>
> Observation to document later:
>
> - runoff increases as CN increases
> - higher CN curves rise faster for the same rainfall
> - `CN = 100` behaves like nearly impervious runoff response

## Part 4: Optional Extensions

**prompt 1**

> next part about extensions • Implement time-area method for watershed routing • Add antecedent moisture condition (AMC) adjustments • Create interactive plot with sliders for P and CN • Compare SCS-CN with other runoff methods (Rational method)

**answer 1**

> Added extension utilities in `runoff_extensions.py`:
>
> - AMC adjustment for Curve Number values under conditions I, II, and III
> - Rational Method peak discharge calculation
> - a simple discrete time-area routing function
> - a comparison helper between SCS-CN and Rational Method outputs
>
> Added `interactive_runoff_plot.py` to provide an interactive matplotlib plot with sliders for `P` and `CN`.
>
> Added `test_extensions.py` to verify:
>
> - AMC ordering behavior
> - Rational Method calculation
> - basic routing output shape and nonnegativity
> - comparison table generation
