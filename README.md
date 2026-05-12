# B站动态监控 - 观势浮生

自动监控UP主 [观势浮生](https://space.bilibili.com/3706967623207490) 的 B站动态，有新内容时推送到钉钉。

## 部署到 GitHub Actions（免费，无需开电脑）

### 第一步：创建 GitHub 仓库
1. 打开 https://github.com/new
2. 仓库名填 `bili-monitor`，选 **Public** 或 **Private** 都可以
3. 点 **Create repository**

### 第二步：上传文件
1. 在仓库页面点 **Add file → Upload files**
2. 把 `D:\bili-monitor\github\` 里面所有文件和文件夹拖进去
3. 点 **Commit changes**

### 第三步：配置 Secrets（敏感信息）
1. 进入仓库 → **Settings → Secrets and variables → Actions**
2. 点 **New repository secret**，依次添加以下 5 个：

| Name | Value |
|------|-------|
| Name | 从哪里获取 |
|------|-----------|
| `BILI_SESSDATA` | B站 F12 → Application → Cookies → `SESSDATA` 的值 |
| `BILI_JCT` | 同位置 → `bili_jct` 的值 |
| `BILI_DEDE_USERID` | 同位置 → `DedeUserID` 的值 |
| `DINGTALK_TOKEN` | 钉钉机器人 Webhook URL 中 `access_token=` 后面的部分 |
| `DINGTALK_SECRET` | 钉钉机器人的 Secret 值 |

### 第四步：配置 Variables（公开信息）
1. 在同一页面点 **Variables → New repository variable**
2. 添加：

| Name | Value |
|------|-------|
| `BILI_UID` | `3706967623207490` |

### 第五步：手动触发一次测试
1. 进入仓库 → **Actions** → **观势浮生动态监控**
2. 点 **Run workflow** → 绿色按钮
3. 等几十秒，看看钉钉有没有收到测试通知

### 第六步：自动运行
配置好后，GitHub Actions 会**每5分钟**自动检查一次，有新动态就推送到钉钉。

### Cookie 过期怎么办？
B站 Cookie 大概几个月过期。过期后：
1. 重新登录 bilibili.com 获取新 Cookie
2. 去仓库 Settings → Secrets 更新 `BILI_SESSDATA`
