# 调用约束元模型接口，保存数据
import os
import requests
from pathlib import Path
import json
import sys
from typing import Dict, Any
# 添加 logger 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

# 导入 model.py 中的 fetch_ability_model_id
if (model_dir := Path(__file__).resolve().parent.parent.parent.parent / "mcp") not in sys.path:
    sys.path.insert(0, str(model_dir))

from logger import log, info, warning, error, debug
from config import APP_NO, CONFIG, get_auth_tokens,ENV

# 固定请求头
HEADERS = {"Content-Type": "application/json"}
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

def fetch_ability_model_id(appNo: str):
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
        info(f"返回参数:{res}")

        if res.get("resultCode") == 0:
            return res.get("data", {}).get("paperId")
    except Exception as e:
        error(f"获取paperId异常: {str(e)}")
    return None

def update_or_save_constraint_model(
        nodeList,
        edgeList) -> Dict[str, Any]:
    """
    增量更新业务约束模型。
    nodeList 包含三种节点类型：数据对象（ac_model）、业务逻辑（logic_ontology）、执行本体（execution_ontology），每种类型的内部字段结构不同。
    edgeList 包含数据对象间的关系边、数据对象与业务逻辑之间的关联边、业务逻辑与执行本体之间的关联边。
    paperId 通过 APP_NO 调用 fetch_ability_model_id 自动获取结果中的paperId。
    """
    try:
        # 入参校验
        if not nodeList or not edgeList:
            return {"success": False, "message": "❌ 参数错误：nodeList和edgeList 不能为空"}

        # 校验 ac_model 节点：至少有一个属性，且每个属性的 name 不能为空
        for node in nodeList:
            if node.get("nodeType") == "ac_model":
                fields = node.get("model", {}).get("fields", [])
                if not fields:
                    return {"success": False, "message": f"❌ 参数错误：节点 {node.get('nodeId')}（{node.get('nodeName')}）至少需要一个属性，不能为空"}
                for i, field in enumerate(fields):
                    if not field.get("name", "").strip():
                        return {"success": False, "message": f"❌ 参数错误：节点 {node.get('nodeId')}（{node.get('nodeName')}）的第 {i + 1} 个属性名称不能为空"}

        # 构建 nodeId -> nodeType 映射
        node_type_map = {node["nodeId"]: node["nodeType"] for node in nodeList}

        # 校验边：relationName 规则
        for edge in edgeList:
            src = edge.get("sourceNodeId")
            tgt = edge.get("targetNodeId")
            src_type = node_type_map.get(src, "")
            tgt_type = node_type_map.get(tgt, "")
            relation_name = edge.get("relationName", "")

            if src_type == "ac_model" and tgt_type == "ac_model":
                if not relation_name:
                    return {"success": False, "message": f"❌ 参数错误：对象节点 {src} 指向对象节点 {tgt} 的边必须填写 relationName"}
            else:
                if relation_name:
                    return {"success": False, "message": f"❌ 参数错误：{src} -> {tgt} 的边 relationName 必须为空字符串"}

        # 自动获取图纸ID
        paperId = fetch_ability_model_id(APP_NO)
        if not paperId:
            return {"success": False, "message": "❌ 未获取到图纸ID，请检查 APP_NO 对应的业务模型配置"}

        # 构造请求体
        payload = {
            "paperId": paperId,
            "nodeList": nodeList,
            "edgeList": edgeList
        }
        info(f"update_or_save_constraint_model 请求参数：{payload}")
        # 环境配置
        INSIDE_CONFIG = INSIDE_ENV_CONFIG.get(ENV, INSIDE_ENV_CONFIG["fat"])
        auth_tokens = get_auth_tokens()
        access_key = INSIDE_CONFIG.get("access_key", "")

        headers = {
            **HEADERS,
            "x-gw-accesskey": access_key,
            **auth_tokens
        }

        # 发送请求
        response = requests.post(
            url=f"{INSIDE_CONFIG['gateway_url']}/dt-ontology-modeling/api/paper/abilityConstraint/saveOrUpdate",
            json=payload,
            headers=headers
        )

        res = response.json()
        info(f"update_or_save_constraint_model 返回参数：{res}")
        success = res.get("success", False)
        message = res.get("message", "操作完成")

        if success:
            # 生成领域本体
            modelPaperId = generate_domain_ont(paperId)
            info(f"generate_domain_ont 返回：paperId={paperId}，modelPaperId={modelPaperId}")
            return {
                "success": True,
                "modelPaperId": modelPaperId,
                "metaPaperId": paperId,
                "message": "增量更新业务模型成功"
            }
        else:
            return {"success": False, "message": f"更新失败：{message}"}

    except Exception as e:
        error(f"请求异常: {str(e)}")
        return {"success": False, "message": f"请求异常：{str(e)}"}


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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "message": "请传入 JSON 参数，例如：python addModel.py '{\"nodeList\":[...],\"edgeList\":[...]}'"}, ensure_ascii=False))
        error("请传入 JSON 参数，例如：python addModel.py '{\"nodeList\":[...],\"edgeList\":[...]}'")
        sys.exit(1)

    data = json.loads(sys.argv[1])
    nodeList = data.get("nodeList")
    edgeList = data.get("edgeList")
    result = update_or_save_constraint_model(nodeList, edgeList)
    info(f"约束元模型更新结果：{result}")
    # 输出 JSON 到标准输出，供调用方解析
    print(json.dumps(result, ensure_ascii=False))
