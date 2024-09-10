import httpx
import time
import csv
import os
from loguru import logger


# 定义一个异步函数来进行测试
async def test_rtsp_stream_capture(stream_name: str, index: int):
    # API URL
    url = f"http://127.0.0.1:8000/capture/{stream_name}"

    # 记录开始时间
    start_time = time.time()

    # 使用 httpx 发送 GET 请求
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    # 计算结束时间
    end_time = time.time()

    # 检查状态码是否为 200
    if response.status_code == 200:
        elapsed_time = end_time - start_time
        logger.info(f"Received image from {stream_name} on iteration {index + 1}. Status code: {response.status_code}, Time elapsed: {elapsed_time:.3f}s")
        # 将响应内容保存为文件进行验证
        with open(f'tmp/test_{index}.jpg', 'wb') as f:
            f.write(response.content)
        return elapsed_time
    else:
        logger.error(f"Failed to receive image from {stream_name} on iteration {index + 1}. Status code: {response.status_code}")
        return None

# 运行测试
async def main():
    stream_name = "192168116811"
    num_tests = 100
    results = []

    # 创建临时文件夹
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    # 开始测试
    logger.info("Starting the tests.")
    for i in range(num_tests):
        elapsed_time = await test_rtsp_stream_capture(stream_name, i)
        if elapsed_time is not None:
            results.append((i + 1, elapsed_time))

    # 将结果保存到 CSV 文件
    with open('tmp/results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Iteration', 'Elapsed Time (s)'])
        writer.writerows(results)

    logger.info("Tests completed. Results saved to tmp/results.csv.")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())