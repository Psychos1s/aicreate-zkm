"""读取约束应用的 stage1.md 内容，输出给 Claude Code 使用"""
import sys
from pathlib import Path

# 添加 logger 和 config 模块路径
if (common_dir := Path(__file__).resolve().parent.parent.parent.parent / "common") not in sys.path:
    sys.path.insert(0, str(common_dir))

from logger import log, info, error
from config import CONFIG, get_app_config_field

import requests


def download_stage1_content() -> str:
    """从 OSS 下载约束应用的 stage1.md 内容"""
    constraint_app_no = get_app_config_field("constraintAppNo")
    if not constraint_app_no:
        error("constraintAppNo 为空，无法读取基础模型")
        return ""

    file_url = f"{CONFIG['oss_url']}/{constraint_app_no}/output/stage1.md"
    info(f"开始下载基础模型: {file_url}")

    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        error(f"下载基础模型失败: {str(e)}")
        return ""


if __name__ == "__main__":
    content = download_stage1_content()
    print(content)
