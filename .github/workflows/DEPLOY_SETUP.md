# GitHub Actions 自动部署配置指南

## 📋 前置条件

1. 阿里云 ECS 服务器已配置好
2. 服务器上已安装 Git 和 Docker（如果使用 Docker 部署）
3. 服务器上已克隆了三个仓库（backend, frontend, worker）

## 🔑 配置 GitHub Secrets

在每个仓库（backend, frontend, worker）的 GitHub 设置中添加以下 Secrets：

### 1. 进入仓库设置
- 打开仓库 → Settings → Secrets and variables → Actions → New repository secret

### 2. 添加以下 Secrets

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `ALIYUN_SSH_PRIVATE_KEY` | SSH 私钥（完整内容，包括 `-----BEGIN` 和 `-----END`） | 见下方说明 |
| `ALIYUN_SERVER_HOST` | 服务器 IP 地址或域名 | `47.xxx.xxx.xxx` |
| `ALIYUN_SSH_USER` | SSH 用户名 | `root` 或 `ubuntu` |
| `ALIYUN_PROJECT_PATH` | 服务器上的项目根目录路径 | `/opt/booklook` |

## 🔐 生成 SSH 密钥对

### 方法 1：使用现有密钥（推荐）

如果您已经有 SSH 密钥：

```bash
# 查看现有密钥
cat ~/.ssh/id_rsa  # 或 id_ed25519

# 复制私钥内容（完整内容，包括 -----BEGIN 和 -----END）
```

### 方法 2：生成新密钥

```bash
# 生成新的 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# 查看私钥（复制完整内容到 GitHub Secrets）
cat ~/.ssh/github_actions_deploy

# 将公钥添加到服务器
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub root@您的服务器IP
```

## 📝 配置步骤

### 1. 在服务器上准备项目目录

```bash
# 创建项目目录
mkdir -p /opt/booklook
cd /opt/booklook

# 克隆三个仓库（如果还没有）
git clone https://github.com/wuyyybbb/booklook_backend.git backend
git clone https://github.com/wuyyybbb/booklook_frontend.git frontend
git clone https://github.com/wuyyybbb/booklook_worker.git worker
```

### 2. 配置 GitHub Secrets

对每个仓库（backend, frontend, worker）重复以下步骤：

1. 打开仓库：`https://github.com/wuyyybbb/booklook_backend`（或 frontend/worker）
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下 4 个 Secrets：
   - `ALIYUN_SSH_PRIVATE_KEY`：您的 SSH 私钥
   - `ALIYUN_SERVER_HOST`：服务器 IP（如 `47.xxx.xxx.xxx`）
   - `ALIYUN_SSH_USER`：SSH 用户名（如 `root`）
   - `ALIYUN_PROJECT_PATH`：项目路径（如 `/opt/booklook`）

### 3. 测试部署

1. 在仓库中创建一个测试提交
2. 推送到 `main` 分支
3. 打开 **Actions** 标签页查看部署进度

## 🚀 工作流说明

### 触发条件

- **自动触发**：推送到 `main` 分支时
- **手动触发**：在 Actions 页面点击 "Run workflow"

### 部署流程

1. **Backend 仓库**：
   - 拉取最新代码
   - 使用 Docker Compose 重新构建并重启服务

2. **Frontend 仓库**：
   - 拉取最新代码
   - 安装依赖并构建
   - 重启 Nginx（如果配置了）

3. **Worker 仓库**：
   - 拉取最新代码
   - 重新构建并重启 Worker 容器

## ⚠️ 注意事项

1. **首次部署**：确保服务器上已正确配置 `.env` 文件
2. **SSH 密钥安全**：不要将私钥提交到代码仓库
3. **服务器权限**：确保 SSH 用户有执行 Docker 命令的权限
4. **网络访问**：确保 GitHub Actions 可以访问您的服务器（可能需要配置防火墙）

## 🔧 故障排查

### 问题 1：SSH 连接失败

```bash
# 在服务器上检查 SSH 服务
sudo systemctl status sshd

# 检查防火墙
sudo ufw status
```

### 问题 2：Docker 权限问题

```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER
```

### 问题 3：查看部署日志

在 GitHub Actions 页面查看详细的部署日志

## 📞 需要帮助？

如果遇到问题，请检查：
1. GitHub Secrets 是否正确配置
2. 服务器 SSH 服务是否正常运行
3. 项目路径是否正确

