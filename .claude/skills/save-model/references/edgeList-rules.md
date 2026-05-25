# edgeList 参数规则

## 总则

- 数据基于 `/output/stage2.md` 文档中业务对象关系和输入输出定义构建
- 禁止传入空值、空数组或空对象

---

## 边的类型及规则

### 1. 数据对象 → 数据对象的关系边

根据给定的业务对象关系表建立数据对象之间的关系边。

| 字段 | 必填 | 说明 |
|------|------|------|
| `sourceNodeId` | ✅ | 数据对象节点 |
| `targetNodeId` | ✅ | 数据对象节点 |
| `relationName` | ✅ | 关系名称（主动语态） |
| `edgeConstraintRule` | ✅ | 边约束规则 |
| `edgeConstraintRuleExample` | ✅ | 边约束规则示例 |
| `edgeConnectRule` | ✅ | 边连接规则 |
| `edgeConnectRuleExample` | ✅ | 边连接规则示例 |

### 2. 数据对象 → 业务逻辑的关联边

| 字段 | 必填 | 说明 |
|------|------|------|
| `sourceNodeId` | ✅ | 数据对象节点 |
| `targetNodeId` | ✅ | 业务逻辑节点 |
| `relationName` | ✅ | **必须为空字符串 `''`** |

> 禁止传入 `edgeConstraintRule`、`edgeConstraintRuleExample`、`edgeConnectRule`、`edgeConnectRuleExample` 字段

### 3. 业务逻辑 → 执行本体的边

| 字段 | 必填 | 说明 |
|------|------|------|
| `sourceNodeId` | ✅ | 业务逻辑节点 |
| `targetNodeId` | ✅ | 执行本体节点 |
| `relationName` | ✅ | **必须为空字符串 `''`** |

> 禁止传入 `edgeConstraintRule`、`edgeConstraintRuleExample`、`edgeConnectRule`、`edgeConnectRuleExample` 字段

### 4. 执行本体 → 数据对象的边

| 字段 | 必填 | 说明 |
|------|------|------|
| `sourceNodeId` | ✅ | 执行本体节点 |
| `targetNodeId` | ✅ | 数据对象节点 |
| `relationName` | ✅ | **必须为空字符串 `''`** |

> 禁止传入 `edgeConstraintRule`、`edgeConstraintRuleExample`、`edgeConnectRule`、`edgeConnectRuleExample` 字段

---

## 全局规则

| 规则 | 说明                                                                                                                                                 |
|------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| **relationName 规则** | 只有数据对象→数据对象的边需要填写 relationName，其余所有边类型 relationName 必须为空字符串 `''`                                                                                   |
| **单边规则** | 任意两个节点之间只能有一种类型的条边，禁止重复。也不能出现A包含B，B包含A的关系                                                                                                          |
| **禁止互逆** | 对象间关系只需定义一次，禁止同时定义互逆关系。如 目标客群 包含 特征标签 后，不能再定义 特征标签 被包含 目标客群 ，仅保留一条即可。以下互逆关系对只能保留主动语态的一方：包含↔被包含/属于、承载↔被承载、表征↔被表征、约束↔被约束、映射↔被映射、控制↔被控制、使用↔被使用、管理↔被管理 |
| **禁止孤立执行本体** | 每个执行本体节点必须至少连接一个业务逻辑节点，禁止出现未被任何业务逻辑关联的执行本体                                                                                                         |
| **禁止自关联** | `sourceNodeId` 和 `targetNodeId` 不得指向同一节点                                                                                                           |
| **禁止业务逻辑直接指向数据对象** | 业务逻辑不能直接连接数据对象，必须经过执行本体中转。正确路径为：数据对象→业务逻辑→执行本体→数据对象                                                                                                |
| **非对象间边禁止额外字段** | 只有数据对象→数据对象的边才允许传入 `edgeConstraintRule`、`edgeConstraintRuleExample`、`edgeConnectRule`、`edgeConnectRuleExample`，其他类型的边禁止传入这些字段                      |
| **单对象闭环** | 若业务逻辑仅关联单个数据对象，连线形成闭环：对象A→逻辑→执行本体→对象A                                                                                                              |

---

## 对象关系去重（🔴 在构建 edgeList 前强制执行）

从 stage2.md 解析业务对象关系后，构建 edgeList 前必须执行以下去重：

1. **去重规则**：
    - ❌ 禁止存在互逆关系对（如包含 vs 被包含、承载 vs 被承载、映射 vs 被映射）
    - ❌ 禁止存在完全重复的关系（源节点、目标节点、关系名称完全相同）
    - ✅ 关系名称必须使用主动语态（保留"包含"，删除"被包含"）
    - ✅ 同一对象对之间可以有多个不同类型的关系（如映射+约束），但不能有互逆关系

2. **互逆关系对清单**（遇到以下任一对时，只保留主动语态的一方）：
    - 包含 ↔ 被包含/属于
    - 承载 ↔ 被承载
    - 表征 ↔ 被表征
    - 约束 ↔ 被约束
    - 映射 ↔ 被映射
    - 控制 ↔ 被控制
    - 使用 ↔ 被使用
    - 管理 ↔ 被管理

---

## 完整示例

```json
[
  {
    "sourceNodeId": "node_object_2",
    "targetNodeId": "node_object_1",
    "relationName": "承载",
    "edgeConstraintRule": "",
    "edgeConstraintRuleExample": "",
    "edgeConnectRule": "",
    "edgeConnectRuleExample": ""
  },
  {
    "sourceNodeId": "node_object_6",
    "targetNodeId": "node_logic_5",
    "relationName": ""
  },
  {
    "sourceNodeId": "node_logic_1",
    "targetNodeId": "node_execution_1",
    "relationName": ""
  },
  {
    "sourceNodeId": "node_execution_1",
    "targetNodeId": "node_object_3",
    "relationName": ""
  },
  {
    "sourceNodeId": "node_execution_5",
    "targetNodeId": "node_object_6",
    "relationName": ""
  }
]
```
