# 新增领域指南

本文档说明如何为 sop-generator 添加新的业务领域。

## 快速开始

复制 `_template` 目录并重命名为新领域 ID：

```bash
cp -r .claude/skills/sop-generator/domains/_template \
      .claude/skills/sop-generator/domains/{your_domain_id}
```

## 详细步骤

### 步骤1: 创建领域目录和配置文件

```
domains/
├── _template/          # 模板目录（参考用）
├── general/            # 通用领域
├── xuzhi/              # 需智领域
└── {your_domain_id}/   # ← 你的新领域
    └── domain.yaml
```

### 步骤2: 填写 domain.yaml

参考模板，修改以下关键字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `domain.id` | 领域唯一标识（英文） | `finance`, `hr`, `supply_chain` |
| `domain.name` | 领域显示名称（中文） | `金融`, `人力`, `供应链` |
| `domain.description` | 领域一句话描述 | 用于 AI 识别和理解 |

### 步骤3: 定制领域知识

根据业务特性，修改以下内容：

**3.1 field_specs（字段生成规范）**
- 保持结构不变
- 修改 `examples` 和 `tips`，体现领域特色

**3.2 constraints（约束规则）**
- 定义该领域的业务约束
- 例如：金融领域需包含"合规性检查"，人力领域需包含"审批流"

**3.3 node_example（节点示例）**
- 提供一个典型的节点完整示例
- 帮助 AI 理解领域术语和表达方式

**3.4 completion_message（完成提示）**
- 定义生成完成后的提示语

### 步骤4: 在 SKILL.md 中添加意图识别

修改 `.claude/skills/sop-generator/SKILL.md` **步骤1-2.2**：

```yaml
**2.2 意图识别（自动推断）：**
- 检测用户输入中的领域关键词：
  - **需智领域关键词**：`需智`、`xuzhi`... → 识别为 `xuzhi`
  - **通用领域**：未匹配以上关键词... → 识别为 `general`
  - **← 新增：你的领域关键词**：`关键词1`、`关键词2`... → 识别为 `{your_domain_id}`
```

## 完整示例

以新增「金融」领域为例：

### 1. 创建目录
```bash
mkdir -p .claude/skills/sop-generator/domains/finance
```

### 2. domain.yaml 关键配置

```yaml
domain:
  id: finance
  name: 金融
  description: 适用于金融业务流程，包含风控、合规、审批等环节

field_specs:
  name:
    examples: ["风险评估", "合规审查", "额度审批", "资金划转"]
    tips: "体现金融业务动作，如'评估XX'、'审查XX'、'审批XX'"
  
  businessLogics:
    examples:
      - "风险评估：评估客户信用等级和还款能力"
      - "合规审查：检查业务是否符合监管要求"
    tips: "体现金融业务规则和风控逻辑"

constraints:
  - "必须包含合规性检查环节"
  - "涉及资金操作需有风控审批"
  - "关键节点需留痕审计"

node_example:
  name: "风险评估"
  desc: "基于客户信息和业务数据评估风险等级"
  input: "客户征信、交易记录、担保信息"
  output: "风险评级、授信建议"
  businessLogics:
    - "收集客户多维度信息"
    - "信用评分计算"
    - "风险等级判定"
  completeCondition:
    - "风险评级已生成"
    - "异常情况已标注"
```

### 3. SKILL.md 添加识别规则

```yaml
- **金融领域关键词**：`金融`、`风控`、`信贷`、`理财` → 识别为 `finance`
```

## 验证

新增领域后，测试以下场景：

1. **显式调用**：`/sop-generator finance` → 应加载金融领域
2. **意图识别**：`帮我设计一个信贷审批流程` → 应自动识别为 finance
3. **第一问题**：应显示"请您详细描述下您认为的**金融**场景业务过程是什么？"
4. **节点生成**：应体现金融领域特色术语

## 注意事项

- **domain.id** 必须全局唯一，使用英文小写+下划线
- **field_specs** 保持结构一致，只修改内容和示例
- **constraints** 不要过多，3-5 条核心约束即可
- 测试通过后，再合并到主分支
