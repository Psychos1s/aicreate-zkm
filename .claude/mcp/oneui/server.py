import json
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import Field

# 初始化 FastMCP 服务
mcp = FastMCP("OneUI")

# 加载卡片配置
config_path = Path(__file__).parent / "cards_config.json"
with open(config_path, 'r', encoding='utf-8') as f:
    CARDS_CONFIG = json.load(f)

# 加载 SDK 配置
sdk_config_path = Path(__file__).parent / "sdk_config.json"
with open(sdk_config_path, 'r', encoding='utf-8') as f:
    SDK_CONFIG = json.load(f)


def _error_response(code: str, message: str, **details) -> str:
    """构建统一错误响应"""
    error = {"code": code, "message": f"{message}，请重新识别准确的参数格式，然后再使用本工具"}
    if details:
        error["details"] = details
    return json.dumps({"error": error}, ensure_ascii=False, indent=2)


def _validate_dynamic_form_schema(args: Dict[str, Any], context: str = "") -> Optional[str]:
    """校验 DynamicForm 的 formSchema 字段结构"""
    prefix = f"{context} " if context else ""
    form_schema = args.get("formSchema")

    if not isinstance(form_schema, list):
        return _error_response(
            "INVALID_FORM_SCHEMA",
            f"{prefix}DynamicForm 的 formSchema 必须是数组"
        )

    if not form_schema:
        return _error_response(
            "EMPTY_FORM_SCHEMA",
            f"{prefix}DynamicForm 的 formSchema 不能为空数组"
        )

    field_config = CARDS_CONFIG["cards"]["DynamicForm"].get("field_schema", {})
    forbidden_props = field_config.get("forbidden_field_props", {})
    supported_types = field_config.get("supported_types", [])

    for i, field in enumerate(form_schema):
        if not isinstance(field, dict):
            return _error_response(
                "INVALID_FIELD",
                f"{prefix}formSchema[{i}] 必须是对象"
            )

        # 检查禁止字段
        for prop, reason in forbidden_props.items():
            if prop in field:
                return _error_response(
                    "FORBIDDEN_FIELD_PROP",
                    f"{prefix}formSchema[{i}] 使用了禁止的属性 '{prop}'",
                    field_index=i,
                    field_key=field.get("key", "unknown"),
                    reason=reason
                )

        # 检查必需字段属性
        if not field.get("label"):
            return _error_response(
                "MISSING_FIELD_LABEL",
                f"{prefix}formSchema[{i}] 缺少 label 属性（字段显示名称）",
                field_index=i,
                hint="使用 label 而不是 title"
            )

        if not field.get("key"):
            return _error_response(
                "MISSING_FIELD_KEY",
                f"{prefix}formSchema[{i}] 缺少 key 属性（字段唯一标识）",
                field_index=i
            )

        field_type = field.get("type")
        if not field_type:
            return _error_response(
                "MISSING_FIELD_TYPE",
                f"{prefix}formSchema[{i}] 缺少 type 属性",
                field_index=i
            )

        if supported_types and field_type not in supported_types:
            return _error_response(
                "UNSUPPORTED_FIELD_TYPE",
                f"{prefix}formSchema[{i}] type='{field_type}' 不支持",
                field_index=i,
                supported_types=supported_types
            )

        # select/multi-select 必须用 dataSource
        if field_type in ("select", "multi-select"):
            if "enum" in field or "enumNames" in field:
                return _error_response(
                    "FORBIDDEN_FIELD_PROP",
                    f"{prefix}formSchema[{i}] select 类型禁止使用 enum/enumNames，必须用 dataSource: [{{label, value}}]",
                    field_index=i,
                    field_key=field.get("key", "unknown")
                )
            data_source = field.get("dataSource")
            if not data_source or not isinstance(data_source, list):
                return _error_response(
                    "MISSING_DATA_SOURCE",
                    f"{prefix}formSchema[{i}] select/multi-select 类型必须提供 dataSource 数组",
                    field_index=i,
                    field_key=field.get("key", "unknown"),
                    hint="dataSource 格式: [{\"label\": \"显示名\", \"value\": \"值\"}]"
                )
            # 检查 dataSource 中 value 是否有重复
            values = [item.get("value") for item in data_source if isinstance(item, dict)]
            duplicates = [v for v in set(values) if values.count(v) > 1]
            if duplicates:
                return _error_response(
                    "DUPLICATE_DATA_SOURCE_VALUE",
                    f"{prefix}formSchema[{i}] dataSource 中存在重复的 value: {', '.join(str(d) for d in duplicates)}",
                    field_index=i,
                    field_key=field.get("key", "unknown"),
                    duplicates=duplicates
                )

    return None


def _validate_card_args(code: str, args: Dict[str, Any], context: str = "") -> Optional[str]:
    """校验内置卡片的 args，返回错误响应字符串或 None（通过）"""
    if code not in CARDS_CONFIG["cards"]:
        return None

    card_config = CARDS_CONFIG["cards"][code]
    prefix = f"{context} " if context else ""

    # 检查 forbidden_args
    forbidden = card_config.get("forbidden_args", {})
    if isinstance(forbidden, (dict, list)):
        violated = [k for k in (forbidden if isinstance(forbidden, list) else forbidden.keys()) if k in args]
    else:
        violated = []

    if violated:
        hints = []
        for k in violated:
            reason = forbidden[k] if isinstance(forbidden, dict) else f"参数 '{k}' 被禁止使用"
            hints.append(f"  - {k}: {reason}")
        required = card_config.get("required_args", {})
        required_keys = ", ".join(required.keys()) if isinstance(required, dict) else str(required)
        return _error_response(
            "FORBIDDEN_ARGS",
            f"{prefix}卡片 {code} 包含被禁止的参数: {', '.join(violated)}",
            violated_args=violated,
            hints=hints,
            correct_usage=f"请使用以下字段: {required_keys}"
        )

    # 检查 required_args
    required = card_config.get("required_args", {})
    if isinstance(required, dict):
        missing_required = [k for k in required if k not in args]
        if missing_required:
            return _error_response(
                "MISSING_REQUIRED_ARGS",
                f"{prefix}卡片 {code} 缺少必需参数: {', '.join(missing_required)}",
                missing_args=missing_required,
                required_args=required
            )

    # DynamicForm 额外校验 formSchema 结构
    if code == "DynamicForm":
        schema_error = _validate_dynamic_form_schema(args, context)
        if schema_error:
            return schema_error

    return None


def _build_args_description() -> str:
    """从 cards_config.json 动态生成 args 参数说明"""
    lines = ["卡片参数 (JSON 对象)\n"]
    for code, cfg in CARDS_CONFIG.get("cards", {}).items():
        lines.append(f"## {code} (version: {cfg.get('version', '0.x')})")
        if cfg.get("description"):
            lines.append(cfg["description"])
        required = cfg.get("required_args", {})
        if isinstance(required, dict) and required:
            lines.append("必需参数:")
            for k, v in required.items():
                lines.append(f"  - {k}: {v}")
        optional = cfg.get("optional_args", {})
        if isinstance(optional, dict) and optional:
            lines.append("可选参数:")
            for k, v in optional.items():
                lines.append(f"  - {k}: {v}")
        forbidden = cfg.get("forbidden_args", {})
        if isinstance(forbidden, dict) and forbidden:
            lines.append("禁止使用的参数:")
            for k, v in forbidden.items():
                lines.append(f"  - {k}: {v}")
        # DynamicForm 的字段规范
        field_schema = cfg.get("field_schema", {})
        if field_schema:
            lines.append("formSchema 字段规范:")
            forbidden_props = field_schema.get("forbidden_field_props", {})
            if forbidden_props:
                lines.append("  禁止的字段属性:")
                for k, v in forbidden_props.items():
                    lines.append(f"    - {k}: {v}")
            supported = field_schema.get("supported_types", [])
            if supported:
                lines.append(f"  支持的字段类型: {', '.join(supported)}")
        lines.append("")
    lines.append("自定义卡片: code 为任意自定义值, args 直接透传")
    return "\n".join(lines)


ARGS_DESCRIPTION = _build_args_description()


@mcp.prompt()
def card_selection_guide() -> str:
    """
    卡片选择指南 - 帮助 AI 智能选择和使用卡片

    当用户需要收集信息或展示交互界面时,请参考此指南
    """
    guide = "# OneUI 卡片选择指南\n\n## 可用卡片配置\n\n"
    guide += json.dumps(CARDS_CONFIG, ensure_ascii=False, indent=2)
    guide += """

## 使用模式

### 模式 1: 内置卡片
code 为 DynamicForm 或 DocumentDownloadCard 时，使用内置验证。

### 模式 2: 自定义卡片
code 为其他任意值时，args 直接透传，不做字段验证，需提供 version。

## 调用示例

### 动态表单（收集用户输入）
```python
card_tool(
    code="DynamicForm",
    version="0.x",
    args={
        "cardMode": True,
        "title": "xxx信息收集",
        "formSchema": [
            {"label": "xxx", "type": "input-text", "key": "xxx", "required": True},
            {"label": "xxx类型", "type": "select", "key": "xxx_type", "required": True,
             "dataSource": [{"label": "类型A", "value": "a"}, {"label": "类型B", "value": "b"}]}
        ]
    }
)
```

### 文件下载
```python
card_tool(
    code="DocumentDownloadCard",
    version="0.x",
    args={"fileUrl": "https://xxx.com/file.pdf", "fileName": "xxx.pdf"}
)
```

### 自定义卡片
```python
card_tool(code="xxx-card-code", version="2.x", args={"xxx": "xxx"})
```

## 注意事项

1. DynamicForm 的 formSchema 字段必须用 label（不是 title），select 必须用 dataSource（不是 enum），dataSource 中 value 不能重复
2. DocumentDownloadCard 只接受标量字段，禁止数组结构
3. 自定义卡片的 args 直接透传，不做验证
4. 所有卡片都必须提供 version
"""
    return guide


@mcp.prompt()
def sdk_api_guide() -> str:
    """
    SDK API 调用指南 - 帮助 AI 了解可用的前端 SDK API

    当用户需要触发前端操作(如打开应用、调用原生能力)时,请参考此指南
    """
    guide = "# OneUI SDK API 调用指南\n\n## 可用 API 白名单\n\n"
    guide += json.dumps(SDK_CONFIG, ensure_ascii=False, indent=2)
    guide += """

## 调用示例

### 打开应用页面
```python
sdk_tool(module="application", api="openApp", payload=["https://xxx.com", "xxx应用"])
```

### 触发自定义行为
```python
sdk_tool(module="action", api="trigger", payload=["refreshList", {"forceUpdate": true}])
```

## 参数说明

- **module**: SDK 模块名称(application, action)
- **api**: API 方法名称(openApp, trigger)
- **payload**: 参数列表，按顺序传递，须满足 min_length 要求

## 错误码

- `MISSING_PARAMS`: 缺少必填参数
- `EMPTY_PAYLOAD`: payload 为空数组
- `API_NOT_ALLOWED`: API 不在白名单中
- `INVALID_PAYLOAD`: payload 参数数量不足
"""
    return guide


# @mcp.prompt()
# def blocks_guide() -> str:
#     """
#     Blocks 协议使用指南 - 帮助 AI 构造结构化回复
#
#     当需要展示结构化内容（卡片 + 文本 + 快捷操作组合）时，请参考此指南
#     """
#     guide = """# Blocks 协议使用指南
#
# ## 何时使用 blocks_tool
#
# | 场景 | 推荐工具 |
# |------|----------|
# | 纯文本回答 | 直接文本回复 |
# | 单张卡片 + 简短消息 | card_tool |
# | 多张卡片、文本穿插卡片、带快捷操作 | **blocks_tool** |
# | 触发前端 SDK 操作 | sdk_tool |
#
# ## Block 类型
#
# ### message（文本消息）
# ```json
# { "type": "message", "content": "支持 **Markdown** 的文本内容" }
# ```
#
# ### card（卡片）
# ```json
# { "type": "card", "code": "xxx", "version": "版本号", "args": { ... } }
# ```
#
# ### quick_reply（快捷回复）
# ```json
# { "type": "quick_reply", "items": [{ "label": "按钮文字", "message": "点击后发送的消息" }] }
# ```
#
# ## 排列规则
#
# 1. 第一个 block 必须是 message
# 2. quick_reply 只能出现在最后，且最多一个
# 3. card 最多 3 个
#
# ## 调用示例
#
# ```python
# blocks_tool(blocks=[
#     { "type": "message", "content": "查询结果如下" },
#     { "type": "card", "code": "DynamicForm", "version": "0.x", "args": {
#         "cardMode": True, "title": "xxx", "formSchema": [...]
#     }},
#     { "type": "quick_reply", "items": [
#         { "label": "xxx操作", "message": "我想xxx" },
#         { "label": "查看更多", "message": "查看更多详情" }
#     ]}
# ])
# ```
#
# ## 可用卡片列表
#
# """
#     guide += json.dumps(CARDS_CONFIG, ensure_ascii=False, indent=2)
#     guide += """
#
# ## 错误码
#
# | 错误码 | 说明 |
# |--------|------|
# | EMPTY_BLOCKS | blocks 为空 |
# | INVALID_BLOCK_TYPE | type 不合法或缺失 |
# | MISSING_FIRST_MESSAGE | 第一个 block 不是 message |
# | MISSING_CONTENT | message 缺少 content |
# | INVALID_QUICK_REPLY_POSITION | quick_reply 不在最后 |
# | DUPLICATE_QUICK_REPLY | quick_reply 超过 1 个 |
# | TOO_MANY_CARDS | card 超过 3 个 |
# | MISSING_CARD_CODE | card 缺少 code |
# | MISSING_CARD_VERSION | card 缺少 version |
# | EMPTY_QUICK_REPLY | quick_reply 的 items 为空 |
# | INVALID_QUICK_REPLY_ITEM | item 缺少 label 或 message |
# """
#     return guide


@mcp.tool()
def card_tool(
    code: Annotated[
        str,
        Field(
            description="卡片类型代码。内置: DynamicForm(收集用户输入), DocumentDownloadCard(文件下载); 支持任意自定义 code",
            examples=["DynamicForm", "DocumentDownloadCard"]
        )
    ] = "",
    version: Annotated[
        str,
        Field(
            description="卡片版本号,必填。内置卡片使用 '0.x'",
            examples=["0.x", "1.0", "2.x"]
        )
    ] = "",
    args: Annotated[
        Optional[Dict[str, Any]],
        Field(
            description=ARGS_DESCRIPTION
        )
    ] = None,
    message: Annotated[
        str,
        Field(
            description="可选的消息文本,兼容旧版本透传"
        )
    ] = ""
) -> str:
    """
    发送结构化卡片到前端，用于收集用户输入、展示交互式界面或提供文件下载。

    当用户需要下载文件、下载模板、导出文档时，必须使用 DocumentDownloadCard 卡片，
    而不是使用 sdk_tool 的 openApp。

    当用户需要填写表单、提交信息时，使用 DynamicForm 卡片。

    支持两种模式:
    1. 内置卡片: DynamicForm(表单收集), DocumentDownloadCard(文件下载)
    2. 自定义卡片: code 为任意值, args 直接透传, 需提供 version
    """
    missing = {}
    if not code:
        missing["code"] = "缺失"
    if not version:
        missing["version"] = "缺失"
    if args is None:
        missing["args"] = "缺失"

    if missing:
        return _error_response("MISSING_PARAMS", "参数不完整,无法发送卡片", missing=missing)

    # 内置卡片验证
    validation_error = _validate_card_args(code, args)
    if validation_error:
        return validation_error

    # 构建卡片数据
    card_code = CARDS_CONFIG["cards"][code]["code"] if code in CARDS_CONFIG["cards"] else code
    card = {"code": card_code, "version": version, "args": args}

    reply = {
        "success": True,
        "message": f"卡片 {code} 已成功推送到前端。",
        "cards": [card]
    }

    return json.dumps(reply, ensure_ascii=False, indent=2)


# VALID_BLOCK_TYPES = {"message", "card", "quick_reply"}


# @mcp.tool()
# def blocks_tool(
#     blocks: Annotated[
#         List[Dict[str, Any]],
#         Field(description="""结构化回复的 blocks 数组。支持三种 block 类型：
# - message: { "type": "message", "content": "文本内容(支持Markdown)" }
# - card: { "type": "card", "code": "卡片代码", "version": "版本号", "args": { ...参数 } }
# - quick_reply: { "type": "quick_reply", "items": [{ "label": "按钮文字", "message": "点击发送的消息" }] }
#
# 规则：第一个必须是 message，quick_reply 只能在最后，card 最多 3 个。""")
#     ]
# ) -> str:
#     """
#     输出结构化 UI 回复（Structured Response），用于展示结构化内容、卡片和快捷操作。
#
#     当需要展示结构化数据、收集用户输入（表单）、提供快捷操作入口时使用此工具。
#     纯文本问答不需要使用此工具。
#     """
#     if not blocks:
#         return _error_response("EMPTY_BLOCKS", "blocks 不能为空")
#
#     card_count = 0
#     quick_reply_count = 0
#     quick_reply_index = -1
#
#     for i, block in enumerate(blocks):
#         btype = block.get("type")
#         if not btype:
#             return _error_response("INVALID_BLOCK_TYPE", f"blocks[{i}] 缺少 type 字段")
#         if btype not in VALID_BLOCK_TYPES:
#             return _error_response("INVALID_BLOCK_TYPE",
#                 f"blocks[{i}] type='{btype}' 不合法，仅支持: {', '.join(VALID_BLOCK_TYPES)}")
#
#         if btype == "message":
#             if not block.get("content"):
#                 return _error_response("MISSING_CONTENT", f"blocks[{i}] message 缺少 content")
#
#         elif btype == "card":
#             card_count += 1
#             card_code = block.get("code")
#             if not card_code:
#                 return _error_response("MISSING_CARD_CODE", f"blocks[{i}] card 缺少 code")
#             if not block.get("version"):
#                 return _error_response("MISSING_CARD_VERSION", f"blocks[{i}] card 缺少 version")
#
#             card_args = block.get("args", {})
#             validation_error = _validate_card_args(card_code, card_args, context=f"blocks[{i}]")
#             if validation_error:
#                 return validation_error
#
#         elif btype == "quick_reply":
#             quick_reply_count += 1
#             quick_reply_index = i
#             items = block.get("items")
#             if not items:
#                 return _error_response("EMPTY_QUICK_REPLY", f"blocks[{i}] quick_reply 的 items 不能为空")
#             for j, item in enumerate(items):
#                 if not item.get("label") or not item.get("message"):
#                     return _error_response(
#                         "INVALID_QUICK_REPLY_ITEM",
#                         f"blocks[{i}].items[{j}] 缺少 label 或 message 字段"
#                     )
#
#     # 结构规则校验
#     if blocks[0].get("type") != "message":
#         return _error_response("MISSING_FIRST_MESSAGE", "第一个 block 必须是 message 类型")
#
#     if quick_reply_count > 1:
#         return _error_response("DUPLICATE_QUICK_REPLY", "quick_reply 最多只能有一个")
#
#     if quick_reply_count == 1 and quick_reply_index != len(blocks) - 1:
#         return _error_response("INVALID_QUICK_REPLY_POSITION", "quick_reply 必须是最后一个 block")
#
#     if card_count > 3:
#         return _error_response("TOO_MANY_CARDS", f"card 最多 3 个，当前 {card_count} 个")
#
#     return json.dumps({
#         "success": True,
#         "message": "结构化内容已成功推送到前端。",
#         "version": "v1.0",
#         "blocks": blocks
#     }, ensure_ascii=False, indent=2)


@mcp.tool()
def sdk_tool(
    module: Annotated[
        str,
        Field(
            description="SDK 模块名称。打开页面/跳转 URL 时填 'application'，触发自定义行为时填 'action'",
            examples=["application", "action"]
        )
    ] = "",
    api: Annotated[
        str,
        Field(
            description="SDK API 名称。打开页面/跳转 URL 时填 'openApp'，触发自定义行为时填 'trigger'",
            examples=["openApp", "trigger"]
        )
    ] = "",
    payload: Annotated[
        Optional[List[Any]],
        Field(
            description="""API 调用参数列表，按顺序传递。
- openApp: [url, name, config?]
- trigger: [name, params?, containerCodeList?]""",
            examples=[["https://ennew.com", "恩牛网"], ["refreshList", {"forceUpdate": True}]]
        )
    ] = None
) -> str:
    """
    触发前端执行操作，例如打开一个应用页面、跳转到指定 URL，或触发自定义行为。

    当用户说"打开某个页面"、"跳转到某个地址"时使用此工具。

    注意：下载文件/模板/文档时，不要用此工具，应使用 card_tool 的 DocumentDownloadCard。

    通过白名单机制控制可用 API，前端消费格式为 { module, api, payload }。
    """
    missing = {}
    if not module:
        missing["module"] = "缺失"
    if not api:
        missing["api"] = "缺失"
    if payload is None:
        missing["payload"] = "缺失"

    if missing:
        return _error_response("MISSING_PARAMS", "参数不完整,无法调用 SDK", missing=missing)

    if not payload:
        return _error_response("EMPTY_PAYLOAD", "payload 不能为空数组")

    # 白名单校验
    api_key = f"{module}.{api}"
    if api_key not in SDK_CONFIG["apis"]:
        allowed = ", ".join(SDK_CONFIG["apis"].keys())
        return _error_response(
            "API_NOT_ALLOWED",
            f"API '{api_key}' 不在白名单中",
            allowed_apis=allowed
        )

    # payload 长度校验
    api_config = SDK_CONFIG["apis"][api_key]
    min_length = api_config["payload_schema"]["min_length"]
    if len(payload) < min_length:
        return _error_response(
            "INVALID_PAYLOAD",
            f"payload 至少需要 {min_length} 个参数,当前只有 {len(payload)} 个"
        )

    return json.dumps({
        "success": True,
        "message": f"SDK API {module}.{api} 已成功触发。",
        "sdk": {"module": module, "api": api, "payload": payload}
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
