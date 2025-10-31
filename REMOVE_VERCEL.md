# 移除 Vercel 自动部署

## 问题说明

提交代码到 GitHub 后，Vercel 会自动触发部署。如果你希望停止这个行为，可以按照以下步骤操作。

## 方法 1：在 Vercel 控制台断开 GitHub 连接（推荐）

这是最简单的方法，不会删除项目，只是停止自动部署：

1. **登录 Vercel 控制台**
   - 访问 https://vercel.com
   - 使用你的账户登录

2. **找到项目**
   - 在控制台中找到 `gutendex` 项目
   - 点击进入项目页面

3. **进入设置**
   - 点击项目页面顶部的 "Settings"（设置）选项卡

4. **断开 Git 连接**
   - 在左侧导航栏中选择 "Git"
   - 找到当前连接的 GitHub 仓库信息
   - 点击 "Disconnect"（断开连接）按钮
   - 确认断开连接

完成后，Vercel 将不再监控你的 GitHub 仓库，提交代码时不会自动触发部署。

## 方法 2：删除 Vercel 项目（彻底移除）

如果你不再需要这个 Vercel 项目：

1. **进入项目设置**
   - 登录 Vercel 控制台
   - 进入 `gutendex` 项目
   - 点击 "Settings"（设置）

2. **删除项目**
   - 滚动到设置页面底部
   - 找到 "Delete Project"（删除项目）选项
   - 点击并按照提示确认删除

⚠️ **注意**：删除项目将永久移除所有部署和数据，此操作不可恢复。

## 本地配置

已更新 `.gitignore` 文件，确保以下 Vercel 相关文件不会被提交：

- `.vercel/` - Vercel 配置目录
- `vercel.json` - Vercel 配置文件
- `.vercelignore` - Vercel 忽略文件

## 验证

断开连接后，你可以：
1. 提交一个测试提交到 GitHub
2. 检查 Vercel 控制台，确认没有自动部署被触发

