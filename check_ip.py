import requests
import re

TIMEOUT = 5


# ================== 判断 IPTV ==================
def get_iptv_content(ip):
    url = f"http://{ip}/"

    try:
        r = requests.get(url, timeout=TIMEOUT)
        text = r.text

        if "#EXTM3U" not in text:
            return None

        pattern = r'#EXTINF.*?\n(https?|rtp)://'
        if re.search(pattern, text):
            return text

    except:
        pass

    return None


# ================== 读取文件 ==================
def read_list(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return [i.strip() for i in f if i.strip()]
    except:
        return []


# ================== 主逻辑 ==================
def main():
    ip_list = read_list("有源IP.txt")

    print(f"共 {len(ip_list)} 个IP\n")

    all_m3u = "#EXTM3U\n\n"

    for ip in ip_list:
        print(f"检测 {ip} ...")

        content = get_iptv_content(ip)

        if content:
            print("✅ 有源，已提取")

            # 去掉重复头
            content = content.replace("#EXTM3U", "").strip()

            # 可选：给每个源加标记
            content = f"#EXTINF:-1 group-title=\"{ip}\",{ip}\n" + content

            all_m3u += content + "\n\n"
        else:
            print("❌ 无源")

    # 保存总 m3u
    with open("output.m3u", "w", encoding="utf-8") as f:
        f.write(all_m3u)

    print("\n完成！已生成 output.m3u")


if __name__ == "__main__":
    main()
