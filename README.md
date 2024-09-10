# FastAPI RTSP 抓拍服务

## 1 简介
本项目提供了一个基于 FastAPI 的服务，用于从 RTSP 流中捕获帧并通过 HTTP 提供服务。它包括一个用于捕获图像的端点和用于测试服务性能的脚本。

## 2 项目结构

```yaml
RTSP-Capture/
│
├── app/					  # 包含 FastAPI 应用程序组件的目录
│   ├── main.py               # 主 FastAPI 应用程序文件
│   ├── rtsp_reader.py        # RTSP 流读取器类，管理视频流
│   ├── config.yaml           # RTSP 地址的配置文件
│
├── logs/                     # 存储 Loguru 日志文件
│   └── rtsp_capture.log      # 自动轮转的日志文件
│
├── tmp/                      # 存储临时文件（图像和结果）的目录
│   ├── results.csv           # 存储的临时测试结果
│   ├── xxx.jpg               # 存储的临时测试图像
│
├── test_script.py            # 用于测试 RTSP 流捕获服务性能的脚本
│
├── requirements.txt          # 项目依赖文件
│
└── README.md                 # 项目说明文件
```

## 3 安装与配置

### 3.1 先决条件

- Python 3.12.4 或更高版本
- 必需的库 (`fastapi`, `httpx`, `loguru` 等)
- 可用的 RTSP 流

### 3.2 安装

1.解压代码压缩包：

```
cd RTSP-Capture
```

2.安装依赖项：

```
pip install -r requirements.txt
```

### 3.3 配置

在 `app` 目录下创建 `config.yaml` 文件，其结构如下：

```yaml
rtsp_streams:
  "camera_id_1": "rtsp://example.com/camera1"
  "camera_id_2": "rtsp://example.com/camera2"
  # 如需添加更多摄像头，请继续添加
```

## 4 运行服务

启动 FastAPI 服务：

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://127.0.0.1:8000` 上运行。host要改为本机IP

## 5 测试

为了测试服务并测量从 RTSP 流捕获图像的性能：

1. 确保服务正在运行。

2. 运行测试脚本：

```python
python test_script.py
```

   测试脚本执行以下操作：

- 向 `/capture/{stream_name}` 端点发送 100 次连续请求。
- 测量每次请求所需的时间。
- 将捕获的图像保存到 `tmp/` 目录。
- 将所用时间保存到名为 `tmp/results.csv` 的 CSV 文件中。

测试脚本的输出将被记录到控制台，并将所用时间的摘要保存到 `tmp/results.csv`。

## 6 调用接口示例

要从特定的 RTSP 流中获取图像，请使用如下命令：

```sh
curl -X GET "http://127.0.0.1:8000/capture/{{camera_id_1}}"
```

这将返回图像的 JPEG 格式数据。你可以将响应保存为文件，例如：

```sh
curl -X GET "http://127.0.0.1:8000/capture/camera_id_1" -o image.jpg
```

## 7 故障排除

如果在设置或测试过程中遇到问题，请检查服务生成的日志 (`logs/rtsp_capture.log`) 和测试脚本的控制台输出以查找错误消息。
