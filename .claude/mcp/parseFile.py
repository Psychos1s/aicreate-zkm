import os
import requests
from fastmcp import FastMCP
from typing import Annotated, Optional, Dict, Any
from pydantic import Field
import logging

# 环境配置：根据不同环境使用不同的 URL 和 accesskey
ENV_CONFIG = {
    "fat": {
        "url": "https://hcs-ai-chat-backend.fat.ennew.com/chat/api/knowledgeBase/parseFile",
        "accesskey": "uXnSpC7JDP6mNC6SFyAqNG1r45apCJPd"
    },
    "uat": {
        "url": "https://ai-chat-backend.uat.ennew.com/chat/api/knowledgeBase/parseFile",
        "accesskey": "BmopB4qgKgWEqvkWK2yyQhkUskg5vcjs"
    },
    "prod": {
        "url": "",
        "accesskey": ""
    }
}

# 从环境变量获取当前环境，默认为 fat,  这种方式有待验证
CURRENT_ENV = os.getenv('ENV', 'fat').lower()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parseFile.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 初始化 FastMCP 服务
mcp = FastMCP("Parse File Service")


@mcp.tool()
def parseFile(
        fileUrl: Annotated[
            str,
            Field(
                description="要解析的文件URL地址。"
            )
        ]
) -> str:
    """
    解析指定URL的文件，返回文件内容结构化数据。
    支持 Excel、Word、PDF 等常见文件格式。
    """
    try:
        request_data = {
            "fileUrl": fileUrl
        }
        logger.info(f"解析文件，请求入参：{request_data}")

        # 获取当前环境的配置
        env = CURRENT_ENV
        if env not in ENV_CONFIG:
            return f"不支持的环境: {env}，支持的环境: {', '.join(ENV_CONFIG.keys())}"

        config = ENV_CONFIG[env]
        response = requests.post(
            url=config["url"],
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "appId": "ai-chat-backend",
                "X-Gw-Accesskey": config["accesskey"]
            }
        )
        response_data = response.json()
        logger.info(f"解析文件，返回结果：{response_data}")

        # 检查响应状态
        if response.status_code != 200:
            return f"文件解析失败: HTTP状态码 {response.status_code}"

        # 检查业务响应码 (code = "0" 表示成功)
        if response_data.get("code") != "0":
            error_msg = response_data.get("message") or "未知错误"
            return f"文件解析失败: {error_msg}"

        # 返回解析结果（data 字段包含解析后的内容）
        data = response_data.get("data", "")
        return data if data else "文件解析成功，但内容为空"
    except Exception as e:
        logger.error(f"文件解析失败，错误：{str(e)}")
        return f"文件解析失败，错误：{str(e)}"


if __name__ == "__main__":
    mcp.run()
