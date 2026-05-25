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
from config import APP_NO, CONFIG

# 初始化 FastMCP 服务
mcp = FastMCP("SOP Tools")

# 获取项目根目录的绝对路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 固定的 business.json 路径(项目相对路径)
BUSINESS_JSON_PATH = os.path.join(PROJECT_ROOT, "business.json")

@mcp.tool()
def addNode(
        node: Annotated[
            Dict[str, Any],
            Field(
                description="要添加的节点数据，包含 id、type、name、desc、input、output、businessLogics、completeCondition 等字段。",
                examples=[{
                    "id": "N3",
                    "type": "task",
                    "name": "数据计算",
                    "desc": "对收集到的蒸汽数据进行汇总计算，得到最终用能量",
                    "input": {
                        "desc": "需输入企业蒸汽数据（达产年、已投产年、新增投产年用能量）"
                    },
                    "output": {
                        "desc": "输出汇总后的企业总用能量，用于后续流程判断"
                    },
                    "businessLogics": "优先获取并处理蒸汽数据，首先尝试获取企业的蒸汽数据。达产年用能量+已投产年用能量+新增投产年用能量，计算完成后，直接跳转至最终输出步骤。",
                    "completeCondition": {
                        "businessRule": "建筑设计使用年限一般为50年左右，根据联网信息和一般核查标准进行输出"
                    },
                    "gatewayRules": [{
                        "conditions": [{
                            "objectCode": "leaveObject(请假对象)",
                            "fieldCode": "leaveDay(请假天数字段)",
                            "fieldType": "Int",
                            "value": 3,
                            "operator": "lessOrEqual"
                        }],
                        "targetNodeId": "N3"
                    }, {
                        "conditions": [{
                            "objectCode": "leaveObject(请假对象)",
                            "fieldCode": "leaveDay(请假天数字段)",
                            "fieldType": "Int"
                        }],
                        "targetNodeId": "N4"
                    }]
                }]
            )
        ]
) -> str:
    """
    向 应用配置 中添加新的流程节点。
    节点ID需唯一，type 可选值为：start、task、gateway、end。
    """
    try:
        request_data = {
            "appNo": APP_NO,
            "bizSopNode": node
        }
        info(f"新增节点，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/addSopNode',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"新增节点，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"添加节点失败: {response_data.get('resultMessage', '未知错误')}"
        return f"节点数据添加成功：{node['name']}"
    except Exception as e:
        error(f"节点添加失败，错误：{str(e)}")
        return f"节点添加失败，错误：{str(e)}"


@mcp.tool()
def updateNode(
        nodeId: Annotated[
            str,
            Field(
                description="要更新的节点ID（例如：N1）。"
            )
        ],
        updateParams: Annotated[
            Dict[str, Any],
            Field(
                description="要更新的节点参数，可包含 name、desc、input、output、businessLogics、completeCondition 等字段。",
                examples=[{
                    "id": "N1",
                    "name": "蒸汽数据收集",
                    "desc": "专门收集企业蒸汽相关数据，为后续计算提供基础",
                    "input": "客户行业、客户基本信息、企业战略、类本体、数据生成模型、相似企业初步信息表",
                    "output": "按基本信息、经营特征、决策链特征、行为偏好特征、需求诊断条件等维度构建的结构化画像",
                    "businessLogics": "优先获取企业蒸汽数据，若蒸汽数据缺失，则提示补充，不进行后续计算",
                    "completeCondition": " 客户画像已生成，结构完整"
                }]
            )
        ]
) -> str:
    """
    更新 应用配置 中指定节点的属性。
    不允许修改节点的 id 字段。
    """
    try:
        request_data = {
            "appNo": APP_NO,
            "nodeId": nodeId,
            "bizSopNode": updateParams
        }
        info(f"更新节点，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/updateSopNode',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"更新节点，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"修改节点失败: {response_data.get('resultMessage', '未知错误')}"
        return f"节点修改成功：{nodeId}"
    except Exception as e:
        error(f"节点更新失败，错误：{str(e)}")
        return f"节点更新失败，错误：{str(e)}"


@mcp.tool()
def deleteNode(
        nodeId: Annotated[
            str,
            Field(
                description="要删除的节点ID（例如：N1）。"
            )
        ]
) -> str:
    """
    从 应用配置 中删除指定的节点。
    """
    try:
        request_data = {
            "appNo": APP_NO,
            "nodeId": nodeId
        }
        info(f"删除节点，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/deleteSopNode',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"删除节点，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"节点删除失败: {response_data.get('resultMessage', '未知错误')}"
        return f"节点删除成功：{nodeId}"
    except Exception as e:
        error(f"节点删除失败，错误：{str(e)}")
        return f"节点删除失败，错误：{str(e)}"


@mcp.tool()
def addEdge(
        edge: Annotated[
            Dict[str, str],
            Field(
                description="要添加的边数据，包含 source 和 target 字段。",
                examples=[{
                    "source": "N1",
                    "target": "N3"
                }]
            )
        ]
) -> str:
    """
    向 应用配置 中添加新的边（连接关系）。
    会检查边是否已存在。
    """
    try:
        request_data = {
            "appNo": APP_NO,
            "bizSopEdge": edge
        }
        info(f"新增边，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/addSopEdge',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"新增边，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"增加边失败: {response_data.get('resultMessage', '未知错误')}"
        return f"增加边数据成功"
    except Exception as e:
        error(f"边添加失败，错误：{str(e)}")
        return f"边添加失败，错误：{str(e)}"


@mcp.tool()
def deleteEdge(
        source: Annotated[
            str,
            Field(
                description="源节点ID。"
            )
        ],
        target: Annotated[
            str,
            Field(
                description="目标节点ID。"
            )
        ]
) -> str:
    """
    从 应用配置 中删除指定的边（连接关系）。
    """
    try:
        request_data = {
            "appNo": APP_NO,
            "bizSopEdge": {"source": source, "target": target}
        }
        info(f"删除边，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/deleteSopEdge',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"删除边，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"删除边失败: {response_data.get('resultMessage', '未知错误')}"
        return f"删除边数据成功"
    except Exception as e:
        error(f"边删除失败，错误：{str(e)}")
        return f"边删除失败，错误：{str(e)}"

@mcp.tool()
def swapNode(
        sourceNodeId: Annotated[
            str,
            Field(
                description="要交换的源节点ID（例如：N1）。"
            )
        ],
        targetNodeId: Annotated[
            str,
            Field(
                description="要交换的目标节点ID（例如：N2）。"
            )
        ]
) -> str:
    """
    交换两个节点的位置。
    """
    try:
        request_data = {
            "appNo": APP_NO,
            "sourceNodeId": sourceNodeId,
            "targetNodeId": targetNodeId
        }
        info(f"交换节点，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/exchangeSopNode',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"交换节点，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            return f"交换节点失败: {response_data.get('message', '未知错误')}"
        return f"交换节点成功"
    except Exception as e:
        error(f"交换节点失败，错误：{str(e)}")
        return f"交换节点失败，错误：{str(e)}"

# @mcp.tool()
# def querySOP():
#     """
#     查询sop数据
#     """
#     try:
#         request_data = {
#             "appNo": APP_NO,
#         }
#         info(f"查询 SOP，请求入参：{request_data}")
#         response = requests.post(
#             url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/querySop',
#             json=request_data,
#             headers={
#                 "Content-Type": "application/json",
#                 "x-gw-accesskey": CONFIG["access_key"],
#             }
#         )
#         response_data = response.json()
#         info(f"查询 SOP，返回结果：{response_data}")
#         if response_data.get("resultCode", "") != 0:
#             raise Exception(response_data.get("message", "未知错误"))
#         return response_data['data']
#     except Exception as e:
#         error(f"查询失败，错误：{str(e)}")

@mcp.tool()
def removeAll() -> str:
    """
    清空 应用配置 的所有节点和边数据。
    有且仅在重新生成流程时调用，会删除所有现有节点和连线，不可恢复。
    """
    try:
        request_data = {
            "appNo": APP_NO,
        }
        info(f"清空SOP，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/initSop',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
            }
        )
        response_data = response.json()
        info(f"清空SOP，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            raise Exception(response_data.get("resultMessage", "未知错误"))
        return "SOP 数据已清空"
    except Exception as e:
        error(f"清空 SOP 失败，错误：{str(e)}")
        return f"清空 SOP 失败，错误：{str(e)}"


# @mcp.tool()
# def batchAddNodesAndEdges(
#         nodes: Annotated[
#             List[Dict[str, Any]],
#             Field(description="要批量添加的节点列表")
#         ] = [],
#         edges: Annotated[
#             List[Dict[str, str]],
#             Field(description="要批量添加的边列表")
#         ] = []
# ) -> str:
#     """
#     批量向 应用配置 文件中添加节点和边。
#     先添加节点，再添加边。会检查ID唯一性和节点存在性。
#     """
#     try:
#         request_data = {
#             "appNo": APP_NO,
#             "bizSop": {"nodes": nodes, "edges": edges}
#         }
#         response = requests.post(
#             url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/sop/batchAddSopNodesAndEdges',
#             json=request_data,
#             headers={
#                 "Content-Type": "application/json",
#                 "x-gw-accesskey": CONFIG["access_key"],
#             }
#         )
#         response_data = response.json()
#         print(f"提交数据成功: {response_data}")
#         if response_data.get("resultCode", "") != 0:
#             raise Exception(response_data.get("message", "未知错误"))
#         print(f"批量增加数据成功：{response_data['resultMessage']}")
#     except Exception as e:
#         return f"批量添加失败，错误：{str(e)}"

# 测试函数
def test():
    """测试 addNode 接口"""
    test_data = {
        "appNo": "sop_a5190666184849b7959d520712294456",
        "bizSopNode": {
            "type": "start",
            "name": "开始",
            "id": "N0"
        }
    }
    removeAll()

if __name__ == "__main__":
    # test()
    mcp.run()