"""
Travel Destination Recommendation MCP Server

This server helps users discover travel destinations based on:
- Activity preferences (beach, adventure, cultural, etc.)
- Budget constraints (budget, moderate, luxury)
- Seasonal preferences (spring, summer, autumn, winter)
- Family-friendliness

Features:
- Activity-based recommendations
- Budget-conscious planning
- Seasonal recommendations
- Family-friendly options
- Multi-criteria search
"""

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware
from pydantic import Field

# Try to import OpenTelemetry middleware (optional)
try:
    from opentelemetry_middleware import OpenTelemetryMiddleware, configure_aspire_dashboard
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger_temp = logging.getLogger("TravelDestinationMCP")
    logger_temp.warning("OpenTelemetry middleware not available - running without instrumentation")

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(message)s")
logger = logging.getLogger("TravelDestinationMCP")
logger.setLevel(logging.INFO)

middleware: list[Middleware] = []
if OTEL_AVAILABLE and os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    logger.info("Setting up Aspire Dashboard instrumentation (OTLP)")
    configure_aspire_dashboard(service_name="travel-destination-mcp")
    middleware = [OpenTelemetryMiddleware(tracer_name="travel.destination.mcp")]

mcp = FastMCP("Travel Destination Recommendations", middleware=middleware if middleware else None)

# ============================================================================
# CONSTANTS
# ============================================================================

# Activity types
BEACH = "BEACH"
ADVENTURE = "ADVENTURE"
CULTURAL = "CULTURAL"
RELAXATION = "RELAXATION"
URBAN_EXPLORATION = "URBAN_EXPLORATION"
NATURE = "NATURE"
WINTER_SPORTS = "WINTER_SPORTS"

VALID_ACTIVITIES = {BEACH, ADVENTURE, CULTURAL, RELAXATION, URBAN_EXPLORATION, NATURE, WINTER_SPORTS}

# Budget categories
BUDGET = "BUDGET"
MODERATE = "MODERATE"
LUXURY = "LUXURY"

VALID_BUDGETS = {BUDGET, MODERATE, LUXURY}

# Seasons
SPRING = "SPRING"
SUMMER = "SUMMER"
AUTUMN = "AUTUMN"
WINTER = "WINTER"
ALL_YEAR = "ALL_YEAR"

VALID_SEASONS = {SPRING, SUMMER, AUTUMN, WINTER, ALL_YEAR}

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Destination:
    name: str
    country: str
    description: str
    activity_type: str
    budget_category: str
    best_season: str
    family_friendly: bool
    highlights: list[str]
    avg_temp_celsius: Optional[int] = None
    currency: Optional[str] = None

@dataclass
class DestinationRecommendations:
    destinations: list[Destination]
    total_count: int
    filters_applied: dict

# ============================================================================
# DESTINATION DATABASE
# ============================================================================

DESTINATIONS_DB = [
    # Beach Destinations
    Destination(
        name="Bali",
        country="Indonesia",
        description="Beautiful beaches with vibrant culture and lush landscapes",
        activity_type=BEACH,
        budget_category=MODERATE,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Pristine beaches", "Hindu temples", "Rice terraces", "Surfing", "Yoga retreats"],
        avg_temp_celsius=28,
        currency="IDR"
    ),
    Destination(
        name="Cancun",
        country="Mexico",
        description="White sandy beaches with crystal clear waters and vibrant nightlife",
        activity_type=BEACH,
        budget_category=MODERATE,
        best_season=WINTER,
        family_friendly=True,
        highlights=["Caribbean beaches", "Mayan ruins", "Water sports", "All-inclusive resorts", "Cenotes"],
        avg_temp_celsius=27,
        currency="MXN"
    ),
    Destination(
        name="Maldives",
        country="Maldives",
        description="Luxurious overwater bungalows and pristine beaches perfect for relaxation",
        activity_type=BEACH,
        budget_category=LUXURY,
        best_season=ALL_YEAR,
        family_friendly=True,
        highlights=["Overwater villas", "Coral reefs", "Snorkeling", "Private islands", "Spa resorts"],
        avg_temp_celsius=30,
        currency="MVR"
    ),
    Destination(
        name="Santorini",
        country="Greece",
        description="Beautiful sunsets, white-washed buildings, and Mediterranean cuisine",
        activity_type=RELAXATION,
        budget_category=LUXURY,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Sunset views", "Blue-domed churches", "Wine tasting", "Black sand beaches", "Caldera views"],
        avg_temp_celsius=25,
        currency="EUR"
    ),

    # Cultural Destinations
    Destination(
        name="Kyoto",
        country="Japan",
        description="Ancient temples, traditional gardens, and rich cultural heritage",
        activity_type=CULTURAL,
        budget_category=MODERATE,
        best_season=SPRING,
        family_friendly=True,
        highlights=["Cherry blossoms", "Buddhist temples", "Traditional tea ceremonies", "Geisha district", "Bamboo forests"],
        avg_temp_celsius=15,
        currency="JPY"
    ),
    Destination(
        name="Rome",
        country="Italy",
        description="Historic city with ancient ruins, art, and delicious cuisine",
        activity_type=CULTURAL,
        budget_category=MODERATE,
        best_season=SPRING,
        family_friendly=True,
        highlights=["Colosseum", "Vatican City", "Trevi Fountain", "Italian cuisine", "Roman Forum"],
        avg_temp_celsius=20,
        currency="EUR"
    ),
    Destination(
        name="Prague",
        country="Czech Republic",
        description="Historic architecture, affordable dining, and rich cultural experiences",
        activity_type=CULTURAL,
        budget_category=BUDGET,
        best_season=SPRING,
        family_friendly=True,
        highlights=["Prague Castle", "Charles Bridge", "Old Town Square", "Gothic architecture", "Beer culture"],
        avg_temp_celsius=18,
        currency="CZK"
    ),
    Destination(
        name="Marrakech",
        country="Morocco",
        description="Vibrant souks, stunning palaces, and exotic culture",
        activity_type=CULTURAL,
        budget_category=BUDGET,
        best_season=SPRING,
        family_friendly=True,
        highlights=["Medina markets", "Jardin Majorelle", "Bahia Palace", "Tagine cuisine", "Desert tours"],
        avg_temp_celsius=22,
        currency="MAD"
    ),

    # Adventure Destinations
    Destination(
        name="Queenstown",
        country="New Zealand",
        description="Adventure capital with stunning landscapes and extreme sports",
        activity_type=ADVENTURE,
        budget_category=MODERATE,
        best_season=SUMMER,
        family_friendly=False,
        highlights=["Bungee jumping", "Skydiving", "Jet boating", "Hiking", "Lake Wakatipu"],
        avg_temp_celsius=18,
        currency="NZD"
    ),
    Destination(
        name="Interlaken",
        country="Switzerland",
        description="Alpine paradise for adventure seekers with breathtaking mountain views",
        activity_type=ADVENTURE,
        budget_category=LUXURY,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Paragliding", "Swiss Alps", "Jungfraujoch", "Hiking trails", "Adventure sports"],
        avg_temp_celsius=16,
        currency="CHF"
    ),
    Destination(
        name="Costa Rica",
        country="Costa Rica",
        description="Rainforests, volcanoes, and incredible biodiversity",
        activity_type=ADVENTURE,
        budget_category=MODERATE,
        best_season=WINTER,
        family_friendly=True,
        highlights=["Zip-lining", "Rainforest tours", "Wildlife", "Volcanoes", "Surfing"],
        avg_temp_celsius=27,
        currency="CRC"
    ),

    # Nature Destinations
    Destination(
        name="Iceland",
        country="Iceland",
        description="Land of fire and ice with stunning natural wonders",
        activity_type=NATURE,
        budget_category=LUXURY,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Northern lights", "Geysers", "Waterfalls", "Blue Lagoon", "Glaciers"],
        avg_temp_celsius=12,
        currency="ISK"
    ),
    Destination(
        name="Patagonia",
        country="Argentina/Chile",
        description="Vast wilderness with glaciers, mountains, and pristine landscapes",
        activity_type=NATURE,
        budget_category=MODERATE,
        best_season=SUMMER,
        family_friendly=False,
        highlights=["Torres del Paine", "Glaciers", "Hiking", "Wildlife", "Remote wilderness"],
        avg_temp_celsius=10,
        currency="ARS/CLP"
    ),
    Destination(
        name="Banff",
        country="Canada",
        description="Canadian Rockies with turquoise lakes and stunning mountain scenery",
        activity_type=NATURE,
        budget_category=MODERATE,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Lake Louise", "Mountain hiking", "Wildlife viewing", "Hot springs", "Scenic drives"],
        avg_temp_celsius=15,
        currency="CAD"
    ),

    # Urban Exploration
    Destination(
        name="New York City",
        country="USA",
        description="Iconic skyline, diverse neighborhoods, world-class museums, and entertainment",
        activity_type=URBAN_EXPLORATION,
        budget_category=LUXURY,
        best_season=ALL_YEAR,
        family_friendly=True,
        highlights=["Statue of Liberty", "Central Park", "Broadway", "Museums", "Shopping"],
        avg_temp_celsius=15,
        currency="USD"
    ),
    Destination(
        name="Tokyo",
        country="Japan",
        description="Futuristic city with traditional culture, amazing food, and vibrant nightlife",
        activity_type=URBAN_EXPLORATION,
        budget_category=MODERATE,
        best_season=SPRING,
        family_friendly=True,
        highlights=["Shibuya crossing", "Temples", "Sushi", "Technology", "Shopping districts"],
        avg_temp_celsius=16,
        currency="JPY"
    ),
    Destination(
        name="Barcelona",
        country="Spain",
        description="Vibrant city with Gaudi architecture, beaches, and Mediterranean culture",
        activity_type=URBAN_EXPLORATION,
        budget_category=MODERATE,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Sagrada Familia", "Park Guell", "Beach promenade", "Tapas", "Gothic Quarter"],
        avg_temp_celsius=24,
        currency="EUR"
    ),

    # Winter Sports
    Destination(
        name="Aspen",
        country="USA",
        description="World-class skiing, snowboarding, and luxurious alpine village",
        activity_type=WINTER_SPORTS,
        budget_category=LUXURY,
        best_season=WINTER,
        family_friendly=False,
        highlights=["Skiing", "Snowboarding", "Luxury resorts", "Apres-ski", "Mountain views"],
        avg_temp_celsius=-5,
        currency="USD"
    ),
    Destination(
        name="Chamonix",
        country="France",
        description="Epic skiing and snowboarding with stunning Mont Blanc views",
        activity_type=WINTER_SPORTS,
        budget_category=LUXURY,
        best_season=WINTER,
        family_friendly=True,
        highlights=["Mont Blanc", "Skiing", "Cable cars", "Alpine village", "Mountaineering"],
        avg_temp_celsius=-2,
        currency="EUR"
    ),
    Destination(
        name="Whistler",
        country="Canada",
        description="Premier ski resort with diverse terrain and village atmosphere",
        activity_type=WINTER_SPORTS,
        budget_category=MODERATE,
        best_season=WINTER,
        family_friendly=True,
        highlights=["Skiing", "Snowboarding", "Village dining", "Peak-to-peak gondola", "Snow activities"],
        avg_temp_celsius=-3,
        currency="CAD"
    ),

    # Relaxation Destinations
    Destination(
        name="Ubud",
        country="Indonesia",
        description="Peaceful retreat with yoga, wellness, and natural beauty",
        activity_type=RELAXATION,
        budget_category=BUDGET,
        best_season=SUMMER,
        family_friendly=True,
        highlights=["Yoga retreats", "Rice paddies", "Monkey forest", "Wellness spas", "Balinese culture"],
        avg_temp_celsius=28,
        currency="IDR"
    ),
    Destination(
        name="Seychelles",
        country="Seychelles",
        description="Tropical paradise with pristine beaches and luxury resorts",
        activity_type=RELAXATION,
        budget_category=LUXURY,
        best_season=ALL_YEAR,
        family_friendly=True,
        highlights=["White sand beaches", "Coral reefs", "Island hopping", "Luxury spas", "Granite boulders"],
        avg_temp_celsius=28,
        currency="SCR"
    ),
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_activity_type(activity: str) -> str:
    """Validate and normalize activity type"""
    activity_upper = activity.upper()
    if activity_upper not in VALID_ACTIVITIES:
        raise ValueError(
            f"Invalid activity type. Please use one of: {', '.join(sorted(VALID_ACTIVITIES))}"
        )
    return activity_upper

def validate_budget_category(budget: str) -> str:
    """Validate and normalize budget category"""
    budget_upper = budget.upper()
    if budget_upper not in VALID_BUDGETS:
        raise ValueError(
            f"Invalid budget category. Please use one of: {', '.join(sorted(VALID_BUDGETS))}"
        )
    return budget_upper

def validate_season(season: str) -> str:
    """Validate and normalize season"""
    season_upper = season.upper()
    if season_upper not in VALID_SEASONS:
        raise ValueError(
            f"Invalid season. Please use one of: {', '.join(sorted(VALID_SEASONS))}"
        )
    return season_upper

def format_destination(dest: Destination) -> str:
    """Format a destination for display"""
    family_status = "Yes" if dest.family_friendly else "No"
    temp_info = f" | {dest.avg_temp_celsius}°C" if dest.avg_temp_celsius else ""

    result = f"📍 {dest.name}, {dest.country}\n"
    result += f"⭐️ {dest.description}\n"
    result += f"🏷️ Activity: {dest.activity_type} | Budget: {dest.budget_category} | "
    result += f"Best Season: {dest.best_season} | Family Friendly: {family_status}{temp_info}\n"
    result += f"✨ Highlights: {', '.join(dest.highlights[:3])}"

    return result

def filter_destinations(
    activity: Optional[str] = None,
    budget: Optional[str] = None,
    season: Optional[str] = None,
    family_friendly: Optional[bool] = None
) -> list[Destination]:
    """Filter destinations based on criteria"""
    results = DESTINATIONS_DB.copy()

    if activity:
        results = [d for d in results if d.activity_type == activity]

    if budget:
        results = [d for d in results if d.budget_category == budget]

    if season:
        results = [d for d in results if d.best_season == season or d.best_season == ALL_YEAR]

    if family_friendly is not None:
        results = [d for d in results if d.family_friendly == family_friendly]

    return results

# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
async def echo_message(
    message: Annotated[str, Field(description="The message to echo back")]
) -> str:
    """
    Echo back the input message exactly as received.
    This is useful for testing the MCP server connection.
    """
    logger.info(f"Echo message: {message}")
    return message

@mcp.tool()
async def get_destinations_by_activity(
    activity_type: Annotated[str, Field(description="Preferred activity type: BEACH, ADVENTURE, CULTURAL, RELAXATION, URBAN_EXPLORATION, NATURE, WINTER_SPORTS")]
) -> str:
    """
    Get travel destination recommendations based on preferred activity type.

    Returns destinations that match the specified activity preference.
    """
    logger.info(f"Getting destinations for activity: {activity_type}")

    try:
        validated_activity = validate_activity_type(activity_type)
        destinations = filter_destinations(activity=validated_activity)

        if not destinations:
            return f"No destinations found for activity type: {validated_activity}"

        result = f"Here are {len(destinations)} {validated_activity.lower()} destinations for you:\n\n"
        result += "\n\n".join([format_destination(d) for d in destinations[:5]])

        logger.info(f"Found {len(destinations)} destinations for {validated_activity}")
        return result

    except ValueError as e:
        logger.error(f"Invalid activity type: {str(e)}")
        return str(e)

@mcp.tool()
async def get_destinations_by_budget(
    budget: Annotated[str, Field(description="Budget category: BUDGET, MODERATE, LUXURY")]
) -> str:
    """
    Get travel destination recommendations based on budget category.

    Returns destinations that fit within the specified budget range.
    """
    logger.info(f"Getting destinations for budget: {budget}")

    try:
        validated_budget = validate_budget_category(budget)
        destinations = filter_destinations(budget=validated_budget)

        if not destinations:
            return f"No destinations found for budget category: {validated_budget}"

        result = f"Here are {len(destinations)} {validated_budget.lower()} destinations for you:\n\n"
        result += "\n\n".join([format_destination(d) for d in destinations[:5]])

        logger.info(f"Found {len(destinations)} destinations for {validated_budget} budget")
        return result

    except ValueError as e:
        logger.error(f"Invalid budget category: {str(e)}")
        return str(e)

@mcp.tool()
async def get_destinations_by_season(
    season: Annotated[str, Field(description="Preferred season: SPRING, SUMMER, AUTUMN, WINTER, ALL_YEAR")]
) -> str:
    """
    Get travel destination recommendations based on preferred season.

    Returns destinations that are best visited during the specified season.
    """
    logger.info(f"Getting destinations for season: {season}")

    try:
        validated_season = validate_season(season)
        destinations = filter_destinations(season=validated_season)

        if not destinations:
            return f"No destinations found for season: {validated_season}"

        result = f"Here are {len(destinations)} destinations best for {validated_season.lower()}:\n\n"
        result += "\n\n".join([format_destination(d) for d in destinations[:5]])

        logger.info(f"Found {len(destinations)} destinations for {validated_season}")
        return result

    except ValueError as e:
        logger.error(f"Invalid season: {str(e)}")
        return str(e)

@mcp.tool()
async def get_destinations_by_preferences(
    activity: Annotated[Optional[str], Field(description="Preferred activity type (optional)")] = None,
    budget: Annotated[Optional[str], Field(description="Budget category (optional)")] = None,
    season: Annotated[Optional[str], Field(description="Preferred season (optional)")] = None,
    family_friendly: Annotated[Optional[bool], Field(description="Whether destination should be family-friendly (optional)")] = None
) -> str:
    """
    Get travel destination recommendations based on multiple criteria.

    Combine multiple preferences to find destinations that match all specified criteria.
    All parameters are optional - specify only the filters you want to apply.
    """
    logger.info(f"Getting destinations with filters - activity: {activity}, budget: {budget}, season: {season}, family_friendly: {family_friendly}")

    try:
        # Validate inputs if provided
        validated_activity = validate_activity_type(activity) if activity else None
        validated_budget = validate_budget_category(budget) if budget else None
        validated_season = validate_season(season) if season else None

        # Filter destinations
        destinations = filter_destinations(
            activity=validated_activity,
            budget=validated_budget,
            season=validated_season,
            family_friendly=family_friendly
        )

        if not destinations:
            return "No destinations found matching your criteria. Try adjusting your preferences."

        # Build filter description
        filters = []
        if validated_activity:
            filters.append(f"activity: {validated_activity}")
        if validated_budget:
            filters.append(f"budget: {validated_budget}")
        if validated_season:
            filters.append(f"season: {validated_season}")
        if family_friendly is not None:
            filters.append(f"family-friendly: {'Yes' if family_friendly else 'No'}")

        filter_desc = ", ".join(filters) if filters else "all destinations"

        result = f"Here are {len(destinations)} destinations matching {filter_desc}:\n\n"
        result += "\n\n".join([format_destination(d) for d in destinations[:5]])

        if len(destinations) > 5:
            result += f"\n\n... and {len(destinations) - 5} more destinations"

        logger.info(f"Found {len(destinations)} destinations matching criteria")
        return result

    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        return str(e)

@mcp.tool()
async def get_all_destinations() -> str:
    """
    Get a list of all available travel destinations.

    Returns all destinations in the database with their details.
    """
    logger.info("Getting all destinations")

    result = f"Here are {len(DESTINATIONS_DB)} popular travel destinations:\n\n"
    result += "\n\n".join([format_destination(d) for d in DESTINATIONS_DB[:10]])

    if len(DESTINATIONS_DB) > 10:
        result += f"\n\n... and {len(DESTINATIONS_DB) - 10} more destinations available"

    logger.info(f"Returned {len(DESTINATIONS_DB)} destinations")
    return result

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("MCP Travel Destination Recommendation server starting (HTTP mode on port 8002)")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002)

