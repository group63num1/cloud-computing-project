#!/usr/bin/env bash
set -euo pipefail

# Enhanced deploy helper
# - If no image is supplied, builds a local image via docker-compose and runs it.
# - If an image is supplied, attempts to `docker pull` it. If registry credentials
#   are provided via env vars, performs `docker login` automatically.
# Usage:
#   ./deploy.sh                 # build local image and run
#   ./deploy.sh <image>         # pull image and run
#   ./deploy.sh <image> <port>  # pull image and run on host <port>

IMAGE=${1:-}
HOST_PORT=${2:-8000}

# Optional env vars for automatic login:
# - DOCKER_USERNAME and DOCKER_PASSWORD (works for most registries)
# - GHCR_TOKEN (for GitHub Container Registry; DOCKER_USERNAME should be your GH username)

function try_login() {
  local registry="$1"
  if [ -n "${DOCKER_USERNAME:-}" ] && [ -n "${DOCKER_PASSWORD:-}" ]; then
    echo "Logging in to $registry using DOCKER_USERNAME..."
    echo "$DOCKER_PASSWORD" | docker login "$registry" -u "$DOCKER_USERNAME" --password-stdin
  elif [ -n "${GHCR_TOKEN:-}" ] && [ "$registry" = "ghcr.io" ]; then
    echo "Logging in to ghcr.io using GHCR_TOKEN..."
    echo "$GHCR_TOKEN" | docker login ghcr.io -u "${DOCKER_USERNAME:-$USER}" --password-stdin
  fi
}

if [ -z "$IMAGE" ]; then
  echo "No image supplied — will build and run local image via docker-compose."
  IMAGE="cnn-classifier:local"
else
  # derive registry from image (first path component)
  if echo "$IMAGE" | grep -q '/'; then
    REGISTRY=$(echo "$IMAGE" | awk -F/ '{print $1}')
  else
    REGISTRY="docker.io"
  fi

  # attempt login if creds available
  try_login "$REGISTRY"

  echo "Attempting to pull image $IMAGE (pull failures are non-fatal)..."
  docker pull "$IMAGE" || true
fi

# --- 清理旧容器/镜像（避免 docker-compose 重建时报错）
echo "Cleaning previous containers/images for project..."
# 停止并移除由上次 compose 创建的容器与网络（保守模式，非交互）
docker-compose down --remove-orphans --volumes || true

# 移除任何残留的项目容器（名称包含 cnn-classifier）
if docker ps -a --filter name=cnn-classifier --format '{{.ID}}' | grep -q .; then
  docker rm -f $(docker ps -a -q --filter name=cnn-classifier) 2>/dev/null || true
fi

# 如果我们要构建本地镜像，移除旧的本地镜像标签以确保重新打包
if [ "$IMAGE" = "cnn-classifier:local" ]; then
  docker image rm -f cnn-classifier:local 2>/dev/null || true
fi

# 清理未使用的镜像缓存（快速回收）
docker image prune -af || true

export IMAGE_NAME="$IMAGE"
export HOST_PORT="$HOST_PORT"

echo "Starting docker-compose with IMAGE_NAME=$IMAGE_NAME and HOST_PORT=$HOST_PORT..."
docker-compose up -d --build

echo "Deployment finished. Run 'docker-compose ps' to check containers and 'docker-compose logs -f' for logs."
