# 智能冰箱 Web Demo

面向黑客松的最小可运行闭环：上传冰箱照片 → AI（Mock）识别食材 → 确认入库 → 一键生成今日菜单 + 营养指标 + 购物清单。

## 功能概览
- 上传/拖拽冰箱照片（单张）
- 点击“识别食材”，Mock AI 返回 6-10 个常见食材
- 在表格中编辑/确认（名称、数量、单位、类别）并入库
- 生成 2 菜 1 汤菜单 + 营养指标 + 购物清单

## 本地启动

```bash
npm install
npm run dev
```

打开 [http://localhost:3000](http://localhost:3000)。

## 数据与 Mock 模式
- 菜谱数据保存在 `data/recipes.json`（至少 20 道）。
- 默认启用 Mock 识别，无需任何 API key。
- 库存写入 `data/inventory.json`；如果在无持久化写入的环境（如 Vercel）部署，系统会自动切换为内存存储（刷新或实例重启会重置）。

## Real Provider（可选）
如需接入真实识别服务：

```bash
export REAL_VISION_ENDPOINT="https://your-endpoint.com/detect"
```

接口收到 `POST { imageName }` 后返回 `DetectedIngredient[]` 即可。若请求失败会自动回退到 Mock。

## Vercel 部署
1. 将仓库推送到 GitHub。
2. 在 Vercel 导入该仓库，保持默认设置。
3. 如需真实识别，配置环境变量 `REAL_VISION_ENDPOINT`。

> 注意：Vercel 的无状态运行环境无法持久化写入 JSON 文件，Demo 会使用内存缓存，刷新或重启会清空库存；用于演示闭环足够。

## 演示流程（无 Key）
1. 进入 `/add` 上传照片（任意图片）。
2. 点击“识别食材”，得到 Mock 列表。
3. 编辑并点击“确认入库”。
4. 前往 `/menu` 生成今日菜单和购物清单。

---

如需扩展到生产环境，可将存储切换到数据库（例如 SQLite + Prisma）。
