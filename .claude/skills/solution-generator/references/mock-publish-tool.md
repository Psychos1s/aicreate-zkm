# Mock 发布约束模型工具说明

## 工具用途

当目标类型为约束模型且用户确认发布时，使用此 mock 工具模拟发布约束模型到运营平台的过程。

## 使用场景

在 `ability-model` 子 skill 中，当满足以下条件时使用：
1. 全局上下文中的"目标类型" = "约束模型"
2. 约束模型已生成完成
3. 用户确认直接发布约束模型

## 使用方法

使用 Bash 工具执行以下命令：

```bash
echo "正在发布约束模型..."
sleep 1
echo "约束模型已成功发布到运营平台"
echo "约束模型 ID: [从 当前进度.md 读取的 abilityModelId 或新生成的 ID]"
echo "发布时间: $(date '+%Y-%m-%d %H:%M:%S')"
```

## 执行步骤

1. **读取约束模型 ID**：
   - 从 `当前进度.md` 中读取 `abilityModelId`
   - 如果不存在，生成一个新的 ID（例如：`MOCK-${RANDOM}`）

2. **执行 mock 发布命令**：
   ```bash
   ABILITY_MODEL_ID=$(grep "约束模型 ID" /Users/wangjisi/code/mine-know当前进度.md | cut -d: -f2 | xargs)
   if [ -z "$ABILITY_MODEL_ID" ] || [ "$ABILITY_MODEL_ID" = "无" ]; then
     ABILITY_MODEL_ID="MOCK-$RANDOM"
   fi

   echo "正在发布约束模型..."
   sleep 1
   echo "约束模型已成功发布到运营平台"
   echo "约束模型 ID: $ABILITY_MODEL_ID"
   echo "发布时间: $(date '+%Y-%m-%d %H:%M:%S')"
   ```

3. **更新当前进度**：
   - 使用 Edit 工具更新 `当前进度.md`
   - 标记阶段 2 为已完成
   - 标记阶段 3 为已跳过
   - 更新完成时间

4. **向用户展示结果**：
   ```
   约束模型已成功发布！

   发布信息：
   - 约束模型 ID: [ID]
   - 发布时间: [时间]
   - 文档位置: /output/约束模型.md

   方案生成已完成，所有交付物已保存在 /output/ 目录。
   ```

## 注意事项

1. **这是 mock 工具**：实际生产环境中，需要替换为真实的 MCP 工具调用
2. **ID 生成规则**：
   - 如果配置文件中已有 `abilityModelId`，使用该 ID
   - 如果没有，生成格式为 `MOCK-[随机数]` 的临时 ID
3. **更新进度文档**：发布成功后，必须更新《当前进度.md》，标记流程完成
4. **跳过阶段 3**：发布约束模型后，阶段 3（生成运行逻辑）将被跳过

## 真实工具接口（待实现）

真实的发布工具应该具有以下接口：

```
工具名称: mcp__constraint_model__publish
参数:
  - constraint_model_path: 约束模型文档路径
  - constraint_model_content: 约束模型内容（JSON 格式）
  - is_strict_mode: 是否严格模式（boolean）
返回:
  - ability_model_id: 发布后的约束模型 ID
  - publish_time: 发布时间
  - status: 发布状态（success / failed）
  - message: 发布消息
```

## 示例

### 示例 1：使用现有 ID

```bash
# 从当前进度.md 读取 ID
ABILITY_MODEL_ID="133505"

echo "正在发布约束模型..."
sleep 1
echo "约束模型已成功发布到运营平台"
echo "约束模型 ID: $ABILITY_MODEL_ID"
echo "发布时间: 2026-05-02 14:30:00"
```

### 示例 2：生成新 ID

```bash
# 生成新 ID
ABILITY_MODEL_ID="MOCK-12345"

echo "正在发布约束模型..."
sleep 1
echo "约束模型已成功发布到运营平台"
echo "约束模型 ID: $ABILITY_MODEL_ID"
echo "发布时间: 2026-05-02 14:30:00"
```

---

**创建日期**：2026-05-02
**版本**：1.0
**状态**：Mock 实现，待替换为真实 MCP 工具
