# DNDi Travel Policy Flight Booking

**No affiliation with the Drugs for Neglected Diseases initiative (DNDi).** The handbook is DNDi's public *Travel and
Reimbursement Policy*, version 3.0 (effective 1 January 2022), bundled verbatim for research. Its download URL was not
recorded (`pilot_work/originals/MANIFEST.md` marks it UNVERIFIED); the raw PDF, sha256 `dcae2c5c...7f2c1c`, is the
pinned copy. Confirm the public URL before citing or publishing this plugin.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the organisation's real travel
policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 2,946 words, 320 lines, sha256 `524c08e4...bfda4e7`, equal to
`pilot_work/originals/dndi/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule. Under stock
NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy` switch of the
NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt:
`harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant to run with
`query: instructions+input`, so a selector sees the traveller's request.

**Size.** Calibrated on the paid Thornton and NJC validation runs (about 0.2 tokens a character of handbook plus 1,800
for the rest of the first prompt), the first call under `full` is about 5,800 input tokens (20,218 characters of
policy), the second about 6,300 (plus a trip record of up to 2,100 characters) and the third about 7,200 (plus a
search of up to 4,100 characters). A 3-call run (`get_trip`, `search_flights`, `submit`) is about 19,300 input
tokens, near 28,000 with the final message and output: far under the hosted cap of 65,536.

**Annex 2.** The air-cost ceiling table (lines 304-317) came out of the PDF with the amounts on lines apart from their
routes and one row garbled. No case depends on reading it: every economy or premium economy fare booked or held is
under the lowest amount any reading gives its trip (EUR 800 within one continent, EUR 1,200 between continents), and
every business fare above that has the Head of Financial Control's written approval of the air cost on file.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's shared list
  plus `HOME_TO_WORK_JOURNEY` and `PERSONAL_COST_PAID_BY_TRAVELER`, and decoy codes from other handbooks' rules.
  Fares are in cents of euros.
- **Success:** every field is one the answer key accepts; the cabin is graded as the chosen offer's own. Score =
  fields right / 6.
- **Reasons on a declined request.** The task instructions say that when the booking is not what the traveller asked
  for, the reason code gives why the request is declined. A declined business or premium economy cabin accepts
  `LONG_FLIGHT_CONDITION_NOT_MET` or `UPGRADE_NOT_ELIGIBLE`, not `LOWEST_FARE`. A nonstop declined because the
  cheaper connection is within the handbook's four-hour margin (lines 103-107) accepts `LOWEST_FARE` beside the
  specific codes, as does an airline wish declined by the least-costly-routing rule (`heather-quay`).
- **No hidden facts:** no scenario has `answer_key_inputs`. Every trip record holds the Travel Request form's approval
  (lines 56-58; Annex 1, lines 269-275: the Staff member's supervisor, or the manager responsible for Consultants,
  Members of a Body of DNDi and Guests).

| Scenario | Category | Expected decision (offer; cabin) | Reason | Approver | Clause (frozen lines of must_keep) |
|---|---|---|---|---|---|
| `bramble-cove` | multi_rule | BOOK (iberia-business; BUSINESS) | MEDICAL_NEED | EXECUTIVE_DIRECTOR or MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or TRAVEL_CLASS (120-122, 133-134, 137-139, 56-58, 269-275) |
| `cinder-vale` | distractor | BOOK (african-economy; ECONOMY) | LOWEST_FARE | MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (102, 103-105, 56-58, 269-275) |
| `cobalt-finch` | easy | BOOK (kenya-economy; ECONOMY) | LOWEST_FARE | NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (102, 103-105, 56-58, 269-275) |
| `ember-lagoon` | boundary_twin | BOOK (india-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EXECUTIVE_DIRECTOR or FINANCIAL_CONTROL_HEAD or MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 133-134, 137-139, 108-111, 56-58, 269-275) |
| `fennel-reach` | hidden_clause | BOOK (kenya-thursday; ECONOMY) | LOWEST_FARE or PERSONAL_COST_PAID_BY_TRAVELER or PERSONAL_TRAVEL_NOT_COVERED | NONE or SUPERVISOR | PERSONAL_LEAVE or TRAVEL_PRINCIPLES (47-50, 102, 103-105, 56-58, 269-275) |
| `garnet-sound` | boundary_twin | BOOK (india-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EXECUTIVE_DIRECTOR or FINANCIAL_CONTROL_HEAD or MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 119, 102, 103-105, 56-58, 269-275) |
| `hazel-tundra` | flag | FLAG_FOR_APPROVAL (evening-business or evening-economy; BUSINESS or ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | EXECUTIVE_DIRECTOR or NOT_NAMED or STRATEGY_OPERATIONS_DIRECTOR | AIR_TRAVEL or TRAVEL_CLASS (124-132, 133-134, 137-139, 108-111, 56-58, 269-275) |
| `heather-quay` | easy | BOOK (kenya-economy; ECONOMY) | LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or LOYALTY_PROGRAMMES or TRAVEL_CLASS (102, 103-105, 106-107, 144-146, 56-58, 269-275) |
| `juniper-dell` | easy | BOOK (klm-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (119, 124-132, 102, 103-105, 56-58, 269-275) |
| `lichen-bay` | boundary_twin | BOOK (kenya-premium; PREMIUM_ECONOMY) | PREMIUM_ECONOMY_ALLOWED | NONE or SUPERVISOR | AIR_TRAVEL or EXTRA_LEGROOM (141-142, 56-58, 269-275) |
| `marlin-crest` | easy | BOOK (british-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EXECUTIVE_DIRECTOR or FINANCIAL_CONTROL_HEAD or MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 133-134, 137-139, 108-111, 56-58, 269-275) |
| `opal-thicket` | multi_rule | BOOK (dubai-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EXECUTIVE_DIRECTOR or FINANCIAL_CONTROL_HEAD or NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 133-134, 137-139, 108-111, 56-58, 269-275) |
| `pewter-glade` | multi_rule | BOOK (african-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EXECUTIVE_DIRECTOR or FINANCIAL_CONTROL_HEAD or MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 119, 102, 103-105, 56-58, 269-275) |
| `quill-brook` | boundary_twin | BOOK (kenya-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or EXTRA_LEGROOM or TRAVEL_CLASS (141-142, 119, 102, 103-105, 56-58, 269-275) |
| `russet-heath` | multi_rule | BOOK (british-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EXECUTIVE_DIRECTOR or FINANCIAL_CONTROL_HEAD or MANAGER_RESPONSIBLE or NONE | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 133-134, 137-139, 108-111, 56-58, 269-275, 112-114) |
| `saffron-weir` | easy | BOOK (india-premium; PREMIUM_ECONOMY) | PREMIUM_ECONOMY_ALLOWED | NONE or SUPERVISOR | AIR_TRAVEL or EXTRA_LEGROOM (141-142, 56-58, 269-275) |
| `slate-loch` | refusal | REFUSE (none; NONE) | HOME_TO_WORK_JOURNEY or OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE or SUPERVISOR | OBJECTIVE_SCOPE or TRAVEL_PRINCIPLES (39, 52, 20-21) |
| `sorrel-pike` | hidden_clause | BOOK (african-economy; ECONOMY) | TRAVELLER_LIMIT_PER_FLIGHT | NONE or SUPERVISOR | INSURANCE or TRAVEL_PRINCIPLES (44-45, 102, 103-105, 56-58, 269-275) |
| `tansy-marsh` | boundary_twin | BOOK (cairo-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (103-105, 106-107, 102, 56-58, 269-275) |
| `thistle-moor` | boundary_twin | BOOK (klm-economy; ECONOMY) | CONNECTION_TOO_LONG or LOWEST_FARE | NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (103-105, 106-107, 102, 56-58, 269-275) |
| `umber-falls` | flag | FLAG_FOR_APPROVAL (british-business; BUSINESS) | APPROVAL_REQUIRED | STRATEGY_OPERATIONS_DIRECTOR | AIR_TRAVEL or CLASS_AND_ROUTE or TRAVEL_CLASS (124-132, 133-134, 137-139, 108-111, 56-58, 269-275, 112-114) |
| `violet-ford` | refusal | REFUSE (none; NONE) | RAIL_PREFERRED | MANAGER_RESPONSIBLE or NONE | MEANS_OF_TRAVEL or RAIL_TRAVEL (160-161) |
| `wren-hollow` | distractor | BOOK (kenya-economy; ECONOMY) | LOWEST_FARE or TRAVELLER_LIMIT_PER_FLIGHT | NONE or SUPERVISOR | AIR_TRAVEL or CLASS_AND_ROUTE or INSURANCE or TRAVEL_CLASS or TRAVEL_PRINCIPLES (102, 103-105, 56-58, 269-275) |
| `yarrow-shoal` | flag | FLAG_FOR_APPROVAL (british-business; BUSINESS) | APPROVAL_REQUIRED or MEDICAL_NEED | EXECUTIVE_DIRECTOR or STRATEGY_OPERATIONS_DIRECTOR | AIR_TRAVEL or TRAVEL_CLASS (120-122, 133-134, 137-139, 56-58, 269-275) |

Mix (EDGE_CASES.md 5.2, 24 row): 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal,
3 flags (12.5%). Decisions: 19 BOOK (5 business, 2 premium economy, 12 economy), 2 REFUSE, 3 FLAG_FOR_APPROVAL. Twin
pairs: a connection 239 against 240 minutes longer than the nonstop (`tansy-marsh`, `thistle-moor`); overnight
nonstops of 540 against 535 minutes (`ember-lagoon`, `garnet-sound`); nonstops of 361 against 360 minutes for
premium economy (`lichen-bay`, `quill-brook`); and, outside the boundary category, a business fare of EUR 5,000.00
against EUR 5,010.00 (`russet-heath`, `umber-falls`) and five against four colleagues on one flight
(`sorrel-pike`, `wren-hollow`).

The three flags, each with clear twins on both sides:

- **"including a maximum of 2 hours of connection time"** (lines 125-129): `hazel-tundra`, flights of 240 + 340
  minutes with a 150-minute connection, overnight, to external partners. Counting up to two hours of the wait gives
  11 hours or more (business); a cap on the connection, or no ground time at all, gives economy. Either offer may be
  held. Twins `opal-thicket` (business) and `garnet-sound` (economy).
- **Approval required (business class).** `yarrow-shoal`: a medical certificate allows business class (lines
  121-122), but the Executive Director's prior approval (lines 133-134) is missing. Twins `bramble-cove` (approved:
  business) and `juniper-dell` (no ground: economy).
- **Approval required (ticket above EUR 5,000).** `umber-falls`: business class is allowed and approved, but the
  ticket is EUR 5,010.00 and line 112 needs the Strategy and Operations Director's approval. Twins `russet-heath`
  (EUR 5,000.00: book) and `garnet-sound` (economy).

Approvers follow the template's rule 4' (SYNC_NOTES.md): a booking accepts `NONE` and every sign-off on file
(the Travel Request form's approver, and the Executive Director and Head of Financial Control where on file); a
refusal accepts `NONE` and the form's approver; a hold accepts only the awaited role(s).

**Duration (`rules.over`).** "business-single-leg": a nonstop of 540 minutes or more (inclusive); a connection is not a
single leg (unclear only if one of its flights alone reaches 540). "business-multi-leg": 660 minutes or more of
combined travel; for a connection, true when the flights alone reach 660 and every connection is within 120 minutes,
false when the whole elapsed journey is under 660, unclear between. "premium-economy": one flight over 360 minutes
(strict). "Overnight travel" (line 130): a flight in the air between midnight and 06:00 on both airports' clocks is
overnight, one in the air at no such time on either clock is not; nothing in between is modelled. Every search has
`background: 0` and `handbook.json` `background_offers` is 0, so a search the case does not pin lists nothing.

Degenerate agents (`tests/test_verifier.py`): one that always holds the right offer as unclear passes 1 case
(`hazel-tundra`); one that always books the cheapest seat with `LOWEST_FARE`, `NONE` and the right section passes
5 (`cinder-vale`, `cobalt-finch`, `heather-quay`, `tansy-marsh`, `wren-hollow`).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller and kind, home and workplace, route, dates, meetings, requested cabin, routing and airline, medical certificate, train, sign-offs, colleagues already ticketed | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-dndi-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, two reason
  codes and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: decisions taken during the build, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/dndi-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
