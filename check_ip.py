import requests
import random
import urllib3

urllib3.disable_warnings()

TIMEOUT = (10, 25)

IP_POOL_FILE = "node_pool.js"
CURRENT_FILE = "current_ip.txt"
OUTPUT_FILE = "output.m3u"

HEADERS = {
    "User-Agent": "VLC/3.0.18 LibVLC/3.0.18"
}

# ================== 常见M3U路径 ==================
M3U_PATHS = [
    "",
    "live.m3u",
    "iptv.m3u",
    "tv.m3u",
    "index.m3u",
    "get.php",
    "playlist.m3u"
]


# ================== 判断是否为M3U ==================
def is_m3u(text):
    if not text:
        return False

    # 只要有频道结构即可认为是M3U
    return ("#EXTINF" in text and "http" in text)


# ================== 获取M3U（核心修复） ==================
def fetch_m3u(ip):

    schemes = ["https", "http"]  # 优先HTTPS

    for scheme in schemes:

        for path in M3U_PATHS:

            url = f"{scheme}://{ip}/{path}"

            try:
                print(f"\n尝试: {url}")

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

                # 调试用（建议打开）
                # print(text[:300])

                if is_m3u(text):
                    print("✅ 找到M3U")
                    return text

                else:
                    print("❌ 不是M3U内容")

            except Exception as e:
                print("请求失败:", e)

    return None


# ================== 提取第一个频道 ==================
def get_first_channel(m3u_text):

    for line in m3u_text.splitlines():
        line = line.strip()
        if line.startswith("http"):
            return line

    return None


# ================== 流检测（改良版） ==================
def test_channel(url):

    print(f"\n测试频道: {url}")

    try:
        r = requests.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            headers=HEADERS,
            verify=False,
            allow_redirects=True
        )

        print("状态码:", r.status_code)

        if r.status_code not in [200, 206]:
            return False

        ctype = r.headers.get("Content-Type", "").lower()
        print("Content-Type:", ctype)

        # HTML直接排除
        if "text/html" in ctype:
            return False

        # 读取数据判断是否活流
        size = 0

        for chunk in r.iter_content(1024):

            if chunk:
                size += len(chunk)

                # 只要有10KB数据就认为有效
                if size > 10 * 1024:
                    print("✅ 流有效")
                    return True

        return False

    except Exception as e:
        print("检测失败:", e)
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
            print("❌ 没有M3U")
            continue

        first = get_first_channel(m3u)

        if not first:
            print("❌ 没有频道")
            continue

        if test_channel(first):
            print("✅ IP可用")
            return ip, m3u

        else:
            print("❌ 频道不可用")

    return None, None


# ================== 主逻辑 ==================
def main():

    pool = read_list(IP_POOL_FILE)
    current = read_list(CURRENT_FILE)

    current_ip = current[0] if current else None

    print(f"当前IP: {current_ip}")

    # ===== 检测当前IP =====
    if current_ip:

        print("\n检测当前IP...")

        m3u = fetch_m3u(current_ip)

        if m3u:

            first = get_first_channel(m3u)

            if first and test_channel(first):

                print("✔ 当前IP可用")
                write_file(OUTPUT_FILE, m3u)
                return

        print("❌ 当前IP不可用，切换")

    # ===== 重新选择 =====
    new_ip, m3u = pick_ip(pool)

    if new_ip:

        write_file(CURRENT_FILE, new_ip)
        write_file(OUTPUT_FILE, m3u)

        print(f"\n✔ 已切换IP: {new_ip}")

    else:
        print("\n❌ 没有可用IP")


if __name__ == "__main__":
    main()
