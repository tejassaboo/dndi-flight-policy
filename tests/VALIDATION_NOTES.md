# Validation notes: dndi-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/dndi-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head ee924c5. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

22/24 valid (91.7%), mean field score 0.972, **easy 5/5**. By category: boundary_twin 6/6, distractor 2/2, easy 5/5, flag 2/3, hidden_clause 1/2, multi_rule 4/4, refusal 2/2.
$0.00111 billed per run, 8,055 prompt tokens per call, 3.96 calls per run;
0 of 24 runs would exceed the hosted 65,536 cap.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| fennel-reach | hidden_clause | right offer (Kenya Airways Thursday) and reason (LOWEST_FARE); clause CLASS_AND_ROUTE; key PERSONAL_LEAVE or TRAVEL_PRINCIPLES | model slip (borderline) | It noted "Her personal leave is approved on the Travel Request form, and she will pay any extra fare", then cited the routing section for "the least costly economy routing" (lines 103-105) and never searched the business-only date. The section that lets DNDi book a Thursday flight at all, and makes the traveller pay the difference over the Sunday-only fare, is 2. Personal leave (lines 46-50) under A. Travel Principles. The clause is the only field that tests this hidden clause (any agent that books the requested day picks the same offer), so it is not widened; FedEx quince-harbor keys only its personal-travel section on the same ground. |
| hazel-tundra | flag | BOOK Kenya Airways economy, LONG_FLIGHT_CONDITION_NOT_MET; key FLAG | model slip | "The available itineraries have a 150-minute (2.5-hour) connection, exceeding the 2-hour limit, so the business-class condition is not met." It read "including a maximum of 2 hours of connection time" (lines 125-129) as a cap on the connection and never weighed counting two hours of it (580 + 120 = 700 minutes). The twins opal-thicket and garnet-sound passed. |

## Fixes

None. All 2 failures are model slips; no key was widened and no record changed.

## Q2

Unchanged: the always-cheapest agent passes **5/24 (21%)**.

## Re-score at the head (stored answers)

22/24 (no key changed). No re-run is required.

## Checks (at the notes commit)

`uv run pytest -q` (215 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, byte-identical `rules.py`,
`tools/stock_verify.py` (0 failures), stock `nanoagent plugin inspect .` (exit 0).
