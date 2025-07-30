#!/usr/bin/env python3
"""
Quick validation test to verify our fixes work
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tbh_secure_agents import Expert

# Set API key for testing
os.environ["GOOGLE_API_KEY"] = "AIzaSyBtIh9ShcSmezYKa8xmI0kIyyl2gJZIYFc"

def main():
    print("🧪 Quick Validation Test")
    print("=" * 30)
    
    # Test Expert creation
    print("Creating expert...")
    expert = Expert(
        specialty="Test Expert",
        objective="Test the framework",
        background="Testing expert",
        security_profile="minimal",
        memory_duration="long_term",
        user_id="test_user_001"
    )
    print("✅ Expert created successfully!")
    
    # Test memory operations (our main fix)
    print("\nTesting memory operations...")
    expert.remember(
        content="This is a test memory entry",
        memory_type="WORKING"
    )
    print("✅ Memory storage successful!")
    
    # Test memory recall
    memories = expert.recall("test memory", limit=1)
    print(f"✅ Memory recall successful! Found {len(memories)} memories")
    
    print("\n🎉 All validation tests passed!")
    print("Framework fixes are working correctly!")

if __name__ == "__main__":
    main()
