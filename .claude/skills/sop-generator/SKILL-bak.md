---
name: sop-generator
description: 业务逻辑编排智能应用生成助手。用于创建、设计和完善业务逻辑编排智能应用，通过结构化对话逐步构建包含节点和连线的应用配置文件。当用户想要创建业务流程、设计业务逻辑、编排业务逻辑、搭建智能应用、配置工作流或使用/sop-generator命令时触发此skill。也适用于需要继续编辑已有业务流程的场景。
---

## 概述

本skill通过对话式交互引导用户构建业务逻辑编排应用，生成包含节点和连线配置的 `business.json` 应用配置文件。


## 工作流程

### ⚠️ 执行顺序：必须按步骤顺序执行

### 步骤1: 
首先根据用户输入判断其意图：

**欢迎语模板：**
```
你好，我是业务逻辑编排专家，专注辅助你通过编排业务逻辑搭建智能应用。
```

**意图判断：**
- 检查用户输入是否与创建业务流程、设计业务逻辑、编排工作流相关
- 如以下情况则判定为非SOP生成相关内容：
   - 日常闲聊（如"今天天气怎么样"、"你好"）
   - 问题咨询（如"什么是SOP"）
   - 非业务流程相关请求
- **给出固定前缀 + 根据用户意图动态生成的回复：**
   - **固定前缀**：`您好，我是业务模型沉淀专家，专注辅助你搭建智能应用。`
   - **动态生成**：`[AI生成] 根据用户的非SOP相关输入，生成个性化的引导语，将话题转向智能应用构建。例如：`
      - 用户问天气 → 示例：如果你想了解天气信息，我可以帮你创建一个天气查询智能应用，需要我来帮你实现吗？
      - 用户闲聊 → 示例：我擅长帮你把业务想法转化为可执行的智能应用流程，有没有具体想实现的功能或流程？

### 步骤2: 加载Schema

在开始构建前，必须加载 `reference/schema.json`，理解节点和连线的数据结构要求。

**操作：** 使用 `Read` 工具读取 `reference/schema.json`

### 步骤3: 检查业务状态

此步骤用于判断是新创建还是继续编辑。

**操作：**
执行python脚本 `.claude/skills/sop-generator/scripts/check_business_json.py`


**判断返回值：**
- `true` - 进入 `步骤5` 继续编辑模式
- `false` - 进入 `步骤4` 进行知识访谈

### 步骤4: 知识访谈

在正式构建流程前，可根据需要进行知识访谈以收集业务领域信息。访谈开始，执行python脚本，更新当前任务状态为访谈：`.claude/skills/sop-generator/scripts/updateProcessStatus.py --process interview`

**触发条件：**
- 用户需要收集复杂的业务领域知识
- 用户想通过结构化访谈方式梳理业务逻辑
- 流程设计需要深入了解特定领域

通过结构化对话逐步收集节点信息，建议按以下顺序：
1. **节点名称** (name)
2. **节点类型** (type) - start|task|gateway|end
3. **节点描述** (desc)
4. **输入信息** (input.desc)
5. **输出信息** (output.desc)
6. **业务逻辑** (businessLogics)
7. **完成条件** (completeCondition.businessRule)

### 步骤5: 流程构建

#### 创建模式

1. 同步任务状态：执行python脚本`.claude/skills/sop-generator/scripts/updateProcessStatus.py --process sop`

2. 基于步骤4知识访谈收集的信息，确保提取到节点数据后，添加节点到 `business.json`
   - 使用 `mcp__sopWrite__batchAddNodesAndEdges` 添加所有节点和边
   - 使用 `mcp__sopWrite__addNode` 添加节点

3. 使用 `mcp__sopWrite__addEdge` 设置节点连接关系

#### 继续编辑模式

1. 加载现有 `business.json` 并显示当前节点和连线

2. 根据用户选择执行操作：
   - **添加节点** - 使用 `mcp__sopWrite__addNode`，自动生成不冲突的ID
   - **更新节点** - 使用 `mcp__sopWrite__updateNode`
   - **删除节点** - 使用 `mcp__sopWrite__deleteNode`
   - **添加连线** - 使用 `mcp__sopWrite__addEdge`
   - **删除连线** - 使用 `mcp__sopWrite__deleteEdge`
   - **生成新流程** - 清空后重新创建

## 数据结构规范

1. 确保所有task节点至少有一条入边和出边
2. 确保没有孤立节点
3. 确保流程从start(N0)开始，到end(N99)结束

### 节点类型 (type)
- `start` - 开始节点（固定为N0）
- `task` - 任务节点（主要业务逻辑）
- `gateway` - 网关节点（分支/汇聚）
- `end` - 结束节点（固定为N99）

### 节点ID生成规则
- start节点固定为 `N0`
- end节点固定为 `N99`
- 中间节点按顺序生成 `N1`, `N2`, `N3`... ，严格使用前缀 `N` + 数字
- ⚠️ 继续编辑时检查现有ID避免冲突

### 输出格式示例

```json
{
  "nodes": [
    {
      "id": "N0",
      "type": "start",
      "name": "开始"
    },
    {
      "id": "N1",
      "type": "task",
      "name": "节点名称",
      "desc": "任务描述",
      "input": {"desc": "输入描述"},
      "output": {"desc": "输出描述"},
      "businessLogics": "执行步骤",
      "completeCondition": {
        "businessRule": "完成规则"
      }
    },
    {
      "id": "N99",
      "type": "end",
      "name": "结束"
    }
  ],
  "edges": [
    {"source": "N0", "target": "N1"},
    {"source": "N1", "target": "N99"}
  ]
}
```

## 对话设计原则

### 信息收集策略
- 每次询问一个问题，避免信息过载
- 有enum限制的字段使用 `AskUserQuestion` 提供选项
- 必填字段确保有值后才继续
- 可选字段询问用户是否需要填写

### 用户命令支持
以下命令可直接响应：
- "添加节点" / "插入节点"
- "更新节点" / "删除节点" / "删除连线"
- "生成新流程" / "重新开始"
- "完成" / "结束" - 终止对话

### 注意事项
- `AskUserQuestion` 不需要暴露变量和文件信息
- 所有 `business.json` 操作使用 `mcp__sopWrite` 系列工具
