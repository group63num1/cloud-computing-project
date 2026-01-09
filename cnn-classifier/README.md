\# CNN图像分类云服务



\## 📖 项目概述

基于PyTorch ResNet18的深度学习图像分类REST API服务，支持1000种ImageNet类别识别。



\## 🚀 快速开始



\### 环境要求

\- Python 3.9+

\- 至少2GB空闲内存

\- Windows/Linux/macOS



\### 安装步骤

```bash

\# 1. 克隆项目

git clone <项目地址>

cd cnn-classifier



\# 2. 创建虚拟环境

python -m venv venv



\# 3. 激活环境 (Windows)
## 部署（本地 & CI/CD）

支持使用 Docker 本地运行以及 GitHub Actions 自动构建并推送到 GitHub Container Registry (GHCR)。

- 本地快速启动（使用 docker-compose）：

```bash
# 在项目根目录运行（会构建镜像并在 8000 端口上启动服务）
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

- 使用 GHCR 自动构建：

1. 将仓库推到 GitHub，主分支为 `main` 或 `master`。
2. 上述 workflow 会在推送时自动构建并将镜像推送到 `ghcr.io/<your-org>/cnn-classifier:latest`。

- 在服务器上从 GHCR 部署：

```bash
./deploy.sh ghcr.io/<your-org>/cnn-classifier:latest
```

注意：将 `<your-org>` 替换为你的 GitHub 组织或用户名；如果使用私有 registry，请确保服务器能登录 GHCR 或使用相应凭据。

**附注**:

- `deploy.sh` 用法：`./deploy.sh <image> [host_port]` 。例如：

```bash
./deploy.sh ghcr.io/my-org/cnn-classifier:latest 8000
```

- 运行前请确保脚本有可执行权限：

```bash
chmod +x deploy.sh
```

环境变量自动登录（可选）:

- 若镜像为私有 registry，可设置 `DOCKER_USERNAME` 与 `DOCKER_PASSWORD` 环境变量，`deploy.sh` 会尝试自动 `docker login`。
- 若使用 GHCR 且想用 token 登录，可设置 `GHCR_TOKEN`（同时 `DOCKER_USERNAME` 为 GH 用户名）。

示例（在服务器上）：

```bash
export DOCKER_USERNAME=myuser
export DOCKER_PASSWORD='s3cr3t'
./deploy.sh ghcr.io/my-org/cnn-classifier:latest 8000
```

## 一键部署（推荐）

如果你想尽可能做到“一键部署”，请按照下面最小步骤：

- 确保脚本有执行权限：

```bash
chmod +x deploy.sh
```

- 本地直接构建并运行（无需参数）：

```bash
./deploy.sh
```

- 或从远端镜像运行：

```bash
# 可选：先登录私有 registry（示例使用环境变量自动登录）
export DOCKER_USERNAME=myuser
export DOCKER_PASSWORD='s3cr3t'
./deploy.sh ghcr.io/my-org/cnn-classifier:latest 8000
```

- 验证服务：

```bash
docker-compose ps
curl http://localhost:8000/health
```

注意：若使用远端私有镜像，确保 `DOCKER_USERNAME`/`DOCKER_PASSWORD` 或 `GHCR_TOKEN` 可用以自动登录。首次启动可能需要下载预训练模型，请确保网络与磁盘空间充足。


venv\\Scripts\\activate



\# 4. 安装依赖

pip install -r requirements.txt



\# 5. 启动服务

python app/main.py

