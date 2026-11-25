# Independent audit: dndi-flight-policy (2026-11-25)

I audited build da4dbad against `WAVE3_AUDIT_BRIEF.md`, `WAVE3_BUILD_BRIEF.md` (all 12 lessons), MASTER_PLAN section 4
and EDGE_CASES sections 1-3 and 5. I read the frozen handbook in full (`src/plugin/data/policy.txt`, 320 lines). Then
I dumped `get_trip` and every pinned `search_flights` output and worked out each answer from the handbook and those
outputs alone, before I read `rules.py`. After that I compared my answers with every accept set (decision, offer,
cabin, reason, approver, clause).

**Verdict: pass after fixes.** The keyed decision and offer were right in all 24 scenarios, and every keyed booking
meets every constraint the handbook states. The one real defect was a date-anchoring ambiguity that affected five
business cases. The other fixes widen narrow reason and clause sets. No answer changed category, and no id changed.

## Defects found and fixed

| Scenario | Problem | Fix |
|---|---|---|
| marlin-crest, opal-thicket, russet-heath, umber-falls, hazel-tundra | Line 131-132, "important meetings with external partners **the same or following day**", gives no anchor day. In each case the overnight flight lands the day after it leaves, and the first meeting was the day after landing, so it fell two days after `travel_date`. A reader who counts from the day of leaving finds the meeting condition fails, so economy, a false failure. In hazel-tundra the flag would instead collapse to an economy BOOK. | Each first meeting now falls on the landing day, which is also the day after leaving, so both counts agree. russet-heath and umber-falls are the twins, and both now read "starting on the afternoon of the 16th" (they land 05:40 and 07:00). opal-thicket reads "afternoon of the 9th" (lands 04:35 and 06:40). hazel-tundra reads "5 pm on the 4th" (lands 10:10 and 12:40). marlin-crest landed at 18:15, so for it alone the world changed: BA now leaves at 14:30 and SQ at 15:00, with the same minutes, fares and offer ids. They land at 11:25 and 12:00 the next day, still overnight on both clocks (in the air from 00:00 to 06:00 on each), and the request reads "5 pm on the 3rd". Each request states a start time, so the answer never depends on arrival time without a deadline (lesson 4). `rules.business_request` now raises if the two counts ever disagree. |
| ember-lagoon, marlin-crest, opal-thicket | These are long-haul business bookings that rely on the Head of Financial Control's approval of the air cost (lines 108-111). That approval sits under "a. Class and route", yet the clause set lacked CLASS_AND_ROUTE, while russet-heath already accepted it. | Business bookings that rely on the air-cost approval now accept CLASS_AND_ROUTE (rules change: `if cost or fare == limit`). |
| wren-hollow | The key accepted INSURANCE (lines 44-45) as the clause, but not the reason code or parent heading for that same rule. Its twin sorrel-pike accepts both. | It now also accepts the reason TRAVELLER_LIMIT_PER_FLIGHT and the clause TRAVEL_PRINCIPLES. |
| fennel-reach | The traveller pays for the personal element (lines 48-50). PERSONAL_TRAVEL_NOT_COVERED is a defensible code for "DNDi does not cover the personal part" (lesson 5). | Added to the reason set. |

`MAX_PASS_ALWAYS_LOWEST`: 5 -> 5 (cinder-vale, cobalt-finch, heather-quay, tansy-marsh, wren-hollow).
`MAX_PASS_ALWAYS_FLAG`: 1 -> 1 (hazel-tundra).

## Builder's open items, settled

- **sorrel-pike: keep SA only.** I asked whether booking the cheapest Kenya Airways seat, as a sixth traveller on
  KQ 1460, is defensible. It is not, for four reasons:
  - "As far as possible" means do it whenever it can be done. Here it can: another nonstop has seats, takes 5
    minutes longer, costs EUR 35 more and lands the day before the meeting.
  - The request says "book me on whatever the handbook prefers", and the handbook states that preference outright.
  - A KQ booking would put six DNDi Travellers on one flight. That breaks the very constraint the clause states, and
    the audit standard requires every keyed booking to meet every stated constraint.
  - The only reading that rescues KQ takes "routing" to mean the city-pair path, so both NBO-JNB nonstops count as
    one routing. That reading makes the clause impossible to satisfy for any nonstop pair, and it ignores the
    clause's stated aim ("diminish collective risks"). The trip record also counts colleagues by flight number.

  The least-cost rule is also only "should", and the specific risk rule takes priority over it. Residual risk: low to
  medium. A model might weigh the two "should" rules the other way.
- **umber-falls approver: keep STRATEGY_OPERATIONS_DIRECTOR only.** Lines 112-114 name the Executive Director only
  "in his/her absence". The record says nothing that makes the Strategy and Operations Director's absence plausible.
  If anything, it shows the Executive Director at work, signing the business-class approval. That approval covers
  the cabin, not a ticket above EUR 5,000.
- **"Overnight" (line 130): clear-cut in every case.** Every business-requested case is either in the air from
  midnight to 06:00 on both airports' clocks (ember-lagoon, garnet-sound, marlin-crest after the fix, opal-thicket's
  second leg, russet-heath, umber-falls, hazel-tundra) or a pure day flight (pewter-glade, 07:30/08:00 to 20:30/20:50
  local; juniper-dell). `rules.overnight` raises on anything in between.
- **"Important meetings": clear-cut.** Every long-haul business case's stated purpose is a named meeting with
  external partners: a negotiation, protocol or funding meetings, or manufacturing-partner meetings. No reader can
  call them unimportant. The anchor-day problem in the same sentence was the real defect (fixed above).
- **Annex 2 (scrambled table): no answer depends on it.** However its rows are read, the table gives no amount below EUR 800,
  and no amount between continents below EUR 1,600. The rules' safe bounds are EUR 800 within a continent and
  EUR 1,200 between continents. Every economy or
  premium economy fare booked or held is under EUR 800 in Europe or under EUR 1,200 between continents. The largest
  are EUR 980 (saffron-weir, Asia to Europe), EUR 960 (cobalt-finch) and EUR 840 (cinder-vale, Africa to South
  America). Two medical business fares are under EUR 800 within Europe: bramble-cove at EUR 610 and yarrow-shoal at
  EUR 580. Every other business fare has the Head of Financial Control's written approval of the air cost on file.
  `ceiling_checked` raises otherwise.

## Checked and left as built

- **Re-derived answers.** I agree with all 21 non-flag keys. The blind-read table in BUILD_NOTES describes the
  pre-audit dates for the five re-dated cases, and their answers are unchanged.
- **thistle-moor / tansy-marsh.** "Total journey time" means elapsed time. The business clause's own wording,
  "combined travel time ... including ... connection time", treats ground time as part of travel time. Measured in
  flying minutes, both connections would sit within four hours. I judge that reading weak and accept only the
  elapsed reading.
- **hazel-tundra** is a genuine flag. The phrase has two defensible readings (count up to 2 hours of the 150-minute
  wait, giving 700 minutes and business; or cap the connection, or leave ground time out, giving economy). Both held
  offers are accepted, together with APPROVAL_REQUIRED and the approvers NOT_NAMED, ED and SOD. umber-falls and
  yarrow-shoal are approval holds over clear text, and their accept sets follow rule 4'.
- **Twins.** Each pair differs in one fact: ember-lagoon/garnet-sound (540 vs 535 minutes), lichen-bay/quill-brook
  (361 vs 360 minutes), russet-heath/umber-falls (EUR 5,000.00 vs EUR 5,010.00), tansy-marsh/thistle-moor (layover
  159 vs 160 minutes), sorrel-pike/wren-hollow (five vs four colleagues). Flight numbers differ only cosmetically.
- **Requests.** No request quotes rule wording or a threshold (`test_lint` passes). Every request asking for a cabin
  the policy may deny has a fallback, except russet-heath, umber-falls, yarrow-shoal and saffron-weir, where the cabin
  asked for is allowed, possibly after approval. The decline sentence (lesson 12) is in `nanoagent.yaml`.
- **slate-loch.** An approved Travel Request form is on file, but approval cannot make a commute DNDi Travel
  (line 39), and the contract field is empty (line 52). REFUSE stands.

## Acceptance outputs (after the fixes)

```
uv run pytest -q                      215 passed
uv run ruff check .                   All checks passed!
uv lock --check                       Resolved 42 packages
python3 ../_template/check_shared.py  : ok
rules.py copies                       byte-identical
stock_verify.py (stock Python)        24 scenarios, 0 failures
stock nanoagent plugin inspect .      exit 0
```
