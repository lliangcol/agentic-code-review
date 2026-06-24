# 接入

## 零侵入使用

全局安装 Skill，然后在任意仓库中显式调用。

```text
Use agentic-code-review to review the current branch.
使用 agentic-code-review review 当前分支。
```

## 项目级提示

如果某个仓库需要重复使用，可将 `assets/AGENTS.snippet.md` 内容加入该仓库的 `AGENTS.md`。

将特定仓库的高风险领域保留在目标仓库自己的说明中，不要写死到本通用 Skill。

## 接入画像

对没有用户的个人原型，保持流程轻量：要求真实测试、保持 CI、先读测试变更，并用风险分层避免过度评审可丢弃代码。

对小团队或已有用户的项目，要求评审入口、验证输出、小 PR、`L2+` 回滚说明，以及用户可见或长期变更的人类合并负责人。

对大型或长期系统，把证据作为强制要求：大范围 diff 需要切片图，agent 生成变更需要决策日志，高风险路径需要异构评审，跟踪团队指标，并为承重代码明确人类所有权。

## 阶段转换触发器

出现任一触发器时，切换到更重一级的接入画像：

- 第一个外部用户或客户可见流程。
- 用户数据、删除、认证、权限、支付、账单、密钥或生产配置。
- 共享 ownership、on-call、长期 API 行为、迁移或跨服务协议。
- agent-generated PR volume 导致 review 等待时间、review duration、零 review 合并或 `Not reviewable` 比率上升。
- 变更需要产品判断，但 agent 或提交者没有写下判断依据。

## PR 模板

可将 `assets/pull_request_template.md` 复制到目标项目的 `.github/pull_request_template.md`。

这是可选项，Skill 正常工作不应依赖它。
