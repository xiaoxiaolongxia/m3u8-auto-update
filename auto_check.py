# -*- coding: utf-8 -*-
# auto_check.py  (格式自适应版：名称/URL 谁前谁后都能识别，URL 带 & 参数也不怕)
import requests
from collections import OrderedDict

# ================= 配置区域 =================
INPUT_FILE = "raw_urls.txt"          # 原始待检测列表
OUTPUT_FILE = "cnTV_AutoUpdate.m3u8" # 输出的有效列表
GROUP_TITLE = "自动更新"             # 分组名
# ==========================================

def read_and_parse(filename):
    """自动识别每一行里以 http 开头的那段作为 URL，其余片段拼成频道名。
    兼容 名称,URL 和 URL,名称 两种顺序，URL 内含 & ? = 等参数不受影响。"""
    unique_entries = OrderedDict()  # key=URL, value=频道名
    try:
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = [p.strip() for p in line.split(",")]

                # 找到以 http 开头的片段 -> 这就是 URL（含 ?key=& 等参数都在同一段里）
                url_idx = None
                for i, p in enumerate(parts):
                    if p.startswith("http://") or p.startswith("https://"):
                        url_idx = i
                        break
                if url_idx is None:
                    continue  # 这行没有链接，跳过

                url = parts[url_idx]

                # 除 URL 之外的所有片段拼回频道名（防止频道名本身带逗号被拆散）
                name_parts = [parts[i] for i in range(len(parts)) if i != url_idx and parts[i]]
                name = ",".join(name_parts).strip() if name_parts else url

                # 按 URL 去重，保留先出现的频道名
                if url not in unique_entries:
                    unique_entries[url] = name
    except FileNotFoundError:
        print("错误：找不到文件 " + filename)
        return []

    return list(unique_entries.items())  # [(url, name), ...]


def check_availability(entries):
    """检测链接可用性：HTTP 200 且开头含 #EXTM3U。iter_content 自动解 gzip。"""
    valid_entries = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for url, name in entries:
        try:
            r = requests.get(url, timeout=15, headers=headers, stream=True)
            if r.status_code == 200:
                chunk = b""
                for piece in r.iter_content(chunk_size=512):
                    chunk = piece
                    break
                sample = chunk.decode("utf-8", errors="ignore")
                r.close()
                if "#EXTM3U" in sample:
                    valid_entries.append((url, name))
                    print("  [OK] 可用: " + name)
                    continue
                print("  [NG] 无效: " + name)
            else:
                print("  [NG] 无效: " + name + " (状态码 " + str(r.status_code) + ")")
                r.close()
        except Exception as e:
            print("  [ERR] 异常: " + name + " (" + str(e)[:50] + "...)")
    return valid_entries


def generate_m3u8(entries, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for url, name in entries:
            f.write('#EXTINF:-1 tvg-name="%s" group-title="%s",%s\n%s\n' % (name, GROUP_TITLE, name, url))
        f.write("#EXT-X-ENDLIST\n")


if __name__ == "__main__":
    print("开始执行链接检测与更新任务...")
    entries = read_and_parse(INPUT_FILE)
    print("解析到去重后的待检测链接数: %d" % len(entries))
    if not entries:
        print("没有可检测的链接，任务结束。")
    else:
        valid = check_availability(entries)
        print("检测完成，有效链接数: %d" % len(valid))
        generate_m3u8(valid, OUTPUT_FILE)
        print("已生成有效列表文件: " + OUTPUT_FILE)
