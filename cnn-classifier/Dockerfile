FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# ====== 关键修复：使用完整的阿里云镜像源替换 ======
# 备份原文件并写入新的源列表
RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo "deb http://mirrors.aliyun.com/debian/ bullseye main non-free contrib" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security bullseye-security main" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 设置阿里云的PyPI镜像
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 下载ImageNet分类标签文件
RUN wget -O imagenet_classes.json \
    https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app/main.py"]