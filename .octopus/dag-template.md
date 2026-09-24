# 玄龙堂 · 任务 DAG 模板

> 借鉴 octopus-workflow analyze-dag：一个 Epic 只产出**一个任务 DAG**，
> 节点=验收标准，边=契约，拓扑=执行计划。矩阵节点从 `matrix-nodes.json` 选派。

```yaml
epic: <slug>                    # 例：card-search
created: <date>
owner: <人或 agent>
nodes:                          # 每个节点是一条可独立验收的任务
  - id: n1
    title: <做什么>
    acceptance: <怎样算完成>     # 节点即验收标准
    assignee:                   # 矩阵节点选派
      node: loong               # 开发主力（dev-primary）
    outputs: [<产物路径>]        # 产物落盘地址（artifact addressing）
  - id: n2
    title: <做什么>
    acceptance: <怎样算完成>
    assignee:
      node: xuan                # 部署主力（deploy-primary）
    needs: [n1]                 # 边 = 依赖/契约：n2 消费 n1 的产物
    contract: <n1 产物如何被 n2 消费>
edges:                          # 显式声明（与 needs 等价的汇总视图）
  - from: n1
    to: n2
    contract: <接口/文件/数据契约>
gates:                          # 单门审查（review-dag）
  - after: [n1, n2]
    check: python3 scripts/check_site.py
fanout:                         # 可并行节点 → 扇出到算力矩阵
  - nodes: [n3, n4, n5]         # 互不依赖的任务
    to: [daoxia-gz, liangma-sv] # compute 角色
```

## 规则

1. **拓扑即计划**：先画 DAG 再开工；有 `needs` 的节点不得提前执行。
2. **节点即验收**：每节点必须写 `acceptance`，能被 `check_site.py` 或等价命令验证。
3. **产物寻址**：跨节点交付物必须落盘到 `docs/matrix-runs/<epic>/<node-id>/`。
4. **并行扇出**：无依赖节点按 `fanout` 扇出到 compute 节点；开发收口到 loong，部署收口到 xuan。
5. **单门审查**：所有节点完成后跑一次守卫（`scripts/check_site.py`），全绿才算 Epic 完成。
