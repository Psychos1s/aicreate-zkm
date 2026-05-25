import os
import requests
from pathlib import Path
import json
import sys
# 添加 logger 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from logger import log, info, warning, error, debug
from config import APP_NO, CONFIG, get_auth_tokens
def save_stage2_mode(mode: str) -> str:
    info(f'三阶段保存模式：{mode}')
    try:
        request_data = {
            "appNo": APP_NO,
            "mode": mode
        }
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/saveStage3Mode',
            #url='http://localhost:12880/api/ioc-workbench/v1/app/sop/saveStage3Mode',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        info(f"提交saveStage3Mode数据入参: {request_data}")
        response_data = response.json()
        info(f"提交saveStage3ModeP数据成功: {response_data}")
        if response_data.get("resultCode", "") != 0:
            raise Exception(response_data.get("message", "未知错误"))
        info(f"saveStage3Mode数据成功：{response_data['resultMessage']}")
        return "保存数据成功"
    except Exception as e:
        return f"保存数据失败，错误：{str(e)}"

if __name__ == "__main__":
    result = save_stage2_mode(sys.argv[1])
    print(result)
    info(f"{result}")