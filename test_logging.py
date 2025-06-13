#!/usr/bin/env python3
"""
Test script for Rowan MCP Server logging
"""

import os
import sys
import logging

# Add src to path
sys.path.insert(0, 'src')

# Set up a test API key if not present
if not os.getenv("ROWAN_API_KEY"):
    os.environ["ROWAN_API_KEY"] = "test_key_for_logging_test"

try:
    from server import logger, log_mcp_call, log_rowan_api_call
    
    print("🧪 Testing Rowan MCP Server Logging...")
    print("=" * 50)
    
    # Test 1: Basic logging
    logger.info("🔬 Test 1: Basic logging test")
    logger.warning("⚠️ Test warning message")
    logger.error("❌ Test error message")
    
    # Test 2: Decorator test
    @log_mcp_call
    def test_function(name: str, value: int = 42):
        logger.info(f"Inside test function with {name} and {value}")
        return f"Test result: {name} = {value}"
    
    result = test_function(name="test_param", value=123)
    print(f"Function result: {result}")
    
    # Test 3: Check log file
    if os.path.exists("rowan_mcp.log"):
        print("\n📁 Log file created successfully!")
        with open("rowan_mcp.log", "r") as f:
            lines = f.readlines()
            print(f"📊 Log file contains {len(lines)} lines")
            if lines:
                print("📝 Last few log entries:")
                for line in lines[-3:]:
                    print(f"   {line.strip()}")
    else:
        print("❌ Log file not found!")
    
    print("\n✅ Logging test completed!")
    print("📁 Check 'rowan_mcp.log' for detailed logs")
    
except Exception as e:
    print(f"❌ Error during logging test: {e}")
    import traceback
    traceback.print_exc() 