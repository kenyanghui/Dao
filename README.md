# 玄龙堂网站

本仓库直接通过 GitHub Pages 部署根目录中的静态 HTML，无需构建步骤。

## 本地预览

```bash
python3 -m http.server 8000
```

访问 `http://localhost:8000/`。修改页面后，应至少检查首页、打坐实证页、移动端导航和站内链接。

## 目录约定

- `index.html`：线上主页。
- `assets/`：公共样式和脚本。
- `cover-image/`：线上图片素材，使用压缩后的 JPEG。
- `dao-cultivation/`：本地 Vite 原型，当前不参与 GitHub Pages 部署。
- `sitemap.xml`、`robots.txt`：搜索引擎入口。

## 发布检查

1. 确认所有本地 `href` 和 `src` 指向存在的文件。
2. 新页面补充 description、canonical 和 Open Graph 信息。
3. 图片优先控制在 500 KB 以内，并在提交前检查画质。
