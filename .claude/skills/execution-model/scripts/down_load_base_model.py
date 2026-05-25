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
def down_load_base_model():
    """
    下载基础模型
    """
    config = read_app_config()
    info(f"当前应用配置：{config}")
    constraint_app_no = config["constraintAppNo"]
    xu_zhi = config['modelType']

    if not constraint_app_no:
        error("constraint_app_no为空")
        return "constraint_app_no为空"

    output_name = 'base_stage3.md'

    stage3_file_url = f"{CONFIG['oss_url']}/{constraint_app_no}/output/stage3.md"
    #stage3_file_url = "https://vlm-temp-storage.obsv3.cn-lflt-1.enncloud.cn/claude-workspace-uat/sop_46e06db8b95242829897b9acad0c31d4/output/stage3.md"
    output_path = download_file_from_url(stage3_file_url, output_name)
    if not output_path:
        error(f"下载基础模型失败，请检查文件路径：{stage3_file_url}")
        return f"下载基础模型失败，请检查文件路径：{stage3_file_url}"

    info(f"下载基础模型成功，保存路径：{output_path}")
    return f"下载基础模型成功，保存路径：{output_path}"


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

    constraint_app_no = config.get("constraintAppNo", "")
    model_type = config.get("modelType", "")

    return {
        "constraintAppNo": constraint_app_no,
        "modelType": model_type
    }
def download_file_from_url(file_url: str, output_name: str, output_path: str = "output") -> str:
    """
    从文件URL下载附件并保存到指定路径

    Args:
        file_url: 文件的URL地址
        output_path: 保存文件的路径，默认为 output/stage2.md

    Returns:
        保存的文件路径
    """
    # 创建输出目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    output_dir = os.path.join(project_root, output_path)

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 下载文件
    try:
        info(f"开始下载文件: {file_url}")
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        # 保存文件
        save_path = os.path.join(output_dir, output_name)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        info(f"文件已下载到: {save_path}")
        return save_path
    except Exception as e:
        error(f"下载异常，错误：{str(e)}")
        return ""

if __name__ == "__main__":
    result = down_load_base_model()
    print(result)
    info(f"{result}")


