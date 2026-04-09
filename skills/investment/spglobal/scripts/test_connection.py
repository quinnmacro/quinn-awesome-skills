#!/usr/bin/env python3
"""
Kensho / S&P Global LLM-ready API Connection Test
支持三种认证方式：Browser Login, Refresh Token, Key Pair
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime


def test_kensho_connection(
    refresh_token: str = None,
    client_id: str = None,
    private_key_path: str = None
) -> dict:
    """
    测试 Kensho LLM-ready API 连接

    Args:
        refresh_token: Kensho refresh token
        client_id: Kensho client ID (for key pair auth)
        private_key_path: Path to private key file

    Returns:
        dict: 测试结果
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "auth_methods": [],
        "tests": []
    }

    # Check available auth methods
    has_refresh_token = bool(refresh_token)
    has_key_pair = bool(client_id and private_key_path and os.path.exists(private_key_path))

    results["auth_methods"] = {
        "refresh_token": has_refresh_token,
        "key_pair": has_key_pair
    }

    # Test 1: MCP Endpoint Reachability
    mcp_url = "https://kfinance.kensho.com/integrations/mcp"
    try:
        req = urllib.request.Request(mcp_url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as response:
            test_endpoint = {
                "name": "MCP Endpoint Reachable",
                "status": "pass" if response.status in [200, 401, 403, 405] else "fail",
                "message": f"HTTP {response.status}"
            }
    except urllib.error.HTTPError as e:
        test_endpoint = {
            "name": "MCP Endpoint Reachable",
            "status": "pass",  # 401/403 means endpoint is reachable, just needs auth
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

    # Test 2: Check auth configuration
    if has_refresh_token:
        test_auth = {
            "name": "Refresh Token Configured",
            "status": "pass",
            "message": f"Token prefix: {refresh_token[:20]}..."
        }
    elif has_key_pair:
        test_auth = {
            "name": "Key Pair Configured",
            "status": "pass",
            "message": f"Client ID: {client_id[:8]}..., Key file exists"
        }
    else:
        test_auth = {
            "name": "Authentication Configuration",
            "status": "fail",
            "message": "No authentication method configured"
        }
    results["tests"].append(test_auth)

    # Test 3: Try API call if authenticated
    if has_refresh_token:
        try:
            # Try to get a simple company search
            test_url = f"{mcp_url}/search?query=AAPL"
            req = urllib.request.Request(test_url)
            req.add_header("Authorization", f"Bearer {refresh_token}")
            req.add_header("Accept", "application/json")

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                test_api = {
                    "name": "API Data Fetch",
                    "status": "pass",
                    "message": f"Successfully retrieved data"
                }
        except urllib.error.HTTPError as e:
            if e.code == 401:
                test_api = {
                    "name": "API Data Fetch",
                    "status": "fail",
                    "message": "Token expired or invalid - get new token at https://kfinance.kensho.com/manual_login/"
                }
            else:
                test_api = {
                    "name": "API Data Fetch",
                    "status": "fail",
                    "message": f"HTTP {e.code}"
                }
        except Exception as e:
            test_api = {
                "name": "API Data Fetch",
                "status": "fail",
                "message": str(e)
            }
    else:
        test_api = {
            "name": "API Data Fetch",
            "status": "skip",
            "message": "No refresh token provided"
        }
    results["tests"].append(test_api)

    # Calculate overall status
    passed = sum(1 for t in results["tests"] if t["status"] == "pass")
    total = len(results["tests"])
    results["summary"] = {
        "passed": passed,
        "total": total,
        "status": "pass" if passed >= 2 else "fail"  # Need at least endpoint + auth
    }

    return results


def print_results(results: dict):
    """打印测试结果"""
    print("\n" + "=" * 60)
    print("  Kensho LLM-ready API Connection Test")
    print("=" * 60)
    print(f"\n  Timestamp: {results['timestamp']}")

    auth = results["auth_methods"]
    print(f"\n  Authentication Methods:")
    print(f"    Refresh Token: {'Yes' if auth['refresh_token'] else 'No'}")
    print(f"    Key Pair: {'Yes' if auth['key_pair'] else 'No'}")

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

    print("\n  Setup Guide:")
    print("  1. Email commercial@kensho.com to get access")
    print("  2. Get refresh token: https://kfinance.kensho.com/manual_login/")
    print("  3. Set KENSHO_REFRESH_TOKEN in .env")
    print("\n" + "=" * 60 + "\n")


def main():
    """主函数"""
    print("\n[Testing] Kensho LLM-ready API Connection...\n")

    # Check environment variables
    refresh_token = os.environ.get("KENSHO_REFRESH_TOKEN", "")
    client_id = os.environ.get("KENSHO_CLIENT_ID", "")
    private_key_path = os.environ.get("KENSHO_PRIVATE_KEY_PATH", "")

    # Allow command line override
    if len(sys.argv) > 1:
        refresh_token = sys.argv[1]
        print(f"  Using refresh token from argument: {refresh_token[:20]}...\n")

    if not refresh_token and not client_id:
        print("[Warning] No authentication configured")
        print("  Set KENSHO_REFRESH_TOKEN or (KENSHO_CLIENT_ID + KENSHO_PRIVATE_KEY_PATH)")
        print("  Get refresh token: https://kfinance.kensho.com/manual_login/\n")

    results = test_kensho_connection(
        refresh_token=refresh_token,
        client_id=client_id,
        private_key_path=private_key_path
    )
    print_results(results)

    # Return exit code
    sys.exit(0 if results["summary"]["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
