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

# 加载 SDK 配置
sdk_config_path = Path(__file__).resolve().parent.parent.parent.parent / "mcp" / "oneui" / "sdk_config.json"
with open(sdk_config_path, 'r', encoding='utf-8') as f:
    SDK_CONFIG = json.load(f)
def _success_response(model_paper_id: str, meta_model_id: str, message: str) -> dict:
    return {"success": True, "modelPaperId": model_paper_id, "metaPaperId": meta_model_id, "message": message}

def _error_response(message: str) -> dict:
    return {"success": False, "message": message}

def copyModel():
    """
    根据模型id复制模型
    """
    config = read_app_config()
    info(f"当前应用配置：{config}")

    constraint_app_no = config["constraintAppNo"]

    if not constraint_app_no:
        error("constraint_app_no为空，复制模型失败")
        return _error_response("constraint_app_no为空")

    stage2_file_url = f"{CONFIG['oss_url']}/{constraint_app_no}/output/stage2.md"
    ability_file_url = f"{CONFIG['oss_url']}/{constraint_app_no}/output/能力模型.md"
    business_file_url = f"{CONFIG['oss_url']}/{constraint_app_no}/output/业务模型.md"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    output_dir = os.path.join(project_root, "output")
    stage2_path = os.path.join(output_dir, "stage2.md")

    if os.path.exists(stage2_path):
        info(f"文件 {stage2_path} 已存在, 直接查询模型")
        model_conf = queryCopyModel()
        meta_model_id = model_conf.get("metaModelPaperId", "")
        domain_model_id = model_conf.get("modelPaperId", "")
        return _success_response(domain_model_id, meta_model_id,
                                 f"约束模型已生成，领域元模型ID：{meta_model_id}，领域本体图ID：{domain_model_id}")

    output_path = download_file_from_url(stage2_file_url, output_dir)
    if not output_path:
        error(f"下载文件失败，重试{business_file_url}")
        output_path = download_file_from_url(business_file_url, output_dir)
        if not output_path:
            error(f"下载文件失败，重试{ability_file_url}")
            output_path = download_file_from_url(ability_file_url, output_dir)
            if not output_path:
                return _error_response(f"业务模型失败，请检查文件路径：{ability_file_url}")

    info(f"复制业务模型成功，保存路径：{output_path}")

    meta_model_id = copy_constraint_model(constraint_app_no)

    # 生成领域本体
    domain_model_id = ""
    if meta_model_id:
        domain_model_id = generate_domain_ont(meta_model_id)
    else:
        error("生成领域本体失败")
        return _error_response("生成领域元模型失败")

    return _success_response(domain_model_id, meta_model_id, f"约束模型已生成，领域元模型ID：{meta_model_id}，领域本体图ID：{domain_model_id}")

def copy_constraint_model(
        constraint_model: str) -> str:

    try:
        auth_tokens = get_auth_tokens()
        request_data = {
            "appNo": constraint_model
        }
        info(f"copy_constraint_model，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/domain-meta/copy',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
                **auth_tokens
            }
        )
        response_data = response.json()
        info(f"copy_constraint_model，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            error(f"复制失败: {response_data.get('message', '未知错误')}")
            return ""
        data = response_data['data']
        info(f"复制成功，生成领域元模型，id：{data}")
        return data
    except Exception as e:
        error(f"复制异常，错误：{str(e)}")
        return ""

def generate_domain_ont(
        domain_model: str) -> str:

    try:
        # 获取认证 token
        auth_tokens = get_auth_tokens()
        request_data = {
            "paperId": domain_model,
            "appNo": APP_NO
        }
        info(f"generate_domain_ont，请求入参：{request_data}")
        response = requests.post(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/domain-ont/generation/V2',
            #url=f'http://localhost:12880/domain-ont/generation',
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "x-gw-accesskey": CONFIG["access_key"],
                **auth_tokens
            }
        )
        response_data = response.json()
        info(f"generate_domain_ont，返回结果：{response_data}")
        if response_data.get("resultCode", "") != 0:
            error(f"generate_domain_ont失败: {response_data.get('message', '未知错误')}")
            return ""
        real_data = response_data['data']
        info(f"生成领域本体图，ID：{real_data['paperId']}")
        return real_data['paperId']
    except Exception as e:
        error(f"generate_domain_ont异常，错误：{str(e)}")
        return ""

def read_app_config(config_path: str = ".app_config.json") -> dict:
    """
    从 .app_config.json 读取配置信息

    Args:
        config_path: 配置文件路径，默认为 .app_config.json

    Returns:
        包含配置信息的字典
    """
    # 获取项目根目录（从脚本位置向上查找3级）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    full_path = os.path.join(project_root, config_path)

    with open(full_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    ability_model_id = config.get("abilityModelId", "")
    constraint_app_no = config.get("constraintAppNo", "")

    return {
        "abilityModelId": ability_model_id,
        "constraintAppNo": constraint_app_no
    }
def download_file_from_url(file_url: str, output_path: str) -> str:
    """
    从文件URL下载附件并保存到指定路径

    Args:
        file_url: 文件的URL地址
        output_path: 保存文件的路径，默认为 output/stage2.md

    Returns:
        保存的文件路径
    """
    # 创建输出目录
    if output_path and not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    # 下载文件
    try:
        info(f"开始下载文件: {file_url}")
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        # 保存文件
        save_path = os.path.join(output_path, "stage2.md")
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        info(f"文件已下载到: {save_path}")
        return save_path
    except Exception as e:
        error(f"下载异常，错误：{str(e)}")
        return ""

def _sdk_error_response(code: str, message: str, **details) -> dict:
    """构建 SDK 调用错误响应"""
    err = {"code": code, "message": message}
    if details:
        err["details"] = details
    return {"success": False, "error": err}

HEADERS = {"Content-Type": "application/json"}
def queryCopyModel() -> dict:
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
            return _error_response(f"查询模型失败: {res.get('message', '未知错误')}")

        data = res.get("data", {})
        if not data:
            return _error_response(f"查询成功，但未找到模型数据 (APP_NO: {APP_NO})")

        metaModelPaperId = data.get("metaModelPaperId", "")
        modelPaperId = data.get("modelPaperId", "")

        if not modelPaperId:
            return _error_response( "业务模型未生成")

        result_json = {
            "metaModelPaperId":{metaModelPaperId},
            "modelPaperId":{modelPaperId}
        }

        return result_json

    except Exception as e:
        error(f"查询模型失败，APP_NO：{APP_NO}，错误：{str(e)}")
        return _error_response(f"查询模型失败，错误：{str(e)}")

if __name__ == "__main__":
    result = copyModel()
    print(result)
    info(f"{result}")


