import requests
from collections import OrderedDict

# ================= 配置区域 =================
INPUT_FILE = "raw_urls.txt"
OUTPUT_FILE = "cnTV_AutoUpdate.m3u8"
GROUP_TITLE = "自动更新"
# ==========================================

def read_and_parse(filename):
    """读取原始列表并解析为 (URL, 频道名) 格式"""
    unique_entries = OrderedDict()
    try:
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                # 严格过滤空行和注释行
                if not line or line.startswith("#"):
                    continue
                
                # 核心逻辑：按英文逗号切割
                parts = line.split(",")
                if len(parts) < 2:
                    continue  # 如果没有逗号，格式不对，直接跳过

                # 【适配新格式】第一部分是 URL，最后一部分是频道名
                url = parts[0].strip() 
                name = parts[-1].strip()

                # 强校验：URL 必须以 http 开头，否则跳过
                if not url.startswith("http"):
                    continue
                
                # 如果频道名是空的，给一个默认值
                if not name:
                    name = "未知频道"

                # 按 URL 去重
                if url not in unique_entries:
                    unique_entries[url] = name
                    
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        return []
    
    return list(unique_entries.items())

def check_availability(entries):
    """检测链接可用性，只读取前 512 字节判断 #EXTM3U"""
    valid_entries = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url, name in entries:
        try:
            # 使用 stream 模式，不下载完整文件，极度节省流量和时间
            r = requests.get(url, timeout=15, headers=headers, stream=True)
            
            if r.status_code == 200:
                # 仅读取前 512 字节
                sample = r.raw.read(512).decode("utf-8", errors="ignore")
                if "#EXTM3U" in sample:
                    valid_entries.append((url, name))
                    print(f"  ✅ 可用: {name}")
                    continue
            print(f"  ❌ 无效: {name}")
        except Exception as e:
            print(f"  ❌ 异常: {name} ({str(e)[:50]}...)")
            
    return valid_entries

def generate_m3u8(entries, filename):
    """生成标准 m3u8 播放列表"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for url, name in entries:
            f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{GROUP_TITLE}",{name}\n{url}\n')
        f.write("#EXT-X-ENDLIST\n")

if __name__ == "__main__":
    print("🚀 开始执行链接检测与更新任务...")
    
    entries = read_and_parse(INPUT_FILE)
    print(f"📂 解析到去重后的待检测链接数: {len(entries)}")
    
    if not entries:
        print("⚠️ 没有可检测的链接，任务结束。")
    else:
        valid_entries = check_availability(entries)
        print(f"\n🎉 检测完成，有效链接数: {len(valid_entries)}")
        generate_m3u8(valid_entries, OUTPUT_FILE)
        print(f"💾 已生成有效列表文件: {OUTPUT_FILE}")
