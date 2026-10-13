import os
import re
import subprocess

# 读取原始待检测链接列表
with open("raw_urls.txt", "r", encoding="utf-8") as f:
    raw_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

valid_urls = []
# 自动去重
unique_urls = list
(dict.fromkeys(raw_lines))

# 检测链接有效性
for url in unique_urls:
    try:
        proc = subprocess.run(
            ["yt-dlp", "--simulate", "--no-check-certificate", "--retries", "2", url],
            capture_output=True,
            timeout=20
        )
        if proc.returncode == 0:
            valid_urls.append(url)
    except:
        continue

# 生成标准m3u8文件
with open("cnTV_AutoUpdate.m3u8", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n")
    for idx, url in enumerate(valid_urls):
        # 自动提取频道名称，适配影视仓识别规则
        channel_name = f"自定义频道{idx+1}"
        f.write(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="自动更新",{channel_name}\n{url}\n')
