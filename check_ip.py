import requests
import random
import subprocess
import re
import urllib3
import time

urllib3.disable_warnings()

TIMEOUT = (10, 25)

IP_POOL_FILE = "node_pool.js"
CURRENT_FILE = "current_ip.txt"
OUTPUT_FILE = "output.m3u"

HEADERS = {
    "User-Agent": "VLC/3.0.18 LibVLC/3.0.18"
}

FFPROBE = "ffprobe"


# ================== 获取M3U ==================
def fetch_m3u(ip):

    schemes = ["https", "http"]

    for scheme in schemes:

        url = f"{scheme}://{ip}/"

        try:
            print(f"\n尝试M3U: {url}")

            r = requests.get(
                url,
                timeout=TIMEOUT,
                headers=HEADERS,
                verify=False,
                allow_redirects=True
            )

            print("状态码:", r.status_code)

            if r.status_code != 200:
                continue

            text = r.text.strip()

            # 宽松判断（防止误杀）
            if "#EXTINF" in text and "http" in text:
                print("✅ 获取M3U成功")
                return text

            else:
                print("❌ 返回内容不是M3U")

        except Exception as e:
            print("请求失败:", e)

    return None


# ================== 提取第一个频道 ==================
def get_first_channel(m3u):

    for line in m3u.splitlines():

        line = line.strip()

        if line.startswith("http"):
            return line

    return None


# ================== ffprobe获取分辨率 ==================
def get_resolution(url):

    cmd = [
        FFPROBE,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        url
    ]

    try:

        result = subprocess.check_output(
            cmd,
            timeout=20,
            stderr=subprocess.STDOUT
        ).decode().strip()

        print("ffprobe结果:", result)

        match = re.match(r"(\d+),(\d+)", result)

        if match:
            return int(match.group(1)), int(match.group(2))

    except Exception as e:

        print("ffprobe失败:", e)

    return None, None


# ================== 高清判断 ==================
def is_hd(w, h):

    if not w:
        return False

    return w >= 1280 and h >= 720


# ================== 测试频道（失败重试1次） ==================
def test_channel(url):

    print(f"\n测试频道: {url}")

    # 最多检测2次
    for attempt in range(1, 3):

        print(f"\n第 {attempt} 次检测...")

        w, h = get_resolution(url)

        # 成功获取分辨率
        if w and h:

            print(f"分辨率: {w}x{h}")

            if is_hd(w, h):

                print("✅ 高清源")

                return True

            else:

                print("❌ 非高清")

                return False

        # 第一次失败后等待1秒
        if attempt < 2:

            print("⚠️ 获取分辨率失败，1秒后重试...")

            time.sleep(1)

    print("❌ 两次检测均失败")

    return False


# ================== 读取列表 ==================
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


# ================== IP检测 ==================
def pick_ip(pool):

    random.shuffle(pool)

    for ip in pool:

        print("\n==============================")
        print(f"测试IP: {ip}")

        m3u = fetch_m3u(ip)

        if not m3u:

            print("❌ M3U失败")

            continue

        first = get_first_channel(m3u)

        if not first:

            print("❌ 无频道")

            continue

        if test_channel(first):

            print("✅ IP可用（高清）")

            return ip, m3u

        else:

            print("❌ 非高清或不可用")

    return None, None


# ================== 主逻辑 ==================
def main():

    pool = read_list(IP_POOL_FILE)

    current = read_list(CURRENT_FILE)

    current_ip = current[0] if current else None

    print(f"当前IP: {current_ip}")

    # ===== 当前IP检测 =====
    if current_ip:

        print("\n检测当前IP...")

        m3u = fetch_m3u(current_ip)

        if m3u:

            first = get_first_channel(m3u)

            if first and test_channel(first):

                print("✔ 当前IP高清可用")

                write_file(OUTPUT_FILE, m3u)

                return

        print("❌ 当前IP不可用，切换")

    # ===== IP池筛选 =====
    new_ip, m3u = pick_ip(pool)

    if new_ip:

        write_file(CURRENT_FILE, new_ip)

        write_file(OUTPUT_FILE, m3u)

        print(f"\n✔ 已切换IP: {new_ip}")

    else:

        print("\n❌ 没有高清源")


# ================== 启动 ==================
if __name__ == "__main__":
    main()
