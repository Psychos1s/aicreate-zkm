#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json

import requests

env = os.getenv('ENV', 'fat').lower()

ENV_CONFIG = {
    "fat": {
        "url": "https://rdfa-gateway.fat.ennew.com/iop-executing-flow/api/iop-executing-flow/v1/executeRuntime/executeToBusiness/0b76698da8fd4147b7034636c3431383/bpm_1769003727839_dcc7c8",
        "x-gw-accesskey": "WSdE3IqssLE1CVqZZfTd2hzNO4hWxEtB",
    },
    "uat": {
        "url": "https://rdfa-gateway.uat.ennew.com/iop-executing-flow/api/iop-executing-flow/v1/executeRuntime/executeToBusiness/0b76698da8fd4147b7034636c3431383/bpm_1769003727839_dcc7c8",
        "x-gw-accesskey": "zfJEFCOzHjSPSAt5nTHrmRL0xH9Gw8TC",
    },
    "prod": {
        "url": "https://rdfa-gateway.ennew.com/iop-executing-flow/api/iop-executing-flow/v1/executeRuntime/executeToBusiness/0b76698da8fd4147b7034636c3431383/bpm_1769003727839_dcc7c8",
        "x-gw-accesskey": "dHSkUDrHqhWeEangefVoM2IKLmLHs1MO",
    }
}

if __name__ == "__main__":
    data = json.load(sys.stdin)
    print("==============hook入参为============")
    print(data)
    session_id = data.get("session_id")
    tool = data.get("tool_name")
    tool_input = data.get("tool_input", {})
    skill_name = tool_input.get("command", "")

    # 只在skill为generate-app-data时执行
    if skill_name != "generate-app-data":
        sys.exit(0)

    # 获取项目根目录名称作为appNo
    app_no = os.path.basename(os.getcwd())

    # 准备请求体
    request_body = {
        "writeStatus": "running",
        "appNo": app_no
    }

    config = ENV_CONFIG.get(env)
    if not config:
        print(f"错误: 不支持的环境配置 - {env}")
        sys.exit(1)

    headers = {
        "Content-Type": "application/json",
        "x-gw-accesskey": config.get("x-gw-accesskey"),
    }

    try:
        response = requests.post(
            url=config.get("url"),
            headers=headers,
            json=request_body,
            timeout=30
        )
        response.raise_for_status()
        print(f"状态同步成功: appNo={app_no}, writeStatus=running")
    except requests.exceptions.RequestException as e:
        print(f"状态同步失败: {e}")
        sys.exit(1)
