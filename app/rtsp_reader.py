import threading
import time
import cv2
from loguru import logger

class RTSPStreamReader:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.frame = None
        self.cap = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """启动后台线程，开始读取RTSP流"""
        self.running = True
        self.cap = cv2.VideoCapture(self.rtsp_url)
        thread = threading.Thread(target=self._update_frame, daemon=True)
        thread.start()

    def _update_frame(self):
        """后台线程持续更新最新的帧"""
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    logger.error(f"Failed to read frame from {self.rtsp_url}")
                    time.sleep(1)
                    continue
                # 使用锁保护帧更新
                with self.lock:
                    self.frame = frame
            else:
                logger.error(f"RTSP stream {self.rtsp_url} is not opened. Retrying in 1 seconds.")
                time.sleep(1)
                self.cap.open(self.rtsp_url)

    def get_frame(self):
        """获取最新的帧"""
        with self.lock:
            return self.frame

    def stop(self):
        """停止流读取"""
        self.running = False
        if self.cap:
            self.cap.release()
        logger.info(f"RTSP stream {self.rtsp_url} stopped.")
