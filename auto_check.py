import requests
from collections import OrderedDict

# ================= 配置区域 =================
INPUT_FILE = "raw_urls.txt"          # 原始待检测列表文件名
OUTPUT_FILE = "cnTV_AutoUpdate.m3u8" # 输出的有效链接文件
GROUP_TITLE = "自动更新"             # 默认分组名称
# ==========================================

def read_and_parse(filename):
    """读取原始列表并解析为 (频道名, URL) 格式，同时按 URL 去重"""
    unique_entries = OrderedDict()
    try:
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                # 忽略空行和注释行
                if not line or line.startswith("#"):
                    continue
                
                # 按逗号分割
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 2:
                    continue

                # 【核心修复】取最后一个元素作为 URL，其余部分拼接作为频道名
                url = parts[-1]
                channel_name = ",".join(parts[:-1])

                # 简单的容错：如果第一个字段刚好以 http 开头，说明没有频道名
                if parts[0].startswith("http"):
                    channel_name = "未知频道"
                    url = parts[0]
                
                # 确保提取到的 URL 是有效的网络地址
                if not url.startswith("http"):
                    continue

                # 以 URL 为 Key 进行去重，保留先出现的频道名
                if url not in unique_entries:
                    unique_entries[url] = channel_name
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}，请确保文件存在于仓库根目录。")
        return []
    
    return list(unique_entries.items())

def check_availability(entries):
    """检测 m3u8 链接的有效性 (HTTP 200 + #EXTM3U 协议头)"""
    valid_entries = []
    # 模拟浏览器请求头，防止被采集站防火墙拦截
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for name, url in entries:
        try:
            # 1. 使用 stream 模式只读取前 512 字节，极省流量和时间
            r = requests.get(url, timeout=15, headers=headers, stream=True)
            
            # 2. 检查状态码
            if r.status_code == 200:
                # 3. 检查响应内容是否包含 m3u8 协议头
                sample = r.raw.read(512).decode("utf-8", "ignore")
                if "#EXTM3U" in sample:
                    valid_entries.append((name, url))
                    print(f"  ✅ 检测通过: {name}")
                    continue
            print(f"  ❌ 无效: {name} (状态码: {r.status_code})")
        except Exception as e:
            print(f"  ❌ 异常: {name} ({str(e)})")
            
    return valid_entries

def generate_m3u8(entries, filename):
    """生成标准 m3u8 播放列表文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in entries:
            # 将真实的频道名写入 tvg-name 属性，完美适配影视仓/TVBox 识别
            f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{GROUP_TITLE}",{name}\n{url}\n')
        f.write("#EXT-X-ENDLIST\n")

if __name__ == "__main__":
    print("🚀 开始执行链接检测与更新任务...")
    
    # 1. 读取并解析源数据
    entries = read_and_parse(INPUT_FILE)
    print(f"📂 解析到去重后的待检测链接数: {len(entries)}")
    
    if not entries:
        print("⚠️ 没有可检测的链接，任务结束。")
    else:
        # 2. 检测有效性
        valid_entries = check_availability(entries)
        print(f"\n🎉 检测完成，有效链接数: {len(valid_entries)}")
        
        # 3. 生成输出文件
        generate_m3u8(valid_entries, OUTPUT_FILE)
        print(f"💾 已生成有效列表文件: {OUTPUT_FILE}")
