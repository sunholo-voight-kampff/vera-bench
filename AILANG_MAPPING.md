# AILANG ↔ VeraBench Problem Mapping

This document maps each VeraBench problem to the AILANG source material that informed the reference solution. The mapping is informal — most problems are small enough that adaptation from an existing benchmark is "look up the AILANG idiom, write 10–30 lines."

## Solution pattern (matches Aver runner)

Following the established `solutions/aver/*.av` pattern: each `solutions/ailang/*.ail` file is a minimal AILANG module that:
1. Defines the entry-point function (per the problem JSON's `entry_point`)
2. Has `export func main() -> () ! {IO}` that calls the function with each test-case args and prints the result on its own line
3. Output lines are compared against `test_cases[].expected` in order

The runner (`run_ailang_baseline` in `vera_bench/baseline_runner.py`) just executes `ailang run --entry main <baseline>` and does line-by-line stdout matching, mirroring how Aver works.

## Per-tier mapping

### Tier 1 — Pure arithmetic (10 problems)

Direct AILANG primitives. All ten map to `if`-as-expression, `Int.mod`, simple comparison patterns. No existing benchmark required as a base — these are 5–10 line solutions.

| Problem | AILANG idiom |
|---------|--------------|
| VB_T1_001 absolute_value | `if x < 0 then -x else x` |
| VB_T1_002 clamp | nested if-else |
| VB_T1_003 signum | nested if-else returning -1/0/1 |
| VB_T1_004 max_of_two | `if a > b then a else b` |
| VB_T1_005 min_of_two | mirror of max |
| VB_T1_006 is_positive | comparison + show |
| VB_T1_007 safe_modulo | guard for div-by-zero |
| VB_T1_008 distance | absolute value of difference |
| VB_T1_009 max_of_three | reuse max_of_two |
| VB_T1_010 double_or_nothing | conditional doubling |

### Tier 2 — String & array (15 problems)

AILANG has `std/string` (concat, length, contains, startsWith, endsWith) and `std/list` (length, filter, map, foldl). All 15 should map cleanly. Reference: existing `benchmarks/list_comprehension.yml`, `benchmarks/fold_reduce.yml`, `benchmarks/balanced_parens.yml`.

| Problem | AILANG idiom |
|---------|--------------|
| VB_T2_001 sum_array | `foldl(+, 0, xs)` |
| VB_T2_002 filter_positives | `filter(\x. x > 0, xs)` |
| VB_T2_003 greeting | string interpolation `"Hello, ${name}"` |
| VB_T2_004 is_empty_string | `length(s) == 0` |
| VB_T2_005 contains_substring | `contains(s, sub)` from std/string |
| VB_T2_006 join_strings | recursive concat with separator |
| VB_T2_007 double_elements | `map(\x. x * 2, xs)` |
| VB_T2_008 count_positives | filter + length |
| VB_T2_009 to_upper | per-char or std/string function |
| VB_T2_010 sum_positives | filter + foldl |
| VB_T2_011 starts_with_prefix | `startsWith` from std/string |
| VB_T2_012 ends_with_suffix | `endsWith` from std/string |
| VB_T2_013 get_char_code | string indexing primitive |
| VB_T2_014 combined_length | length addition |
| VB_T2_015 is_longer_than | length comparison |

**Likely AILANG stdlib gaps to surface in M3**: `to_upper`, `get_char_code` may not be in std/string. Document any gaps; may need to skip or implement on the fly.

### Tier 3 — ADTs & match (15 problems)

AILANG's strength tier. Reference: `benchmarks/adt_option.yml`, `benchmarks/binary_tree_sum.yml`, `benchmarks/expression_evaluator.yml`, `benchmarks/exhaustive_pattern_matching.yml`.

| Problem | AILANG idiom |
|---------|--------------|
| VB_T3_001 list_length | match on cons-list |
| VB_T3_002 tree_depth | recursive match on tree ADT |
| VB_T3_003 expression_evaluator | DIRECT analog: `benchmarks/expression_evaluator.yml` |
| VB_T3_004 list_sum | foldl + or match-recurse |
| VB_T3_005 tree_sum | DIRECT analog: `benchmarks/binary_tree_sum.yml` |
| VB_T3_006 option_unwrap_or | match `Option` with default |
| VB_T3_007 list_contains | match-recurse + comparison |
| VB_T3_008 tree_count_leaves | recursive match on tree |
| VB_T3_009 list_append | structural recursion |
| VB_T3_010 list_last | match on `[x]` and `[h, ...t]` |
| VB_T3_011 safe_divide | Option-returning function |
| VB_T3_012 pair_sum | tuple destructuring in match |
| VB_T3_013 classify_sign | match on `<0` / `==0` / `>0` |
| VB_T3_014 color_code | enum/sum-type match |
| VB_T3_015 either_select | Either ADT (build via Result.Ok/Err) |

### Tier 4 — Recursion & termination (10 problems)

AILANG handles all these via direct recursion. Reference: `benchmarks/recursion_fibonacci.yml`, `benchmarks/gcd_lcm.yml`, `benchmarks/merge_sort.yml`.

| Problem | AILANG idiom |
|---------|--------------|
| VB_T4_001 fibonacci | DIRECT analog: `benchmarks/recursion_fibonacci.yml` |
| VB_T4_002 greatest_common_divisor | DIRECT analog: `benchmarks/gcd_lcm.yml` |
| VB_T4_003 even_odd_mutual_recursion | letrec / mutually recursive `func` |
| VB_T4_004 power | recursive multiplication |
| VB_T4_005 sum_to_n | recursive addition |
| VB_T4_006 list_reverse | structural recursion with accumulator |
| VB_T4_007 count_digits | recursive division |
| VB_T4_008 multiply | recursive addition (Peano-style) |
| VB_T4_009 list_nth | indexed recursion on cons-list |
| VB_T4_010 div_natural | recursive subtraction |

### Tier 5 — Multi-function & effects (10 problems)

AILANG has explicit effect rows: `! {IO}`, `! {State}` (if state effects ship), `! {Exn}` (via Result). Reference: `benchmarks/effect_*.yml`, `benchmarks/state_machine_*.yml`.

| Problem | AILANG idiom |
|---------|--------------|
| VB_T5_001 counter | mutable counter via threading or State effect |
| VB_T5_002 greeter_io_boundary | pure helper + IO main wrapper |
| VB_T5_003 safe_division_exceptions | Result/Option for division-by-zero |
| VB_T5_004 accumulator | foldl-shape with State or threaded |
| VB_T5_005 checked_index | bounds-check returning Option |
| VB_T5_006 state_double | State effect or explicit threading |
| VB_T5_007 exn_negate | Result-typed negation |
| VB_T5_008 print_numbers | IO loop printing 1..n |
| VB_T5_009 state_max | running maximum via State |
| VB_T5_010 safe_head | Option-typed head of list |

**Risk for tier 5**: Vera's State and Exn effects map differently to AILANG. State threading vs explicit State effect; Exn vs Result. May need creative translation; problems where Vera's effect semantics don't have a clean AILANG analog will be noted as known-limitations rather than passing.

## Summary

- **No problems** require fundamentally new AILANG functionality
- **~7 problems** have a direct existing AILANG benchmark to adapt (expression_evaluator, binary_tree_sum, recursion_fibonacci, gcd_lcm, plus some balanced_parens / list_comprehension fragments)
- **~10 problems** may surface stdlib gaps (string functions, possibly state effects)
- **~43 problems** are simple primitives writeable in 10–30 lines from the AILANG teaching prompt

Total estimated solution-writing time: ~3h for the bulk + ~1h for tier 5 effects gymnastics.
