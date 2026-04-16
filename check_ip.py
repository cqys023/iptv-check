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


# ================== 检测第一个频道 ==================
def first_channel_ok(m3u_text):
    try:
        lines = m3u_text.splitlines()

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()

                    r = requests.get(url, timeout=TIMEOUT)

                    return r.status_code == 200

        return False

    except:
        return False


# ================== 文件操作 ==================
def read_list(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return [i.strip() for i in f if i.strip()]
    except:
        return []


def write_file(file, content):
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


# ================== 清空 current ==================
def clear_current():
    open(CURRENT_FILE, "w", encoding="utf-8").close()


# ================== 优选IP ==================
def pick_best_ip(pool):
    random.shuffle(pool)

    for ip in pool:
        print(f"优选检测: {ip}")

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
    current_list = read_list(CURRENT_FILE)

    current_ip = current_list[0] if current_list else None

    print(f"当前IP: {current_ip}")

    # ================== Step1：检测当前IP ==================
    if current_ip:
        m3u = fetch_m3u(current_ip)

        if m3u and first_channel_ok(m3u):
            print("✔ 当前IP可用")

            write_file(OUTPUT_FILE, m3u)
            return

        print("❌ 当前IP失效，开始切换")

    # ================== Step2：清空 current ==================
    clear_current()

    # ================== Step3：优选新IP ==================
    new_ip, m3u = pick_best_ip(pool)

    if new_ip:
        write_file(CURRENT_FILE, new_ip)   # ✅ 写入新IP
        write_file(OUTPUT_FILE, m3u)       # ✅ 写入m3u

        print(f"✔ 已切换IP: {new_ip}")

    else:
        print("⚠️ 未找到可用IP")


if __name__ == "__main__":
    main()
