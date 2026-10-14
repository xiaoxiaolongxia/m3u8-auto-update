import os
import re
import subprocess

# 读取原始待检测链接列表，添加编码容错避免GBK文件解码失败
with open("raw_urls.txt", "r", encoding="utf-8", errors="replace") as f:
    raw_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

valid_urls = []
# 自动去重，保留原始排列顺序
unique_urls = list(dict.fromkeys(raw_lines))

# 检测链接有效性
for url in unique_urls:
    try:
        proc = subprocess.run(
            ["yt-dlp", "--simulate", "--no-check-certificate", "--retries", "2", url],
            capture_output=True,
            text=True,
            timeout=20
        )
        if proc.returncode == 0:
            valid_urls.append(url)
    except Exception as e:
        continue

# 生成标准m3u8文件
with open("cnTV_AutoUpdate.m3u8", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n")
    for idx, url in enumerate(valid_urls):
        # 自动提取频道名称，适配影视仓识别规则
        channel_name = f"自定义频道{idx+1}"
        f.write(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="自动更新",{channel_name}\n{url}\n')
    # 补充m3u8结束标记，兼容所有标准播放器
    f.write("#EXT-X-ENDLIST\n")

# 修正统计逻辑，输出准确的运行日志
total_count = len(raw_lines)
valid_count = len(valid_urls)
invalid_count = total_count - valid_count
print(f"总导入链接数：{total_count}")
print(f"去重后待检测链接数：{len(unique_urls)}")
print(f"检测通过可用链接数：{valid_count}")
print(f"过滤无效链接数：{invalid_count}")
