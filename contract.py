"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-dndi-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    HOME_TO_WORK_JOURNEY = "HOME_TO_WORK_JOURNEY"
    PERSONAL_COST_PAID_BY_TRAVELER = "PERSONAL_COST_PAID_BY_TRAVELER"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    TRAVEL_PACKAGE_NOT_ITEMIZED = "TRAVEL_PACKAGE_NOT_ITEMIZED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: DNDi Travel and Reimbursement Policy, version 3.0 (effective 1 January 2022).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    BRAMBLE_COVE = "bramble-cove"
    CINDER_VALE = "cinder-vale"
    COBALT_FINCH = "cobalt-finch"
    EMBER_LAGOON = "ember-lagoon"
    FENNEL_REACH = "fennel-reach"
    GARNET_SOUND = "garnet-sound"
    HAZEL_TUNDRA = "hazel-tundra"
    HEATHER_QUAY = "heather-quay"
    JUNIPER_DELL = "juniper-dell"
    LICHEN_BAY = "lichen-bay"
    MARLIN_CREST = "marlin-crest"
    OPAL_THICKET = "opal-thicket"
    PEWTER_GLADE = "pewter-glade"
    QUILL_BROOK = "quill-brook"
    RUSSET_HEATH = "russet-heath"
    SAFFRON_WEIR = "saffron-weir"
    SLATE_LOCH = "slate-loch"
    SORREL_PIKE = "sorrel-pike"
    TANSY_MARSH = "tansy-marsh"
    THISTLE_MOOR = "thistle-moor"
    UMBER_FALLS = "umber-falls"
    VIOLET_FORD = "violet-ford"
    WREN_HOLLOW = "wren-hollow"
    YARROW_SHOAL = "yarrow-shoal"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    SUPERVISOR = "SUPERVISOR"
    MANAGER_RESPONSIBLE = "MANAGER_RESPONSIBLE"
    EXECUTIVE_DIRECTOR = "EXECUTIVE_DIRECTOR"
    STRATEGY_OPERATIONS_DIRECTOR = "STRATEGY_OPERATIONS_DIRECTOR"
    FINANCIAL_CONTROL_HEAD = "FINANCIAL_CONTROL_HEAD"
    FINANCE_DIRECTOR = "FINANCE_DIRECTOR"
    FINANCE_PLANNING_DIRECTOR = "FINANCE_PLANNING_DIRECTOR"
    HR_ORGANISATIONAL_DIRECTOR = "HR_ORGANISATIONAL_DIRECTOR"
    GLOBAL_EXECUTIVE_TEAM = "GLOBAL_EXECUTIVE_TEAM"
    TRAVEL_OFFICER = "TRAVEL_OFFICER"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"


class Clause(Enum):
    """The handbook's sections, by heading."""

    OBJECTIVE_SCOPE = "OBJECTIVE_SCOPE"
    TRAVEL_PRINCIPLES = "TRAVEL_PRINCIPLES"
    INSURANCE = "INSURANCE"
    PERSONAL_LEAVE = "PERSONAL_LEAVE"
    ARRANGING_TRAVEL = "ARRANGING_TRAVEL"
    TRAVEL_EXPENSES = "TRAVEL_EXPENSES"
    SUITABILITY_OF_EXPENSES = "SUITABILITY_OF_EXPENSES"
    MEANS_OF_TRAVEL = "MEANS_OF_TRAVEL"
    AIR_TRAVEL = "AIR_TRAVEL"
    CLASS_AND_ROUTE = "CLASS_AND_ROUTE"
    TRAVEL_CLASS = "TRAVEL_CLASS"
    EXTRA_LEGROOM = "EXTRA_LEGROOM"
    LOYALTY_PROGRAMMES = "LOYALTY_PROGRAMMES"
    CARBON_FOOTPRINT = "CARBON_FOOTPRINT"
    RAIL_TRAVEL = "RAIL_TRAVEL"
    ACCOMMODATION = "ACCOMMODATION"
    TIME_OFF_IN_LIEU = "TIME_OFF_IN_LIEU"
    TRAVEL_INSURANCE = "TRAVEL_INSURANCE"
    REQUEST_WORKFLOW = "REQUEST_WORKFLOW"
    COSTS_ANNEX = "COSTS_ANNEX"


class TravellerKind(Enum):
    STAFF = "STAFF"
    CONSULTANT = "CONSULTANT"
    BODY_MEMBER = "BODY_MEMBER"
    GUEST = "GUEST"


class Counterparts(Enum):
    EXTERNAL_PARTNERS = "EXTERNAL_PARTNERS"
    COLLEAGUES_ONLY = "COLLEAGUES_ONLY"


class Routing(Enum):
    ANY = "ANY"
    NONSTOP = "NONSTOP"


class SignOffSubject(Enum):
    TRAVEL_REQUEST = "TRAVEL_REQUEST"
    BUSINESS_CLASS = "BUSINESS_CLASS"
    AIR_COST = "AIR_COST"
    TICKET_PRICE = "TICKET_PRICE"


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The signer's role in the organisation"]
    name: Annotated[str, "Their name"]
    subject: Annotated[SignOffSubject, "What they signed: the trip's request form, a business class seat, the trip's air cost, or the price of the ticket"]
    covers: Annotated[str, "What the sign-off says, in plain words"]


@dataclass
class Colleague(Output):
    name: Annotated[str, "The colleague's name"]
    flight_number: Annotated[str, "The flight they are already ticketed on, as search_flights lists it"]
    date: Annotated[str, "That flight's local departure date, YYYY-MM-DD"]
    cabin: Annotated[Cabin, "The cabin they are ticketed in"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title or role"]
    traveller_kind: Annotated[TravellerKind, "STAFF: employed by the organisation, interns and volunteers included; CONSULTANT: on a consultancy agreement; BODY_MEMBER: sits on its board or one of its committees; GUEST: someone it invited to a meeting or event"]
    home_airport: Annotated[Airport, "The airport nearest the traveller's home"]
    workplace_airport: Annotated[Airport, "The airport nearest the traveller's usual place of work"]
    contract_travel_terms: Annotated[str, "Terms about travel in the traveller's own contract that differ from the handbook; empty when there are none"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    business_travel_date: Annotated[str, "The day the work itself would need the flight, YYYY-MM-DD; the same as travel_date unless the traveller adds days of their own"]
    return_date: Annotated[str, "For a round trip bought as one fare, the day to fly back, YYYY-MM-DD; empty for one way"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    planning_note: Annotated[str, "The traveller's written reason for booking this close to the trip; empty when they gave none"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    first_meeting_date: Annotated[str, "The day of the trip's first meeting or event at the destination, YYYY-MM-DD, local there"]
    meeting_with: Annotated[Counterparts, "Who the trip's meetings are with: people from outside the organisation, or only its own people"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    requested_routing: Annotated[Routing, "NONSTOP when the traveller asks for a nonstop flight; ANY otherwise"]
    requested_airline: Annotated[str, "The airline the traveller asks for, as search_flights names airlines; empty when none"]
    traveller_pays_difference: Annotated[bool, "Whether the traveller offers to pay, out of pocket, what the requested ticket costs above the one the organisation would buy"]
    personal_days_approved: Annotated[bool, "Whether days of the traveller's own added to the trip are approved on its request form; false when none are added"]
    medical_certificate_on_file: Annotated[bool, "Whether a doctor's certificate on file says the traveller's health requires a business class seat"]
    train_minutes: Annotated[int, "The fastest train between the trip's two cities, station to station, in minutes; zero when no train links them"]
    train_arrives_in_time: Annotated[bool, "Whether that train gets the traveller there in time for the trip's business; false when there is no train"]
    sign_offs: Annotated[list[SignOff], "Sign-offs already on file for this trip, each given before today"]
    travelling_with: Annotated[list[Colleague], "Colleagues on the same trip who are already ticketed; empty when none"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
