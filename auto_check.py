from collections import OrderedDict

INPUT_FILE = "raw_urls.txt"
OUTPUT_FILE = "cnTV_AutoUpdate.m3u8"
GROUP_TITLE = "自动更新"


def read_and_parse(filename: str):
    entries: OrderedDict[str, str] = OrderedDict()

    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(",")
            if len(parts) < 2:
                continue

            url = ""
            name = ""

            for part in parts:
                part = part.strip()
                if part.lower().startswith("http"):
                    url = part
                    break

            if url:
                name = ",".join(p.strip() for p in parts if p.strip() != url)
            else:
                continue

            if not name:
                name = "未知频道"

            if url not in entries:
                entries[url] = name

    return list(entries.items())


def generate_m3u8(entries, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for url, name in entries:
            f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{GROUP_TITLE}",{name}\n{url}\n')
        f.write("#EXT-X-ENDLIST\n")


if __name__ == "__main__":
    entries = read_and_parse(INPUT_FILE)
    print(f"共解析到 {len(entries)} 个链接")
    generate_m3u8(entries, OUTPUT_FILE)
    print(f"已生成 {OUTPUT_FILE}")
