#!/usr/bin/env python3
"""
LLM Agent Helper for Skills
Usage: python llm_agent.py "prompt" [--system "system prompt"] [--json]

Loads environment from .env and calls LLM API.
Supports both Anthropic and Infini providers.
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Load .env from project root
def load_env():
    env_files = [
        Path(__file__).parent.parent / ".env",  # skills/.env
        Path(__file__).parent.parent.parent / ".env",  # project root .env
        Path.home() / ".claude" / "skills" / "quinn-awesome-skills" / ".env",
    ]

    for env_file in env_files:
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Only set if not already defined
                        if key not in os.environ:
                            os.environ[key] = value
            break

load_env()

# Now import after env is loaded
try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def get_provider_config():
    """Get LLM provider configuration from environment."""
    provider = os.environ.get("LLM_PROVIDER", "infini")

    if provider == "anthropic":
        return {
            "provider": "anthropic",
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "base_url": os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "model": os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "claude-sonnet-4-20250514"),
        }
    elif provider == "infini":
        return {
            "provider": "infini",
            "api_key": os.environ.get("INFINI_API_KEY", ""),
            "base_url": os.environ.get("INFINI_BASE_URL", "https://cloud.infini-ai.com/maas/coding"),
            "model": os.environ.get("LLM_MODEL", "glm-5"),
        }
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def call_llm(prompt: str, system_prompt: str = None, json_mode: bool = False) -> str:
    """Call LLM API and return response."""
    config = get_provider_config()

    if not config["api_key"]:
        raise ValueError(f"API key not configured for provider: {config['provider']}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": float(os.environ.get("LLM_TEMPERATURE", "0")),
    }

    # OpenAI-compatible endpoint
    url = f"{config['base_url']}/v1/chat/completions"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]

        if json_mode:
            # Try to parse as JSON
            try:
                return json.dumps(json.loads(content), ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                return content

        return content

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="LLM Agent Helper for Skills")
    parser.add_argument("prompt", help="User prompt to send to LLM")
    parser.add_argument("--system", "-s", help="System prompt", default=None)
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--provider", "-p", help="Override provider (anthropic/infini)")

    args = parser.parse_args()

    # Override provider if specified
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider

    try:
        result = call_llm(args.prompt, args.system, args.json)

        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding="utf-8")

        print(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
