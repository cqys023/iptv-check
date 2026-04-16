import requests

TIMEOUT = 5

INPUT_FILE = "有源IP.txt"
OUTPUT_FILE = "output.m3u"


def is_valid_m3u(text):
    """判断是否是有效 m3u"""
    return "#EXTM3U" in text and "#EXTINF" in text


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        ips = [i.strip() for i in f if i.strip()]

    print(f"共检测 {len(ips)} 个IP\n")

    for ip in ips:
        url = f"http://{ip}/"
        print(f"检测 {url} ...")

        try:
            r = requests.get(url, timeout=TIMEOUT)
            text = r.text

            # 判断是否可用 IPTV
            if is_valid_m3u(text):
                print(f"✅ 找到可用源: {url}")

                # 直接保存
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"✔ 已导出: {OUTPUT_FILE}")
                return  # 只要第一个可用就退出

            else:
                print("❌ 不可用")

        except:
            print("❌ 请求失败")

    print("\n没有找到可用源")


if __name__ == "__main__":
    main()
