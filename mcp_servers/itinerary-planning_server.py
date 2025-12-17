import logging
import os
import random
import re
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, date as date_type
from pathlib import Path
from typing import Annotated

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from faker import Faker
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware
from pydantic import Field

# Try to import OpenTelemetry middleware (optional)
try:
    from opentelemetry_middleware import OpenTelemetryMiddleware, configure_aspire_dashboard
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger_temp = logging.getLogger("ItineraryPlanningMCP")
    logger_temp.warning("OpenTelemetry middleware not available - running without instrumentation")

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(message)s")
logger = logging.getLogger("ItineraryPlanningMCP")
logger.setLevel(logging.INFO)

middleware: list[Middleware] = []
if OTEL_AVAILABLE and os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    logger.info("Setting up Aspire Dashboard instrumentation (OTLP)")
    configure_aspire_dashboard(service_name="itinerary-planning-mcp")
    middleware = [OpenTelemetryMiddleware(tracer_name="itinerary.planning.mcp")]

mcp = FastMCP("Itinerary Planning", middleware=middleware if middleware else None)
fake = Faker()


@dataclass
class Hotel:
    name: str
    address: str
    location: str
    rating: float
    price_per_night: float
    hotel_type: str
    amenities: list[str]
    available_rooms: int


@dataclass
class HotelSuggestions:
    hotels: list[Hotel]


@dataclass
class Airport:
    code: str
    name: str
    city: str


@dataclass
class FlightSegment:
    flight_number: str
    from_airport: Airport
    to_airport: Airport
    departure: str
    arrival: str
    duration_minutes: int


@dataclass
class FlightConnection:
    airport_code: str
    duration_minutes: int


@dataclass
class Flight:
    flight_id: str
    airline: str
    flight_number: str
    aircraft: str
    from_airport: Airport
    to_airport: Airport
    departure: str
    arrival: str
    duration_minutes: int
    is_direct: bool
    price: float
    currency: str
    available_seats: int
    cabin_class: str
    segments: list[FlightSegment]
    connection: FlightConnection | None


@dataclass
class FlightSuggestions:
    departure_flights: list[Flight]
    return_flights: list[Flight]


def validate_iso_date(date_str: str, param_name: str) -> date_type:
    """
    Validates that a string is in ISO format (YYYY-MM-DD) and returns the parsed date.

    Args:
        date_str: The date string to validate
        param_name: Name of the parameter for error messages

    Returns:
        The parsed date object

    Raises:
        ValueError: If the date is not in ISO format or is invalid
    """
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not iso_pattern.match(date_str):
        raise ValueError(f"{param_name} must be in ISO format (YYYY-MM-DD), got: {date_str}")

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid {param_name}: {e}")


@mcp.tool()
async def suggest_hotels(
        location: Annotated[str, Field(description="Location (city or area) to search for hotels")],
        check_in: Annotated[str, Field(description="Check-in date in ISO format (YYYY-MM-DD)")],
        check_out: Annotated[str, Field(description="Check-out date in ISO format (YYYY-MM-DD)")],
) -> HotelSuggestions:
    """
    Suggest hotels based on location and dates.
    """
    logger.info(f"Searching hotels in {location} from {check_in} to {check_out}")

    # Validate dates
    check_in_date = validate_iso_date(check_in, "check_in")
    check_out_date = validate_iso_date(check_out, "check_out")

    # Ensure check_out is after check_in
    if check_out_date <= check_in_date:
        logger.error("Invalid dates: check_out must be after check_in")
        raise ValueError("check_out date must be after check_in date")

    # Create realistic mock data for hotels
    hotel_types = ["Luxury", "Boutique", "Budget", "Business"]
    amenities = ["Free WiFi", "Pool", "Spa", "Gym", "Restaurant", "Bar", "Room Service", "Parking"]

    # Generate a rating between 3.0 and 5.0
    def generate_rating():
        return round(random.uniform(3.0, 5.0), 1)

    # Generate a price based on hotel type
    def generate_price(hotel_type):
        price_ranges = {
            "Luxury": (250, 600),
            "Boutique": (180, 350),
            "Budget": (80, 150),
            "Resort": (200, 500),
            "Business": (150, 300),
        }
        min_price, max_price = price_ranges.get(hotel_type, (100, 300))
        return round(random.uniform(min_price, max_price))

    # Generate between 3 and 8 hotels
    num_hotels = random.randint(3, 8)
    hotels = []

    neighborhoods = [
        "Downtown",
        "Historic District",
        "Waterfront",
        "Business District",
        "Arts District",
        "University Area",
    ]

    for i in range(num_hotels):
        hotel_type = random.choice(hotel_types)
        hotel_amenities = random.sample(amenities, random.randint(3, 6))
        neighborhood = random.choice(neighborhoods)

        hotel = Hotel(
            name=f"{hotel_type} {['Hotel', 'Inn', 'Suites', 'Resort', 'Plaza'][random.randint(0, 4)]}",
            address=fake.street_address(),
            location=f"{neighborhood}, {location}",
            rating=generate_rating(),
            price_per_night=generate_price(hotel_type),
            hotel_type=hotel_type,
            amenities=hotel_amenities,
            available_rooms=random.randint(1, 15),
        )
        hotels.append(hotel)

    # Sort by rating to show best hotels first
    hotels.sort(key=lambda x: x.rating, reverse=True)

    logger.info(f"Found {len(hotels)} hotels in {location}")
    return HotelSuggestions(hotels=hotels)


@mcp.tool()
async def suggest_flights(
        from_location: Annotated[str, Field(description="Departure location (city or airport)")],
        to_location: Annotated[str, Field(description="Destination location (city or airport)")],
        departure_date: Annotated[str, Field(description="Departure date in ISO format (YYYY-MM-DD)")],
        return_date: Annotated[str, Field(description="Return date in ISO format (YYYY-MM-DD)")],
) -> FlightSuggestions:
    """
    Suggest flights based on locations and dates.
    """
    logger.info(f"Searching flights from {from_location} to {to_location}, departing {departure_date}, returning {return_date}")

    # Validate dates
    dep_date = validate_iso_date(departure_date, "departure_date")
    ret_date = validate_iso_date(return_date, "return_date")

    # Ensure return date is after departure date
    if ret_date <= dep_date:
        logger.error("Invalid dates: return_date must be after departure_date")
        raise ValueError("return_date must be after departure_date")

    # Create realistic mock data for flights
    airlines = [
        "SkyWings",
        "Global Air",
        "Atlantic Airways",
        "Pacific Express",
        "Mountain Jets",
        "Stellar Airlines",
        "Sunshine Airways",
        "Northern Flights",
    ]

    aircraft_types = ["Boeing 737", "Airbus A320", "Boeing 787", "Airbus A350", "Embraer E190", "Bombardier CRJ900"]

    # Generate airport codes based on locations
    def generate_airport_code(city):
        # Simple simulation of airport codes
        # In reality, this would use a database of real airport codes
        vowels = "AEIOU"
        consonants = "BCDFGHJKLMNPQRSTVWXYZ"

        # Use first letter of city if possible
        first_char = city[0].upper()
        if first_char in consonants:
            code = first_char
        else:
            code = random.choice(consonants)

        # Add two random letters, preferring consonants
        for _ in range(2):
            if random.random() < 0.7:  # 70% chance of consonant
                code += random.choice(consonants)
            else:
                code += random.choice(vowels)

        return code

    from_code = generate_airport_code(from_location)
    to_code = generate_airport_code(to_location)

    # Generate departure flights
    departure_flights = []
    num_dep_flights = random.randint(3, 7)

    for _ in range(num_dep_flights):
        # Generate departure time (between 6 AM and 10 PM)
        hour = random.randint(6, 22)
        minute = random.choice([0, 15, 30, 45])
        # Convert date to datetime before setting hour and minute
        dep_time = datetime.combine(dep_date, datetime.min.time()).replace(hour=hour, minute=minute)

        # Flight duration between 1 and 8 hours
        flight_minutes = random.randint(60, 480)
        arr_time = dep_time + timedelta(minutes=flight_minutes)

        # Determine if this is a direct or connecting flight
        is_direct = random.random() < 0.6  # 60% chance of direct flight

        from_airport = Airport(
            code=from_code,
            name=f"{from_location} International Airport",
            city=from_location,
        )
        to_airport = Airport(
            code=to_code,
            name=f"{to_location} International Airport",
            city=to_location,
        )

        # Add connection info for non-direct flights
        flight_segments = []
        connection_airport = None
        connection_duration_minutes = 0
        if not is_direct:
            # Create a connection point
            connection_codes = ["ATL", "ORD", "DFW", "LHR", "CDG", "DXB", "AMS", "FRA"]
            connection_code = random.choice(connection_codes)

            # Split the flight into segments
            segment1_duration = round(flight_minutes * random.uniform(0.3, 0.7))
            segment2_duration = flight_minutes - segment1_duration

            connection_time = random.randint(45, 180)  # between 45 minutes and 3 hours

            segment1_arrival = dep_time + timedelta(minutes=segment1_duration)
            segment2_departure = segment1_arrival + timedelta(minutes=connection_time)

            flight_segments = [
                FlightSegment(
                    flight_number=f"{random.choice('ABCDEFG')}{random.randint(100, 9999)}",
                    from_airport=from_airport,
                    to_airport=Airport(
                        code=connection_code,
                        name=f"{connection_code} International Airport",
                        city=connection_code,
                    ),
                    departure=dep_time.isoformat(),
                    arrival=segment1_arrival.isoformat(),
                    duration_minutes=segment1_duration,
                ),
                FlightSegment(
                    flight_number=f"{random.choice('ABCDEFG')}{random.randint(100, 9999)}",
                    from_airport=Airport(
                        code=connection_code,
                        name=f"{connection_code} International Airport",
                        city=connection_code,
                    ),
                    to_airport=to_airport,
                    departure=segment2_departure.isoformat(),
                    arrival=arr_time.isoformat(),
                    duration_minutes=segment2_duration,
                ),
            ]
            connection_airport = connection_code
            connection_duration_minutes = connection_time

        flight = Flight(
            flight_id=str(uuid.uuid4())[:8].upper(),
            airline=random.choice(airlines),
            flight_number=f"{random.choice('ABCDEFG')}{random.randint(100, 9999)}",
            aircraft=random.choice(aircraft_types),
            from_airport=from_airport,
            to_airport=to_airport,
            departure=dep_time.isoformat(),
            arrival=arr_time.isoformat(),
            duration_minutes=flight_minutes,
            is_direct=is_direct,
            price=round(random.uniform(99, 999), 2),
            currency="USD",
            available_seats=random.randint(1, 30),
            cabin_class=random.choice(["Economy", "Premium Economy", "Business", "First"]),
            segments=flight_segments,
            connection=FlightConnection(
                airport_code=connection_airport,
                duration_minutes=connection_duration_minutes,
            ) if not is_direct else None,
        )
        departure_flights.append(flight)

    # Generate return flights if return_date is provided
    return_flights = []
    if ret_date:
        num_ret_flights = random.randint(3, 7)

        for _ in range(num_ret_flights):
            # Similar logic as departure flights but for return
            hour = random.randint(6, 22)
            minute = random.choice([0, 15, 30, 45])
            # Convert date to datetime before setting hour and minute
            dep_time = datetime.combine(ret_date, datetime.min.time()).replace(hour=hour, minute=minute)

            flight_minutes = random.randint(60, 480)
            arr_time = dep_time + timedelta(minutes=flight_minutes)

            is_direct = random.random() < 0.6

            from_airport = Airport(
                code=to_code,
                name=f"{to_location} International Airport",
                city=to_location
            )
            to_airport = Airport(
                code=from_code,
                name=f"{from_location} International Airport",
                city=from_location
            )

            # Add connection info for non-direct flights
            flight_segments = []
            connection_airport = None
            connection_duration_minutes = None
            if not is_direct:
                connection_codes = ["ATL", "ORD", "DFW", "LHR", "CDG", "DXB", "AMS", "FRA"]
                connection_code = random.choice(connection_codes)

                segment1_duration = round(flight_minutes * random.uniform(0.3, 0.7))
                segment2_duration = flight_minutes - segment1_duration

                connection_time = random.randint(45, 180)

                segment1_arrival = dep_time + timedelta(minutes=segment1_duration)
                segment2_departure = segment1_arrival + timedelta(minutes=connection_time)

                flight_segments = [
                    FlightSegment(
                        flight_number=f"{random.choice('ABCDEFG')}{random.randint(100, 9999)}",
                        from_airport=from_airport,
                        to_airport=Airport(
                            code=connection_code,
                            name=f"{connection_code} International Airport",
                            city=connection_code,
                        ),
                        departure=dep_time.isoformat(),
                        arrival=segment1_arrival.isoformat(),
                        duration_minutes=segment1_duration,
                    ),
                    FlightSegment(
                        flight_number=f"{random.choice('ABCDEFG')}{random.randint(100, 9999)}",
                        from_airport=Airport(
                            code=connection_code,
                            name=f"{connection_code} International Airport",
                            city=connection_code,
                        ),
                        to_airport=to_airport,
                        departure=segment2_departure.isoformat(),
                        arrival=arr_time.isoformat(),
                        duration_minutes=segment2_duration,
                    ),
                ]
                connection_airport = connection_code
                connection_duration_minutes = connection_time

            flight = Flight(
                flight_id=str(uuid.uuid4())[:8].upper(),
                airline=random.choice(airlines),
                flight_number=f"{random.choice('ABCDEFG')}{random.randint(100, 9999)}",
                aircraft=random.choice(aircraft_types),
                from_airport=from_airport,
                to_airport=to_airport,
                departure=dep_time.isoformat(),
                arrival=arr_time.isoformat(),
                duration_minutes=flight_minutes,
                is_direct=is_direct,
                price=round(random.uniform(99, 999), 2),
                currency="USD",
                available_seats=random.randint(1, 30),
                cabin_class=random.choice(["Economy", "Premium Economy", "Business", "First"]),
                segments=flight_segments,
                connection=FlightConnection(
                    airport_code=connection_airport,
                    duration_minutes=connection_duration_minutes,
                ) if not is_direct else None,
            )

            return_flights.append(flight)

    # Combine into a single response
    response = FlightSuggestions(
        departure_flights=departure_flights,
        return_flights=return_flights if ret_date else []
    )

    logger.info(f"Found {len(departure_flights)} departure flights and {len(return_flights)} return flights")

    # Return the flights
    return response


if __name__ == "__main__":
    logger.info("MCP Itinerary Planning server starting (HTTP mode on port 8001)")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
