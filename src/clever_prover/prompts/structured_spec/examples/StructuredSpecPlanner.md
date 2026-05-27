`conv start`

`example_user`
[NL DESCRIPTION]
def find_magnitude(x: int) -> int
"""
Given an integer x, your task is to find the magnitude of x.
The magnitude of an integer is defined as the absolute value of the integer.
"""

[SPECIFICATION SIGNATURE]
def generated_spec
-- function signature
(impl: Int → Int)
-- inputs
(x: Int) : Prop :=

`example_assistant`
[SPEC PLAN]
[PROBLEM SUMMARY]
The function returns the absolute value of an integer input.

[INPUTS]
- `x`: the integer whose magnitude should be returned

[OUTPUT]
- the return value is the magnitude of `x`, i.e. the nonnegative integer equal to `x` if `x >= 0` and `-x` if `x < 0`

[PRECONDITIONS]
- None

[CASE SPLITS]
- `x >= 0`
- `x < 0`

[SEMANTIC CONSTRAINTS]
- the implementation must return some result
- if `x >= 0`, the result should equal `x`
- if `x < 0`, the result should equal `-x`
- the result should be nonnegative

[QUANTIFIER / SHAPE]
- use `∃ result, impl x = result ∧ ...`
- define a local `spec` predicate on `result`
- express the sign cases with implication or conjunctions inside `spec`

[LEAN CONSTRUCTION HINTS]
- a local `let spec (result : Int) := ...` is appropriate
- keep the proposition simple and directly tied to the result

[CONFIDENCE NOTES]
- High confidence: the result is absolute value with two sign cases
- Low confidence: whether nonnegativity needs to be stated explicitly or is derivable from the case split
[END]


`example_user`
[NL DESCRIPTION]
def is_square(x: int, y: int) -> bool
"""
Given two integers x and y, your task is to find if x is a square of y.
The function should return true if x is a square of y, otherwise false.
"""

[SPECIFICATION SIGNATURE]
def generated_spec
-- function signature
(impl: Int → Int → Bool)
-- inputs
(x: Int)
(y: Int) : Prop :=

`example_assistant`
[SPEC PLAN]
[PROBLEM SUMMARY]
The function should decide whether `x` equals the square of `y`.

[INPUTS]
- `x`: the candidate square value
- `y`: the integer whose square is being checked

[OUTPUT]
- the return value is a boolean indicating whether `x = y^2`

[PRECONDITIONS]
- None

[CASE SPLITS]
- `x = y * y`
- `x ≠ y * y`

[SEMANTIC CONSTRAINTS]
- the implementation must return some boolean result
- the result is true exactly when `x = y^2`

[QUANTIFIER / SHAPE]
- use `∃ result, impl x y = result ∧ ...`
- define a local `spec` predicate on the boolean result
- use a biconditional relating `result = true` and the arithmetic condition

[LEAN CONSTRUCTION HINTS]
- it is often easier for later proof to express the boolean meaning with `result = true ↔ ...`
- keep arithmetic notation stable and proof-friendly

[CONFIDENCE NOTES]
- High confidence: the result should characterize whether `x` is the square of `y`
- Low confidence: whether to express the arithmetic condition as `y * y` or `y^2`
[END]

`conv end`
