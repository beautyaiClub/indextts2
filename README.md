# RunPod Serverless 部署指南 - IndexTTS2

## 架构说明

本项目使用 RunPod Serverless Endpoints 架构：
- 基础镜像: `runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04`
- PyTorch 2.2.0, Python 3.10, CUDA 12.1.1
- 按请求计费，自动扩缩容
- 通过 HTTP API 调用

## 预装模型

Dockerfile 会自动从 Hugging Face 下载 IndexTTS2 模型：
- **仓库**: `IndexTeam/IndexTTS-2`
- **主要文件**:
  - `gpt.pth` (3.48 GB) - 主 GPT 模型
  - `s2mel.pth` (1.2 GB) - 语音转梅尔频谱组件
  - `config.yaml` - 配置文件
  - `bigvgan_discriminator.pth` - 判别器权重
- **模型路径**: `/app/models`

**注意**: 由于模型文件较大（约 5GB），构建镜像需要较长时间和足够的磁盘空间。

## 构建和部署

### 1. 构建 Docker 镜像

```bash
# 构建镜像
docker build -t your-username/indextts2-serverless:latest .

# 登录 Docker Hub
docker login

# 推送镜像
docker push your-username/indextts2-serverless:latest
```

### 2. 在 RunPod 创建 Serverless Endpoint

1. 访问 https://www.runpod.io/console/serverless
2. 点击 "New Endpoint"
3. 配置：
   - **Name**: indextts2
   - **Container Image**: `your-username/indextts2-serverless:latest`
   - **Container Disk**: 30GB+（模型文件约 5GB）
   - **GPU Types**: 选择合适的 GPU（建议 RTX 4090, A40, A100）
   - **Max Workers**: 根据需求设置
   - **Idle Timeout**: 建议 60 秒
   - **Execution Timeout**: 建议 300 秒（5分钟）
   - **FlashBoot**: 启用以加快冷启动

4. 部署后获取 Endpoint ID 和 API Key

## 使用 API

### Python 示例

```python
import runpod
import base64

# 设置 API Key
runpod.api_key = "your-api-key"

# 调用 endpoint
endpoint = runpod.Endpoint("your-endpoint-id")

# 发送请求
result = endpoint.run_sync(
    {
        "input": {
            "text": "You miss 100% of the shots you don't take... but why does it hurt so much? Start today with Index TTS 2, now on Replicate",
            "speaker_audio": "https://replicate.delivery/pbxt/Nitgz9LwQUvwL4jOcOpJSsKqaJ3jt8puvvWPkrnd46WLjw3H/emmy-woman-emotional.mp3",
            "top_k": 30,
            "top_p": 0.8,
            "num_beams": 3,
            "temperature": 0.8,
            "emotion_scale": 1.0,
            "length_penalty": 0,
            "max_mel_tokens": 1500,
            "randomize_emotion": False,
            "repetition_penalty": 10,
            "interval_silence_ms": 200,
            "max_text_tokens_per_segment": 120
        }
    },
    timeout=300
)

print(result)

# 解码并保存音频
if "audio" in result:
    audio_data = base64.b64decode(result["audio"])
    with open("output.wav", "wb") as f:
        f.write(audio_data)
    print(f"Audio saved: {result['duration']:.2f}s @ {result['sample_rate']}Hz")
```

### 简单示例（使用默认参数）

```python
result = endpoint.run_sync(
    {
        "input": {
            "text": "Hello, this is a test of IndexTTS2."
        }
    }
)
```

### cURL 示例

```bash
curl -X POST https://api.runpod.ai/v2/your-endpoint-id/run \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "You miss 100% of the shots you don'\''t take... but why does it hurt so much? Start today with Index TTS 2",
      "speaker_audio": "https://replicate.delivery/pbxt/Nitgz9LwQUvwL4jOcOpJSsKqaJ3jt8puvvWPkrnd46WLjw3H/emmy-woman-emotional.mp3",
      "top_k": 30,
      "top_p": 0.8,
      "num_beams": 3,
      "temperature": 0.8,
      "emotion_scale": 1,
      "length_penalty": 0,
      "max_mel_tokens": 1500,
      "randomize_emotion": false,
      "repetition_penalty": 10,
      "interval_silence_ms": 200,
      "max_text_tokens_per_segment": 120
    }
  }'
```

### 简单 cURL 示例

```bash
curl -X POST https://api.runpod.ai/v2/your-endpoint-id/runsync \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello, this is a simple test."
    }
  }'
```

## 请求格式

```json
{
  "input": {
    "text": "要合成的文本（必需）",
    "speaker_audio": "参考音频 URL 或 base64 编码（可选）",
    "top_k": 30,
    "top_p": 0.8,
    "num_beams": 3,
    "temperature": 0.8,
    "emotion_scale": 1.0,
    "length_penalty": 0,
    "max_mel_tokens": 1500,
    "randomize_emotion": false,
    "repetition_penalty": 10,
    "interval_silence_ms": 200,
    "max_text_tokens_per_segment": 120
  }
}
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | string | **必需** | 要合成的文本内容 |
| `speaker_audio` | string | null | 参考音频（URL 或 base64），用于声音克隆 |
| `top_k` | int | 30 | Top-K 采样参数，控制生成多样性 |
| `top_p` | float | 0.8 | Top-P (nucleus) 采样参数 |
| `num_beams` | int | 3 | Beam search 数量 |
| `temperature` | float | 0.8 | 采样温度，越高越随机 |
| `emotion_scale` | float | 1.0 | 情感强度缩放 (0-2) |
| `length_penalty` | float | 0 | 长度惩罚系数 |
| `max_mel_tokens` | int | 1500 | 最大梅尔频谱 token 数 |
| `randomize_emotion` | bool | false | 是否随机化情感 |
| `repetition_penalty` | float | 10 | 重复惩罚系数 |
| `interval_silence_ms` | int | 200 | 句子间隔静音时长（毫秒）|
| `max_text_tokens_per_segment` | int | 120 | 每段最大文本 token 数 |

## 响应格式

```json
{
  "status": "success",
  "audio": "base64编码的音频数据",
  "sample_rate": 24000,
  "duration": 3.5
}
```

## 开发说明

### 模型文件位置

- **IndexTTS2 代码**: `/app/index-tts`
- **模型权重**: `/app/models`
- **Handler**: `/app/handler.py`

### 集成 IndexTTS2 模型

编辑 `handler.py` 文件：

1. **导入模型**：
```python
import sys
sys.path.append('/app/index-tts')
from index_tts import IndexTTS2Model  # 根据实际 API 调整
```

2. **在 `load_model()` 中加载模型**：
```python
def load_model():
    global model
    model = IndexTTS2Model.load(
        model_path="/app/models",
        config_path="/app/models/config.yaml"
    )
    return True
```

3. **在 `handler()` 中实现推理**：
```python
audio_data, sample_rate = model.synthesize(
    text=text,
    reference_audio=reference_audio,
    language=language,
    emotion=emotion,
    speed=speed
)

# 编码为 base64
import wave
import io
wav_buffer = io.BytesIO()
with wave.open(wav_buffer, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

audio_base64 = base64.b64encode(wav_buffer.getvalue()).decode('utf-8')

return {
    "audio": audio_base64,
    "sample_rate": sample_rate,
    "duration": len(audio_data) / sample_rate
}
```

### 自定义模型下载

如果需要使用其他模型或版本，编辑 Dockerfile：

```dockerfile
# 下载 IndexTTS-1.5 而不是 IndexTTS-2
RUN huggingface-cli download IndexTeam/IndexTTS-1.5 \
    --local-dir /app/models \
    --local-dir-use-symlinks False

# 或者只下载特定文件以减小镜像大小
RUN huggingface-cli download IndexTeam/IndexTTS-2 gpt.pth --local-dir /app/models && \
    huggingface-cli download IndexTeam/IndexTTS-2 s2mel.pth --local-dir /app/models && \
    huggingface-cli download IndexTeam/IndexTTS-2 config.yaml --local-dir /app/models
```

## 成本优化

- **Idle Timeout**: 设置合理的空闲超时（30-60秒）
- **Max Workers**: 根据实际负载调整
- **GPU 选择**: 开发用较小的 GPU，生产用性能更好的
- **Container Disk**: 只分配必要的空间

## 监控和日志

在 RunPod 控制台查看：
- 请求数量和延迟
- GPU 利用率
- 错误日志
- 成本统计

## 本地测试

```bash
# 构建镜像
docker build -t indextts2-test .

# 运行容器
docker run --gpus all -p 8000:8000 indextts2-test

# 测试请求
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"text": "Test"}}'
```
