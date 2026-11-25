"""Writes the DNDi scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Flight numbers that a trip record refers to (colleagues' flights) are read from the shared world, so they
match what search_flights lists. Expected answers are hand-written here; tests/test_scenarios.py checks them
against rules.solve.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from plugin.world import pinned_offers

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on -----
SCOPE = keep(20, 21, "travel for DNDi business and funded by DNDi (\"DNDi Travel\")",
             "the policy covers travel for DNDi business")
COMMUTE = keep(39, 39, "Journeys between an individual's home and regular place of work are not considered DNDi Travel.",
               "the journey between home and the regular place of work is not DNDi Travel")
FOOTNOTE = keep(52, 52, "Unless stated otherwise in the DNDi Traveller's contract",
                "the footnote's exception: the traveller's contract")
ROUTINGS = keep(44, 45, None, "separate routings so that no more than five DNDi Travellers take the same routing")
PERSONAL = keep(47, 50, None, "personal leave: incidental, approved on the Travel Request form, traveller pays the "
                "difference")
REQUEST = keep(56, 58, "must be completed and approved before booking the elements of DNDi Travel",
               "the Travel Request form is approved before booking")
WORKFLOW = keep(269, 275, None, "Annex 1: who approves the Travel Request form for each kind of traveller")
ECONOMY = keep(102, 102, "DNDi Travellers shall always use economy class.", "economy class")
ROUTE = keep(103, 105, None, "the least costly economy routing within four hours of the most direct route")
PREFERENCE = keep(106, 107, None, "personal preference is not a basis for the route; a lower cost alternative may be "
                  "imposed")
COST = keep(108, 111, None, "the air cost above the Annex 2 ceilings needs the Head of Financial Control's prior "
            "written approval")
TICKET = keep(112, 114, None, "every ticket above EUR 5,000 needs the Strategy and Operations Director's approval "
              "before purchase")
ALL_ECONOMY = keep(119, 119, "All DNDi Travel must be in economy class.", "economy class")
MEDICAL = keep(120, 122, None, "business class for a medical condition documented by a medical certificate")
CONDITIONS = keep(124, 132, None, "business class: nine hours single leg or 11 hours multi-leg, overnight, external "
                  "partners the same or following day")
BUSINESS_APPROVAL = keep(133, 134, None, "all business class needs the Executive Director's prior approval")
OPTIONS = keep(137, 139, None, "at least two business options; the most economical is selected")
LEGROOM = keep(141, 142, None, "premium economy when one flight is over 6 hours")
LOYALTY = keep(144, 146, None, "loyalty programmes only if the most direct, adequate and economic route is still "
               "selected")
RAIL = keep(160, 161, "train trips under 6 hours shall be selected over flying, whenever possible",
            "a train under 6 hours instead of the flight")

# ----- nearby clauses that must not change the answer -----
PLAN = aside(115, 117, "DNDi Travellers shall endeavor to plan DNDi Travel at least 45 days in advance for "
             "intercontinental DNDi Travel", "an endeavour to plan ahead, with exceptions documented: not a ban")
MAY_NOT = aside(135, 136, "DNDi may not allow business class travel in some specific cases",
                "a discretion the Executive Director's approval already settles")
RECUPERATION = aside(222, 223, "Staff are entitled to a half day recuperation the following day",
                     "time off after overnight travel, not a cabin rule")
INSURED_LEAVE = aside(41, 43, "covered by DNDi travel insurance for seven calendar days",
                      "insurance cover for personal days, not who pays the fare")
LEGROOM_ASIDE = aside(141, 142, "shall be authorized to purchase extra legroom or a premium economy ticket",
                      "a permission the traveller does not take")
ANNEX_COSTS = aside(304, 304, "Annex 2: Costs", "the ceilings table; the fares booked are under every amount in it, or "
                    "the air cost is approved")
TAXI = aside(172, 172, "arrival or departure either before 08.00 or after 20.00", "a taxi rule, not a flight rule")
ACCOMMODATION = aside(210, 210, "When the DNDi Traveller is staying for one week or more",
                      "an accommodation rule about trip length")

# ----- builders -----


def trip(kind="STAFF", form_role=None, form_name="Grace Wanjiru", home="", **fields):
    base = {
        "traveller_name": "", "traveller_title": "", "traveller_kind": kind, "home_airport": "",
        "workplace_airport": "", "contract_travel_terms": "", "origin": "", "destination": "", "travel_date": "",
        "business_travel_date": "", "return_date": "", "booking_date": "", "planning_note": "", "purpose": "",
        "first_meeting_date": "", "meeting_with": "EXTERNAL_PARTNERS", "requested_cabin": "ECONOMY",
        "requested_routing": "ANY", "requested_airline": "", "traveller_pays_difference": False,
        "personal_days_approved": False, "medical_certificate_on_file": False, "train_minutes": 0,
        "train_arrives_in_time": False, "sign_offs": None, "travelling_with": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    base["home_airport"] = base["home_airport"] or home or base["origin"]
    base["workplace_airport"] = base["workplace_airport"] or base["home_airport"]
    if not base["business_travel_date"]:
        base["business_travel_date"] = base["travel_date"]
    role = form_role or ("SUPERVISOR" if kind == "STAFF" else "MANAGER_RESPONSIBLE")
    form = sign(role, form_name, "TRAVEL_REQUEST", "The Travel Request form for this trip, approved before booking")
    base["sign_offs"] = [form] + (base["sign_offs"] or [])
    return base


def sign(role, name, subject, covers):
    return {"role": role, "name": name, "subject": subject, "covers": covers}


ED_IF = sign("EXECUTIVE_DIRECTOR", "Laurent Mercier", "BUSINESS_CLASS",
             "Business class for this trip, if the handbook's conditions for business class are met")
HFC = sign("FINANCIAL_CONTROL_HEAD", "Anna Keller", "AIR_COST",
           "The trip's air cost above the Annex 2 ceiling, for a business class ticket")


def offer(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": sorted(reasons),
            "approvers": sorted(set(approvers)), "clauses": sorted(set(clauses)), "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=0, name="main"):
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


def first_flight(scenario_id, search_spec, slot):
    for name, made in pinned_offers(scenario_id, search_spec):
        if name == slot:
            return made.segments[0].flight_number
    raise KeyError(slot)


S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    if isinstance(searches, dict):
        searches = [searches]
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


SUP = ["NONE", "SUPERVISOR"]  # rule 4': the Travel Request form's approval on file, or NONE
MGR = ["MANAGER_RESPONSIBLE", "NONE"]
LONG_BUSINESS = ["INTERNATIONAL_LONG_FLIGHT", "LONG_FLIGHT_APPROVED"]
NOT_LONG = ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"]
LOWEST_CLAUSES = ["AIR_TRAVEL", "CLASS_AND_ROUTE", "TRAVEL_CLASS"]
BUSINESS = ["AIR_TRAVEL", "TRAVEL_CLASS"]
LEGROOM_CLAUSES = ["AIR_TRAVEL", "EXTRA_LEGROOM"]
BASE = [ECONOMY, ROUTE, REQUEST, WORKFLOW]
LONG_KEEP = [CONDITIONS, BUSINESS_APPROVAL, OPTIONS, COST, REQUEST, WORKFLOW]
BUSINESS_ROLES = ["EXECUTIVE_DIRECTOR", "STRATEGY_OPERATIONS_DIRECTOR"]
FALLBACK = "Business class please, if the policy allows it; otherwise economy is fine."

# ===== easy (5) =====

scenario(
    "cobalt-finch", "easy", ["upgrade_not_taken"],
    "I'm flying New York JFK to Nairobi on January 26th for the trial-site meetings with our Kenyan research partners, "
    "which start on the 28th. Plain economy is fine - the cheapest you can find.",
    trip(traveller_name="Daniel Osei", traveller_title="Clinical Operations Manager, New York office",
         form_name="Rebecca Lindqvist", origin="JFK", destination="NBO", travel_date="2027-01-26",
         booking_date="2026-12-01", purpose="Trial-site meetings with the Kenyan research partners in Nairobi",
         first_meeting_date="2027-01-28"),
    search("JFK", "NBO", "2027-01-26", {
        "kenya": {"carrier": "KQ", "depart": "12:25", "minutes": [845]},
        "delta": {"carrier": "DL", "depart": "21:00", "minutes": [850]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 96000),
        offer("kenya-premium", "kenya", "PREMIUM_ECONOMY", 158000),
        offer("kenya-business", "kenya", "BUSINESS", 520000),
        offer("delta-economy", "delta", "ECONOMY", 101500),
        offer("delta-premium", "delta", "PREMIUM_ECONOMY", 165000),
        offer("delta-business", "delta", "BUSINESS", 549000),
    ]),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["LOWEST_FARE"], SUP, LOWEST_CLAUSES),
    BASE,
    "Two nonstops; the traveller asks for plain economy. Economy class always (lines 102, 119) and the least costly "
    "routing (lines 103-105): Kenya Airways at EUR 960. Premium economy would be authorized (a flight over 6 hours, "
    "lines 141-142) and business class might be, but the traveller does not ask. EUR 960 is under every amount the "
    "Annex 2 table gives a trip between continents. The Travel Request form is approved by the supervisor (lines "
    "56-58, 272).",
    distractors=[LEGROOM_ASIDE])

scenario(
    "juniper-dell", "easy", [],
    "Amsterdam to Madrid on February 9th for the afternoon meeting with the Spanish medicines agency. " + FALLBACK,
    trip(kind="BODY_MEMBER", traveller_name="Pieter van Dam", traveller_title="Member, Scientific Advisory Committee",
         form_name="Ines Moreau", origin="AMS", destination="MAD", travel_date="2027-02-09", booking_date="2027-01-05",
         purpose="Meeting with the Spanish medicines agency in Madrid", first_meeting_date="2027-02-09",
         requested_cabin="BUSINESS", train_minutes=650),
    search("AMS", "MAD", "2027-02-09", {
        "klm": {"carrier": "KL", "depart": "07:05", "minutes": [165]},
        "iberia": {"carrier": "IB", "depart": "08:30", "minutes": [160]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 14800),
        offer("klm-business", "klm", "BUSINESS", 52000),
        offer("iberia-economy", "iberia", "ECONOMY", 16200),
        offer("iberia-business", "iberia", "BUSINESS", 56000),
    ]),
    expected("BOOK", ["klm-economy"], ["ECONOMY"], NOT_LONG, MGR, BUSINESS + LOWEST_CLAUSES),
    [ALL_ECONOMY, CONDITIONS, ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "A morning flight of under three hours within Europe: none of the business-class grounds applies (no medical "
    "certificate, lines 121-122; under nine hours and no overnight travel, lines 124-132), so economy class (lines "
    "102, 119), the cheaper KLM fare, which is the fallback the traveller gives. The train takes over ten hours, far "
    "from the 6-hour rail rule. The manager responsible approved the Travel Request form (Annex 1, line 274).")

scenario(
    "saffron-weir", "easy", ["dearer_option"],
    "Delhi to London Heathrow on February 3rd for the partner workshop at the London university on the 4th. I'd like "
    "premium economy.",
    trip(traveller_name="Priya Raman", traveller_title="Regulatory Affairs Lead, New Delhi office",
         form_name="Arjun Mehta", origin="DEL", destination="LHR", travel_date="2027-02-03",
         booking_date="2026-12-10", purpose="Partner workshop at a London university", first_meeting_date="2027-02-04",
         requested_cabin="PREMIUM_ECONOMY"),
    search("DEL", "LHR", "2027-02-03", {
        "india": {"carrier": "AI", "depart": "13:30", "minutes": [590]},
        "british": {"carrier": "BA", "depart": "14:20", "minutes": [595]},
    }, [
        offer("india-economy", "india", "ECONOMY", 54000),
        offer("india-premium", "india", "PREMIUM_ECONOMY", 98000),
        offer("british-economy", "british", "ECONOMY", 57500),
        offer("british-premium", "british", "PREMIUM_ECONOMY", 104000),
    ]),
    expected("BOOK", ["india-premium"], ["PREMIUM_ECONOMY"], ["PREMIUM_ECONOMY_ALLOWED"], SUP, LEGROOM_CLAUSES),
    [LEGROOM, REQUEST, WORKFLOW],
    "Nonstops of 590 and 595 minutes: one flight over 6 hours, so a premium economy ticket is authorized (lines "
    "141-142) and the traveller asks for it: the cheaper premium economy fare, Air India at EUR 980, under every Annex "
    "2 amount for a trip between continents. No sign-off is named for premium economy.")

scenario(
    "marlin-crest", "easy", ["dearer_option", "overnight", "date_arithmetic"],
    "London Heathrow to Singapore on March 2nd for the supply-contract negotiation with our Singapore manufacturing "
    "partner, starting at 5 pm on the 3rd. " + FALLBACK,
    trip(kind="CONSULTANT", traveller_name="Helen Ashworth", traveller_title="Consultant, chemistry manufacturing",
         form_name="Thomas Brun", origin="LHR", destination="SIN", travel_date="2027-03-02", booking_date="2027-01-04",
         purpose="Supply-contract negotiation with the Singapore manufacturing partner", first_meeting_date="2027-03-03",
         requested_cabin="BUSINESS", sign_offs=[ED_IF, HFC]),
    search("LHR", "SIN", "2027-03-02", {
        "british": {"carrier": "BA", "depart": "14:30", "minutes": [775]},
        "singapore": {"carrier": "SQ", "depart": "15:00", "minutes": [780]},
    }, [
        offer("british-economy", "british", "ECONOMY", 88000),
        offer("british-business", "british", "BUSINESS", 410000),
        offer("singapore-economy", "singapore", "ECONOMY", 91000),
        offer("singapore-business", "singapore", "BUSINESS", 438000),
    ]),
    expected("BOOK", ["british-business"], ["BUSINESS"], LONG_BUSINESS,
             MGR + ["EXECUTIVE_DIRECTOR", "FINANCIAL_CONTROL_HEAD"], BUSINESS + ["CLASS_AND_ROUTE"]),
    LONG_KEEP,
    "Overnight nonstops of 775 and 780 minutes (single leg nine hours or more) leave London in the afternoon and land "
    "on March 3rd before noon; the negotiation with the external partner starts at 5 pm that day, the day of landing "
    "and the day after leaving, so 'the same or following day' holds counted from either end (lines 124-132). The Executive Director approved business "
    "class beforehand (lines 133-134) and the Head of Financial Control approved the air cost above the Annex 2 "
    "ceiling (lines 108-111). Of the two business options the most economical (lines 137-139): BA at EUR 4,100, not "
    "above EUR 5,000.",
    distractors=[MAY_NOT, ANNEX_COSTS])

scenario(
    "heather-quay", "easy", [],
    "Nairobi to London Heathrow on January 20th for the donor review on the 22nd. I'd like British Airways so I "
    "collect my Avios; if that isn't possible, book what the policy allows - I have to be at the review.",
    trip(traveller_name="Wanjiku Kamau", traveller_title="Partnerships Officer, Nairobi office",
         form_name="Samuel Otieno", origin="NBO", destination="LHR", travel_date="2027-01-20",
         booking_date="2026-12-02", purpose="Donor review in London", first_meeting_date="2027-01-22",
         requested_airline="British Airways"),
    search("NBO", "LHR", "2027-01-20", {
        "kenya": {"carrier": "KQ", "depart": "23:10", "minutes": [525]},
        "british": {"carrier": "BA", "depart": "22:40", "minutes": [520]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 61000),
        offer("british-economy", "british", "ECONOMY", 66500),
    ]),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["LOWEST_FARE", "LOYALTY_PROGRAM_PREFERENCE"], SUP,
             LOWEST_CLAUSES + ["LOYALTY_PROGRAMMES"]),
    [ECONOMY, ROUTE, PREFERENCE, LOYALTY, REQUEST, WORKFLOW],
    "Two overnight nonstops, five minutes apart in journey time. Personal preference shall not be the basis for "
    "selecting a route (lines 106-107) and loyalty programmes are allowed only while the most direct, adequate and "
    "economic route is still selected (lines 144-146): the least costly routing, Kenya Airways at EUR 610. The "
    "airline wish is declined on the lowest-cost rule itself, so LOWEST_FARE is accepted beside "
    "LOYALTY_PROGRAM_PREFERENCE.")

# ===== boundary twins (6) =====

AMS_REQUEST = ("Nairobi to Amsterdam on January 27th for the partner workshop on the 29th. I'd prefer the KLM nonstop "
               "if possible; if the handbook wants something else, book that.")


def amsterdam(layover):
    return search("NBO", "AMS", "2027-01-27", {
        "klm": {"carrier": "KL", "depart": "23:55", "minutes": [510]},
        "cairo": {"carrier": "MS", "via": ["CAI"], "depart": "23:55", "minutes": [300, 290], "layovers": [layover]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 72000),
        offer("cairo-economy", "cairo", "ECONOMY", 51000),
    ])


AMS_TRIP = {"traveller_title": "Pharmacovigilance Specialist, Nairobi office", "form_name": "Samuel Otieno",
                "origin": "NBO", "destination": "AMS", "travel_date": "2027-01-27", "booking_date": "2026-12-03",
                "purpose": "Workshop with the Dutch research partners", "first_meeting_date": "2027-01-29",
                "requested_routing": "NONSTOP"}

scenario(
    "tansy-marsh", "boundary_twin", ["multi_leg"], AMS_REQUEST,
    trip(traveller_name="Brian Mwangi", **AMS_TRIP), amsterdam(159),
    expected("BOOK", ["cairo-economy"], ["ECONOMY"],
             ["ALTERNATE_ROUTE_TOO_EXPENSIVE", "ALTERNATE_ROUTE_WITHIN_MARGIN", "COST_SAVINGS", "LOWEST_FARE"], SUP,
             LOWEST_CLAUSES),
    [ROUTE, PREFERENCE, ECONOMY, REQUEST, WORKFLOW],
    "Both leave at 23:55. The KLM nonstop takes 510 minutes; the EgyptAir connection through Cairo 749 (300 + 159 on "
    "the ground + 290), 239 minutes more: it does not exceed the most direct route's journey time by four or more "
    "hours (lines 103-105), and it is EUR 210 cheaper. Personal preference is not a basis for the route and the lower "
    "cost alternative may be imposed (lines 106-107): the connection. It lands on the 28th, a day before the "
    "workshop.",
    twin_of="thistle-moor", twin_fact="connection layover 159 or 160 minutes (journey 239 or 240 minutes longer)")

scenario(
    "thistle-moor", "boundary_twin", ["multi_leg", "dearer_option"], AMS_REQUEST,
    trip(traveller_name="Brian Mwangi", **AMS_TRIP), amsterdam(160),
    expected("BOOK", ["klm-economy"], ["ECONOMY"], ["CONNECTION_TOO_LONG", "LOWEST_FARE"], SUP, LOWEST_CLAUSES),
    [ROUTE, PREFERENCE, ECONOMY, REQUEST, WORKFLOW],
    "As tansy-marsh, but the Cairo connection takes 750 minutes, 240 more than the nonstop: exactly four hours, so it "
    "exceeds the most direct route's journey time by four or more hours (lines 103-105) and is not an acceptable "
    "routing. The least costly acceptable routing is the KLM nonstop the traveller asked for.",
    twin_of="tansy-marsh", twin_fact="connection layover 159 or 160 minutes (journey 239 or 240 minutes longer)")

LON_REQUEST = ("Mumbai to London Heathrow on February 16th for the protocol meetings with our UK research partners "
               "on the 17th. " + FALLBACK)


def mumbai(minutes):
    return search("BOM", "LHR", "2027-02-16", {
        "india": {"carrier": "AI", "depart": "01:55", "minutes": [minutes]},
        "british": {"carrier": "BA", "depart": "02:40", "minutes": [minutes]},
    }, [
        offer("india-economy", "india", "ECONOMY", 52000),
        offer("india-business", "india", "BUSINESS", 295000),
        offer("british-economy", "british", "ECONOMY", 55000),
        offer("british-business", "british", "BUSINESS", 312000),
    ])


LON_TRIP = {"kind": "CONSULTANT", "traveller_name": "Kavita Desai", "traveller_title": "Consultant, regulatory strategy",
                "form_name": "Arjun Mehta", "origin": "BOM", "destination": "LHR", "travel_date": "2027-02-16",
                "booking_date": "2026-12-18", "purpose": "Protocol meetings with the UK research partners",
                "first_meeting_date": "2027-02-17", "requested_cabin": "BUSINESS", "sign_offs": [ED_IF, HFC]}
ON_FILE = MGR + ["EXECUTIVE_DIRECTOR", "FINANCIAL_CONTROL_HEAD"]

scenario(
    "ember-lagoon", "boundary_twin", ["dearer_option", "overnight"], LON_REQUEST, trip(**LON_TRIP), mumbai(540),
    expected("BOOK", ["india-business"], ["BUSINESS"], LONG_BUSINESS, ON_FILE, BUSINESS + ["CLASS_AND_ROUTE"]),
    LONG_KEEP,
    "Overnight nonstops (leaving 01:55 and 02:40, landing that morning) scheduled at 540 minutes: a single leg "
    "journey of nine hours or more (inclusive, line 125). The traveller meets the external partners the following "
    "day; the Executive Director approved business class and the Head of Financial Control the air cost. The most "
    "economical business option: Air India at EUR 2,950.",
    twin_of="garnet-sound", twin_fact="nonstops scheduled at 540 or 535 minutes",
    distractors=[RECUPERATION])

scenario(
    "garnet-sound", "boundary_twin", ["overnight", "upgrade_not_taken"], LON_REQUEST, trip(**LON_TRIP), mumbai(535),
    expected("BOOK", ["india-economy"], ["ECONOMY"], NOT_LONG, ON_FILE, BUSINESS + LOWEST_CLAUSES),
    [CONDITIONS, ALL_ECONOMY, ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "As ember-lagoon, but the nonstops are scheduled at 535 minutes: under nine hours, so the business-class "
    "conditions are not met (lines 124-132) whatever the Executive Director pre-approved. Economy class, the fallback "
    "the traveller gives: Air India at EUR 520. Premium economy would be authorized (lines 141-142) but the traveller "
    "asked for economy as the fallback.",
    twin_of="ember-lagoon", twin_fact="nonstops scheduled at 540 or 535 minutes")

DEL_REQUEST = ("Nairobi to Delhi on February 1st for the manufacturing partner visit on the 2nd. Premium economy "
               "please, if the policy allows it; otherwise economy is fine.")


def delhi(minutes):
    return search("NBO", "DEL", "2027-02-01", {
        "kenya": {"carrier": "KQ", "depart": "09:40", "minutes": [minutes]},
        "india": {"carrier": "AI", "depart": "11:20", "minutes": [minutes]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 41000),
        offer("kenya-premium", "kenya", "PREMIUM_ECONOMY", 69000),
        offer("india-economy", "india", "ECONOMY", 44500),
        offer("india-premium", "india", "PREMIUM_ECONOMY", 73000),
    ])


DEL_TRIP = {"traveller_name": "Faith Njoroge", "traveller_title": "Quality Assurance Manager, Nairobi office",
                "form_name": "Samuel Otieno", "origin": "NBO", "destination": "DEL", "travel_date": "2027-02-01",
                "booking_date": "2026-12-07", "purpose": "Visit to the Indian manufacturing partner",
                "first_meeting_date": "2027-02-02", "requested_cabin": "PREMIUM_ECONOMY"}

scenario(
    "lichen-bay", "boundary_twin", ["dearer_option"], DEL_REQUEST, trip(**DEL_TRIP), delhi(361),
    expected("BOOK", ["kenya-premium"], ["PREMIUM_ECONOMY"], ["PREMIUM_ECONOMY_ALLOWED"], SUP, LEGROOM_CLAUSES),
    [LEGROOM, REQUEST, WORKFLOW],
    "Nonstops scheduled at 361 minutes: one flight over 6 hours (strict, lines 141-142), so premium economy is "
    "authorized and asked for: the cheaper premium fare, Kenya Airways at EUR 690.",
    twin_of="quill-brook", twin_fact="nonstops scheduled at 361 or 360 minutes")

scenario(
    "quill-brook", "boundary_twin", [], DEL_REQUEST, trip(**DEL_TRIP), delhi(360),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], NOT_LONG, SUP, LEGROOM_CLAUSES + LOWEST_CLAUSES),
    [LEGROOM, ALL_ECONOMY, ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "Nonstops scheduled at exactly 360 minutes: not over 6 hours (lines 141-142), so premium economy is not "
    "authorized; economy class (lines 102, 119), the fallback the traveller gives: Kenya Airways at EUR 410.",
    twin_of="lichen-bay", twin_fact="nonstops scheduled at 361 or 360 minutes")

# ===== multi-rule (4) =====

scenario(
    "opal-thicket", "multi_rule", ["multi_leg", "overnight", "dearer_option"],
    "Delhi to Johannesburg on March 8th for the trial-protocol meetings with our South African research partners, "
    "starting on the afternoon of the 9th. " + FALLBACK,
    trip(traveller_name="Rohan Iyer", traveller_title="Head of Clinical Development, New Delhi office",
         form_name="Arjun Mehta", origin="DEL", destination="JNB", travel_date="2027-03-08",
         booking_date="2027-01-10", purpose="Trial-protocol meetings with the South African research partners",
         first_meeting_date="2027-03-09", requested_cabin="BUSINESS", sign_offs=[ED_IF, HFC]),
    search("DEL", "JNB", "2027-03-08", {
        "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "19:00", "minutes": [220, 490], "layovers": [75]},
        "doha": {"carrier": "QR", "via": ["DOH"], "depart": "20:30", "minutes": [245, 495], "layovers": [80]},
    }, [
        offer("dubai-economy", "dubai", "ECONOMY", 69000),
        offer("dubai-business", "dubai", "BUSINESS", 362000),
        offer("doha-economy", "doha", "ECONOMY", 72000),
        offer("doha-business", "doha", "BUSINESS", 389000),
    ]),
    expected("BOOK", ["dubai-business"], ["BUSINESS"], LONG_BUSINESS, SUP + ["EXECUTIVE_DIRECTOR",
                                                                             "FINANCIAL_CONTROL_HEAD"],
             BUSINESS + ["CLASS_AND_ROUTE"]),
    LONG_KEEP,
    "Multi-leg journeys: Emirates flies 220 + 490 = 710 minutes with a 75-minute connection, Qatar 245 + 495 = 740 "
    "with 80. The flights alone reach 11 hours and each connection is within two hours, so the multi-leg condition "
    "holds on every reading of lines 125-129. The second flights cross the night; the traveller meets the external "
    "partners on the afternoon of the 9th, the day of landing and the day after leaving. Executive Director and Head of Financial Control approvals are on "
    "file: the most economical business option, Emirates at EUR 3,620.")

scenario(
    "pewter-glade", "multi_rule", ["upgrade_not_taken"],
    "London Heathrow to Johannesburg on March 10th; the meetings with our South African clinical partners start on "
    "the 11th. " + FALLBACK,
    trip(kind="CONSULTANT", traveller_name="Oliver Grant", traveller_title="Consultant, clinical trial monitoring",
         form_name="Thomas Brun", origin="LHR", destination="JNB", travel_date="2027-03-10", booking_date="2027-01-12",
         purpose="Meetings with the South African clinical partners", first_meeting_date="2027-03-11",
         requested_cabin="BUSINESS", sign_offs=[ED_IF, HFC]),
    search("LHR", "JNB", "2027-03-10", {
        "british": {"carrier": "BA", "depart": "07:30", "minutes": [660]},
        "african": {"carrier": "SA", "depart": "08:00", "minutes": [650]},
    }, [
        offer("british-economy", "british", "ECONOMY", 79000),
        offer("british-business", "british", "BUSINESS", 365000),
        offer("african-economy", "african", "ECONOMY", 76000),
        offer("african-business", "african", "BUSINESS", 349000),
    ]),
    expected("BOOK", ["african-economy"], ["ECONOMY"], NOT_LONG, ON_FILE, BUSINESS + LOWEST_CLAUSES),
    [CONDITIONS, ALL_ECONOMY, ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "Nonstops of 650 and 660 minutes (well over nine hours) to meetings with external partners the next day, but "
    "they leave London in the morning and land at 20:30 and 20:50 local: the flights do not include overnight travel "
    "(line 130), so the conditions are not all met (lines 124-132) and the Executive Director's conditional "
    "pre-approval does not apply. Economy class, the fallback given: South African Airways at EUR 760.")

JNB_REQUEST = ("Johannesburg to London Heathrow on March 15th for meetings with our UK funding partners starting on "
               "the afternoon of the 16th. Business class, please.")


def london(fare):
    return search("JNB", "LHR", "2027-03-15", {
        "british": {"carrier": "BA", "depart": "21:10", "minutes": [710]},
        "virgin": {"carrier": "VS", "depart": "19:55", "minutes": [705]},
    }, [
        offer("virgin-economy", "virgin", "ECONOMY", 81000),
        offer("virgin-business", "virgin", "BUSINESS", 524000),
        offer("british-economy", "british", "ECONOMY", 78000),
        offer("british-business", "british", "BUSINESS", fare),
    ])


JNB_TRIP = {"kind": "CONSULTANT", "traveller_name": "Thandiwe Nkosi", "traveller_title": "Consultant, health economics",
                "form_name": "Thomas Brun", "origin": "JNB", "destination": "LHR", "travel_date": "2027-03-15",
                "booking_date": "2027-01-15", "purpose": "Meetings with the UK funding partners",
                "first_meeting_date": "2027-03-16", "requested_cabin": "BUSINESS", "sign_offs": [ED_IF, HFC]}

scenario(
    "russet-heath", "multi_rule", ["dearer_option", "overnight"], JNB_REQUEST, trip(**JNB_TRIP), london(500000),
    expected("BOOK", ["british-business"], ["BUSINESS"], LONG_BUSINESS, ON_FILE, BUSINESS + ["CLASS_AND_ROUTE"]),
    LONG_KEEP + [TICKET],
    "Overnight nonstops of 705 and 710 minutes, landing on the morning of the 16th, to meetings with external "
    "partners that afternoon (the day of landing, the day after leaving): business class "
    "is allowed and the Executive Director approved it; the Head of Financial Control approved the air cost. The most "
    "economical business option is BA at exactly EUR 5,000.00, which is not above EUR 5,000 (line 112), so no "
    "Strategy and Operations Director approval is needed: book it.",
    twin_of="umber-falls", twin_fact="the BA business fare is EUR 5,000.00 or EUR 5,010.00")

scenario(
    "bramble-cove", "multi_rule", ["dearer_option"],
    "Copenhagen to Madrid on February 23rd for the Board meeting on the 24th. My doctor's certificate says I must fly "
    "business class after my spinal surgery, and the Executive Director has approved it. Business class, please.",
    trip(kind="BODY_MEMBER", traveller_name="Mette Holm", traveller_title="Member, Board of Directors",
         form_name="Ines Moreau", origin="CPH", destination="MAD", travel_date="2027-02-23", booking_date="2027-01-08",
         purpose="Board of Directors meeting in Madrid", first_meeting_date="2027-02-24", meeting_with="COLLEAGUES_ONLY",
         requested_cabin="BUSINESS", medical_certificate_on_file=True, train_minutes=1500,
         sign_offs=[sign("EXECUTIVE_DIRECTOR", "Laurent Mercier", "BUSINESS_CLASS",
                         "Business class for this trip, on the traveller's medical certificate")]),
    search("CPH", "MAD", "2027-02-23", {
        "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "07:00", "minutes": [95, 165], "layovers": [70]},
        "iberia": {"carrier": "IB", "depart": "09:15", "minutes": [200]},
    }, [
        offer("frankfurt-economy", "frankfurt", "ECONOMY", 19800),
        offer("frankfurt-business", "frankfurt", "BUSINESS", 66500),
        offer("iberia-economy", "iberia", "ECONOMY", 17500),
        offer("iberia-business", "iberia", "BUSINESS", 61000),
    ]),
    expected("BOOK", ["iberia-business"], ["BUSINESS"], ["MEDICAL_NEED"], ["EXECUTIVE_DIRECTOR"] + MGR, BUSINESS),
    [MEDICAL, BUSINESS_APPROVAL, OPTIONS, REQUEST, WORKFLOW],
    "A medical condition documented by a medical certificate obliges business class (lines 121-122), however short "
    "the flight; the Executive Director's prior approval is on file (lines 133-134). Of the two business options the "
    "most economical (lines 137-139): Iberia at EUR 610, under every Annex 2 amount for travel within Europe.")

# ===== hidden clause (2) =====

NBO_REQUEST = ("Nairobi to Johannesburg on February 8th for the clinical-trial investigators' meeting on the 9th. "
               "{count} of our team are already booked on the Kenya Airways morning flight; book me on whatever the "
               "handbook prefers.")


def johannesburg():
    return search("NBO", "JNB", "2027-02-08", {
        "kenya": {"carrier": "KQ", "depart": "07:30", "minutes": [245]},
        "african": {"carrier": "SA", "depart": "10:05", "minutes": [250]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 38000),
        offer("african-economy", "african", "ECONOMY", 41500),
    ])


TEAM = ["Joseph Kiprop", "Mercy Achieng", "Peter Mutua", "Lucy Wairimu", "Daniel Korir"]


def team(scenario_id, count):
    flight = first_flight(scenario_id, johannesburg(), "kenya-economy")
    return [{"name": name, "flight_number": flight, "date": "2027-02-08", "cabin": "ECONOMY"} for name in TEAM[:count]]


NBO_TRIP = {"traveller_name": "Esther Chebet", "traveller_title": "Clinical Trial Manager, Nairobi office",
                "form_name": "Samuel Otieno", "origin": "NBO", "destination": "JNB", "travel_date": "2027-02-08",
                "booking_date": "2027-01-04", "purpose": "Clinical-trial investigators' meeting in Johannesburg",
                "first_meeting_date": "2027-02-09"}

scenario(
    "sorrel-pike", "hidden_clause", ["multi_traveller", "outside_air_section", "dearer_option"],
    NBO_REQUEST.format(count="Five"), trip(travelling_with=team("sorrel-pike", 5), **NBO_TRIP), johannesburg(),
    expected("BOOK", ["african-economy"], ["ECONOMY"], ["TRAVELLER_LIMIT_PER_FLIGHT"], SUP,
             ["INSURANCE", "TRAVEL_PRINCIPLES"]),
    [ROUTINGS, ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "Five colleagues are already ticketed on the Kenya Airways flight. Under 1. Insurance (lines 44-45), separate "
    "routings should be taken, as far as possible, to avoid more than five DNDi Travellers on the same routing: a "
    "sixth would break it, and the South African Airways nonstop is a separate routing with seats, 5 minutes longer, "
    "arriving the day before the meeting. Book it, EUR 415.",
    twin_of="wren-hollow", twin_fact="five or four colleagues already on the Kenya Airways flight")

scenario(
    "fennel-reach", "hidden_clause", ["personal_travel", "date_arithmetic", "outside_air_section", "upgrade_not_taken"],
    "Delhi to Nairobi for the trial-site review that starts on Monday February 15th. I'd like to fly out on Thursday "
    "the 11th and spend three days in Nairobi on my own time first - it's on my approved travel request, and I'll pay "
    "any extra fare.",
    trip(traveller_name="Meera Pillai", traveller_title="Clinical Research Associate, New Delhi office",
         form_name="Arjun Mehta", origin="DEL", destination="NBO", travel_date="2027-02-11",
         business_travel_date="2027-02-14", booking_date="2026-12-14",
         purpose="Trial-site review in Nairobi, with three personal days before it", first_meeting_date="2027-02-15",
         traveller_pays_difference=True, personal_days_approved=True),
    [
        search("DEL", "NBO", "2027-02-11", {
            "kenya": {"carrier": "KQ", "depart": "08:30", "minutes": [375]},
            "india": {"carrier": "AI", "depart": "10:15", "minutes": [380]},
        }, [
            offer("kenya-thursday", "kenya", "ECONOMY", 49500),
            offer("india-thursday", "india", "ECONOMY", 52000),
        ], name="personal"),
        search("DEL", "NBO", "2027-02-14", {
            "kenya": {"carrier": "KQ", "depart": "08:30", "minutes": [375]},
            "india": {"carrier": "AI", "depart": "10:15", "minutes": [380]},
        }, [
            offer("kenya-sunday", "kenya", "ECONOMY", 46000),
            offer("india-sunday", "india", "ECONOMY", 48500),
        ], name="business-only"),
    ],
    expected("BOOK", ["kenya-thursday"], ["ECONOMY"], ["LOWEST_FARE", "PERSONAL_COST_PAID_BY_TRAVELER",
                                                      "PERSONAL_TRAVEL_NOT_COVERED"], SUP,
             ["PERSONAL_LEAVE", "TRAVEL_PRINCIPLES"]),
    [PERSONAL, ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "Personal leave may be connected with DNDi Travel when incidental and approved on the Travel Request form, and "
    "the traveller pays any difference above the DNDi Travel alone (lines 46-50). The traveller flies Thursday the "
    "11th: book the least costly Thursday fare (Kenya Airways EUR 495); DNDi bears the Sunday-only cost (EUR 460) and "
    "the traveller the EUR 35 more. Premium economy would be authorized (flights over 6 hours) but is not asked for.",
    distractors=[INSURED_LEAVE])

# ===== distractor (2) =====

scenario(
    "cinder-vale", "distractor", ["date_arithmetic", "month_end", "upgrade_not_taken"],
    "Johannesburg to Sao Paulo on December 17th for the meeting with our Brazilian partners on the 18th. They only "
    "fixed the date this week, so it's short notice. The cheapest fare the handbook allows is fine.",
    trip(kind="CONSULTANT", traveller_name="Sipho Dlamini", traveller_title="Consultant, access and pricing",
         form_name="Thomas Brun", origin="JNB", destination="GRU", travel_date="2026-12-17", booking_date="2026-11-27",
         planning_note="The Brazilian partners fixed the meeting date on 25 November; the request form was approved "
                       "and the trip booked as soon as possible after that.",
         purpose="Meeting with the Brazilian partners", first_meeting_date="2026-12-18"),
    search("JNB", "GRU", "2026-12-17", {
        "african": {"carrier": "SA", "depart": "10:40", "minutes": [600]},
        "latam": {"carrier": "LA", "depart": "13:15", "minutes": [595]},
    }, [
        offer("african-economy", "african", "ECONOMY", 84000),
        offer("african-premium", "african", "PREMIUM_ECONOMY", 142000),
        offer("latam-economy", "latam", "ECONOMY", 87500),
        offer("latam-premium", "latam", "PREMIUM_ECONOMY", 146000),
    ]),
    expected("BOOK", ["african-economy"], ["ECONOMY"], ["LOWEST_FARE"], MGR, LOWEST_CLAUSES),
    BASE,
    "Booked November 27th for December 17th: 20 days ahead (4 left in November, 17 in December), under the 45 days "
    "of planning lines 115-117 ask for an intercontinental trip. That line is an endeavour 'to obtain the lowest "
    "price', with the exception documented by the traveller (the planning note): it does not bar the booking. The "
    "least costly economy routing: South African Airways at EUR 840. Premium economy is authorized but not asked for.",
    distractors=[PLAN, LEGROOM_ASIDE])

scenario(
    "wren-hollow", "distractor", ["multi_traveller"],
    NBO_REQUEST.format(count="Four"), trip(travelling_with=team("wren-hollow", 4), **NBO_TRIP), johannesburg(),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["LOWEST_FARE", "TRAVELLER_LIMIT_PER_FLIGHT"], SUP,
             LOWEST_CLAUSES + ["INSURANCE", "TRAVEL_PRINCIPLES"]),
    [ECONOMY, ROUTE, REQUEST, WORKFLOW],
    "As sorrel-pike, but four colleagues are on the Kenya Airways flight: with this traveller five DNDi Travellers take "
    "that routing, which is not more than five (lines 44-45). The least costly routing: Kenya Airways at EUR 380.",
    twin_of="sorrel-pike", twin_fact="five or four colleagues already on the Kenya Airways flight",
    distractors=[aside(44, 45, "to avoid more than five DNDi Travellers taking the same routing",
                       "five travellers on one routing is still within the limit")])

# ===== refusal (2) =====

scenario(
    "violet-ford", "refusal", ["outside_air_section"],
    "Please book me a flight from Zurich to Paris on February 25th for the afternoon meeting with our French "
    "partners. If flying isn't allowed, I'll take the train and book it myself.",
    trip(kind="CONSULTANT", traveller_name="Lukas Brunner", traveller_title="Consultant, formulation development",
         form_name="Ines Moreau", origin="ZRH", destination="CDG", travel_date="2027-02-25", booking_date="2027-01-18",
         purpose="Afternoon meeting with the French partners in Paris", first_meeting_date="2027-02-25",
         train_minutes=245, train_arrives_in_time=True),
    search("ZRH", "CDG", "2027-02-25", {
        "swiss": {"carrier": "LX", "depart": "07:10", "minutes": [80]},
        "france": {"carrier": "AF", "depart": "08:40", "minutes": [80]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 18500),
        offer("france-economy", "france", "ECONOMY", 19900),
    ]),
    expected("REFUSE", [], ["NONE"], ["RAIL_PREFERRED"], MGR, ["MEANS_OF_TRAVEL", "RAIL_TRAVEL"]),
    [RAIL],
    "The fastest train takes 245 minutes and arrives in time for the meeting. Line 160: train trips under 6 hours "
    "shall be selected over flying, whenever possible. DNDi buys no flight; the traveller takes the train.",
    distractors=[TAXI])

scenario(
    "slate-loch", "refusal", ["outside_air_section"],
    "I live in Toronto and work at our New York office. Please book my usual Monday flight down on February 22nd so "
    "I'm at my desk that morning.",
    trip(traveller_name="Claire Dubois", traveller_title="Grants Manager, New York office", form_name="Rebecca Lindqvist",
         origin="YYZ", destination="JFK", home="YYZ", workplace_airport="JFK", travel_date="2027-02-22",
         booking_date="2027-01-20", purpose="A week of work at the New York office", first_meeting_date="2027-02-22",
         meeting_with="COLLEAGUES_ONLY", train_minutes=750),
    search("YYZ", "JFK", "2027-02-22", {
        "canada": {"carrier": "AC", "depart": "06:30", "minutes": [95]},
        "delta": {"carrier": "DL", "depart": "07:15", "minutes": [100]},
    }, [
        offer("canada-economy", "canada", "ECONOMY", 21000),
        offer("delta-economy", "delta", "ECONOMY", 23500),
    ]),
    expected("REFUSE", [], ["NONE"], ["HOME_TO_WORK_JOURNEY", "OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"],
             SUP, ["OBJECTIVE_SCOPE", "TRAVEL_PRINCIPLES"]),
    [COMMUTE, FOOTNOTE, SCOPE],
    "The traveller's home is Toronto and her regular place of work is the New York office. Line 39: journeys between "
    "an individual's home and regular place of work are not DNDi Travel, and her contract says nothing otherwise (line "
    "52). DNDi buys no ticket. The supervisor's approval of a request form changes nothing (rule 4(b)).",
    distractors=[ACCOMMODATION])

# ===== flag (3) =====

scenario(
    "hazel-tundra", "flag", ["multi_leg", "overnight", "unclear_phrase"],
    "Johannesburg to Mumbai on March 3rd for meetings with our Indian manufacturing partner starting at 5 pm on the "
    "4th. "
    + FALLBACK,
    trip(kind="CONSULTANT", traveller_name="Naledi Mokoena", traveller_title="Consultant, supply chain",
         form_name="Thomas Brun", origin="JNB", destination="BOM", travel_date="2027-03-03", booking_date="2027-01-05",
         purpose="Meetings with the Indian manufacturing partner", first_meeting_date="2027-03-04",
         requested_cabin="BUSINESS", sign_offs=[ED_IF, HFC]),
    search("JNB", "BOM", "2027-03-03", {
        "evening": {"carrier": "KQ", "via": ["NBO"], "depart": "18:30", "minutes": [240, 340], "layovers": [150]},
        "late": {"carrier": "KQ", "via": ["NBO"], "depart": "21:00", "minutes": [240, 340], "layovers": [150]},
    }, [
        offer("evening-economy", "evening", "ECONOMY", 61000),
        offer("evening-business", "evening", "BUSINESS", 321000),
        offer("late-economy", "late", "ECONOMY", 63500),
        offer("late-business", "late", "BUSINESS", 338000),
    ]),
    expected("FLAG_FOR_APPROVAL", ["evening-business", "evening-economy"], ["BUSINESS", "ECONOMY"],
             ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], ["EXECUTIVE_DIRECTOR", "NOT_NAMED",
                                                            "STRATEGY_OPERATIONS_DIRECTOR"], BUSINESS,
             phrase="including a maximum of 2 hours of connection time"),
    LONG_KEEP,
    "Both itineraries fly 240 + 340 = 580 minutes with a 150-minute connection in Nairobi (journey 730 minutes), "
    "overnight, to meetings with an external partner on the evening of landing (the day after leaving); no flight alone reaches nine hours. The "
    "multi-leg condition counts 'the combined travel time of the journey ... 11 hours or more, including a maximum of "
    "2 hours of connection time' (lines 125-129). Counting up to two hours of the wait gives 700 minutes (business); "
    "reading the maximum as a cap on the connection, or leaving ground time out, gives no business class. Hold the "
    "most economical business fare (or the economy fare of the other reading) for the Executive Director.",
    flag_twins=["opal-thicket", "garnet-sound"],
    ambiguity={"phrase": "including a maximum of 2 hours of connection time",
               "readings": [("up to two hours of the connection count towards the 11 hours: 580 + 120 = 700 minutes, "
                             "business class"),
                            ("a multi-leg journey qualifies only with connections of at most two hours (or the ground "
                             "time does not count at all): no business class, economy")]})

scenario(
    "yarrow-shoal", "flag", ["approval_required"],
    "London Heathrow to Rome on February 17th for the afternoon workshop with the Italian research partners. My "
    "doctor's certificate says I have to fly business class while my hip heals; it's on file. Business class, please.",
    trip(kind="CONSULTANT", traveller_name="Margaret Ellis", traveller_title="Consultant, epidemiology",
         form_name="Thomas Brun", origin="LHR", destination="FCO", travel_date="2027-02-17", booking_date="2027-01-11",
         purpose="Workshop with the Italian research partners", first_meeting_date="2027-02-17",
         requested_cabin="BUSINESS", medical_certificate_on_file=True, train_minutes=720),
    search("LHR", "FCO", "2027-02-17", {
        "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "07:20", "minutes": [85, 110], "layovers": [65]},
        "british": {"carrier": "BA", "depart": "08:10", "minutes": [150]},
    }, [
        offer("frankfurt-economy", "frankfurt", "ECONOMY", 18900),
        offer("frankfurt-business", "frankfurt", "BUSINESS", 63000),
        offer("british-economy", "british", "ECONOMY", 16500),
        offer("british-business", "british", "BUSINESS", 58000),
    ]),
    expected("FLAG_FOR_APPROVAL", ["british-business"], ["BUSINESS"], ["APPROVAL_REQUIRED", "MEDICAL_NEED"],
             BUSINESS_ROLES, BUSINESS),
    [MEDICAL, BUSINESS_APPROVAL, OPTIONS, REQUEST, WORKFLOW],
    "The medical certificate allows business class (lines 121-122), but all business class travel requires the "
    "Executive Director's prior approval, or by delegation the Operations and Strategy Director's (lines 133-134), and "
    "none is on file. Hold the most economical business fare (BA EUR 580) for that approval. Approval required, not "
    "'no compliant offer'.",
    flag_twins=["bramble-cove", "juniper-dell"],
    ambiguity="none: the Executive Director's prior approval is required and missing; the text is clear")

scenario(
    "umber-falls", "flag", ["approval_required", "overnight"], JNB_REQUEST, trip(**JNB_TRIP), london(501000),
    expected("FLAG_FOR_APPROVAL", ["british-business"], ["BUSINESS"], ["APPROVAL_REQUIRED"],
             ["STRATEGY_OPERATIONS_DIRECTOR"], BUSINESS + ["CLASS_AND_ROUTE"]),
    LONG_KEEP + [TICKET],
    "As russet-heath, but the most economical business fare is BA at EUR 5,010.00: above EUR 5,000, so line 112 "
    "requires the Strategy and Operations Director's approval before purchase (the others named only in that "
    "person's absence). Business class itself is allowed and approved, and the air cost is approved; hold the fare "
    "for the Strategy and Operations Director.",
    twin_of="russet-heath", twin_fact="the BA business fare is EUR 5,000.00 or EUR 5,010.00",
    flag_twins=["russet-heath", "garnet-sound"],
    ambiguity="none: the Strategy and Operations Director's approval of a ticket above EUR 5,000 is required and missing")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
