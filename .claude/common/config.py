"""
系统环境配置模块
提供不同环境的 API 地址、访问密钥等配置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

from logger import info

# 获取当前环境，默认为 fat
ENV = os.getenv('ENV', 'fat').lower()

# 获取应用编号
APP_NO = os.path.basename(os.getcwd())
# APP_NO = "sop_a5190666184849b7959d520712294456"

# SOP 流程执行 URL 常量
SOP_PROCESS_URL = "/iop-executing-flow/api/iop-executing-flow/v1/executeRuntime/executeToBusiness/0b76698da8fd4147b7034636c3431383/bpm_1769003727839_dcc7c8"

ENV_CONFIG: Dict[str, Dict[str, Any]] = {
    "dev": {
        "access_key": "",
        "gateway_url": "https://rdfa-gateway.fat.ennew.com"
    },
    "fat": {
        "access_key": "WSdE3IqssLE1CVqZZfTd2hzNO4hWxEtB",
        "gateway_url": "https://rdfa-gateway.fat.ennew.com",
        "oss_url": "https://vlm-temp-storage.obsv3.cn-lflt-1.enncloud.cn/claude-workspace-fat",
        "gateway_url_inside": "https://rdfa-gateway-inside.fat.ennew.com",
        "access_key_inside": "TpQ44CJMHyYTSIQAtDdwpglkkxnWK6zR"
    },
    "uat": {
        "access_key": "TsKwADFuHBGYXdfUVi4t7A2fckOLReH8",
        "gateway_url": "https://rdfa-gateway.uat.ennew.com",
        "gateway_url_inside": "https://rdfa-gateway-inside.uat.ennew.com",
        "access_key_inside": "wzbR82y5WPVxZc3SgzkWdk9KSuOG0YFb",
        "oss_url": "https://vlm-temp-storage.obsv3.cn-lflt-1.enncloud.cn/claude-workspace-uat"
    },
    "prod": {
        "access_key": "9GeND2MF703TwYh3XQj1crMlz3Yp4eYi",
        "gateway_url": "https://rdfa-gateway.ennew.com"
    }
}


# 获取当前环境配置
CONFIG = ENV_CONFIG.get(ENV, ENV_CONFIG["fat"])


# 动态变量配置文件
APP_CONFIG_FILE = Path(__file__).parent.parent.parent / ".app_config.json"

# 动态变量
AUTH_TOKEN_KEY = 'ennUnifiedAuthorization'
CSRF_TOKEN_KEY = 'ennUnifiedCsrfToken'


def get_app_config_field(field: str) -> Any:
    """
    读取 .app_config.json 中的指定字段

    Args:
        field: 字段名称，如 'constraintAppNo'

    Returns:
        字段值，不存在则返回 None
    """
    if not APP_CONFIG_FILE.exists():
        raise FileNotFoundError(f"应用配置文件不存在: {APP_CONFIG_FILE}")

    with open(APP_CONFIG_FILE, 'r', encoding='utf-8') as f:
        app_config = json.load(f)

    return app_config.get(field)


def get_auth_tokens() -> Dict[str, str]:
    """
    实时读取 .app_config.json 中的认证 token

    Returns:
        Dict[str, str]: 包含 ennu_auth 和 csrf_token 的字典

    Raises:
        FileNotFoundError: 配置文件不存在
        KeyError: 配置文件缺少必要的字段
        json.JSONDecodeError: 配置文件格式错误
    """
    if not APP_CONFIG_FILE.exists():
        raise FileNotFoundError(f"应用配置文件不存在: {APP_CONFIG_FILE}")

    with open(APP_CONFIG_FILE, 'r', encoding='utf-8') as f:
        app_config = json.load(f)

    tokens = {
        AUTH_TOKEN_KEY: app_config.get(AUTH_TOKEN_KEY),
        CSRF_TOKEN_KEY: app_config.get(CSRF_TOKEN_KEY)
    }
    info(f"读取配置文件: {APP_CONFIG_FILE}；get_auth_tokens 返回: {tokens}")
    return tokens




