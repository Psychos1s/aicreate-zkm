---
name: sop-generator
description: 业务逻辑编排能力构建生成助手。支持领域驱动模式（通过 /sop-generator <domain> 加载特定领域知识）和通用模式生成 应用配置。当用户创建业务流程、设计业务逻辑、编排工作流或编辑现有流程时触发。
---

## 工作流程

### 步骤1: 意图识别与领域加载

**1. 意图校验：**
- 分析用户输入，判断是否有清晰的业务流程构建意图
- **禁止调用 AskUserQuestion**，仅做意图分析
- 无论意图是否清晰，均进入下一步

**2. 自动识别领域：**

**2.1 显式指定领域（优先级最高）：**
- 若用户输入包含 `/sop-generator <domain>`，以用户指定的 domain 为准

**2.2 意图识别（自动推断）：**
- 检测用户输入中的领域关键词：
    - **需智领域关键词**：`需智`、`xuzhi`、`需求智能`、`企业需求` → 识别为 `xuzhi`
    - **通用领域**：未匹配以上关键词，或输入为通用业务描述 → 识别为 `general`

**2.3 领域确定：**
- 根据上述识别结果，AI 内部记录：
    - `current_domain_id` = 识别的领域 ID（如 `xuzhi` 或 `general`）
    - `current_domain_name` = 从对应 domain.yaml 读取的 `domain.name`（如 `需智` 或 `通用`）
- 后续流程均基于这两个变量执行

### 步骤2: 知识访谈（通用流程）

执行：`python .claude/skills/sop-generator/scripts/updateProcessStatus.py --process interview`

**2.1 第一问题：**（禁止调用 AskUserQuestion）
```
请您详细描述下您认为的{current_domain_name}场景业务过程是什么？
```
（例如：识别为需智领域 → "需智"；通用领域 → "通用"）

**2.2 用户回答后，加载领域知识：**

执行：`python .claude/skills/sop-generator/scripts/domain_loader.py --domain {current_domain_id} --action all`

加载 L1 - 平台领域知识：
- `field_specs`：字段生成规范
- `node_example`：完整节点示例
- `constraints`：领域约束规则
- `completion_message`：完成提示模板

执行：`python .claude/skills/sop-generator/scripts/domain_loader.py --domain {current_domain_id} --action schema_meta`

加载 L2 - 约束元（如果存在）：
- `schema_meta`：领域对象类型定义（模糊的意图、目标客群、需求价值指标等）
- 用于指导输入输出的对象类型选择

**知识分层说明：**
- L1（platform）：提供字段格式规范和基础示例（必有）
- L2（schema）：提供可选的业务对象类型词典（可选）
- L3（business）：提供业务规则和流程（后期扩展，可选）

**2.3 意图处理：**

| 意图 | 判定标准 | 步骤2 | 步骤3 |
|------|----------|-------|-------|
| 强 | 有步骤关键词+序号词 **且** 能提取≥2有效节点 | 过渡确认 | question 展示列表 |
| 弱有效 | 有结构但内容空洞 **或** 有业务方向但无步骤 | 生成建议流程 | 简化确认 |
| 弱无效 | 无业务方向 | 追问 | 等待输入 |

**判定逻辑：**
1. 初筛：含["步骤/节点/环节"]且含序号词["第一/然后/1."]
2. 校验：能否提取≥2节点（名称+动作）
3. 细分：是否有业务主题词

**强意图处理：**
1. 生成节点列表
2. 普通文本输出：
   ```
   基于领域知识已生成下面流程：
   1. {节点1名称}：{说明}
   2. {节点2名称}：{说明}
   ...
   请确认或告知调整内容。
   ```
3. 接收用户输入 -> 
              - 确认 --> 进入步骤3
              - 修改内容 --> 重新判断意图，进入相应处理

**弱有效处理：**
1. 基于领域知识生成建议流程（3-5节点）
2. 普通文本输出（仅此处一次）：
   ```
   基于领域知识生成建议流程如下：
   1. {节点1名称}：{说明}
   2. {节点2名称}：{说明}
   ...
   请确认或告知调整内容。
   ```
3. 接收用户输入 ->   
              - 确认 --> 进入步骤3
              - 修改内容 --> 重新判断意图，进入相应处理

**弱无效处理：**
1. 普通文本输出：
   ```
   您想构建什么样的业务流程？可以描述：
   - 涉及哪些环节？
   - 或输入"示例"查看参考流程
   ```
2. 接收用户输入
3. 重新判断意图，进入相应处理

⚠️ **规则**：步骤2仅输出列表（无详细字段）；强意图步骤3展示，弱有效步骤3简化确认；弱无效追问至有效；详情统一在步骤4生成。

### 步骤3: 节点确认（最多3轮）

**AskUserQuestion 格式：**
```json
{"questions": [{"question": "{动态内容}", "header": "节点确认", "options": [{"label": "没问题，帮我生成业务 SOP", "description": "自动补全所有节点详情"}, {"label": "其他", "description": "描述您要修改的内容或其他需求"}]}]}
```

**动态内容：**
- 强意图首次：`已整理关键步骤：\n{列表}\n\n请确认：`
- 弱意图首次：`请确认上述流程是否符合需求：`
- 修改后：`已调整：\n{列表}\n\n请确认：`
- 第3轮追加：`（建议确认当前版本）`

**循环流程：**
```
轮次 = 0
while 轮次 < 3:
    轮次 += 1
    使用 AskUserQuestion
    if "没问题，帮我生成业务 SOP": 进入步骤4
    elif "其他":
        普通文本："请描述调整内容，或输入'重新描述'回到上一步。"
        接收输入：
        - "重新描述": 回步骤2
        - 无法理解:
            普通文本："抱歉没理解。请：1.说明修改哪个节点 2.描述想要的效果 3.输入'重新描述'"
            再次接收：
            - "重新描述": 回步骤2
            - 仍无法理解: continue
            - 理解: 处理并继续循环
        - 理解: 处理并继续循环
    - 普通文本： 理解: 处理并继续循环   
```

⚠️ **强制规则**：AskUserQuestion 前禁止普通文本输出列表；步骤2弱意图已展示则步骤3简化；无法理解须在步骤3内追问，禁止回步骤2；2次无法理解引导先确认。

### 步骤4: 生成节点详情

**Step 0: 绑定领域约束元（不要阻塞影响节点生成）**

执行：`python .claude/skills/sop-generator/scripts/bind_domain_knowledge.py --domain {current_domain_id}`

- 从 `domain.yaml` 读取 `constraintPaperId`，为空则不调用
- 失败不中断流程，继续生成节点

⚠️ **用户已确认节点列表，一次性生成所有节点详情**
**Step 1: 参考领域知识生成**

| 字段 | 生成策略                              | 知识来源 |
|------|---------------------------------------|---------|
| name | 体现代办事项，动词+业务对象             | L1 `field_specs.name` |
| type | 节点类型：`task`（任务节点）或 `gateway`（网关节点）。若节点包含**判断分支、条件决策、多路径选择**等业务逻辑，则设为 `gateway`；否则设为 `task` | AI理解业务逻辑 |
| desc | 一句话说明业务目标                     | L1 `field_specs.desc` |
| input.desc | **列出业务对象类型名称**（如"模糊的意图"、"需求价值指标"）| **L2 `schema_meta` 对象池 + L1 格式示例** |
| output.desc | **列出业务对象类型名称**（如"清晰意图"、"需要的能力"）   | **L2 `schema_meta` 对象池 + L1 格式示例** |
| businessLogics | 按业务步骤描述业务动作和判断分支  | L1 `field_specs.businessLogics` + AI理解 |
| completeCondition | 从业务验收角度定义完成标准 **对象格式** `{ "businessRule": "string" }`，多条标准用`\n`分隔 | L1 `field_specs.completeCondition` + AI理解 |
| gatewayRules      | 当且仅当节点是条件网关节点时生成该字段， **对象格式** `[{"ruleText":"条件分支1","targetNodeId":"目标节点id"},{"ruleText":"条件分支2","targetNodeId":"目标节点id"}]` | L1 `field_specs.gatewayRules` + desc字段的语义 + AI理解 |

**输入输出生成规则（关键）：**

1. **对象类型来源**：优先从 L2 `schema_meta` 定义的对象类型中选择
   - 需智领域对象池：模糊的意图、目标客群、需求价值指标、特征标签、清晰的意图、需要的能力

2. **节点选择逻辑**：
   - 分析当前节点的业务目标
   - 从对象池中选择与该节点输入/输出相关的对象类型
   - 参照 L1 `field_specs.input/output.examples` 的格式组织

3. **上下游衔接**：
   - 当前节点的输入应引用上游节点输出的对象类型
   - 保持对象类型在流程中的连贯流转

4. **格式规范**：
   - 生成的是**对象类型名称**（如"模糊意图列表"），不是对象属性
   - 使用业务语言，不是技术字段名

**生成原则：**
- 用业务语言描述，不是技术模板
- 输入输出是**业务对象类型**（来自约束元），不是数据格式或字段
- **completeCondition** 字段类型一定要按照要求去生成
- 业务逻辑描述业务步骤和判断条件
- 生产型企业判断：生产/制造/设备等关键词，或制造业/能源/化工行业
- 节点间输入输出保持对象类型衔接

**条件网关节点处理**
- 仅当业务逻辑businessLogics中出现"如果...则..."、"当...时"、"根据...判断"、"若" 等明确分支条件时，该节点才是条件网关节点(节点类型是gateway)
- 不需要收集input.desc，output.desc

### 步骤5: 加载Schema

使用 `ReadFile` 读取 `reference/schema.json`，理解节点和连线的数据结构。
- 使用 `ReadFile` 读取项目根目下的 `.app_config.json`，获取文件中的ennunifiedauthorization、ennunifiedcsrftoken、env字段。
- `.app_config.json`中内容结构如下：
```json
{
  "env": "fat",
  "ennunifiedauthorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJVbmlmeUF1dGhTU08iLCJoYXNUZW5hbnQiOnRydWUsImxvZ2luVHlwZSI6IjEwMDAiLCJpc3MiOiIxMzQxNTcxMjk2MTUzMDE4MzcwIiwidGVybWluYWxUeXBlIjoiUEMtV0VCLTE3NzUxMDI5NTM5ODkiLCJhdWQiOiJhdWQiLCJoYXNSZWxhdGlvbnNoaXBUZW5hbnQiOmZhbHNlLCJuYmYiOjE3NzUxMDMyNzQsImFwcElkIjoiaW9jLXdvcmtiZW5jaC1mcm9udCIsIm5pY2tuYW1lIjoi5byg5rC45piKIiwidGVuYW50SWQiOiIxMzc3NTE3NDE4MzQ0NTUwNDAyIiwiZ3JhbnRjb2RlIjoiTVRNME1UVTNNVEk1TmpFMU16QXhPRE0zTUNOUVF5MVhSVUl0TVRjM05URXdNamsxTXprNE9TTXdNekppTXpjNU16ZGpNemd5T0dWbU5EYzFOelF6T1dWbVpHUm1PRFl5TlEiLCJleHAiOjE3NzUxODk2NzQsImlhdCI6MTc3NTEwMzI3NCwianRpIjoiMmY5ZmIzMmEtYTNkZS00MTA2LWE4M2UtM2RhNjJhNGQzNWY2IiwidXNlcm5hbWUiOiJ0LVpIQU5HWU9OR0hBTyJ9.Z9B6b1tCvbPx71dpWhyi6zOABbTK-3Dqk6NoQOMhyYsFzJPLMMxIQ-Ikp1dQFzQiSFiqLlDwL4nbbzvUPDEPIdbcQjK3k2bdNs_u9cCn90iYW20VWkNHbGkpdDYjiVxJ9AMQ81IlKYzzOA2sj5LfpkhP2s-rQMspJYq7_rHtg90",
  "ennunifiedcsrftoken": "e6e82b1f7bd2e1b0faffca81d1586d1e"
}
```

### 步骤6: 检查业务状态

执行：`python .claude/skills/sop-generator/scripts/check_business_json.py`

- `true` → 进入步骤9（继续编辑）
- `false` → 进入步骤7（流程构建）

### 步骤7: 流程构建

开始提示:
   **开始生成业务逻辑编排内容**

执行：`python .claude/skills/sop-generator/scripts/updateProcessStatus.py --process sop`

严格按**开始节点→业务节点→连线→业务节点**交替的方式来生成应用配置（⚠️ 逐个顺序调用，禁止并行）：

1. 添加开始节点 `N0`，**message字段由AI根据应用名称和描述动态生成欢迎语**：
   ```json
   {"id": "N0", "type": "start", "name": "开始", "message": "AI生成的欢迎语"}
   ```
2. 基于知识访谈收集的信息，添加节点到 `应用配置`, 严格遵循Schema规范
   - 使用 `mcp__sopWrite__addNode` 添加节点
   - 使用 `mcp__sopWrite__addEdge` 设置节点连接关系

3. 添加结束节点 `N99`，**message字段由AI根据应用名称生成结束语**：
   ```json
   {"id": "N99", "type": "end", "name": "结束", "message": "AI生成的结束语"}
   ```

4. 在生成节点后满足连线条件，立刻开始添加连线，禁止所有节点生成完成后才开始连线。
5. 流程里的节点连线不能断开


### 步骤8: 完成提示

> 已为您生成 {current_domain_name} SOP
> 如需调整，请随时告知或在右侧面板修改。

### 步骤9: 流程编辑（持续监听）

⚠️ **SOP生成完成后，持续监听用户输入，处理修改请求**

**意图强度识别：**

| 强度 | 判定标准 | 示例 |
|------|----------|------|
| 强意图 | 操作类型 + 节点名称 + 修改内容（完整） | "删除'风险评估'节点"、"修改'需求收集'的描述为'XX'" |
| 弱意图 | 信息不完整或模糊 | "改一下"、"这个不对"、"删了" |

**意图类型识别（在执行前判断）：**

| 类型 | 标记词 | 处理方式 |
|------|--------|----------|
| 执行意图 | 直接描述操作，无疑问词 | 直接执行 |
| 疑问意图 | 含`能不能`、`行不行`、`好不好`、`是否可以`、`对吗` | 思考分析后给方案 |

---

**执行意图处理（直接执行）：**

**判定标准：** 强意图 且 不含疑问词

- **删除：** 解析节点名称 → 定位 nodeId → `mcp__sopWrite__deleteNode(nodeId)`→ `mcp__sopWrite__deleteEdge` → `mcp__sopWrite__addEdge` → "已删除'XX'"
- **修改：** 解析节点名称和内容 → `mcp__sopWrite__updateNode(nodeId, params)` → "已更新'XX'的XX"
- **添加：** 解析位置和新节点 → `mcp__sopWrite__addNode` → `mcp__sopWrite__deleteEdge` → `mcp__sopWrite__addEdge` → "已添加'XX'"
- **交换：** 解析两个节点的ID，如果意图出现序数（例如第一个节点），则计数从0开始。开始节点和结束节点不能参与交换 → `mcp__sopWrite__swapNode(sourceNodeId,targetNodeId)` → "已交换'XX'和'YY'"


---

**疑问意图处理（思考-分析-建议-确认）：**

**判定标准：** 含疑问词（`能不能`、`行不行`、`可不可以`、`好不好`、`对吗`、`是否要`）

**处理流程（禁止直接执行）：**
1. **理解意图**：提取操作类型、目标节点、用户真实诉求
2. **影响分析**：分析该节点作用、上下游依赖、操作后果
3. **给出方案**：明确回答 + 理由 + 2-3个替代选项
4. **等待确认**：询问用户选择，接收确认后再执行

**示例：**
- 用户："第一个节点能不能删除"
- AI："不建议删除'初步信息收集'，因为它是下游'需求诊断'的输入。建议：1.保留 2.简化 3.确认删除。您选哪个？"

---

**弱意图处理（自然语言追问，最多3轮）：**

识别缺失要素，单次追问一个问题：
- 缺操作类型："您是想删除、修改还是添加节点？"
- 缺目标节点："您要对哪个节点进行操作？"
- 缺修改内容："您希望如何修改'XX'？请详细描述。"

**追问后流转：**
1. 接收用户回答
2. **重新进行意图识别（强度+类型）**
3. 识别为**强执行意图**（强意图+无疑问词）→ 直接执行
4. 识别为**疑问意图**（含疑问词）→ 思考分析后给方案
5. 识别为**弱意图** → 继续追问（轮次+1，最多3轮）
6. **3轮后仍无法识别** → 提示："请明确描述：操作类型 + 节点名称 + 修改内容"

## 注意事项
- 删除 `最后一个节点`: 不是删除N99节点，是删除N99前一个节点 



### 步骤10: 支持发布和生成数据模型（前提是已完成步骤8）

当用户输入`开始生成数据模型` 或者 `发布` 时，使用 `mcp__oneui__card_tool` 推送不同卡片：
生成数据模型:
```json
{
  "message": "开始生成数据模型",
  "code": "GenerateDataOntology",
  "version": "0.x",
  "args": {
    "appNo": ""
  }
}
```

发布:
```json
{
  "message": "发布",
  "code": "GenerateCapabilityModel",
  "version": "0.x",
  "args": {
    "appNo": "",
    "appName": ""
  }
}
```

## 数据结构规范

### 节点类型
- `start` - 开始节点（固定 N0）
- `task` - 任务节点
- `gateway` - 条件网关节点
- `end` - 结束节点（固定 N99）

### ID生成规则
- N0（开始）、N99（结束）
- 中间节点：N1, N2, N3...
- 继续编辑时检查避免冲突

### 完整节点示例
```json
{
  "id": "N1",
  "type": "task",
  "name": "节点名称",
  "desc": "任务描述",
  "input": {"desc": "输入描述"},
  "output": {"desc": "输出描述"},
  "businessLogics": "执行步骤",
  "completeCondition": {"businessRule": "完成规则"}, 
  "gatewayRules": [{
    "ruleText": "条件分支1",
    "targetNodeId": "目标节点id"
  }, {
    "ruleText": "条件分支2",
    "targetNodeId": "目标节点id"
  }]
}
```

## 注意事项

- `应用配置`的操作都使用工具`mcp__sopWrite`，如果调用失败，请触发重试：**最大重试3次**。**若3次重试后仍然失败，则直接提示用户失败原因，终止本次流程**
- 展示给用户时**禁止使用节点ID**，使用节点名称
- 生成节点详情时**一次性生成所有字段**，**禁止分阶段多次确认**
- 用户确认节点列表后，直接生成所有内容，最后**仅一次整体确认**（确认正确/其他）
- 禁止使用 `TodoWrite`
- 最后一个节点
