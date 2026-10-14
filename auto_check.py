import os
import re
import requests

with open("raw_urls.txt", "r", encoding="utf-8", errors="replace") as f:
    raw_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

unique_urls = list(dict.fromkeys(raw_lines))

valid_urls = []

for url in unique_urls:
    try:
        resp = requests.head(
            url,
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code == 200:
            try:
                r = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "Mozilla/5.0"})
                sample = r.raw.read(2048).decode("utf-8", errors="ignore")
                if "#EXTM3U" in sample:
                    valid_urls.append(url)
                    continue
            except Exception:
                pass
    except Exception:
        pass

with open("cnTV_AutoUpdate.m3u8", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for idx, url in enumerate(valid_urls):
        channel_name = f"自定义频道{idx + 1}"
        f.write(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="自动更新",{channel_name}\n{url}\n')
    f.write("#EXT-X-ENDLIST\n")

total_count = len(raw_lines)
unique_count = len(unique_urls)
valid_count = len(valid_urls)
invalid_unique = unique_count - valid_count

print(f"总导入链接数：{total_count}")
print(f"去重后待检测链接数：{unique_count}")
print(f"检测通过可用链接数：{valid_count}")
print(f"去重后无效链接数：{invalid_unique}")
