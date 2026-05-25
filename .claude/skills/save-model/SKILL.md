---
name: save-model
description: 解析 output/stage2.md 文档内容，构建 nodeList 和 edgeList 请求参数，调用脚本保存业务模型，并触发前端自定义行为。
context: fork
---

# 业务模型保存

将已确认的业务模型保存到系统。必须在业务模型文档（output/stage2.md）已生成且内容无误后执行。

**🔴 全程静默执行**：除步骤 2 中规定的提示语外，禁止向用户输出任何其他文字（包括文件读取说明、推理过程、技术细节、进度描述等）。

## 执行流程

### 步骤 1：构建请求参数

**🔴 全程静默执行，禁止向用户输出任何中间过程、推理说明或技术细节（包括 nodeList、edgeList、执行本体节点等词汇）。**

**🔴 数据来源**：
从 `output/stage2.md` 文档读取最新的内容，所有的参数构建都基于最新的文档内容

**🔴 原文提取铁律**：
- 对象名称、属性名称、属性定义、对象定义、规则描述、逻辑表达式、关系名称、约束规则等所有字段，**必须逐字原文提取，禁止任何总结、改写、润色、补充、推断**
- 文档中怎么写，JSON 中就怎么填，保持原文的措辞、标点、格式完全不变
- ❌ 禁止用自己的话重新表述
- ❌ 禁止合并、拆分、重组原文内容
- ❌ 禁止添加文档中不存在的描述

**🔴 加载规则**：调用工具前，先读取以下规则文件，严格遵循其中的节点/边结构和字段要求，构建请求参数 nodeList 和 edgeList：
- `.claude/skills/save-model/references/nodeList-rules.md`（节点类型、字段定义、执行本体推导规则、专业领域知识数据提取规则、完整示例）
- `.claude/skills/save-model/references/edgeList-rules.md`（边类型规则、全局约束）

**🔴 参数格式**：必须构建为 `{"nodeList": [...], "edgeList": [...]}` 单个 JSON 对象，作为唯一入参传给脚本。

### 步骤 2：调用脚本保存

1. 向用户展示提示：`正在基于文档生成业务本体...`
2. 执行脚本：`python .claude/skills/save-model/scripts/addModel.py <步骤1构建的请求参数>`
3. 判断返回JSON格式结果：
   - 若 `success` 是 `True`：从输出中获取 `modelPaperId` 和 `metaPaperId`，写入状态文件 `output/save-model-result.json`：`{"status": "success", "modelPaperId": "<脚本返回JSON中的modelPaperId>", "metaPaperId": "<脚本返回JSON中的metaPaperId>"}`，然后**静默调用** MCP 工具 `mcp__oneui__sdk_tool`：
      * `module`: "action"
      * `api`: "trigger"
      * `payload`:` ["modelPaperAction", { "metaPaperId": "<脚本返回JSON中的metaPaperId>", "modelPaperId": "<脚本返回JSON中的modelPaperId>" }]`
        传参示例：
        ```json
        {
        "module": "action",
        "api": "trigger",
        "payload": [
        "modelPaperAction",
        {
        "metaPaperId": "56911",
        "modelPaperId": "56910"
        }
        ]
        }
        ```
⚠️ metaPaperId 和 modelPaperId 必填，值从脚本返回的 JSON 中提取。
❌ 禁止使用 module: "application" 或 api: "openApp"，这是错误的调用方式。
- **🔴 脚本调用必须成功**：调用失败则自动重试，最多重试 3 次
- **失败**（`success` 为 `False` 或重试耗尽）：写入状态文件 `output/save-model-result.json`：`{"status": "error", "message": "具体错误信息"}`，并向用户提示：`业务本体生成失败，请检查文档后重试`


4. 完成后提示用户：`业务本体生成成功！`
