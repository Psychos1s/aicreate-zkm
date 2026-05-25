# nodeList 参数规则

## 总则

- 必须包含以下三种类型的全部节点，不得遗漏任何一种
- 每个节点的 `nodeId`、`nodeName` 和 `nodeType` 都是必填字段，且不能为空
- 数据来源：从 `output/stage2.md` 文档中解析业务对象和业务逻辑，禁止凭空生成
- 禁止传入空值、空数组或空对象。每种节点包含的属性，必须有值
- 必须原文提取，禁止总结加工。比如对象名称是“这是燃气炉”，提取的对象名就是原文“这是燃气炉”
---

## 1. 数据对象节点（`nodeType='ac_model'`）

| 字段 | 说明 |
|------|------|
| `nodeId` | 格式：`node_object_*` |
| `nodeName` | 节点名称 |
| `nodeType` | `ac_model` |

使用 `model` 字段，包含以下属性：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 对象名称 |
| `definition` | ✅ | 对象定义 |
| `modelConstraintRule` | ✅ | 对象生成规则与约束 |
| `modelConstraintRuleExample` | ✅ | 示例 |
| `modelInstanceConstraintRule` | ✅ | 对象实例生成规则与约束 |
| `modelInstanceConstraintRuleExample` | ✅ | 示例 |
| `dynamicFieldConstraintRule` | ✅ | 动态属性生成规则 |
| `dynamicFieldConstraintRuleExample` | ✅ | 示例 |
| `fields[]` | ✅ | 属性列表，每项包含： |
| `fields[].name` | ✅ | 属性名称，**不能为空** |
| `fields[].definition` | ✅ | 属性定义（数据类型） |
| `fields[].fieldConstraintRule` | ✅ | 属性值规则与约束 |
| `fields[].fieldConstraintRuleExample` | ✅ | 示例 |

> ⚠️ 每个对象至少需要一个属性，如果属性为空则提示用户新增。

---

## 2. 业务逻辑节点（`nodeType='logic_ontology'`）

| 字段 | 说明 |
|------|------|
| `nodeId` | 格式：`node_logic_*` |
| `nodeName` | 节点名称 |
| `nodeType` | `logic_ontology` |

使用 `logicOntology` 字段，包含以下属性：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 业务逻辑名称 |
| `definition` | ✅ | 规则定义 |
| `logicConstraintRule` | ✅ | 逻辑表达式：具体的计算公式或条件判断表达式，如 `效率=产量/消耗量` 或 `若库存<安全线→触发补货` |
| `input` | ✅ | 数组类型，依赖的数据对象列表 |
| `output` | ✅ | 数组类型，产生的数据对象或关系列表 |
| `example[]` | ✅ | 示例数组，每项包含： |
| `example[].input` | ✅ | 输入示例 |
| `example[].output` | ✅ | 输出示例 |
| `example[].logicConstraintRule` | ✅ | 逻辑表达式示例 |
| `example[].executionRule` | ✅ | 执行规则示例（会触发哪些动作，对应执行本体） |

---

## 3. 执行本体节点（`nodeType='execution_ontology'`）

| 字段 | 说明 |
|------|------|
| `nodeId` | 格式：`node_execution_*` |
| `nodeName` | 节点名称 |
| `nodeType` | `execution_ontology` |

使用 `executionOntology` 字段，包含以下属性：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 执行本体名称 |
| `description` | ✅ | 执行本体描述 |
| `type` | ✅ | 执行本体类型（如：映射转换、条件判断、数值计算、数据聚合、规则匹配等） |

**🔴 执行本体节点推导规则**：
- nodeList 中必须包含 `execution_ontology` 节点，且每条业务逻辑对应生成**一个**执行本体节点，不得遗漏
- `name`：根据业务逻辑名称和执行规则描述命名（如"诊断参数映射执行"）
- `description`：从该业务逻辑的执行规则中提取，描述具体执行动作
- `type`：根据执行规则的操作类型判断，从以下选项中选择：映射转换、条件判断、数值计算、数据聚合、规则匹配

---

## 4. 专业领域知识数据提取规则

**数据来源**：从 `/output/stage2.md` 文档中提取已写入的专业领域知识数据，填入对应节点的 example 字段：

| 节点类型 | 提取目标 |
|----------|---------|
| `logic_ontology` | 将业务逻辑实例填入 `example[]` 数组（input / output / logicConstraintRule / executionRule） |
| `ac_model` | 将业务对象实例填入 `modelInstanceConstraintRuleExample` 和各属性的 `fieldConstraintRuleExample` |

- ❌ 禁止在用户已提供专业领域知识数据的情况下，用 AI 自行生成的示例替代

---

## 5. 完整示例

```json
[
  {
    "nodeId": "node_object_x",
    "nodeName": "模糊的意图",
    "nodeType": "ac_model",
    "model": {
      "name": "模糊的意图",
      "definition": "",
      "modelConstraintRule": "",
      "modelConstraintRuleExample": "",
      "modelInstanceConstraintRule": "",
      "modelInstanceConstraintRuleExample": "",
      "dynamicFieldConstraintRule": "",
      "dynamicFieldConstraintRuleExample": "",
      "fields": [
        {
          "name": "字段名称",
          "definition": "",
          "fieldConstraintRule": "",
          "fieldConstraintRuleExample": ""
        }
      ]
    }
  },
  {
    "nodeId": "node_logic_x",
    "nodeName": "诊断参数值映射",
    "nodeType": "logic_ontology",
    "logicOntology": {
      "name": "诊断参数值映射",
      "definition": "",
      "logicConstraintRule": "",
      "input": ["特征标签"],
      "output": ["需求价值指标"],
      "example": [
        {
          "input": "",
          "output": "",
          "logicConstraintRule": "",
          "executionRule": ""
        }
      ]
    }
  },
  {
    "nodeId": "node_execution_x",
    "nodeName": "诊断参数映射执行",
    "nodeType": "execution_ontology",
    "executionOntology": {
      "name": "诊断参数映射执行",
      "description": "",
      "type": ""
    }
  }
]
```
