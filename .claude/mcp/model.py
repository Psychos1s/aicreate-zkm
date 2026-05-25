import threading
import requests
from fastmcp import FastMCP
from typing import Annotated, Optional, Dict, Any, List
from pydantic import Field
import os
from pathlib import Path
import sys

# 添加 logger 模块路径
if (logger_dir := Path(__file__).resolve().parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(logger_dir))

from logger import log, info, warning, error, debug
from config import APP_NO, CONFIG, get_auth_tokens, ENV

# 初始化 FastMCP 服务
mcp = FastMCP("Model Tools")

# 获取项目根目录的绝对路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 固定的 business.json 路径(项目相对路径)
BUSINESS_JSON_PATH = os.path.join(PROJECT_ROOT, "business.json")


# 环境配置
INSIDE_ENV_CONFIG: Dict[str, Dict[str, Any]] = {
    "dev": {
        "access_key": "03xrP24S64j1bXsNIGux3YVI46C4ssh8",
        "gateway_url": "https://rdfa-gateway-inside.dev.ennew.com"
    },
    "fat": {
        "access_key": "TpQ44CJMHyYTSIQAtDdwpglkkxnWK6zR",
        "gateway_url": "https://rdfa-gateway-inside.fat.ennew.com"
    },
    "uat": {
        "access_key": "wzbR82y5WPVxZc3SgzkWdk9KSuOG0YFb",
        "gateway_url": "https://rdfa-gateway-inside.uat.ennew.com"
    },
    "prod": {
        "access_key": "FOUJYntkmkuZzqJlxIOXQ8EQySE2tvLw",
        "gateway_url": "https://rdfa-gateway-inside.ennew.com"
    }
}

HEADERS = {"Content-Type": "application/json"}

# ====================== 内部工具方法 ======================
def fetch_ability_model_id(appNo: str) -> Optional[str]:
    """根据 appNo 获取 paperId"""
    try:
        info(f"请求参数:{appNo}")
        auth_tokens = get_auth_tokens()
        access_key = CONFIG.get("access_key", "")
        headers = {
            **HEADERS,
            "x-gw-accesskey": access_key,
            **auth_tokens
        }

        response = requests.post(
            url=f"{CONFIG['gateway_url']}/ioc-workbench/domain-meta/init",
            json={"appNo": appNo},
            headers=headers
        )
        res = response.json()
        info(f"返回参数:{response}")

        if res.get("resultCode") == 0:
            return res.get("data", {}).get("paperId")
    except Exception as e:
        error(f"获取paperId异常: {str(e)}")
    return None

def saveExampleData():
    """生成图谱实例数据"""
    try:
        info(f"saveExampleData，请求参数:{APP_NO}")
        auth_tokens = get_auth_tokens()
        access_key = CONFIG.get("access_key", "")
        headers = {
            **HEADERS,
            "x-gw-accesskey": access_key,
            **auth_tokens
        }

        response = requests.post(
            url=f"{CONFIG['gateway_url']}/ioc-workbench/api/ioc-workbench/v1/app/sop/saveExampleData",
            json={"appNo": APP_NO},
            headers=headers
        )
        info(f"saveExampleData，返回参数:{response}")

    except Exception as e:
        error(f"saveExampleData异常: {str(e)}")
    return None


def generate_domain_ont(domain_model: str) -> str:
    try:
        # 获取认证 token
        auth_tokens = get_auth_tokens()
        request_data = {
            "paperId": domain_model,
            "appNo": APP_NO
        }
        info(f"生成本体，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/domain-ont/generation/V2',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
                **auth_tokens
            }
        )
        response_data = response.json()
        info(f"生成本体成功，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"生成本体失败: {response_data.get('message', '未知错误')}"
        real_data = response_data['data']
        info(f"生成本体成功，返回结果：{real_data['paperId']}")
        return real_data['paperId']
    except Exception as e:
        error(f"生成本体失败，错误：{str(e)}")
        return f"生成本体失败，错误：{str(e)}"




@mcp.tool()
def upload_file(file_path: str) -> Optional[str]:
    """
    上传文件到文件服务，返回文件URL
    """
    try:
        auth_tokens = get_auth_tokens()
        access_key = CONFIG.get("access_key", "")

        headers = {
            "x-gw-accesskey": access_key,
            **auth_tokens
        }

        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                url=f"{CONFIG['gateway_url']}/dt-biz-base/api/front/file/upload",
                files=files,
                headers=headers
            )

        res = response.json()
        if res.get("success", False):
            return res.get("data")

        error(f"文件上传失败：{res.get('message', '未知错误')}")
        return None

    except Exception as e:
        error(f"文件上传异常：{str(e)}")
        return None

if __name__ == "__main__":
    mcp.run()