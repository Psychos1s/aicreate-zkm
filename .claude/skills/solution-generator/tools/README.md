# 约束元工具说明

## 工具概述

本目录包含两个工具脚本：

1. `get-constraint-meta.sh` - 获取完整的约束元数据
2. `get-constraint-meta-empty.sh` - 模拟未获取到约束元的情况（测试用）

## 文件位置

```
.claude/skills/solution-generator/tools/get-constraint-meta.sh
.claude/skills/solution-generator/tools/get-constraint-meta-empty.sh
```

## 工具1：get-constraint-meta.sh

返回包含6个核心数据对象的完整本体结构定义：

1. **模糊的意图** - 需求的归纳总结和规范化处理
2. **目标客群** - 有共同特征且存在需求的客户群体
3. **需求价值指标** - 用于识别、衡量和满足需求的指标体系
4. **特征标签** - 描述目标客群特征的标签参数
5. **清晰的意图** - 融合分析结果后的详细需求结构
6. **需要的能力** - 转化为对供给方能力的需求

## 使用方法

### 在命令行中使用

```bash
bash .claude/skills/solution-generator/tools/get-constraint-meta.sh
```

### 在 Skill 中使用

在步骤2（生成数据模型）中，使用 Bash 工具调用：

```
使用 Bash 工具执行：
bash .claude/skills/solution-generator/tools/get-constraint-meta.sh
```

## 输出格式

输出为 Markdown 格式，包含：

- 对象定义
- 对象属性（表格形式）
- 关联关系（表格形式）
- 示例说明
- 补充说明

## 数据结构示例

### 对象定义
```markdown
## 2.1 对象1：模糊的意图

**定义**：对同一类需求的归纳总结和规范化处理...

**属性**：
| 属性名称 | 定义 | 规则 |
|---------|------|------|
| 需求名称 | ... | ... |
```

### 关联关系
```markdown
**关联关系**：
| 关联对象 | 关系名称 | 关联规则 |
|---------|---------|---------|
| 模糊的意图 | 承载 | ... |
```

## 在 Skill 中的应用

### 步骤2：生成数据模型

1. 首先调用此工具获取约束元
2. 将约束元内容展示给用户
3. 询问用户是否需要补充
4. 基于约束元和用户反馈，分析具体的数据对象

### 示例流程

```
1. 执行工具获取约束元
   → bash .claude/skills/solution-generator/tools/get-constraint-meta.sh

2. 展示约束元给用户
   → "已查到本领域必须涉及的核心的数据对象如下所示..."

3. 用户确认或补充
   → 根据反馈调整数据对象

4. 生成最终的数据模型
   → 写入解决方案文档
```

## 约束元包含的核心概念

### 关系类型
- 承载
- 被表征
- 包含 / 被包含
- 映射
- 约束 / 被约束

### 指标维度
- 功能
- 质量
- 数量
- 交付
- 情感
- 价格

### 特征维度
- 行为偏好特征（决策偏好、历史行为）
- 商业运营特征（战略方向、经营策略、商业模式）
- 系统机理特征（材料条件、工艺条件、设备条件、能源动力条件）

### 诊断规则类型
1. 基于数理逻辑定义的计算函数
2. 基于机理规则定义的物理、化学方程式
3. 基于商业经验构建的分析模型
4. 基于行为规律总结的经验模型
5. 自定义的其他诊断规则

## 测试工具

### 测试 get-constraint-meta.sh
```bash
# 查看完整输出
bash .claude/skills/solution-generator/tools/get-constraint-meta.sh

# 查看前30行
bash .claude/skills/solution-generator/tools/get-constraint-meta.sh | head -30

# 搜索特定对象
bash .claude/skills/solution-generator/tools/get-constraint-meta.sh | grep -A 10 "模糊的意图"
```

### 测试 get-constraint-meta-empty.sh
```bash
# 应该返回空数组 []
bash .claude/skills/solution-generator/tools/get-constraint-meta-empty.sh
```

## 工具2：get-constraint-meta-empty.sh

### 功能说明
模拟未获取到约束元的情况，返回空数组 `[]`。

### 使用场景
用于测试在没有约束元的情况下，系统如何完全依靠主动分析来生成数据对象。这个工具帮助验证：
- 系统在缺少约束元时的处理逻辑
- 主动分析数据对象的能力
- 错误处理和降级方案

### 使用方法

#### 在命令行中使用
```bash
bash .claude/skills/solution-generator/tools/get-constraint-meta-empty.sh
```

#### 在 Skill 中使用
在步骤2（生成数据模型）中，可以临时替换工具调用来测试无约束元场景：

```bash
# 将这行
bash .claude/skills/solution-generator/tools/get-constraint-meta.sh

# 替换为
bash .claude/skills/solution-generator/tools/get-constraint-meta-empty.sh
```

### 预期行为
当使用此工具时，系统应该：
1. 识别返回的是空数组
2. 跳过展示约束元的步骤
3. 直接进入主动分析数据对象的流程
4. 完全依靠对需求的理解来生成数据模型

## 注意事项

1. 工具返回的是 mock 数据，用于演示和参考
2. 实际使用时，可以根据具体领域替换为真实的约束元数据
3. 约束元是数据对象分析的参考基础，不是唯一依据
4. 需要结合用户的具体需求和业务场景进行调整

## 扩展方向

1. 支持从数据库或 API 获取约束元
2. 支持多领域的约束元切换
3. 支持约束元的动态更新
4. 添加约束元的验证机制
