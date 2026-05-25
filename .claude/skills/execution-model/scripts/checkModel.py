import requests
import sys
from pathlib import Path

# 添加 logger 和 config 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from logger import log, info, warning, error, debug
from config import APP_NO, CONFIG, get_auth_tokens

HEADERS = {"Content-Type": "application/json"}


def checkModel() -> str:
    """
    根据当前项目的 APP_NO 查询应用配置模型数据。
    """
    try:
        auth_tokens = get_auth_tokens()
        access_key = CONFIG.get("access_key", "")
        headers = {
            **HEADERS,
            "x-gw-accesskey": access_key,
            **auth_tokens
        }

        info(f"checkModel 请求 APP_NO：{APP_NO}")

        response = requests.get(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/bot/get/{APP_NO}',
            headers=headers
        )
        res = response.json()
        info(f"checkModel 返回：{res}")

        if res.get("resultCode") != 0:
            return f"查询模型失败: {res.get('message', '未知错误')}"

        data = res.get("data", {})
        if not data:
            return f"查询成功，但未找到模型数据 (APP_NO: {APP_NO})"

        metaModelPaperId = data.get("metaModelPaperId", "")
        modelPaperId = data.get("modelPaperId", "")

        if not modelPaperId:
            return "业务模型未生成"

        result_lines = [
            f"领域元模型ID ：{metaModelPaperId}",
            f"领域本体图ID ：{modelPaperId}",
        ]

        return "\n".join(result_lines)

    except Exception as e:
        error(f"查询模型失败，APP_NO：{APP_NO}，错误：{str(e)}")
        return f"查询模型失败，错误：{str(e)}"


if __name__ == "__main__":
    result = checkModel()
    print(result)
