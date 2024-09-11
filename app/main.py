from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from loguru import logger
import cv2
from io import BytesIO
import yaml
from rtsp_reader import RTSPStreamReader
from contextlib import asynccontextmanager

# 配置 Loguru 日志，增加日志文件并控制日志大小和保留天数
logger.add("logs/rtsp_capture.log", rotation="10 MB", retention="10 days", level="INFO")

# 加载配置文件
def load_config(config_file: str = 'config.yaml') -> dict:
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Loaded configuration from {config_file}.")
        return config['rtsp_streams']
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        raise e

# 初始化 FastAPI 应用，使用 lifespan 事件处理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时的日志
    logger.info("-----------------Starting FastAPI application and initializing RTSP stream readers.-----------------")

    # 加载 RTSP 流配置
    rtsp_streams = load_config()
    stream_readers = {}

    # 启动所有 RTSP 流读取器
    for stream_name, rtsp_url in rtsp_streams.items():
        try:
            logger.info(f"Initializing RTSP stream for {stream_name} at {rtsp_url}")
            stream_reader = RTSPStreamReader(rtsp_url)
            stream_reader.start()
            stream_readers[stream_name] = stream_reader
            logger.info(f"Successfully started RTSP stream for {stream_name}")
        except Exception as e:
            logger.error(f"Error starting RTSP stream {stream_name}: {e}")

    # 将流读取器存储到 app.state 中
    app.state.stream_readers = stream_readers

    # 继续启动应用
    yield

    # 应用关闭时的日志
    logger.info("Shutting down FastAPI application, stopping RTSP stream readers.")

    # 在应用关闭时停止所有 RTSP 流读取器
    for stream_name, stream_reader in stream_readers.items():
        try:
            stream_reader.stop()
            logger.info(f"Stopped RTSP stream for {stream_name}.")
        except Exception as e:
            logger.error(f"Error stopping RTSP stream {stream_name}: {e}")

# 创建 FastAPI 实例，使用 lifespan 管理应用生命周期
app = FastAPI(lifespan=lifespan)

# 抽帧接口
@app.get("/capture/{stream_name}")
async def capture_image(stream_name: str, request: Request):
    # 获取所有 RTSP 流读取器
    stream_readers = request.app.state.stream_readers

    if stream_name not in stream_readers:
        logger.warning(f"Stream {stream_name} not found in RTSP streams.")
        raise HTTPException(status_code=404, detail="Stream not found")

    # 获取对应的 RTSP 流读取器
    stream_reader = stream_readers[stream_name]
    frame = stream_reader.get_frame()

    if frame is None:
        logger.error(f"Failed to capture frame from {stream_name}. No frame available.")
        raise HTTPException(status_code=500, detail="No frame available")
    
    # 将图片转换为 JPEG 格式
    _, jpeg_image = cv2.imencode('.jpg', frame)

    # 日志记录成功抓拍
    logger.info(f"Successfully captured frame from {stream_name}.")

    # 将图像流返回
    return StreamingResponse(BytesIO(jpeg_image.tobytes()), media_type="image/jpeg")

# 启动 FastAPI 应用
if __name__ == '__main__':
    import uvicorn
    logger.info("Starting the application using Uvicorn.")
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
