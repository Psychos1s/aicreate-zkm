#!/usr/bin/env python3
"""
匹配概念对象。
"""

import os
import json
import sys

import requests
from pathlib import Path

# 添加 common 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from config import APP_NO, CONFIG, get_auth_tokens, get_env

app_no = os.path.basename(os.getcwd())
#app_no = "ea3aa5c5fadb45fe96d8c78e1c103943"

ENV_CONFIG = {
    "dev": {
        "url": "https://rdfa-gateway.fat.ennew.com/ioc-workbench",
        "access_key": "",
        "metaPaperId": 13735
    },
    "fat": {
        "url": "https://rdfa-gateway.fat.ennew.com/ioc-workbench",
        "access_key": "WSdE3IqssLE1CVqZZfTd2hzNO4hWxEtB"
    },
    "uat": {
        "url": "https://rdfa-gateway.uat.ennew.com/ioc-workbench",
        "access_key": "TsKwADFuHBGYXdfUVi4t7A2fckOLReH8",
    },
    "prod": {
        "url": "https://rdfa-gateway.ennew.com/ioc-workbench",
        "access_key": "9GeND2MF703TwYh3XQj1crMlz3Yp4eYi",
    }
}



def concept_object_match(inout):
        biz_sop_inout = match_conceptual_object_call(inout)
        return biz_sop_inout

def match_conceptual_object_call(inout):
    try:
        # 获取认证 token
        auth_tokens = get_auth_tokens()
        env = get_env()

        request_data = {
            "inout": inout,
        }
        response = requests.post(
            url=f'{ENV_CONFIG[env]["url"]}/api/ioc-workbench/v1/app/bot/conceptualObject/match',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": ENV_CONFIG[env]["access_key"],
                'Authorization': auth_tokens['ennunifiedauthorization'],
                'x-csrf-token': auth_tokens['ennunifiedcsrftoken'],
            }
        )
        response_data = response.json()
        print(f"提交数据成功：{response_data}")
        if response_data.get("resultCode", "") != 0:
            raise Exception(response_data.get("message", "未知错误"))
        print(f"matchConceptualObject return：{response_data['data']}")
        return response_data['data']
    except Exception as e:
        print(f"提交数据失败：{str(e)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='概念对象匹配')
    parser.add_argument('--inout', type=str, help='输入输出')


    args = parser.parse_args()

    if args.inout is None:
        print("错误：必须传入 --inout 输入输出")
        sys.exit(1)

    concept_object_match(args.inout)
