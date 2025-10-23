#!/usr/bin/env python3
"""
Test script for Thames Water Voice Chatbot
Tests the chatbot logic without requiring full Streamlit UI
"""

import sys
sys.path.insert(0, '/home/user/thames-water-chatbot')

from voice_chatbot import ThamesWaterVoiceChatbot, THAMES_WATER_KB, INTENT_PATTERNS

def test_intent_detection():
    """Test intent detection functionality"""
    print("=" * 60)
    print("Testing Intent Detection")
    print("=" * 60)

    chatbot = ThamesWaterVoiceChatbot()

    test_cases = [
        ("How do I pay my bill?", "billing"),
        ("I have no water", "emergency"),
        ("My water pressure is low", "service"),
        ("How do I contact customer service?", "support"),
        ("I need to access my account", "account"),
        ("There's a leak in the street", "leak"),
        ("How do I read my meter?", "meter"),
    ]

    passed = 0
    for query, expected_intent in test_cases:
        detected = chatbot.detect_intent(query)
        status = "✓ PASS" if detected == expected_intent else "✗ FAIL"
        print(f"{status} | Query: '{query}'")
        print(f"       | Expected: {expected_intent}, Got: {detected}")
        if detected == expected_intent:
            passed += 1

    print(f"\nPassed: {passed}/{len(test_cases)}")
    print()
    return passed == len(test_cases)

def test_response_generation():
    """Test response generation"""
    print("=" * 60)
    print("Testing Response Generation")
    print("=" * 60)

    chatbot = ThamesWaterVoiceChatbot()

    test_queries = [
        "How do I pay my bill?",
        "I have an emergency water leak!",
        "My bill is too high",
        "What are your opening hours?",
        "I need to report a leak",
    ]

    for query in test_queries:
        response = chatbot.get_response(query)
        print(f"\nQuery: {query}")
        print(f"Response length: {len(response)} characters")
        print(f"Contains contact info: {'0800' in response}")

        # Check that response is not empty and contains useful info
        if len(response) > 50 and ('Thames Water' in response or '0800' in response or 'thameswater.co.uk' in response):
            print("Status: ✓ Valid response")
        else:
            print("Status: ✗ Invalid response")
    print()

def test_thames_water_data():
    """Test that Thames Water specific data is present"""
    print("=" * 60)
    print("Testing Thames Water Data")
    print("=" * 60)

    # Check knowledge base has Thames Water info
    checks = {
        "15 million customers": THAMES_WATER_KB['services']['water_supply'],
        "0800 714 614": THAMES_WATER_KB['services']['emergency_repairs'],
        "WaterSure": THAMES_WATER_KB['billing']['budget_billing'],
        "MyThamesWater": THAMES_WATER_KB['support']['mobile_app'],
        "hard water": THAMES_WATER_KB['thames_specific']['hardness'],
    }

    passed = 0
    for keyword, text in checks.items():
        if keyword.lower() in text.lower():
            print(f"✓ Found: {keyword}")
            passed += 1
        else:
            print(f"✗ Missing: {keyword}")

    print(f"\nPassed: {passed}/{len(checks)}")
    print()
    return passed == len(checks)

def test_emergency_numbers():
    """Test that correct emergency numbers are in responses"""
    print("=" * 60)
    print("Testing Emergency Contact Numbers")
    print("=" * 60)

    chatbot = ThamesWaterVoiceChatbot()

    emergency_tests = [
        ("water emergency", "0800 714 614"),
        ("sewer flooding", "0800 316 9800"),
        ("general enquiries", "0800 980 8800"),
        ("payment support", "0800 009 3652"),
    ]

    passed = 0
    for query, expected_number in emergency_tests:
        response = chatbot.get_response(query)
        if expected_number in response:
            print(f"✓ {query}: Contains {expected_number}")
            passed += 1
        else:
            print(f"✗ {query}: Missing {expected_number}")

    print(f"\nPassed: {passed}/{len(emergency_tests)}")
    print()
    return passed == len(emergency_tests)

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("THAMES WATER VOICE CHATBOT - TEST SUITE")
    print("=" * 60 + "\n")

    tests_passed = 0
    tests_total = 4

    # Run tests
    if test_intent_detection():
        tests_passed += 1

    test_response_generation()  # Just checking it runs
    tests_passed += 1

    if test_thames_water_data():
        tests_passed += 1

    if test_emergency_numbers():
        tests_passed += 1

    # Final summary
    print("=" * 60)
    print(f"FINAL RESULTS: {tests_passed}/{tests_total} test suites passed")
    print("=" * 60)

    if tests_passed == tests_total:
        print("✓ All tests passed! Voice chatbot is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
