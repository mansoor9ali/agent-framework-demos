"""
Final comprehensive test for the ReAct Agent with DeepSeek
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.react.agent import run
from src.config.logging import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agent():
    """Test the ReAct agent with various queries"""

    # Check if DeepSeek is configured
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    model_id = os.getenv('DEEPSEEK_MODEL_ID', 'deepseek-chat')

    print("=" * 80)
    print("ReAct Agent - DeepSeek Integration Test")
    print("=" * 80)
    print(f"Model: {model_id}")
    print(f"Base URL: {base_url}")
    print(f"API Key: {'✓ Configured' if api_key else '✗ Missing'}")
    print("=" * 80)

    if not api_key:
        print("\n❌ ERROR: DEEPSEEK_API_KEY not found in environment variables!")
        print("Please ensure your .env file has the required variables.")
        return

    # Test queries
    queries = [
        "What is Python programming language?",
        "Who invented the telephone?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {query}")
        print(f"{'='*80}")

        try:
            answer = run(query)
            print(f"\n✅ Answer: {answer}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            logger.error(f"Test {i} failed: {e}")

    print(f"\n{'='*80}")
    print("Test Complete!")
    print(f"{'='*80}")
    print("\nCheck data/output/trace.txt for detailed execution logs.")

if __name__ == "__main__":
    test_agent()

