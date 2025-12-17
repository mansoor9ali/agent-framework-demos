"""
Customer Query Analysis MCP Server

This server analyzes customer queries to understand:
- Customer emotion (happy, sad, angry, neutral)
- Intent (book_flight, cancel_flight, change_flight, inquire, complaint)
- Requirements (business, economy, first_class)
- Preferences (window, aisle, extra_legroom)

Features:
- Natural language query analysis
- Emotion detection
- Intent classification
- Requirement extraction
- Preference identification
"""

import asyncio
import logging
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

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
    logger_temp = logging.getLogger("CustomerQueryMCP")
    logger_temp.warning("OpenTelemetry middleware not available - running without instrumentation")

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(message)s")
logger = logging.getLogger("CustomerQueryMCP")
logger.setLevel(logging.INFO)

middleware: list[Middleware] = []
if OTEL_AVAILABLE and os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    logger.info("Setting up Aspire Dashboard instrumentation (OTLP)")
    configure_aspire_dashboard(service_name="customer-query-mcp")
    middleware = [OpenTelemetryMiddleware(tracer_name="customer.query.mcp")]

mcp = FastMCP("Customer Query Analysis", middleware=middleware if middleware else None)

# ============================================================================
# CONSTANTS
# ============================================================================

# Emotions
HAPPY = "happy"
SAD = "sad"
ANGRY = "angry"
NEUTRAL = "neutral"

EMOTIONS = [HAPPY, SAD, ANGRY, NEUTRAL]

# Intents
BOOK_FLIGHT = "book_flight"
CANCEL_FLIGHT = "cancel_flight"
CHANGE_FLIGHT = "change_flight"
INQUIRE = "inquire"
COMPLAINT = "complaint"

INTENTS = [BOOK_FLIGHT, CANCEL_FLIGHT, CHANGE_FLIGHT, INQUIRE, COMPLAINT]

# Requirements (cabin class)
BUSINESS = "business"
ECONOMY = "economy"
FIRST_CLASS = "first_class"

REQUIREMENTS = [BUSINESS, ECONOMY, FIRST_CLASS]

# Preferences (seating)
WINDOW = "window"
AISLE = "aisle"
EXTRA_LEGROOM = "extra_legroom"

PREFERENCES = [WINDOW, AISLE, EXTRA_LEGROOM]

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CustomerQueryAnalysisResult:
    """Result of customer query analysis"""
    customer_query: str
    emotion: str
    intent: str
    requirements: str
    preferences: str
    confidence_score: float
    analysis_summary: str

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def analyze_emotion(query: str) -> str:
    """
    Analyze the emotion from the customer query.
    In a real implementation, this would use NLP/sentiment analysis.
    """
    query_lower = query.lower()

    # Simple keyword-based emotion detection
    angry_keywords = ["angry", "furious", "terrible", "worst", "hate", "frustrated", "annoyed", "unacceptable"]
    sad_keywords = ["sad", "disappointed", "unhappy", "upset", "unfortunate", "regret"]
    happy_keywords = ["happy", "great", "excellent", "wonderful", "amazing", "thank", "love", "perfect"]

    if any(word in query_lower for word in angry_keywords):
        return ANGRY
    elif any(word in query_lower for word in sad_keywords):
        return SAD
    elif any(word in query_lower for word in happy_keywords):
        return HAPPY
    else:
        return NEUTRAL

def analyze_intent(query: str) -> str:
    """
    Analyze the intent from the customer query.
    In a real implementation, this would use NLP/intent classification.
    """
    query_lower = query.lower()

    # Simple keyword-based intent detection
    if any(word in query_lower for word in ["book", "reserve", "purchase", "buy"]):
        return BOOK_FLIGHT
    elif any(word in query_lower for word in ["cancel", "refund", "abort"]):
        return CANCEL_FLIGHT
    elif any(word in query_lower for word in ["change", "modify", "reschedule", "update"]):
        return CHANGE_FLIGHT
    elif any(word in query_lower for word in ["complain", "complaint", "issue", "problem", "terrible", "worst"]):
        return COMPLAINT
    else:
        return INQUIRE

def analyze_requirements(query: str) -> str:
    """
    Analyze the cabin class requirements from the customer query.
    """
    query_lower = query.lower()

    if any(word in query_lower for word in ["first class", "first-class", "premium"]):
        return FIRST_CLASS
    elif any(word in query_lower for word in ["business class", "business-class", "business"]):
        return BUSINESS
    else:
        return ECONOMY

def analyze_preferences(query: str) -> str:
    """
    Analyze the seating preferences from the customer query.
    """
    query_lower = query.lower()

    if any(word in query_lower for word in ["window", "window seat"]):
        return WINDOW
    elif any(word in query_lower for word in ["aisle", "aisle seat"]):
        return AISLE
    elif any(word in query_lower for word in ["extra legroom", "legroom", "more space"]):
        return EXTRA_LEGROOM
    else:
        # Default random preference
        return random.choice(PREFERENCES)

def calculate_confidence_score(query: str) -> float:
    """
    Calculate confidence score based on query complexity and keywords found.
    In a real implementation, this would use ML model confidence.
    """
    query_lower = query.lower()
    keywords_found = 0

    # Check for various keywords
    all_keywords = [
        "book", "cancel", "change", "flight", "seat", "window", "aisle",
        "business", "economy", "first", "help", "please", "thank", "complaint"
    ]

    for keyword in all_keywords:
        if keyword in query_lower:
            keywords_found += 1

    # Base confidence + bonus for keywords found
    base_confidence = 0.6
    keyword_bonus = min(keywords_found * 0.05, 0.35)

    return min(base_confidence + keyword_bonus, 0.99)

def generate_analysis_summary(emotion: str, intent: str, requirements: str, preferences: str) -> str:
    """Generate a human-readable summary of the analysis"""
    emotion_desc = {
        HAPPY: "positive and satisfied",
        SAD: "disappointed or upset",
        ANGRY: "frustrated or angry",
        NEUTRAL: "neutral"
    }

    intent_desc = {
        BOOK_FLIGHT: "book a new flight",
        CANCEL_FLIGHT: "cancel an existing flight",
        CHANGE_FLIGHT: "modify their flight booking",
        INQUIRE: "get information",
        COMPLAINT: "lodge a complaint"
    }

    summary = f"Customer appears {emotion_desc.get(emotion, 'neutral')} and wants to {intent_desc.get(intent, 'inquire')}. "
    summary += f"They prefer {requirements} class seating"

    if preferences in [WINDOW, AISLE]:
        summary += f" with a {preferences} seat"
    elif preferences == EXTRA_LEGROOM:
        summary += f" with extra legroom"

    summary += "."

    return summary

# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
async def analyze_customer_query(
    customer_query: Annotated[str, Field(description="The customer query to analyze")]
) -> str:
    """
    Analyzes the customer query and provides a detailed response.

    This tool performs comprehensive analysis including:
    - Emotion detection (happy, sad, angry, neutral)
    - Intent classification (book_flight, cancel_flight, change_flight, inquire, complaint)
    - Requirements extraction (business, economy, first_class)
    - Preferences identification (window, aisle, extra_legroom)
    - Confidence scoring

    Returns a formatted analysis result with all extracted information.
    """
    logger.info(f"Received customer query: {customer_query}")

    # Simulate some processing time (like the C# version)
    await asyncio.sleep(1)

    # Analyze the query
    emotion = analyze_emotion(customer_query)
    intent = analyze_intent(customer_query)
    requirements = analyze_requirements(customer_query)
    preferences = analyze_preferences(customer_query)
    confidence = calculate_confidence_score(customer_query)
    summary = generate_analysis_summary(emotion, intent, requirements, preferences)

    # Create result
    result = CustomerQueryAnalysisResult(
        customer_query=customer_query,
        emotion=emotion,
        intent=intent,
        requirements=requirements,
        preferences=preferences,
        confidence_score=confidence,
        analysis_summary=summary
    )

    # Format output
    output = f"📊 Customer Query Analysis Result\n"
    output += f"{'=' * 60}\n\n"
    output += f"📝 Original Query:\n{result.customer_query}\n\n"
    output += f"💭 Analysis Summary:\n{result.analysis_summary}\n\n"
    output += f"📈 Detailed Breakdown:\n"
    output += f"  • Emotion: {result.emotion.upper()} 😊\n"
    output += f"  • Intent: {result.intent.replace('_', ' ').title()} 🎯\n"
    output += f"  • Requirements: {result.requirements.replace('_', ' ').title()} Class 💺\n"
    output += f"  • Preferences: {result.preferences.replace('_', ' ').title()} Seat 🪑\n"
    output += f"  • Confidence Score: {result.confidence_score:.2%} 📊\n"

    logger.info(f"Analysis complete - Emotion: {emotion}, Intent: {intent}, Confidence: {confidence:.2%}")

    return output

@mcp.tool()
async def get_analysis_categories() -> str:
    """
    Get all available analysis categories and their possible values.

    Returns information about:
    - Available emotions
    - Possible intents
    - Cabin class requirements
    - Seating preferences
    """
    logger.info("Retrieving analysis categories")

    output = "📋 Customer Query Analysis Categories\n"
    output += "=" * 60 + "\n\n"

    output += "😊 Emotions:\n"
    for emotion in EMOTIONS:
        output += f"  • {emotion.upper()}\n"

    output += "\n🎯 Intents:\n"
    for intent in INTENTS:
        output += f"  • {intent.replace('_', ' ').title()}\n"

    output += "\n💺 Requirements (Cabin Class):\n"
    for req in REQUIREMENTS:
        output += f"  • {req.replace('_', ' ').title()}\n"

    output += "\n🪑 Preferences (Seating):\n"
    for pref in PREFERENCES:
        output += f"  • {pref.replace('_', ' ').title()}\n"

    logger.info("Categories retrieved successfully")
    return output

@mcp.tool()
async def batch_analyze_queries(
    queries: Annotated[list[str], Field(description="List of customer queries to analyze")]
) -> str:
    """
    Analyze multiple customer queries in batch.

    This is useful for processing multiple queries efficiently.
    Returns a summary of all analyses.
    """
    logger.info(f"Batch analyzing {len(queries)} queries")

    if not queries:
        return "No queries provided for analysis."

    if len(queries) > 10:
        return "Maximum 10 queries allowed per batch. Please reduce the number of queries."

    results = []

    for idx, query in enumerate(queries, 1):
        # Analyze each query
        emotion = analyze_emotion(query)
        intent = analyze_intent(query)
        requirements = analyze_requirements(query)
        preferences = analyze_preferences(query)
        confidence = calculate_confidence_score(query)

        results.append({
            'query': query,
            'emotion': emotion,
            'intent': intent,
            'requirements': requirements,
            'preferences': preferences,
            'confidence': confidence
        })

    # Format batch output
    output = f"📊 Batch Analysis Results ({len(queries)} queries)\n"
    output += "=" * 60 + "\n\n"

    for idx, result in enumerate(results, 1):
        output += f"Query #{idx}:\n"
        output += f"  📝 Text: {result['query'][:50]}{'...' if len(result['query']) > 50 else ''}\n"
        output += f"  😊 Emotion: {result['emotion'].upper()}\n"
        output += f"  🎯 Intent: {result['intent'].replace('_', ' ').title()}\n"
        output += f"  💺 Class: {result['requirements'].replace('_', ' ').title()}\n"
        output += f"  🪑 Seat: {result['preferences'].replace('_', ' ').title()}\n"
        output += f"  📊 Confidence: {result['confidence']:.2%}\n\n"

    logger.info(f"Batch analysis complete for {len(queries)} queries")
    return output

@mcp.tool()
async def get_query_statistics(
    queries: Annotated[list[str], Field(description="List of queries to get statistics for")]
) -> str:
    """
    Get statistical analysis of multiple queries.

    Returns aggregated statistics including:
    - Most common emotion
    - Most common intent
    - Average confidence score
    - Distribution of requirements and preferences
    """
    logger.info(f"Calculating statistics for {len(queries)} queries")

    if not queries:
        return "No queries provided for statistics."

    emotion_counts = {e: 0 for e in EMOTIONS}
    intent_counts = {i: 0 for i in INTENTS}
    req_counts = {r: 0 for r in REQUIREMENTS}
    pref_counts = {p: 0 for p in PREFERENCES}
    confidences = []

    for query in queries:
        emotion = analyze_emotion(query)
        intent = analyze_intent(query)
        requirements = analyze_requirements(query)
        preferences = analyze_preferences(query)
        confidence = calculate_confidence_score(query)

        emotion_counts[emotion] += 1
        intent_counts[intent] += 1
        req_counts[requirements] += 1
        pref_counts[preferences] += 1
        confidences.append(confidence)

    # Calculate statistics
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
    most_common_intent = max(intent_counts.items(), key=lambda x: x[1])[0]

    # Format output
    output = f"📈 Query Statistics ({len(queries)} queries analyzed)\n"
    output += "=" * 60 + "\n\n"

    output += f"🎯 Overall Metrics:\n"
    output += f"  • Average Confidence: {avg_confidence:.2%}\n"
    output += f"  • Most Common Emotion: {most_common_emotion.upper()}\n"
    output += f"  • Most Common Intent: {most_common_intent.replace('_', ' ').title()}\n\n"

    output += "😊 Emotion Distribution:\n"
    for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(queries)) * 100
        output += f"  • {emotion.upper()}: {count} ({percentage:.1f}%)\n"

    output += "\n🎯 Intent Distribution:\n"
    for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(queries)) * 100
        output += f"  • {intent.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n"

    logger.info(f"Statistics calculated - Avg confidence: {avg_confidence:.2%}")
    return output

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("MCP Customer Query Analysis server starting (HTTP mode on port 8003)")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8003)

