#!/usr/bin/env python3
"""
检查应用配置数据。

返回值：
- True:
- False:
"""

import sys
from pathlib import Path

import requests

# 添加 common 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from config import APP_NO, CONFIG, get_auth_tokens

def check_business_json():
    try:
        if check_sop_nodes():
            # 文件存在，返回 true
            print("true")
            return True
        else:
            # 返回 false 表示文件是新创建的
            print("false")
            return False
    except Exception as e:
        print(f"error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def check_sop_nodes():
    """
    查询 SOP 并检查 nodes 是否为空。

    返回值：
    - True: nodes 不为空
    - False: nodes 为空或查询失败

    注意：此函数只返回布尔值，不输出到stdout，避免重复输出
    """
    try:
        sop_data = querySOP()
        if sop_data and 'nodes' in sop_data:
            nodes = sop_data['nodes']
            if nodes and len(nodes) > 0:
                return True
        return False
    except Exception as e:
        print(f"检查 SOP nodes 失败：{str(e)}", file=sys.stderr)
        return False

def querySOP():
    try:
        # 获取认证 token
        auth_tokens = get_auth_tokens()

        request_data = {
            "appNo": APP_NO,
        }
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/querySop',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
                **auth_tokens
            }
        )
        response_data = response.json()
        if response_data.get("resultCode", "") != 0:
            raise Exception(response_data.get("message", "未知错误"))
        print(f"查询应用配置，结果：{response_data['data']}")
        return response_data['data']
    except Exception as e:
        print(f"提交数据失败：{str(e)}")
        raise

if __name__ == "__main__":

    check_business_json()
