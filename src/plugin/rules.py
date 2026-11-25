"""The answer key's rules for the DNDi Travel and Reimbursement Policy, version 3.0 (effective 1 January 2022), as
exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a
verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. Three thresholds, each measured the way its clause says:

- "business-single-leg" (lines 125, 130-132): "when a single leg journey is nine hours or more". Inclusive
  ("or more"): a nonstop of 540 scheduled minutes qualifies, 539 does not. A journey with a connection is not
  a single-leg journey, so it is False, unless one of its flights alone reaches 540 minutes, which a reader
  could also call a single leg of nine hours or more (None).
- "business-multi-leg" (lines 125-129): "for multi-leg journeys if the combined travel time of the journey is
  11 hours or more, including a maximum of 2 hours of connection time". Inclusive. For a nonstop the combined
  time is its one flight. For a connection the phrase "including a maximum of 2 hours of connection time" has
  readings that differ: the ground time counts up to two hours, or a connection over two hours breaks the
  journey, or only the flights count. True when the flights alone reach 660 minutes and every connection is
  within 120 minutes (every reading agrees); False when the whole elapsed journey is under 660 minutes (every
  reading agrees); otherwise None, the scenario's unclear phrase.
- "premium-economy" (lines 141-142): "when one flight is over 6 hours". Strict ("over"), per flight: True
  when any one flight's scheduled minutes exceed 360.

The scheduled minutes stand for the flying time: nothing else is known when the ticket is bought.

Annex 2 (lines 304-317): the air-cost ceilings came out of the PDF with the amounts on lines apart from their
routes and one row garbled, so no scenario depends on reading the table. Every economy or premium economy
fare a case books or holds is under the lowest amount any reading of the table gives its trip (800 euros for a
trip within one continent, 1,200 euros between continents); every business fare above that has the Head of
Financial Control's written approval of the trip's air cost on file (lines 108-111). `ceiling_checked` raises
otherwise.

Approvers. Line 56-58 and Annex 1 (lines 269-275): the Travel Request form is approved before booking, by the
Staff member's supervisor or, for Consultants, Members of a Body of DNDi and Guests, by the manager responsible;
every trip record holds that approval. Under the template's rule 4' (SYNC_NOTES.md), a booking whose sign-offs
are already on file accepts each of those roles and NONE, and a sign-off on file that the decision does not use
is accepted beside NONE (rule 4(b)); a hold accepts only the role(s) it awaits (NOT_NAMED where the handbook
names none).
"""

from contract import Approver, Cabin, Clause, Counterparts, Decision, ReasonCode, Routing, SignOffSubject, TravellerKind

from .world import day_number, days_between, utc_minute, utc_offset

HANDBOOK = "DNDi Travel and Reimbursement Policy, version 3.0, effective 1 January 2022"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.OBJECTIVE_SCOPE: "I. Objective & Scope",
    Clause.TRAVEL_PRINCIPLES: "A. Travel Principles",
    Clause.INSURANCE: "1. Insurance",
    Clause.PERSONAL_LEAVE: "2. Personal leave",
    Clause.ARRANGING_TRAVEL: "B. Process for arranging DNDi Travel",
    Clause.TRAVEL_EXPENSES: "C. Travel Expenses",
    Clause.SUITABILITY_OF_EXPENSES: "2. Suitability of expenses",
    Clause.MEANS_OF_TRAVEL: "D. Means of DNDi Travel",
    Clause.AIR_TRAVEL: "1. Air Travel",
    Clause.CLASS_AND_ROUTE: "a. Class and route",
    Clause.TRAVEL_CLASS: "b. Travel class",
    Clause.EXTRA_LEGROOM: "c. Extra legroom",
    Clause.LOYALTY_PROGRAMMES: "d. Loyalty programmes",
    Clause.CARBON_FOOTPRINT: "e. Carbon footprint",
    Clause.RAIL_TRAVEL: "2. Rail Travel",
    Clause.ACCOMMODATION: "E. Accommodation",
    Clause.TIME_OFF_IN_LIEU: "1. Time off in lieu rules for DNDi Travel",
    Clause.TRAVEL_INSURANCE: "3. DNDi Travel insurance",
    Clause.REQUEST_WORKFLOW: "Annex 1: DNDi Travel Request Workflow",
    Clause.COSTS_ANNEX: "Annex 2: Costs",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both
# sides of each). ">=" is inclusive ("or more"), ">" strict ("over").
DURATION_RULES = (
    {"name": "business-single-leg", "minutes": 540, "operator": ">=", "lines": [125, 125],
     "quote": "when a single leg journey is nine hours or more"},
    {"name": "business-multi-leg", "minutes": 660, "operator": ">=", "lines": [125, 128],
     "quote": "for multi-leg journeys if the combined travel time of the journey is 11 hours or more, including a "
              "maximum of 2 hours of connection time"},
    {"name": "premium-economy", "minutes": 360, "operator": ">", "lines": [141, 142],
     "quote": "DNDi Travellers shall be authorized to purchase extra legroom or a premium economy ticket when one "
              "flight is over 6 hours."},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 125-129: at most 2 hours of connection time, and the journey "resumes within 12 hours".
CONNECTION_MINUTES = 120
RESUME_MINUTES = 720
# Lines 103-105: the least costly economy routing, "provided that the total journey time does not exceed the
# total journey time of the most direct route by four or more hours": 240 minutes more is too long, 239 is not.
MARGIN_MINUTES = 240
# Line 112: "Every airline ticket above EUR 5'000" needs the Strategy and Operations Director's approval.
TICKET_LIMIT_CENTS = 500_000
# Lines 44-45: avoid "more than five DNDi Travellers taking the same routing".
MOST_ON_ONE_ROUTING = 5
# Line 160: "train trips under 6 hours shall be selected over flying, whenever possible". Only trains well
# away from the line are modelled: under 360 minutes and on time (refuse the flight), or 480 minutes or more.
TRAIN_LIMIT = 360
TRAIN_FAR = 480
# Lines 115-117: plan "at least 45 days in advance for intercontinental DNDi Travel and 15 days in advance for
# regional DNDi Travel" (an endeavour, not a ban).
PLAN_DAYS_INTERCONTINENTAL = 45
PLAN_DAYS_REGIONAL = 15
# Annex 2, read cautiously (see the module docstring): below every amount any reading could give.
SAFE_REGIONAL_CENTS = 80_000
SAFE_INTERCONTINENTAL_CENTS = 120_000
# The continents of the countries the scenarios fly between.
CONTINENTS = {
    "GB": "EUROPE", "IE": "EUROPE", "FR": "EUROPE", "NL": "EUROPE", "DE": "EUROPE", "CH": "EUROPE", "ES": "EUROPE",
    "IT": "EUROPE", "DK": "EUROPE", "US": "NORTH_AMERICA", "CA": "NORTH_AMERICA", "BR": "SOUTH_AMERICA",
    "ZA": "AFRICA", "KE": "AFRICA", "EG": "AFRICA", "IN": "ASIA", "SG": "ASIA", "JP": "ASIA",
}
# Night, for "Flights include overnight travel" (line 130): a flight is clearly overnight when it is in the air
# between midnight and 06:00 on the clocks of both the airport it leaves and the airport it reaches, and
# clearly not when it is in the air at no such time on either clock.
NIGHT_END = 6 * 60

TRAVEL_REQUEST_ROLE = {
    TravellerKind.STAFF: Approver.SUPERVISOR, TravellerKind.CONSULTANT: Approver.MANAGER_RESPONSIBLE,
    TravellerKind.BODY_MEMBER: Approver.MANAGER_RESPONSIBLE, TravellerKind.GUEST: Approver.MANAGER_RESPONSIBLE,
}
# Line 133-134: business class needs the Executive Director's prior approval, or by delegation the Operations
# and Strategy Director's.
BUSINESS_ROLES = [Approver.EXECUTIVE_DIRECTOR, Approver.STRATEGY_OPERATIONS_DIRECTOR]
# Lines 110-111: the Head of Financial Control, or the Finance Director in that person's absence.
COST_ROLES = [Approver.FINANCIAL_CONTROL_HEAD, Approver.FINANCE_DIRECTOR]
# Lines 112-114: the Strategy and Operations Director (the others only in that person's absence).
TICKET_ROLES = [Approver.STRATEGY_OPERATIONS_DIRECTOR]

UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]
CONNECTION_PHRASE = "including a maximum of 2 hours of connection time"

LOWEST_CLAUSES = [Clause.CLASS_AND_ROUTE, Clause.AIR_TRAVEL, Clause.TRAVEL_CLASS]
ROUTE_CLAUSES = [Clause.CLASS_AND_ROUTE, Clause.AIR_TRAVEL]
BUSINESS_CLAUSES = [Clause.TRAVEL_CLASS, Clause.AIR_TRAVEL]
LEGROOM_CLAUSES = [Clause.EXTRA_LEGROOM, Clause.AIR_TRAVEL]
LONG_BUSINESS = [ReasonCode.LONG_FLIGHT_APPROVED, ReasonCode.INTERNATIONAL_LONG_FLIGHT]
NOT_LONG = [ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET, ReasonCode.UPGRADE_NOT_ELIGIBLE]


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s flights out reach or pass the handbook's ``rule``."""
    if offer.return_segments:
        raise ValueError("a round trip is not modelled by this handbook's scenarios")
    flights = [segment.scheduled_minutes for segment in offer.segments]
    limit = LIMITS[rule]
    if rule == "premium-economy":
        return max(flights) > limit
    if rule == "business-single-leg":
        if len(flights) == 1:
            return flights[0] >= limit
        return None if max(flights) >= limit else False
    if rule == "business-multi-leg":
        if any(layover > RESUME_MINUTES for layover in offer.layover_minutes):
            raise ValueError("a connection over 12 hours is not modelled")
        if sum(flights) >= limit and all(layover <= CONNECTION_MINUTES for layover in offer.layover_minutes):
            return True
        if offer.elapsed_minutes < limit:
            return False
        return None
    raise ValueError(f"unknown duration rule {rule!r}")


def long_enough(offer):
    """Lines 125-129, either branch: True, False or None (unclear)."""
    verdicts = {over("business-single-leg", offer), over("business-multi-leg", offer)}
    if True in verdicts:
        return True
    return False if verdicts == {False} else None


def night_overlap(start_utc, end_utc, offset):
    """Whether the UTC minutes [start, end) cover any time from midnight to 06:00 on a clock at ``offset``."""
    start, end = start_utc + offset, end_utc + offset
    day = start // 1440
    while day * 1440 < end:
        if day * 1440 < end and day * 1440 + NIGHT_END > start:
            return True
        day += 1
    return False


def overnight(offer):
    """Line 130, "Flights include overnight travel": True when some flight is clearly overnight, False when every
    flight is clearly a day flight; anything else is not modelled."""
    kinds = []
    for segment in offer.segments:
        start, end = utc_minute(segment.depart_utc), utc_minute(segment.arrive_utc)
        clocks = {night_overlap(start, end, utc_offset(segment.origin)),
                  night_overlap(start, end, utc_offset(segment.destination))}
        kinds.append(clocks.pop() if len(clocks) == 1 else None)
    if True in kinds:
        return True
    if all(kind is False for kind in kinds):
        return False
    raise ValueError("a flight overnight on one airport's clock only is not modelled")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def one(offers, what):
    if len(offers) != 1:
        raise ValueError(f"{what}: {len(offers)} offers tie or none is listed; not modelled")
    return offers[0]


def signed(trip, subject):
    return [record for record in trip.sign_offs if record.subject == subject]


def roles(records):
    return [record.role for record in records]


def on_route(trip, offers, date):
    return [offer for offer in offers if offer.segments[0].origin == trip.origin.code
            and offer.segments[-1].destination == trip.destination.code and offer.segments[0].depart_local[:10] == date]


def intercontinental(trip):
    return CONTINENTS[trip.origin.country] != CONTINENTS[trip.destination.country]


def ceiling_checked(trip, offer):
    """Annex 2 is never read: the fare is under every reading's amount, or the air cost's approval is on file.
    Returns the cost approvers the booking relies on."""
    safe = SAFE_INTERCONTINENTAL_CENTS if intercontinental(trip) else SAFE_REGIONAL_CENTS
    if offer.fare_cents <= safe:
        return []
    approved = [role for role in roles(signed(trip, SignOffSubject.AIR_COST)) if role in COST_ROLES]
    if offer.cabin in (Cabin.ECONOMY, Cabin.PREMIUM_ECONOMY) or not approved:
        raise ValueError("a fare that a reading of the Annex 2 table could put over its ceiling is not modelled")
    return approved


def routing(trip, economy):
    """Lines 103-107: the least costly economy routing whose total journey time is less than four hours over the
    most direct route's; personal preference is not a basis for choosing a route. Returns (offers, reasons,
    note)."""
    if not economy:
        raise ValueError("no economy offer can be bought")
    fewest = min(offer.stops for offer in economy)
    direct = min(offer.elapsed_minutes for offer in economy if offer.stops == fewest)
    acceptable = [offer for offer in economy if offer.elapsed_minutes - direct < MARGIN_MINUTES]
    chosen = one(cheapest(acceptable), "cheapest acceptable economy routing")
    low = cheapest(economy)
    if chosen not in low:
        return ([chosen], [ReasonCode.CONNECTION_TOO_LONG, ReasonCode.LOWEST_FARE],
                (f"lines 103-105: the cheaper routing takes {low[0].elapsed_minutes - direct} minutes more than the most "
                 "direct route, four hours or more, so the least costly acceptable routing is booked"))
    if trip.requested_routing == Routing.NONSTOP and chosen.stops:
        nonstops = cheapest([offer for offer in economy if offer.stops == 0])
        if not nonstops:
            raise ValueError("a nonstop request with no nonstop listed is not modelled")
        extra = chosen.elapsed_minutes - direct
        # The nonstop asked for is declined on the handbook's own lowest-routing test, so LOWEST_FARE stays beside
        # the specific codes (lead's decision, the same in every plugin).
        return ([chosen], [ReasonCode.LOWEST_FARE, ReasonCode.COST_SAVINGS, ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE,
                           ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN],
                (f"lines 103-107: the connection is cheaper and takes {extra} minutes more than the most direct route, "
                 "less than four hours, and personal preference is not a basis for choosing the route, so the "
                 "connection is booked"))
    if any(offer.stops == 0 for offer in economy) and chosen.stops:
        raise ValueError("a cheapest connection for a traveller who did not ask for a nonstop is not modelled")
    return [chosen], [ReasonCode.LOWEST_FARE], "lines 102-105: the least costly economy routing"


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its searches: the decision, and every accepted offer id,
    cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused by this
    handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.return_date:
        raise ValueError("a round-trip ticket is not modelled")
    form = roles(signed(trip, SignOffSubject.TRAVEL_REQUEST))
    if form != [TRAVEL_REQUEST_ROLE[trip.traveller_kind]]:
        raise ValueError("every case holds one approved Travel Request form, by the role Annex 1 names")
    on_file = [Approver.NONE, *roles(trip.sign_offs)]
    ends = {trip.origin.code, trip.destination.code}
    if trip.home_airport.code != trip.workplace_airport.code and ends == {trip.home_airport.code,
                                                                          trip.workplace_airport.code}:
        if trip.contract_travel_terms:
            raise ValueError("a contract that covers the journey to work is not modelled")
        return answer(Decision.REFUSE, [], [ReasonCode.HOME_TO_WORK_JOURNEY, ReasonCode.OUTSIDE_POLICY_SCOPE,
                                            ReasonCode.PERSONAL_TRAVEL_NOT_COVERED], on_file,
                      [Clause.TRAVEL_PRINCIPLES, Clause.OBJECTIVE_SCOPE],
                      "Line 39: journeys between an individual's home and regular place of work are not DNDi Travel, and "
                      "the footnote's exception (line 52, the traveller's contract) does not apply; lines 20-21: the "
                      "policy covers travel for DNDi business. DNDi buys no ticket.")
    if trip.train_minutes:
        if trip.train_minutes < TRAIN_LIMIT:
            if not trip.train_arrives_in_time:
                raise ValueError("a short train that does not arrive in time is not modelled")
            return answer(Decision.REFUSE, [], [ReasonCode.RAIL_PREFERRED], on_file,
                          [Clause.RAIL_TRAVEL, Clause.MEANS_OF_TRAVEL],
                          f"Line 160: train trips under 6 hours shall be selected over flying whenever possible; the "
                          f"train takes {trip.train_minutes} minutes and arrives in time. DNDi buys no flight.")
        if trip.train_minutes < TRAIN_FAR:
            raise ValueError("a train of six to eight hours is not modelled")
    travel = on_route(trip, offers, trip.travel_date)
    seated = [offer for offer in travel if offer.seats_available]
    economy = [offer for offer in seated if offer.cabin == Cabin.ECONOMY]
    planning(trip)
    if trip.business_travel_date != trip.travel_date:
        return personal(trip, offers, economy, on_file)
    if trip.travelling_with:
        return crowd(trip, economy, on_file)
    if trip.requested_cabin == Cabin.BUSINESS:
        return business_request(trip, seated, economy, on_file)
    if trip.requested_cabin == Cabin.PREMIUM_ECONOMY:
        return premium_request(trip, seated, economy, on_file)
    if trip.requested_cabin != Cabin.ECONOMY or trip.traveller_pays_difference:
        raise ValueError("this economy request is not modelled")
    return economy_request(trip, economy, on_file)


def planning(trip):
    """Lines 115-117: plan at least 45 days ahead (intercontinental) or 15 (regional), "endeavor", with any
    exception documented by the traveller: never a refusal. Cases booked later carry the traveller's note."""
    ahead = days_between(trip.booking_date, trip.travel_date)
    least = PLAN_DAYS_INTERCONTINENTAL if intercontinental(trip) else PLAN_DAYS_REGIONAL
    if ahead < least and not trip.planning_note:
        raise ValueError("a late booking without the traveller's documented reason is not modelled")
    if ahead >= least and trip.planning_note:
        raise ValueError("a planning note on a trip planned in time is not modelled")
    return ahead < least


def economy_request(trip, economy, on_file):
    chosen, reasons, note = routing(trip, economy)
    clauses = [*LOWEST_CLAUSES]
    notes = [note]
    for offer in chosen:
        ceiling_checked(trip, offer)
    if trip.requested_airline:
        if any(offer.carrier == trip.requested_airline for offer in chosen) or reasons != [ReasonCode.LOWEST_FARE]:
            raise ValueError("an airline wish that the least costly routing meets is not modelled")
        # Line 106 and lines 144-146 decline the airline because the least costly routing must still be taken: the
        # ground is the lowest-cost rule itself, so LOWEST_FARE stays beside LOYALTY_PROGRAM_PREFERENCE.
        reasons = [*reasons, ReasonCode.LOYALTY_PROGRAM_PREFERENCE]
        clauses.append(Clause.LOYALTY_PROGRAMMES)
        notes.append("line 106: personal preference shall not be the basis for selecting a route; lines 144-146: "
                     "loyalty programmes only as long as the most direct, adequate and economic route is still selected")
    if planning(trip):
        notes.append(f"lines 115-117: the trip is booked {days_between(trip.booking_date, trip.travel_date)} days "
                     "ahead, but planning ahead is an endeavour and the traveller documented the exception, so the "
                     "cheapest fare is still bought")
    return answer(Decision.BOOK, chosen, reasons, on_file, clauses, "; ".join(notes) + ".")


def declined(trip, economy, on_file, reasons, clauses, why):
    """A better cabin the traveller may not have: the least costly economy routing instead. The reason names why
    the cabin is declined, so LOWEST_FARE (the economy fare's own reason) is not accepted."""
    chosen, routing_reasons, note = routing(trip, economy)
    if routing_reasons != [ReasonCode.LOWEST_FARE]:
        raise ValueError("a declined cabin whose economy fare turns on the routing rule is not modelled")
    for offer in chosen:
        ceiling_checked(trip, offer)
    return answer(Decision.BOOK, chosen, reasons, on_file, [*clauses, *LOWEST_CLAUSES], f"{why}; {note}.")


def premium_request(trip, seated, economy, on_file):
    """Lines 141-142: premium economy when one flight is over 6 hours."""
    premium = [offer for offer in seated if offer.cabin == Cabin.PREMIUM_ECONOMY]
    verdicts = {over("premium-economy", offer) for offer in [*premium, *economy]}
    if len(verdicts) != 1 or not premium:
        raise ValueError("premium offers on both sides of the 6-hour line, or none, are not modelled")
    if verdicts.pop():
        chosen = one(cheapest(premium), "cheapest premium economy fare")
        if chosen.stops:
            raise ValueError("a premium economy fare on a connection is not modelled")
        ceiling_checked(trip, chosen)
        return answer(Decision.BOOK, [chosen], [ReasonCode.PREMIUM_ECONOMY_ALLOWED], on_file, LEGROOM_CLAUSES,
                      "Lines 141-142: a flight over 6 hours, so a premium economy ticket is authorized and the traveller "
                      "asks for one: the cheapest premium economy fare.")
    return declined(trip, economy, on_file, NOT_LONG, LEGROOM_CLAUSES,
                    "Lines 141-142: premium economy is authorized only when one flight is over 6 hours, and no flight "
                    "here is; lines 102 and 119: economy class")


def business_request(trip, seated, economy, on_file):
    """Lines 119-139: business class only for a documented medical condition or a long overnight journey to
    meetings with external partners, always with the Executive Director's prior approval; of at least two
    business options the most economical is chosen."""
    business = [offer for offer in seated if offer.cabin == Cabin.BUSINESS]
    if len(business) < 2:
        raise ValueError("fewer than two business options is not modelled (lines 137-139)")
    low = one(cheapest(business), "cheapest business fare")
    approved = [role for role in roles(signed(trip, SignOffSubject.BUSINESS_CLASS)) if role in BUSINESS_ROLES]
    if trip.medical_certificate_on_file:
        cost = ceiling_checked(trip, low)
        if cost:
            raise ValueError("a medical business fare above the Annex 2 amounts is not modelled")
        if approved:
            return answer(Decision.BOOK, [low], [ReasonCode.MEDICAL_NEED], on_file, BUSINESS_CLAUSES,
                          "Lines 121-122: a medical condition documented by a medical certificate obliges the traveller "
                          "to fly business class; lines 133-134: the Executive Director approved it beforehand; lines "
                          "137-139: the most economical of the business options.")
        return answer(Decision.FLAG_FOR_APPROVAL, [low], [ReasonCode.APPROVAL_REQUIRED, ReasonCode.MEDICAL_NEED],
                      BUSINESS_ROLES, BUSINESS_CLAUSES,
                      "Lines 121-122: the medical certificate allows business class, but lines 133-134: all business "
                      "class travel requires the Executive Director's prior approval (or the Operations and Strategy "
                      "Director's by delegation), and none is on file: hold the most economical business fare.")
    lengths = {long_enough(offer) for offer in business}
    nights = {overnight(offer) for offer in business}
    if len(lengths) != 1 or len(nights) != 1:
        raise ValueError("business options on both sides of a condition are not modelled (set background 0)")
    length, night = lengths.pop(), nights.pop()
    arrival = day_number(low.segments[-1].arrive_local[:10])
    meets = trip.meeting_with == Counterparts.EXTERNAL_PARTNERS and day_number(trip.first_meeting_date) - arrival in (0, 1)
    failing = []
    if length is False:
        failing.append("the journey is under nine hours on a single leg and under 11 hours combined (lines 125-129)")
    if not night:
        failing.append("the flights do not include overnight travel (line 130)")
    if not meets:
        failing.append("the traveller does not meet external partners the same or following day (lines 131-132)")
    if failing:
        return declined(trip, economy, on_file, NOT_LONG, BUSINESS_CLAUSES,
                        f"Lines 124-132: business class needs every condition met, and {'; '.join(failing)}; lines "
                        "102 and 119: economy class")
    if not approved:
        raise ValueError("a long-journey business request without the Executive Director's approval is not modelled")
    cost = ceiling_checked(trip, low)
    relied = [*on_file]
    if length is None:
        held = [low, one(routing(trip, economy)[0], "economy reading")]
        return answer(Decision.FLAG_FOR_APPROVAL, held, UNCLEAR_REASONS, [Approver.NOT_NAMED, *BUSINESS_ROLES],
                      BUSINESS_CLAUSES,
                      "Lines 125-129: the flights alone are under 11 hours and the connection is over two hours; the "
                      "handbook counts 'combined travel time ... including a maximum of 2 hours of connection time', "
                      "which may count two hours of the wait (11 hours or more: business) or exclude a journey whose "
                      "connection is longer, or the ground time altogether (under 11 hours: economy). Hold for the "
                      "Executive Director, who approves business class (lines 133-134).", phrase=CONNECTION_PHRASE)
    if low.fare_cents > TICKET_LIMIT_CENTS:
        ticket = [role for role in roles(signed(trip, SignOffSubject.TICKET_PRICE)) if role in TICKET_ROLES]
        if ticket:
            raise ValueError("a ticket above EUR 5,000 already approved is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, [low], [ReasonCode.APPROVAL_REQUIRED], TICKET_ROLES,
                      [*BUSINESS_CLAUSES, Clause.CLASS_AND_ROUTE],
                      f"Lines 124-134: business class is allowed and approved, but line 112: every airline ticket above "
                      f"EUR 5,000 must be approved before purchase by the Strategy and Operations Director; the most "
                      f"economical business fare is {low.fare_cents} cents and no such approval is on file: hold it.")
    clauses = [*BUSINESS_CLAUSES]
    if low.fare_cents == TICKET_LIMIT_CENTS:
        clauses.append(Clause.CLASS_AND_ROUTE)
    return answer(Decision.BOOK, [low], LONG_BUSINESS, [*relied, *cost], clauses,
                  "Lines 124-132: the journey is long enough, includes overnight travel and the traveller meets external "
                  "partners the same or next day; lines 133-134: the Executive Director approved business class; lines "
                  "137-139: the most economical business option; lines 108-111: the air cost is approved in writing by "
                  "the Head of Financial Control"
                  + ("; line 112: the ticket is not above EUR 5,000." if low.fare_cents == TICKET_LIMIT_CENTS else "."))


def crowd(trip, economy, on_file):
    """Lines 44-45: as far as possible, separate routings so that no more than five DNDi Travellers take the same
    routing."""
    if trip.requested_cabin != Cabin.ECONOMY or trip.requested_airline:
        raise ValueError("a group case outside plain economy is not modelled")
    taken = {}
    for colleague in trip.travelling_with:
        if colleague.cabin != Cabin.ECONOMY:
            raise ValueError("a colleague outside economy is not modelled")
        taken[(colleague.flight_number, colleague.date)] = taken.get((colleague.flight_number, colleague.date), 0) + 1

    def riders(offer):
        return max(taken.get((segment.flight_number, segment.depart_local[:10]), 0) for segment in offer.segments)

    chosen, reasons, note = routing(trip, economy)
    if reasons != [ReasonCode.LOWEST_FARE]:
        raise ValueError("a group case that turns on the routing rule is not modelled")
    if riders(chosen[0]) < MOST_ON_ONE_ROUTING:
        clauses = [*LOWEST_CLAUSES, Clause.INSURANCE]
        return answer(Decision.BOOK, chosen, reasons, on_file, clauses,
                      f"{note}; lines 44-45: with this traveller {riders(chosen[0]) + 1} DNDi Travellers take that "
                      "routing, not more than five.")
    others = [offer for offer in economy if riders(offer) < MOST_ON_ONE_ROUTING]
    alternative, alt_reasons, _ = routing(trip, others)
    if alt_reasons != [ReasonCode.LOWEST_FARE]:
        raise ValueError("a separate routing that turns on the routing rule is not modelled")
    return answer(Decision.BOOK, alternative, [ReasonCode.TRAVELLER_LIMIT_PER_FLIGHT], on_file,
                  [Clause.INSURANCE, Clause.TRAVEL_PRINCIPLES],
                  "Lines 44-45: five DNDi Travellers already take the cheapest routing, and a sixth would be more than "
                  "five; a separate routing is possible, so the least costly economy fare on another routing.")


def personal(trip, offers, economy, on_file):
    """Lines 46-50: personal leave connected with DNDi Travel, incidental and approved on the Travel Request form;
    the traveller pays any difference above the cost of the DNDi Travel alone."""
    if trip.requested_cabin != Cabin.ECONOMY or trip.requested_airline or not trip.personal_days_approved:
        raise ValueError("only approved personal days in economy are modelled")
    wanted, reasons, _ = routing(trip, economy)
    alone = [offer for offer in on_route(trip, offers, trip.business_travel_date)
             if offer.seats_available and offer.cabin == Cabin.ECONOMY]
    base, _, _ = routing(trip, alone)
    if reasons != [ReasonCode.LOWEST_FARE] or wanted[0].fare_cents <= base[0].fare_cents:
        raise ValueError("only a dearer personal date bought at the least costly routing is modelled")
    if not trip.traveller_pays_difference:
        raise ValueError("a personal date without the traveller paying the difference is not modelled")
    extra = wanted[0].fare_cents - base[0].fare_cents
    return answer(Decision.BOOK, wanted, [ReasonCode.PERSONAL_COST_PAID_BY_TRAVELER, ReasonCode.LOWEST_FARE], on_file,
                  [Clause.PERSONAL_LEAVE, Clause.TRAVEL_PRINCIPLES],
                  f"Lines 46-50: the personal days are incidental and approved on the Travel Request form; DNDi pays the "
                  f"cost of the DNDi Travel alone ({base[0].fare_cents} cents) and the traveller pays the {extra} cents "
                  "more of the least costly fare on the day they leave, which is the ticket booked.")
