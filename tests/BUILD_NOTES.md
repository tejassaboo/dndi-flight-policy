# Build notes: dndi-flight-policy (wave 3, 2026-11-24)

Built to `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md` from the frozen handbook
`pilot_work/originals/dndi/frozen/dndi_policy.txt` (DNDi Travel and Reimbursement Policy v3.0, effective 2022-01-01;
2,946 words, 320 lines, sha256 524c08e4...bfda4e7; under 10,000 words, so 24 scenarios). Made with
`_template/instantiate.py --slug dndi --task-id book-dndi-flight --currency EUR --background 0 --scenarios 24`. The
user was asleep; every choice below is the recommended one, taken without asking. The source URL is UNVERIFIED
(MANIFEST.md); the raw PDF's sha256 is in `handbook.json`.

## Flight rules the handbook supports (frozen line numbers)

| Clause | Lines | Operator / kind | Used by |
|---|---|---|---|
| Always economy class | 102, 119 | mandatory default | every economy case |
| Least costly economy routing, unless its journey time exceeds the most direct route's by four or more hours | 103-105 | "four or more" inclusive: 240 minutes more is out, 239 in | tansy-marsh / thistle-moor; every economy case |
| Personal preference is not a basis for the route; a cheaper acceptable alternative may be imposed | 106-107 | mandatory | tansy-marsh, heather-quay |
| Air cost above the Annex 2 ceilings needs the Head of Financial Control's prior written approval | 108-111 | mandatory; table unreadable | approval on file in every business case above EUR 800 (see decision 2) |
| Ticket above EUR 5,000 needs the Strategy and Operations Director's approval before purchase | 112-114 | "above" strict | russet-heath (5,000.00: book) / umber-falls (5,010.00: hold) |
| Plan 45 days ahead (intercontinental) or 15 (regional); exceptions documented | 115-117 | "endeavor": soft | cinder-vale (distractor) |
| Business class for a medical condition documented by a certificate | 120-122 | exception | bramble-cove, yarrow-shoal |
| Business class when a single leg is nine hours or more, or a multi-leg journey 11 hours or more "including a maximum of 2 hours of connection time"; overnight; important meetings with external partners the same or following day | 124-132 | "or more" inclusive; conjunctive | marlin-crest, ember-lagoon / garnet-sound, opal-thicket, pewter-glade, russet-heath, umber-falls, hazel-tundra (flag), juniper-dell |
| All business class needs the Executive Director's prior approval (or the Operations and Strategy Director by delegation) | 133-134 | mandatory | every business booking; yarrow-shoal (hold) |
| At least two business options; the most economical is selected | 137-139 (+ 293-294) | mandatory | every business case |
| Premium economy or extra legroom when one flight is over 6 hours | 141-142 | "over" strict, per flight | saffron-weir, lichen-bay / quill-brook |
| Loyalty programmes only while the most direct, adequate and economic route is selected | 144-146 | mandatory | heather-quay |
| Train trips under 6 hours shall be selected over flying, whenever possible | 160-161 | "under" strict; "whenever possible" | violet-ford (refusal) |
| Separate routings so that no more than five DNDi Travellers take the same routing | 44-45 | "as far as possible ... should" | sorrel-pike / wren-hollow |
| Personal leave: incidental, approved on the Travel Request form, traveller pays the difference | 46-50 | mandatory | fennel-reach |
| Home to regular place of work is not DNDi Travel (unless the contract says otherwise) | 39, 52 | definition | slate-loch (refusal) |
| Travel Request form approved before booking; Annex 1 approver by traveller kind | 56-58, 269-275 | precondition | every trip record holds it |

No refundable-fare, preferred-carrier, advance-purchase-ban, overnight-stop or national-carrier rule exists, so none is
tested. "The journey to the next destination resumes within 12 hours" (lines 128-129) is coded (a connection over 12
hours raises) but no case comes near it. The DNDi-discretion sentence (lines 135-136) is a distractor only: every
business booking has the Executive Director's approval on file, which settles DNDi's discretion.

## Decisions taken (recommended choices)

1. **Duration measure.** Scheduled minutes stand for flying time. Business: a nonstop of 540 minutes or more is a
   "single leg journey ... nine hours or more"; a connection qualifies on the multi-leg branch only when every reading
   of "including a maximum of 2 hours of connection time" agrees (flights alone 660+ and every connection within 120:
   yes; whole elapsed journey under 660: no). Between is the one unclear flag, `hazel-tundra`. A connection with one
   flight of 540+ would be unclear on the single-leg branch; no case has one. Premium economy: "one flight is over 6
   hours" is per flight and strict (361 yes, 360 no).
2. **Annex 2 avoided.** The ceiling table (lines 304-317) is scrambled, so no case depends on reading it. Every
   economy and premium economy fare booked or held is under EUR 800 (within one continent) or EUR 1,200 (between
   continents), under every amount any reading gives the trip; every business fare above EUR 800 has the Head of
   Financial Control's written approval of the air cost on file. `rules.ceiling_checked` raises otherwise.
3. **"Overnight travel"** (line 130) is undefined. Every case is clear: an overnight flight is in the air between
   midnight and 06:00 on the clocks of both airports (marlin-crest 21:20 to 18:15 next day, ember-lagoon 01:55 to
   05:25); a day flight is in the air at no such time on either clock (pewter-glade 07:30 to 20:30, the short European
   flights). Anything else raises.
4. **"Important meetings with external partners the same or following day."** Every business case names external
   partners (research, manufacturing, funding partners) and a first meeting the day after landing; "important" is
   read as satisfied by meetings that are the trip's purpose. Not tested as a twin.
5. **The Executive Director's pre-approval is conditional** ("if the handbook's conditions for business class are
   met"), so the record never decides the cabin by itself: ember-lagoon / garnet-sound and pewter-glade carry the same
   sign-off and get different cabins.
6. **Routing margin.** "Most direct route" = the routing with the fewest stops, and its shortest journey time; journey
   time = elapsed minutes. In the twins both routings leave at 23:55, so elapsed and arrival differences agree, and the
   workshop is two days after landing (lesson 4).
7. **EUR 5,000 rule.** Strict "above". The hold accepts only the Strategy and Operations Director (the fallbacks of
   lines 113-114 apply only in that person's absence, which the record does not state). The Executive Director's
   business-class approval does not stand in for it.
8. **Five travellers on one routing** (lines 44-45). Read as binding where a separate routing is possible ("as far as
   possible ... should be taken to avoid"): sorrel-pike accepts only the separate SA nonstop. This is the case I am
   least sure of (see the risk list).
9. **Trains** (line 160). A train under 6 hours that arrives in time: REFUSE the flight (`RAIL_PREFERRED`). Trains of
   6 to 8 hours are not modelled (the clause opens "encouraged ... e.g."); every other European case has a train over
   10 hours.
10. **Personal leave** (fennel-reach). The ticket is the one the traveller flies (Thursday); DNDi bears the Sunday-only
    cost and the traveller the difference. Both dates are pinned searches and both are in the trip record (lesson 8).
11. **Commute refusal** (slate-loch): home Toronto, regular place of work the New York office, no contract terms.
12. **Approvers** (SYNC_NOTES 4'). Every booking accepts NONE plus every sign-off on file (the Travel Request form's
    approver: SUPERVISOR for Staff, MANAGER_RESPONSIBLE otherwise; EXECUTIVE_DIRECTOR and FINANCIAL_CONTROL_HEAD where
    on file, used or not, rule 4(b)). Refusals accept NONE and the form's approver. Holds: yarrow-shoal
    EXECUTIVE_DIRECTOR or STRATEGY_OPERATIONS_DIRECTOR (lines 133-134); umber-falls STRATEGY_OPERATIONS_DIRECTOR;
    hazel-tundra NOT_NAMED, EXECUTIVE_DIRECTOR or STRATEGY_OPERATIONS_DIRECTOR (the business-class approvers), never
    NONE. The approver enum's "Head of Financial Control" is spelled `FINANCIAL_CONTROL_HEAD` because the lint rejects
    the handbook's own 4-word phrase in contract text.
13. **Reason codes.** Handbook codes: `HOME_TO_WORK_JOURNEY`, `PERSONAL_COST_PAID_BY_TRAVELER`. Declined cabins accept
    `LONG_FLIGHT_CONDITION_NOT_MET` or `UPGRADE_NOT_ELIGIBLE`, never `LOWEST_FARE` (lesson 12). The nonstop declined by
    the margin test (tansy-marsh) accepts `LOWEST_FARE`, `COST_SAVINGS`, `ALTERNATE_ROUTE_TOO_EXPENSIVE` and
    `ALTERNATE_ROUTE_WITHIN_MARGIN`; the airline wish (heather-quay) `LOWEST_FARE` and `LOYALTY_PROGRAM_PREFERENCE`
    (the ground is the least-cost rule itself). The commute refusal accepts `HOME_TO_WORK_JOURNEY`,
    `OUTSIDE_POLICY_SCOPE`, `PERSONAL_TRAVEL_NOT_COVERED`. Business bookings accept `LONG_FLIGHT_APPROVED` and
    `INTERNATIONAL_LONG_FLIGHT`. Decoys (subjects grepped, none in the text): FLY_AMERICA_US_CARRIER_REQUIRED,
    OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING, DENIED_BOARDING_NOT_ALLOWED, CHANCELLOR_WRITTEN_AUTHORIZATION,
    DOUBLE_BOOKING_PROHIBITED, PRIVATE_AIRCRAFT_NOT_APPROVED, TRAVEL_PACKAGE_NOT_ITEMIZED, SAME_CLASS_AS_CUSTOMER,
    CANDIDATE_TRIP_NOT_COVERED. Dropped: WEEKEND_* (weekend travel in F.1), NEXT_OF_KIN_TRAVEL (dependants, line 79),
    EXTENDED_TRAVEL_SAVINGS (trips extended with personal leave, line 42).
14. **Requests.** Every request that asks for a cabin the policy may deny gives a fallback ("otherwise economy is
    fine"); russet-heath and umber-falls ask "Business class, please." with no fallback because business is allowed
    there (an economy fallback would invite booking economy instead of holding for the EUR 5,000 sign-off). No request
    states a duration or threshold (lesson 6). Every request says when the business starts (lesson 4).
15. **Ids.** The first scenario in file order must not be a refusal (`test_a_tampered_reference_fails` tampers it to
    REFUSE), so the commute refusal is `slate-loch`, not the first draft's `amber-loch`.
16. **Degenerate baselines.** Always-flag passes 1 (hazel-tundra). Always-cheapest (cheapest seat, LOWEST_FARE, NONE)
    passes 5 of 24 (21%): cinder-vale, cobalt-finch, heather-quay, tansy-marsh, wren-hollow.
    `MAX_PASS_ALWAYS_FLAG = 1`, `MAX_PASS_ALWAYS_LOWEST = 5`.

Mix: 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal, 3 flags (12.5%). Decisions:
19 BOOK (5 business, 2 premium economy, 12 economy), 2 REFUSE, 3 FLAG. Overlays: multi_leg 4, date_arithmetic 3,
month_end 1, personal_travel 1, multi_traveller 2, dearer_option 9, upgrade_not_taken 5, outside_air_section 4,
overnight 7.

## Hosted-cap estimate

0.2 tokens a character of policy plus 1,800 (Thornton/NJC paid calibration): 20,218 characters gives about 5,800
input tokens on call 1, about 6,300 on call 2 (largest trip record 2,072 characters) and about 7,200 on call 3
(largest search 4,122 characters). A 3-call run is about 19,300 input tokens, near 28,000 with the final message and
output: under the 65,536 hosted cap with about 37,000 to spare.

## Blind read (non-flag scenarios), from the handbook text and the tool outputs only

I dumped `get_trip` and every `search_flights` output the record names and re-derived each answer from the frozen text
alone, before comparing with the keys.

| Scenario | My reading | Agrees |
|---|---|---|
| bramble-cove | certificate obliges business (121-122), ED approval on file (133-134); cheaper of two business options: IB EUR 610 | yes |
| cinder-vale | 20 days ahead is under 45, but "endeavor" and documented (115-117): cheapest economy SA EUR 840; PE not asked | yes |
| cobalt-finch | plain economy asked; cheapest nonstop KQ EUR 960 | yes |
| ember-lagoon | 540-minute overnight nonstop (nine hours or more), partners next day, ED + HFC on file: AI business EUR 2,950 | yes |
| fennel-reach | approved personal days; book Thursday's cheapest KQ EUR 495, traveller pays EUR 35 over Sunday's EUR 460 (47-50) | yes |
| garnet-sound | 535 minutes, under nine hours: business not allowed; economy fallback AI EUR 520 | yes |
| heather-quay | preference is no basis for the route (106), loyalty only if the economic route is kept (144-146): KQ EUR 610 | yes |
| juniper-dell | short day flight in Europe, no medical ground: economy KLM EUR 148; train over 10 hours | yes |
| lichen-bay | 361 minutes is over 6 hours: premium economy KQ EUR 690 | yes |
| marlin-crest | 775-minute overnight, partners on the day after landing, ED + HFC: BA business EUR 4,100 | yes |
| opal-thicket | 220 + 490 flights, 75-minute connection: 11 hours on every reading, overnight second leg: EK business EUR 3,620 | yes |
| pewter-glade | 650-660 minutes but 07:30-20:30 daytime, not overnight: economy SA EUR 760 | yes |
| quill-brook | exactly 360 minutes is not over 6 hours: economy KQ EUR 410 | yes |
| russet-heath | business allowed and approved; EUR 5,000.00 is not above EUR 5,000 (112): BA business | yes |
| saffron-weir | 590-minute flight over 6 hours, premium asked: AI EUR 980 | yes |
| slate-loch | Toronto home to New York workplace is not DNDi Travel (39), contract silent (52): REFUSE | yes |
| sorrel-pike | five colleagues on KQ 1460; a sixth would be more than five (44-45); separate routing SA EUR 415 | yes |
| tansy-marsh | connection 749 against 510 minutes, 239 more (< four hours), EUR 210 cheaper; preference no basis: MS EUR 510 | yes |
| thistle-moor | 750 minutes, exactly four hours more: not acceptable; KLM nonstop EUR 720 | yes |
| violet-ford | 245-minute train arriving in time; trains under 6 hours selected over flying (160): REFUSE | yes |
| wren-hollow | four colleagues, so five in all: within the limit; cheapest KQ EUR 380 | yes |

All 21 non-flag scenarios agree. Least certain (two-reader risk):

- **sorrel-pike**: "as far as possible, separate routings should be taken" is "should"; a reader could book the
  cheapest Kenya Airways seat as permitted. I keyed the separate routing because a separate routing with seats is
  plainly possible and the request leaves the choice to the handbook.
- **pewter-glade**: a reader might call a flight landing at 20:50 "overnight" in a loose sense; the times were moved
  to a 07:30 departure to keep it a day flight.
- **"important meetings"** (lines 131-132): undefined; every business case's purpose is a named negotiation or
  protocol meeting with external partners, so the condition is read as met.
- **umber-falls approvers**: only STRATEGY_OPERATIONS_DIRECTOR is accepted; a reader naming the Executive Director
  (the first fallback, line 113) fails.

## Template change requests

- **Add Geneva (GVA)** to the shared world (`world.py` AIRPORTS; Swiss LX would want it as a hub). DNDi's head office
  is in Geneva, and a Geneva base is the natural traveller for this handbook. Worked around: travellers are based at
  DNDi's other offices (Nairobi, New Delhi, New York) or are consultants and members of governing bodies in London,
  Johannesburg, Mumbai, Zurich, Amsterdam and Copenhagen. Rio de Janeiro (GIG), Kinshasa (FIH), Kuala Lumpur (KUL)
  and Addis Ababa (ADD) would also suit DNDi offices but are not needed.
- Observation (not blocking): the lint and `test_duration.py` model only absolute duration thresholds; the routing
  margin (240 minutes over the most direct route) is a relative one, coded as a constant and tested through its twin
  pair, as in fedex-office.

## Acceptance outputs (final)

```
$ uv run pytest -q
215 passed in 2.07s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 10ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .  (stock checkout)
exit 0
$ nanoagent plugin pack . <scratchpad>/dndi-flight-policy.tar.gz  (stock checkout)
packed . into .../dndi-flight-policy.tar.gz (165444 bytes)
$ python ../_template/tools/stock_verify.py .  (stock checkout Python)
bramble-cove         right=True score=1.00 identical=True wrong-decision-rejected=True
cinder-vale          right=True score=1.00 identical=True wrong-decision-rejected=True
cobalt-finch         right=True score=1.00 identical=True wrong-decision-rejected=True
ember-lagoon         right=True score=1.00 identical=True wrong-decision-rejected=True
fennel-reach         right=True score=1.00 identical=True wrong-decision-rejected=True
garnet-sound         right=True score=1.00 identical=True wrong-decision-rejected=True
hazel-tundra         right=True score=1.00 identical=True wrong-decision-rejected=True
heather-quay         right=True score=1.00 identical=True wrong-decision-rejected=True
juniper-dell         right=True score=1.00 identical=True wrong-decision-rejected=True
lichen-bay           right=True score=1.00 identical=True wrong-decision-rejected=True
marlin-crest         right=True score=1.00 identical=True wrong-decision-rejected=True
opal-thicket         right=True score=1.00 identical=True wrong-decision-rejected=True
pewter-glade         right=True score=1.00 identical=True wrong-decision-rejected=True
quill-brook          right=True score=1.00 identical=True wrong-decision-rejected=True
russet-heath         right=True score=1.00 identical=True wrong-decision-rejected=True
saffron-weir         right=True score=1.00 identical=True wrong-decision-rejected=True
slate-loch           right=True score=1.00 identical=True wrong-decision-rejected=True
sorrel-pike          right=True score=1.00 identical=True wrong-decision-rejected=True
tansy-marsh          right=True score=1.00 identical=True wrong-decision-rejected=True
thistle-moor         right=True score=1.00 identical=True wrong-decision-rejected=True
umber-falls          right=True score=1.00 identical=True wrong-decision-rejected=True
violet-ford          right=True score=1.00 identical=True wrong-decision-rejected=True
wren-hollow          right=True score=1.00 identical=True wrong-decision-rejected=True
yarrow-shoal         right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
