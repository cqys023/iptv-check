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

        if "#EXTM3U" in text and "#EXTINF" in text:
            return text

    except:
        pass

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


# ================== 读取 ==================
def read_list(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return [i.strip() for i in f if i.strip()]
    except:
        return []


# ================== 写入 ==================
def write_file(file, content):
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


# ================== 优选 ==================
def pick_ip(pool):
    random.shuffle(pool)

    for ip in pool:
        print(f"测试: {ip}")

        m3u = fetch_m3u(ip)
        if not m3u:
            continue

        if first_channel_ok(m3u):
            return ip, m3u

    return None, None


# ================== 主逻辑 ==================
def main():
    pool = read_list(IP_POOL_FILE)
    current = read_list(CURRENT_FILE)

    current_ip = current[0] if current else None

    print("当前IP:", current_ip)

    # ================== 检测当前 ==================
    if current_ip:
        m3u = fetch_m3u(current_ip)

        if m3u and first_channel_ok(m3u):
            print("当前IP可用")

            write_file(OUTPUT_FILE, m3u)
            return

        print("当前IP失效，切换...")

    # ================== 优选 ==================
    new_ip, m3u = pick_ip(pool)

    if new_ip:
        write_file(CURRENT_FILE, new_ip)   # ✔ 清空并写入新IP
        write_file(OUTPUT_FILE, m3u)

        print("切换成功:", new_ip)

    else:
        print("无可用IP")


if __name__ == "__main__":
    main()
