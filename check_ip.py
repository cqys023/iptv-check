import requests

TIMEOUT = 5
OUTPUT_FILE = "output.m3u"


def fetch_m3u(ip):
    url = f"http://{ip}/"

    try:
        r = requests.get(url, timeout=TIMEOUT)

        print(f"返回状态: {r.status_code}")

        text = r.text.strip()

        if "#EXTM3U" in text and "#EXTINF" in text:
            return text

    except Exception as e:
        print(f"请求失败: {e}")

    return None


def main():
    with open("有源IP.txt", "r", encoding="utf-8") as f:
        ips = [i.strip() for i in f if i.strip()]

    print(f"共 {len(ips)} 个IP")

    for ip in ips:
        print(f"\n检测 {ip}")

        m3u = fetch_m3u(ip)

        if m3u:
            print("✅ 找到可用源")

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(m3u)

            print(f"✔ 已生成 {OUTPUT_FILE}")

            return

        else:
            print("❌ 不可用")

    print("\n⚠️ 没有找到任何可用源")


if __name__ == "__main__":
    main()
