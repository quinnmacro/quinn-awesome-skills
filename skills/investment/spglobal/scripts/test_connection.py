#!/usr/bin/env python3
"""
S&P Global MCP Connection Test Script
测试 S&P Global API 连接状态
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime


def test_spglobal_connection(api_key: str = None) -> dict:
    """
    测试 S&P Global MCP 连接

    Args:
        api_key: S&P Global API Key (可选，默认从环境变量读取)

    Returns:
        dict: 测试结果
    """
    if not api_key:
        api_key = os.environ.get("SPGLOBAL_API_KEY", "")

    results = {
        "timestamp": datetime.now().isoformat(),
        "api_key_set": bool(api_key),
        "api_key_prefix": api_key[:8] + "..." if api_key and len(api_key) > 8 else "N/A",
        "tests": []
    }

    # Test 1: Check API key format
    test_key_format = {
        "name": "API Key Format",
        "status": "pass" if api_key and len(api_key) > 20 else "fail",
        "message": f"Key length: {len(api_key) if api_key else 0}" if api_key else "API key not set"
    }
    results["tests"].append(test_key_format)

    # Test 2: MCP Endpoint Reachability
    mcp_url = "https://kfinance.kensho.com/integrations/mcp"
    try:
        req = urllib.request.Request(mcp_url, method="HEAD")
        req.add_header("Authorization", f"Bearer {api_key}")
        with urllib.request.urlopen(req, timeout=10) as response:
            test_endpoint = {
                "name": "MCP Endpoint Reachable",
                "status": "pass" if response.status in [200, 401, 403] else "fail",
                "message": f"HTTP {response.status}"
            }
    except urllib.error.HTTPError as e:
        test_endpoint = {
            "name": "MCP Endpoint Reachable",
            "status": "pass" if e.code in [401, 403] else "fail",
            "message": f"HTTP {e.code} (Auth required - endpoint reachable)"
        }
    except urllib.error.URLError as e:
        test_endpoint = {
            "name": "MCP Endpoint Reachable",
            "status": "fail",
            "message": str(e.reason)
        }
    except Exception as e:
        test_endpoint = {
            "name": "MCP Endpoint Reachable",
            "status": "fail",
            "message": str(e)
        }
    results["tests"].append(test_endpoint)

    # Test 3: Try a simple API call (if key available)
    if api_key:
        try:
            # Try to get company info for Apple (AAPL)
            test_url = f"{mcp_url}/companies?ticker=AAPL"
            req = urllib.request.Request(test_url)
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Accept", "application/json")

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                test_api_call = {
                    "name": "API Data Fetch",
                    "status": "pass",
                    "message": f"Retrieved data for AAPL"
                }
        except urllib.error.HTTPError as e:
            if e.code == 401:
                test_api_call = {
                    "name": "API Data Fetch",
                    "status": "fail",
                    "message": "Authentication failed - check API key"
                }
            elif e.code == 403:
                test_api_call = {
                    "name": "API Data Fetch",
                    "status": "fail",
                    "message": "Access forbidden - check subscription"
                }
            else:
                test_api_call = {
                    "name": "API Data Fetch",
                    "status": "fail",
                    "message": f"HTTP {e.code}"
                }
        except Exception as e:
            test_api_call = {
                "name": "API Data Fetch",
                "status": "fail",
                "message": str(e)
            }
    else:
        test_api_call = {
            "name": "API Data Fetch",
            "status": "skip",
            "message": "No API key provided"
        }
    results["tests"].append(test_api_call)

    # Calculate overall status
    passed = sum(1 for t in results["tests"] if t["status"] == "pass")
    total = len(results["tests"])
    results["summary"] = {
        "passed": passed,
        "total": total,
        "status": "pass" if passed == total else "fail"
    }

    return results


def print_results(results: dict):
    """打印测试结果"""
    print("\n" + "=" * 60)
    print("  S&P Global MCP Connection Test")
    print("=" * 60)
    print(f"\n  Timestamp: {results['timestamp']}")
    print(f"  API Key Set: {'Yes' if results['api_key_set'] else 'No'}")
    if results['api_key_set']:
        print(f"  Key Prefix: {results['api_key_prefix']}")

    print("\n  Tests:")
    print("-" * 60)

    for test in results["tests"]:
        status_icon = {
            "pass": "[PASS]",
            "fail": "[FAIL]",
            "skip": "[SKIP]"
        }.get(test["status"], "[?]")

        print(f"  {status_icon} {test['name']}")
        print(f"     {test['message']}")

    print("-" * 60)
    summary = results["summary"]
    print(f"\n  Result: {summary['passed']}/{summary['total']} tests passed")
    print(f"  Overall: {'[PASS]' if summary['status'] == 'pass' else '[FAIL]'}")
    print("\n" + "=" * 60 + "\n")


def main():
    """主函数"""
    print("\n[Search] Testing S&P Global MCP Connection...\n")

    # Check environment
    api_key = os.environ.get("SPGLOBAL_API_KEY", "")

    if not api_key:
        print("[Warning] SPGLOBAL_API_KEY environment variable not set")
        print("   Set it with: export SPGLOBAL_API_KEY='your_key'")
        print("   Or pass as argument: python test_connection.py YOUR_KEY\n")

        if len(sys.argv) > 1:
            api_key = sys.argv[1]
            print(f"   Using key from argument: {api_key[:8]}...\n")

    results = test_spglobal_connection(api_key)
    print_results(results)

    # Return exit code
    sys.exit(0 if results["summary"]["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
