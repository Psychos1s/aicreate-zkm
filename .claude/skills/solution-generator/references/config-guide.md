# .app_config.json 配置说明

## 配置文件位置

项目根目录：`.app_config.json`

## 配置字段说明

### solution-generator 相关字段

| 字段 | 类型 | 必填 | 说明 | 可选值 |
|------|------|------|------|--------|
| `source` | string | 是 | 领域类型 | `layer2`（基础领域/通用领域）<br>`layer3`（特定行业领域） |
| `modelType` | string | 是 | 是否需智 | `need`（需智）<br>其他值（非需智，如 `default`） |
| `target` | string | 是 | 目标类型 | `constraint-model`（约束模型）<br>`app-model`（运行模型） |

### 其他字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `env` | string | 环境配置（如 `fat`、`prod`） |
| `ennunifiedauthorization` | string | 统一认证 token |
| `ennunifiedcsrftoken` | string | CSRF token |

## 配置示例

### 示例 1：基础领域 + 运行模型（默认配置）

```json
{
  "env": "fat",
  "source": "layer3",
  "modelType": "need",
  "target": "app-model"
}
```

**说明**：
- 领域类型：基础领域（通用领域）
- 不是需智
- 目标类型：运行模型
- 不存在约束模型
- **执行流程**：完整三阶段（需求分析 → 业务模型 → 运行逻辑）

### 示例 2：特定行业领域 + 运行模型

```json
{
  "env": "fat",
  "source": "layer3",
  "modelType": "need",
  "target": "app-model"
}
```

**说明**：
- 领域类型：特定行业领域
- 不是需智
- 目标类型：运行模型
- 不存在约束模型
- **执行流程**：完整三阶段，阶段 2 会提取对象实例

### 示例 3：基础领域 + 约束模型

```json
{
  "env": "fat",
  "source": "layer2",
  "modelType": "need",
  "target": "constraint-model"
}
```

**说明**：
- 领域类型：基础领域
- 不是需智
- 目标类型：约束模型
- 不存在约束模型
- **执行流程**：阶段 1 → 阶段 2（生成约束模型）→ 可选择直接发布或继续阶段 3

### 示例 4：需智 + 运行模型 + 已有约束模型

```json
{
  "env": "fat",
  "source": "layer3",
  "modelType": "need",
  "target": "app-model"
}
```

**说明**：
- 领域类型：特定行业领域
- 是需智
- 目标类型：运行模型
- 存在约束模型（ID: 133505）
- **执行流程**：
  * 初始化时自动获取约束模型
  * 阶段 2 会基于约束模型初始化业务模型
  * 如果是严格模式，不允许扩展

### 示例 5：特定行业领域 + 约束模型 + 已有约束模型

```json
{
  "env": "fat",
  "source": "layer3",
  "modelType": "default",
  "target": "constraint-model"
}
```

**说明**：
- 领域类型：特定行业领域
- 不是需智
- 目标类型：约束模型
- 存在约束模型（ID: 133505）
- **执行流程**：
  * 初始化时自动获取约束模型
  * 阶段 2 会引导用户修改和确认约束模型

## 字段影响说明

### `source` 字段的影响

- **`layer2`（基础领域）**：
  * 阶段 2 不需要提取对象实例
  * 只生成对象结构（数据对象、业务逻辑对象、关系）

- **`layer3`（特定行业领域）**：
  * 阶段 1 如果有约束模型，需要挖掘业务逻辑对象的具体内容
  * 阶段 2 必须提取所有对象的实例
  * 对象实例只能从上下文或访谈获取，不能 AI 自行推测

### `modelType` 字段的影响

- **`need`（需智）**：
  * 试运行时处理方式不同（具体逻辑待实现）

- **其他值（非需智）**：
  * 按标准流程处理

### `target` 字段的影响

- **`constraint-model`（约束模型）**：
  * 阶段 2 生成约束模型
  * 用户可以选择直接发布约束模型，跳过阶段 3
  * 约束模型包含"使用方式"（严格模式 or 非严格模式）

- **`app-model`（运行模型）**：
  * 阶段 2 生成业务模型
  * 必须完成阶段 3（生成运行逻辑）

## 测试场景

### 场景 1：从零开始生成运行模型（最常见）

```json
{
  "source": "layer2",
  "modelType": "default",
  "target": "app-model"
}
```

### 场景 2：基于约束模型生成运行模型

```json
{
  "source": "layer3",
  "modelType": "default",
  "target": "app-model"
}
```

### 场景 3：生成约束模型

```json
{
  "source": "layer2",
  "modelType": "default",
  "target": "constraint-model"
}
```

### 场景 4：修改已有约束模型

```json
{
  "source": "layer3",
  "modelType": "default",
  "target": "constraint-model"
}
```

---

**创建日期**：2026-05-02
**版本**：1.0
**适用范围**：solution-generator 及其子 skill
