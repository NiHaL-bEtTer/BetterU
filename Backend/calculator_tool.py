"""
calculator_tool.py
------------------
Tool wrapper around calculator.py.

The LLM (llama3 via Ollama) calls nutrition_calculator_tool() to get
accurate numbers. The LLM never performs the math itself — it only
receives the results and explains them to the user.

Usage:
    from calculator_tool import nutrition_calculator_tool
    result = nutrition_calculator_tool(user_data)

Test:
    python calculator_tool.py
"""

import json
import sys
import os

# Ensure calculator.py is found even when called from a different directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import full_nutrition_calculation


def nutrition_calculator_tool(user_data):
    """
    Entry point for the LLM backend (FastAPI /calculate and /chat endpoints).

    Accepts a user profile dict, runs all nutrition calculations via
    calculator.py, and returns a clean JSON-serialisable dict.

    On invalid input returns an error dict instead of raising, so the
    LLM always receives a structured response.

    Args:
        user_data (dict): must contain:
            age      (int)   – years
            sex      (str)   – 'male' or 'female'
            weight   (float) – kg
            height   (float) – cm
            activity (str)   – sedentary|light|moderate|active|very_active
            goal     (str)   – bulk|maintain|cut

    Returns:
        dict: full nutrition results, or {'error': str} on failure
    """
    try:
        result = full_nutrition_calculation(user_data)
        return result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


# ---------------------------------------------------------------------------
# Test runner — python calculator_tool.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    test_cases = [
        {
            "label": "18-year-old male · moderate · bulk",
            "data": {
                "age":      18,
                "sex":      "male",
                "weight":   75,
                "height":   180,
                "activity": "moderate",
                "goal":     "bulk",
            },
        },
        {
            "label": "30-year-old female · light · cut",
            "data": {
                "age":      30,
                "sex":      "female",
                "weight":   65,
                "height":   165,
                "activity": "light",
                "goal":     "cut",
            },
        },
        {
            "label": "45-year-old male · active · maintain",
            "data": {
                "age":      45,
                "sex":      "male",
                "weight":   90,
                "height":   175,
                "activity": "active",
                "goal":     "maintain",
            },
        },
        {
            "label": "Missing fields (error handling test)",
            "data": {
                "age":    25,
                "sex":    "female",
                # weight, height, activity, goal deliberately omitted
            },
        },
        {
            "label": "Invalid activity level (error handling test)",
            "data": {
                "age":      22,
                "sex":      "male",
                "weight":   80,
                "height":   178,
                "activity": "olympic_athlete",   # invalid
                "goal":     "bulk",
            },
        },
    ]

    for case in test_cases:
        print()
        print("=" * 58)
        print(f"  {case['label']}")
        print("=" * 58)
        result = nutrition_calculator_tool(case["data"])
        print(json.dumps(result, indent=4))

    print()