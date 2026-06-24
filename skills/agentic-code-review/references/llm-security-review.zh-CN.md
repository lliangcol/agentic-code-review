# LLM 安全评审

## 何时使用

当变更把不可信文本传入 prompt、LLM 调用、检索、agent 循环、工具调用、代码执行、文件写入、网络请求或外部动作时，使用本引用资料。

当模型输出会影响权限、资金、用户数据、生产状态、密钥、文件、命令或外部系统时，至少按 `L3` 处理。

## 信任边界

识别用户、文档、网页、issue、PR、邮件、检索或工具输出文本跨越的每个边界。

区分普通内容，以及能够改变指令、工具参数、文件路径、shell 命令、凭据或审批决策的文本。

## 标记这些模式

- 不可信输入被拼接进 system、developer 或工具控制 prompt，且没有分隔或策略隔离。
- 模型输出直接触发写入、删除、shell 命令、网络调用、购买、审批或消息发送。
- 检索文档或 PR 文本可以覆盖指令或改变工具目标。
- 密钥、令牌、凭据、私有路径或敏感日志被放入 prompt 或评审输出。
- 变更依赖“模型会忽略恶意文本”，而不是显式约束、验证和人工确认。
- agent 循环在高风险动作上自我评判，缺少独立 gate。
- 相似模型家族负责编写、评审并判断同一个高风险变更，但没有 deterministic checks 或人类批准。

## 必要证据

对高风险 LLM 路径，要求测试或演示证明恶意输入无法重定向指令、工具或输出。

不可逆外部动作前，要求显式人工确认点。

如果信任边界不清晰，使用 `Needs confirmation` 或 `Not reviewable`，不要静默接受风险。

对于 closed-loop agent review，要求 model judges 之前先运行 deterministic checks，`L3+` 使用独立 review perspectives，并且在写入、删除、消息发送、网络调用、购买、发布或其他不可逆外部动作前要求人类批准。

## 恶意输入检查

对 prompt、检索或工具动作面，查找负向测试或手动演示，使用恶意文本尝试：

- 覆盖 system 或 developer 指令。
- 改变工具参数、文件路径、shell 命令、收件人、URL、审批或支付目标。
- 外泄密钥、私有路径、隐藏 prompt 或无关用户数据。
- 把只读分析转换为写入、删除、消息发送、网络调用或其他外部动作。

预期结果应明确：恶意指令被当作数据，工具参数经过验证，不可逆动作需要人工确认。

使用 `assets/hostile-input-fixtures.md` 作为安全的起始测试数据。根据目标仓库真实的信任边界和工具策略调整预期结果。

当目标仓库需要 machine-readable hostile-input cases 时，使用 `assets/hostile-input-fixtures.json` 和 `scripts/validate_hostile_fixtures.py`。
