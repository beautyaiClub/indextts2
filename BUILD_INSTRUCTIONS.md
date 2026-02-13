# 构建和部署指南

## 前置要求

1. Docker 已安装
2. Docker Hub 账号
3. RunPod 账号和 API Key
4. 足够的磁盘空间（至少 20GB）

## 步骤 1: 构建 Docker 镜像

```bash
# 克隆或进入项目目录
cd /path/to/indextts2

# 构建镜像（这将需要较长时间，因为要下载约 5GB 的模型）
docker build -t your-dockerhub-username/indextts2-serverless:latest .

# 预计构建时间：20-40 分钟（取决于网络速度）
```

## 步骤 2: 推送到 Docker Hub

```bash
# 登录 Docker Hub
docker login

# 推送镜像
docker push your-dockerhub-username/indextts2-serverless:latest
```

## 步骤 3: 在 RunPod 创建 Serverless Endpoint

1. 访问 https://www.runpod.io/console/serverless
2. 点击 "New Endpoint"
3. 填写配置：
   - **Endpoint Name**: indextts2
   - **Container Image**: `your-dockerhub-username/indextts2-serverless:latest`
   - **Container Disk**: 30GB
   - **GPU Types**: 选择 RTX 4090 或 A40（推荐）
   - **Max Workers**: 3-5（根据预算调整）
   - **Idle Timeout**: 60 秒
   - **Execution Timeout**: 300 秒
   - **FlashBoot**: 启用（加快冷启动）

4. 点击 "Deploy"

## 步骤 4: 测试 Endpoint

获取 Endpoint ID 和 API Key 后：

```bash
# 安装 runpod Python SDK
pip install runpod

# 运行测试脚本
python test_endpoint.py YOUR_ENDPOINT_ID YOUR_API_KEY
```

## 步骤 5: 集成到应用

参考 README.md 中的 API 使用示例。

## 故障排查

### 构建失败
- 检查网络连接（需要下载模型）
- 确保有足够的磁盘空间
- 如果 Hugging Face 下载失败，可能需要设置镜像或代理

### 运行时错误
- 检查 RunPod 日志
- 确认模型文件已正确下载到镜像中
- 验证 GPU 内存是否足够

### 冷启动慢
- 启用 FlashBoot
- 考虑使用 RunPod 的 Network Volume
- 增加 Idle Timeout 以保持 worker 活跃

## 成本估算

- **构建**: 免费（本地构建）
- **存储**: Docker Hub 免费层或 RunPod Registry
- **运行**: 按 GPU 使用时间计费
  - RTX 4090: ~$0.40/小时
  - A40: ~$0.60/小时
  - 仅在处理请求时计费

## 优化建议

1. **减小镜像大小**: 只下载必需的模型文件
2. **使用缓存**: 利用 Docker 层缓存加快重建
3. **监控使用**: 定期检查 RunPod 控制台的成本和性能指标
