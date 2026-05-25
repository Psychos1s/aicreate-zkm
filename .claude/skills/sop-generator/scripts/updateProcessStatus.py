#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
from pathlib import Path

import requests

# 添加 common 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from config import APP_NO, CONFIG, SOP_PROCESS_URL,  get_auth_tokens

if __name__ == "__main__":
    import argparse
    # interview:开始访谈
    # sop:
    parser = argparse.ArgumentParser(description='更新流程状态')
    parser.add_argument('--process', type=str, help='要更新的状态')
    args = parser.parse_args()

    if args.process is None:
        print("错误：必须传入 --process 参数指定要更新的状态")
        sys.exit(1)

    # 准备请求体
    request_body = {
        "process": args.process,
        "appNo": APP_NO
    }

    # 获取认证 token
    auth_tokens = get_auth_tokens()

    headers = {
        "Content-Type": "application/json",
        "x-gw-accesskey": CONFIG.get("access_key"),
        **auth_tokens
    }

    try:
        response = requests.post(
            url=CONFIG.get("gateway_url") + SOP_PROCESS_URL,
            headers=headers,
            json=request_body,
            timeout=30
        )
        response.raise_for_status()
        print(f"状态同步成功: appNo={APP_NO}, process={args.process}")
    except requests.exceptions.RequestException as e:
        print(f"状态同步失败: {e}")
        sys.exit(1)
