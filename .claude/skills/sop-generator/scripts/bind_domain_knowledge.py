#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绑定领域约束元到应用（失败不中断流程）
用法: python bind_domain_knowledge.py --domain <domain_id>
"""
import os
import sys
from pathlib import Path

import requests
import yaml

# 添加 common 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from config import APP_NO, CONFIG, get_auth_tokens

DOMAIN_KNOWLEDGE_URL = "/ioc-workbench/api/ioc-workbench/v1/app/sop/domainKnowledge"


def get_domain_file(domain_id: str) -> Path:
    """获取领域配置文件路径"""
    script_dir = Path(__file__).resolve().parent
    domain_file = script_dir.parent / "domains" / domain_id / "domain.yaml"
    if not domain_file.exists():
        domain_file = domain_file.with_suffix('.yml')
    return domain_file


def load_domain_config(domain_id: str) -> dict:
    """加载领域配置"""
    domain_file = get_domain_file(domain_id)
    if not domain_file.exists():
        return {}
    
    with open(domain_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def bind_domain_knowledge(domain_id: str) -> bool:
    """
    绑定领域约束元到应用
    失败不中断流程，仅打印日志
    """
    try:
        # 加载领域配置获取 constraintPaperId
        config = load_domain_config(domain_id)
        domain_info = config.get('domain', {})
        constraint_paper_id = domain_info.get('constraintPaperId')
        
        # constraintPaperId 为空，不调用接口
        if not constraint_paper_id:
            return True
        
        # 准备请求参数
        request_body = {
            "appNo": APP_NO,
            "domain": domain_id,
            "constraintPaperId": str(constraint_paper_id)
        }
        
        # 获取认证 token
        auth_tokens = get_auth_tokens()
        
        headers = {
            "Content-Type": "application/json",
            "x-gw-accesskey": CONFIG.get("access_key"),
            **auth_tokens
        }
        
        # 发送请求
        response = requests.post(
            url=CONFIG.get("gateway_url") + DOMAIN_KNOWLEDGE_URL,
            headers=headers,
            json=request_body,
            timeout=30
        )
        response.raise_for_status()
        
        print(f"约束元绑定成功: domain={domain_id} appNo={APP_NO} constraintPaperId={constraint_paper_id}")
        return True
        
    except Exception as e:
        # 接口调用失败不报错，仅打印日志，不中断流程
        print(f"约束元绑定失败（继续生成）: {e}")
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', type=str, required=True)
    args = parser.parse_args()
    
    bind_domain_knowledge(args.domain)
    sys.exit(0)  # 始终返回成功，不中断流程
