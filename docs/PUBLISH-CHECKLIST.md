# 发布清单 (PUBLISH-CHECKLIST)

每次迭代发布前按序执行，全部通过才推送。

## 1. 内容更新

- [ ] 新卡 txt 遵循现有结构：诗 → 篇名 → 寓言 → 点睛 → 一悟/一问/一行
- [ ] 新卡 png 与 txt 编号配对，放入对应卡组目录

## 2. 构建

- [ ] `python3 scripts/build_cards.py --images`（压缩新图 + 重建 JSON）
- [ ] 确认输出无 WARN（jpg 缺失）

## 3. 漂移守卫

- [ ] `python3 scripts/check_site.py` 通过（链接 / 图片体积 / 数据一致性 / 编码 / SEO）

## 4. 本地预览

- [ ] `python3 -m http.server 8000`
- [ ] 首页：今日一签正常显示
- [ ] cards.html：筛选 tab、卡片弹窗、深链（如 `#zonghui-03`）正常
- [ ] 移动端（≤640px）导航与网格正常

## 5. 提交规范

- [ ] 提交信息格式：`类型: 摘要`（类型：content / fix / feat / chore）
- [ ] 单次提交尽量单一目的，不混内容与代码改动

## 6. 发布后

- [ ] GitHub Pages 站点抽查首页与卡集页
- [ ] `.original-png-backup/` 确认线上画质后可清理对应原始 png

## 7. 矩阵并行（可选，大迭代时启用）

- [ ] `python3 scripts/matrix.py health` 确认目标节点在线
- [ ] 按 `.octopus/dag-template.md` 拆解任务 DAG（无依赖节点才可扇出）
- [ ] `python3 scripts/matrix.py fanout <epic> 任务.md...` 生成分派
- [ ] 浏览器 web 直连各节点，投喂 `docs/matrix-runs/<epic>/prompts/` 任务包
- [ ] 各节点产物回收到 `docs/matrix-runs/<epic>/<node-id>/`，收口跑守卫
