import json
import sys

import requests

import os
from pathlib import Path

# 添加 logger 模块路径
if (logger_dir := Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(logger_dir))

from logger import log, info, warning, error, debug
from config import APP_NO, CONFIG, get_auth_tokens


def read_progress_file() -> str:
    """读取项目目录下的当前进度.md文件"""
    project_root = Path(__file__).resolve().parent.parent.parent
    progress_path = project_root / "当前进度.md"
    if progress_path.exists():
        return progress_path.read_text(encoding="utf-8")
    return ""


def read_appConfig_file() -> str:
    """读取项目目录下的.app_config.json文件"""
    project_root = Path(__file__).resolve().parent.parent.parent
    config_path = project_root / ".app_config.json"
    if config_path.exists():
        return config_path.read_text(encoding="utf-8")
    return ""


def getConstraintAppName(appNo: str = None) -> str:
    """根据应用编号查询继承的基础模型名称。
    """
    try:
        auth_tokens = get_auth_tokens()
        access_key = CONFIG.get("access_key", "")
        headers = {
            "x-gw-accesskey": access_key,
            **auth_tokens
        }

        response = requests.get(
            url=f'{CONFIG["gateway_url"]}/ioc-workbench/api/ioc-workbench/v1/app/bot/get/platform/{appNo}',
            headers=headers
        )
        res = response.json()

        if res.get("resultCode") != 0:
            return f"查询模型失败: {res.get('message', '未知错误')}"

        appName = res.get("data").get("appName", "")

        info(f"继承应用appNo：{appNo}, appName：{appName}")

        return appName

    except Exception as e:
        error(f"查询基础模型失败，APP_NO：{appNo}，错误：{str(e)}")
        return f"查询基础模型失败，错误：{str(e)}"

if __name__ == "__main__":
    data = json.load(sys.stdin)
    info("==============UserSession入参为============")
    info(str(data))

    # 读取当前进度.md，作为后续内容的参考
    progress_content = read_progress_file()
    if progress_content:
        info("==============当前进度============")
        info(progress_content)
        print("当前应用appNo是" + APP_NO)
        print("\n--- 当前进度 ---\n" + progress_content + "\n--- 结束 ---\n")

    config_content = read_appConfig_file()
    if config_content:
        app_config = json.loads(config_content)
        info(app_config)
        constraintAppNo = app_config.get("constraintAppNo", "")
        if constraintAppNo:
            print("是否基于基础模型：是")
            constraintAppName = getConstraintAppName(constraintAppNo)
            print("基础模型名称：" + constraintAppName)
            app_config["是否基于基础模型"] = "是"
            app_config["基础模型名称"] = constraintAppName
        else:
            print("是否基于基础模型：否")
            app_config["是否基于基础模型"] = "否"

        # 写回配置文件
        config_path = Path(__file__).resolve().parent.parent.parent / ".app_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(app_config, f, ensure_ascii=False, indent=4)
        info(f"已更新配置文件: isBasedOnBaseModel={app_config['isBasedOnBaseModel']}, baseModelName={app_config.get('baseModelName', '')}")
