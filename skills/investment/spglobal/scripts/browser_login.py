#!/usr/bin/env python3
"""
Kensho Browser Login - 获取 Refresh Token
用法: python browser_login.py
"""

import sys
import os

def main():
    print("\n" + "=" * 60)
    print("  Kensho Browser Login")
    print("=" * 60)
    print("\n  即将打开浏览器进行 Okta 登录...")
    print("  请使用你的 Kensho 凭据登录")
    print("  登录成功后浏览器会自动关闭\n")
    print("-" * 60)

    try:
        from kfinance.client.kfinance import Client

        # Browser login - 自动打开浏览器
        client = Client()

        # 获取 access token
        access_token = client.access_token

        print("\n" + "=" * 60)
        print("  [SUCCESS] 登录成功!")
        print("=" * 60)
        print(f"\n  Access Token:\n  {access_token[:80]}...\n")

        # 测试查询
        print("-" * 60)
        print("  测试 API: 查询 AAPL...")
        print("-" * 60)

        try:
            ticker = client.ticker("AAPL")
            print(f"\n  [OK] Ticker: {ticker}")
        except Exception as e:
            print(f"\n  [INFO] {e}")

        # 保存 token
        token_file = os.path.expanduser("~/.kensho_refresh_token")
        with open(token_file, "w") as f:
            f.write(access_token)
        print(f"\n  Token 已保存到: {token_file}")

        # 提示配置
        print("\n" + "=" * 60)
        print("  下一步: 将 token 添加到 .env 文件")
        print("=" * 60)
        print(f"\n  KENSHO_REFRESH_TOKEN={access_token[:50]}...\n")
        print("  或完整 token:")
        print(f"  KENSHO_REFRESH_TOKEN={access_token}\n")

        return 0

    except Exception as e:
        print("\n" + "=" * 60)
        print("  [ERROR] 登录失败")
        print("=" * 60)
        print(f"\n  {e}\n")
        print("  可能原因:")
        print("  1. 没有 Kensho 账号 - 发邮件到 commercial@kensho.com")
        print("  2. 浏览器弹出被阻止 - 允许弹出窗口")
        print("  3. Okta 凭据错误 - 检查用户名密码\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
