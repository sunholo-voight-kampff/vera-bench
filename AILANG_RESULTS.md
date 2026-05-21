# AILANG on VeraBench — AI-Authored Reference Results

**Solutions authored by:** Claude Opus 4.7 (effort: high), 2026-05-21
**AILANG language authored by:** multi-model team — Claude (Anthropic), GPT (OpenAI), Gemini (Google), 2024–2026
**AILANG version:** `dev` branch as of 2026-05-21 (includes `std/bytes.byteAt`)
**VeraBench version:** v0.0.11 (fork: `sunholo-data/vera-bench`)

## TL;DR

**AILANG passes 100% of testable VeraBench problems with AI-authored reference solutions.** Notable: AILANG is the only target language in VeraBench where *both* the language design AND the reference code are AI-authored.

| Tier | Tests | check@1 | run_correct@1 |
|------|-------|---------|---------------|
| 1 (pure arithmetic) | 10 | **100%** (10/10) | **100%** (10/10) |
| 2 (string + array) | 7 | **100%** (7/7) | **100%** (7/7) |
| 3 (ADTs + match) | 5 | **100%** (5/5) | **100%** (5/5) |
| 4 (recursion) | 8 | **100%** (8/8) | **100%** (8/8) |
| 5 (multi-fn + effects) | 6 | **100%** (6/6) | **100%** (6/6) |
| **Total testable** | **36** | **100%** | **100%** |

Plus 24 problems with `test_cases: []` (no graded output) — all 24 pass `check@1`.

Comparison to VeraBench v0.0.7's published headline numbers:

| Run | Mode | check@1 | run_correct@1 |
|-----|------|---------|---------------|
| **AILANG (this work)** | AI-authored + iterated | **100%** | **100%** |
| Vera + Kimi K2.5 | LLM single-shot | 100% | 100% |
| Vera + GPT-4.1 | LLM single-shot | — | 91% |
| Vera + Claude Opus 4 | LLM single-shot | — | 88% |
| Python + Kimi K2.5 | LLM single-shot | — | 86% |
| TypeScript + Kimi K2.5 | LLM single-shot | — | 91% |

### Important framing — these are AI-authored solutions, in an AI-authored language

**AILANG is unique among the languages in VeraBench: the language itself is 100% AI-authored, by a multi-model team.** Vera, Python, TypeScript, and Aver were all designed by human teams. AILANG's compiler, runtime, type system, effect rows, stdlib, and teaching prompt were collaboratively authored across Claude, OpenAI (GPT), and Gemini models over the course of its development. The solutions in `solutions/ailang/` were written by Claude Opus 4.7 (effort: high) on 2026-05-21, given AILANG's own [teaching prompt](https://ailang.sunholo.com/docs/prompts/current). **An AI multi-model team designed the language; a single AI then wrote production-quality code in it.**

This is the meta-finding worth surfacing in the talk:

- VeraBench's published LLM rows: *Human-designed language; AI writes the code.* Standard methodology.
- AILANG's row: *AI-designed language (Claude + OpenAI + Gemini); AI writes the code (Claude Opus 4.7).* End-to-end AI-authored stack — the full circle.

The methodological distinction vs VeraBench's published LLM numbers is also **the eval mode**:

- **VeraBench's published LLM numbers** (`vera-bench run --language vera --model <m>`) are *single-shot LLM calls per problem*: the harness sends the problem JSON + Vera's SKILL.md to the LLM, captures the response, runs it once, grades it. No iteration.
- **This baseline** is *AI-authored with iteration*: the same Claude Opus 4.7 wrote each solution from scratch given AILANG's teaching prompt, then each solution was tested via the same VeraBench harness; failures (e.g. lambda syntax in the initial T2_001 attempt; `get_char_code` missing stdlib support → added `std/bytes.byteAt` upstream) were iterated to convergence. This is closer to how a real agent works in a coding harness with retries than to a single-shot eval.

The honest claim is: **AILANG (the AI-designed language) can faithfully express every solvable VeraBench problem when an AI agent writes the code with normal iteration feedback.** That establishes the ceiling. The single-shot floor — what AILANG looks like when an LLM is called once per problem with only the prompt to go on — is what the planned LLM-eval mode (`vera-bench run --language ailang --model <m>`) will measure.

The contrast itself is informative: VeraBench's "AI writes Vera one-shot" hits 100% with Kimi K2.5 (a human-designed language). Our "AI writes AILANG with iteration" also hits 100% with Claude Opus 4.7 (an AI-designed language). The full-circle pattern — AI designs the language, AI writes the code in it — is testable now in a way it wasn't before this contribution.

## How to reproduce

```bash
# 1. Install AILANG (must include std/bytes.byteAt, added 2026-05-21)
git clone https://github.com/sunholo-data/ailang.git
cd ailang && make install
ailang --version  # should be >= v0.20.1 (post-2026-05-21 commit)

# 2. Install VeraBench (this fork)
git clone https://github.com/sunholo-data/vera-bench.git
cd vera-bench
uv venv && uv pip install -e .

# 3. Run AILANG baselines
source .venv/bin/activate
vera-bench baselines --language ailang

# Expected output: 36 problems, check@1 = 100%, run_correct = 100%, ~11s wall-clock.
```

## What's included

- **`solutions/ailang/VB_T*_*.ail` (60 files)** — one reference solution per VeraBench problem, written following the same harness pattern as `solutions/aver/`. Each file is a single AILANG module with the entry-point function + a `main` that prints test-case results line-by-line.
- **`vera_bench/baseline_runner.py`** — `run_ailang_baseline` and `_EXT["ailang"] = ".ail"` wired into the existing runner machinery. Mirrors the structure of `run_aver_baseline`.
- **`vera_bench/cli.py`** — adds `"ailang"` to the `--language` choice + a not-on-PATH guard with a clear error message.
- **`AILANG_MAPPING.md`** — per-tier discussion of how AILANG idioms map onto VeraBench problem shapes (with cross-references to AILANG's own benchmark suite for the closest analogs).

## Methodology notes

- **AILANG version**: tested against AILANG `main` after commit `503e8812` (the commit that added `std/bytes.byteAt`). For older AILANG versions, `VB_T2_013_get_char_code` will fail (returns 0 placeholder) but everything else passes.
- **Test execution**: each `.ail` file's `main` function is invoked via `ailang run --quiet --relax-modules --caps IO --entry main <file>`. Test cases are printed line-by-line on stdout; the harness compares against `test_cases[].expected` from the problem JSON (reusing the same `_aver_output_matches` helper that normalises Vera-style 1/0 bools to true/false).
- **Bool normalisation**: AILANG prints `true`/`false`. VeraBench's `expected` field uses both 1/0 (Vera convention) and "true"/"false" strings. The matcher accepts both representations.
- **`AILANG_TRACE=off`**: the baseline runner sets this env so AILANG's tracing infrastructure doesn't probe the OTLP endpoint on every invocation. Halves the per-problem overhead vs the default trace tier.

## Per-problem timing

Total sweep wall-time: ~11 seconds for 36 testable problems + 24 check-only problems. Per-problem wall_time_s is roughly 0.3s — dominated by AILANG's compile-on-every-run model (parse + type-check + effect-check + execute happens in a single `ailang run` invocation per problem). This is fundamentally different from Python's pre-compiled bytecode startup; the comparison is not "Python is faster than AILANG at the language level" but "Python's runtime model amortises differently than AILANG's at this scale."

For perf-honest reporting, the metric of interest is `tests_passed / tests_total` per problem (correctness), not wall_time_s. AILANG's runtime once the program is loaded is generally millisecond-scale; the overhead is in subprocess startup.

## Known limitations & follow-ups

- **LLM-eval mode (`vera-bench run --language ailang`)** is not yet wired. The `run` subcommand currently only handles vera, python, typescript, and aver. Adding AILANG to that path requires (a) extending the click choice in `cli.py`, (b) implementing a prompt loader that fetches AILANG's teaching prompt via `ailang prompt`, and (c) hooking the LLM-generated output into the same `run_ailang_baseline` execution path. Tracked in [AILANG's M-VERA-BENCH-INTEGRATION design doc](https://github.com/sunholo-data/ailang/blob/dev/design_docs/planned/v0_23_0/m-vera-bench-integration.md) Phase 2.
- **`verify@1` parity**: Vera's `verify_tier1`/`verify_tier3` columns report Z3 contract verification. AILANG has Z3-backed `requires`/`ensures` via `ailang verify` but the current AILANG solutions don't ship with VeraBench's contract translations. Phase 2 of the design doc covers translating `contracts.requires`/`ensures` from problem JSON into AILANG syntax and reporting `verify@1` per-problem.
- **`get_char_code`**: required adding `std/bytes.byteAt` upstream in AILANG. The benchmark surfaced a real stdlib gap; tracked + shipped in [AILANG's M-BYTES-TOINTS-BYTEAT design doc](https://github.com/sunholo-data/ailang/blob/dev/design_docs/planned/v0_23_0/m-bytes-toints-byteAt.md). Solutions older than 2026-05-21 use a placeholder; current solution uses `byteAt`.

## Why AILANG belongs in VeraBench

[AILANG](https://ailang.sunholo.com/) is a member of the Verification camp in the AI-native-languages survey (per the Negroni Venture Studios ["Three Camps Alike in Dignity"](https://negroniventurestudios.com/2026/05/20/three-camps-alike-in-dignity/) post). Both Vera and AILANG ship Z3-backed contracts as a core feature (Vera via mandatory contracts + De Bruijn slot refs; AILANG via `requires`/`ensures` + HM types with row-polymorphic effect rows). Both target LLM-authored code as the primary use case.

Running both against the same benchmark suite enables a direct head-to-head verification-camp comparison — something neither project has published before. This baseline contribution is the foundation; the next step is the LLM-eval comparison.
