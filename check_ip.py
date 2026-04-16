import requests
import random

TIMEOUT = 5

IP_POOL_FILE = "有源IP.txt"
CURRENT_FILE = "current_ip.txt"
OUTPUT_FILE = "output.m3u"


# ================== 获取M3U ==================
def fetch_m3u(ip):
    url = f"http://{ip}/"

    try:
        r = requests.get(url, timeout=TIMEOUT)
        text = r.text.strip()

        if "#EXTM3U" not in text:
            return None

        return text

    except:
        return None


# ================== 检测第一个频道是否可用 ==================
def first_channel_ok(m3u_text):
    try:
        lines = m3u_text.splitlines()

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()

                    # 只测第一个频道
                    r = requests.get(url, timeout=TIMEOUT)
                    if r.status_code == 200:
                        return True
                    else:
                        return False

        return False

    except:
        return False


# ================== 读取文件 ==================
def read_list(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return [i.strip() for i in f if i.strip()]
    except:
        return []


def write_file(file, content):
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


# ================== 优选IP ==================
def pick_best_ip(ip_list):
    random.shuffle(ip_list)

    for ip in ip_list:
        print(f"优选测试: {ip}")

        m3u = fetch_m3u(ip)
        if not m3u:
            continue

        if first_channel_ok(m3u):
            print(f"✔ 可用IP: {ip}")
            return ip, m3u

    return None, None


# ================== 主逻辑 ==================
def main():
    pool = read_list(IP_POOL_FILE)
    current_ips = read_list(CURRENT_FILE)

    current_ip = current_ips[0] if current_ips else None

    print(f"当前IP: {current_ip}")

    # ================== Step1：测试当前IP ==================
    if current_ip:
        print("检测当前IP...")

        m3u = fetch_m3u(current_ip)

        if m3u and first_channel_ok(m3u):
            print("✔ 当前IP可用")

            write_file(OUTPUT_FILE, m3u)
            return

        print("❌ 当前IP失效，开始优选")

    # ================== Step2：优选新IP ==================
    new_ip, m3u = pick_best_ip(pool)

    if new_ip:
        write_file(CURRENT_FILE, new_ip)
        write_file(OUTPUT_FILE, m3u)
        print(f"✔ 已切换IP: {new_ip}")
    else:
        print("⚠️ 没有找到可用IP")


if __name__ == "__main__":
    main()
