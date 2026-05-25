import json

import requests
import sys
from pathlib import Path

# 添加 logger 和 config 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from logger import log, info, warning, error, debug
from config import APP_NO, CONFIG, get_auth_tokens


def load_and_submit_sop():
    """
    读取 output/sop.json 文件并提交到 batch_add_nodes_and_edges
    """
    try:
        sop_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "output" / "sop.json"

        if not sop_path.exists():
            return f"文件不存在: {sop_path}"

        with open(sop_path, 'r', encoding='utf-8') as f:
            stage3_data = json.load(f)

        info(f"成功读取 sop.json，开始提交...")

        result = batch_add_nodes_and_edges(bizSop=stage3_data)
        return result

    except json.JSONDecodeError as e:
        return f"JSON 解析错误: {str(e)}"
    except Exception as e:
        return f"处理失败，错误: {str(e)}"

def batch_add_nodes_and_edges(
        bizSop: dict

) -> str:
    """
#     批量向 应用配置 文件中添加节点和边。
#     先添加节点，再添加边。会检查ID唯一性和节点存在性。
#     """
    try:
        request_data = {
            "appNo": APP_NO,
            "bizSop": bizSop
        }
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/save',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        info(f"提交SOP数据入参: {request_data}")
        response_data = response.json()
        info(f"提交SOP数据成功: {response_data}")
        if response_data.get("resultCode", "") != 0:
            raise Exception(response_data.get("message", "未知错误"))
        info(f"批量增加数据成功：{response_data['resultMessage']}")
        return "批量增加数据成功"
    except Exception as e:
        return f"批量添加失败，错误：{str(e)}"

if __name__ == "__main__":
    print(load_and_submit_sop())