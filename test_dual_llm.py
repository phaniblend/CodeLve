"""
Test script for Dual LLM Handler with CodeT5+
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from dual_llm_handler import DualLLMHandler


def test_dual_llm_handler():
    """Test the Dual LLM Handler"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Initialize handler
    handler = DualLLMHandler()
    
    # Initialize models
    print("\n=== Initializing Models ===")
    if handler.initialize():
        print("[SUCCESS] Models initialized successfully!")
        print(f"Model Info: {handler.get_model_info()}")
    else:
        print("[ERROR] Failed to initialize models")
        return
    
    # Test queries
    test_queries = [
        {
            "query": "generate a React component for a todo list",
            "context": ""
        },
        {
            "query": "create a function to validate email addresses",
            "context": ""
        },
        {
            "query": "fix this bubble sort function",
            "context": """def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                # Missing swap logic"""
        },
        {
            "query": "complete this function",
            "context": """def fibonacci(n):
    if n <= 1:
        return n
    else:"""
        },
        {
            "query": "explain how this works",
            "context": """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)"""
        }
    ]
    
    # Run tests
    for i, test in enumerate(test_queries, 1):
        print(f"\n=== Test {i}: {test['query']} ===")
        
        try:
            response, used_code_model = handler.process_query(
                test['query'], 
                test['context']
            )
            
            print(f"Used Code Model: {used_code_model}")
            print(f"Response:\n{response}\n")
        except Exception as e:
            print(f"[ERROR] Test failed: {str(e)}")
        
        print("-" * 50)
    
    # Test pattern-based generation
    print("\n=== Testing Pattern-Based Generation ===")
    patterns = {
        "style": "functional",
        "framework": "react",
        "state": "hooks"
    }
    specs = {
        "name": "UserProfile",
        "props": ["name", "email", "avatar"]
    }
    
    try:
        result = handler.generate_with_patterns("component", patterns, specs)
        print(f"Generated Component:\n{result}")
    except Exception as e:
        print(f"[ERROR] Pattern generation failed: {str(e)}")
    
    # Cleanup
    handler.cleanup()
    print("\n[SUCCESS] Test completed!")


if __name__ == "__main__":
    test_dual_llm_handler()