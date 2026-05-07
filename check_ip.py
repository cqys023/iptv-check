import requests
import random
import urllib3

# ================== 忽略 HTTPS 证书警告 ==================
urllib3.disable_warnings()

# ================== 配置 ==================
TIMEOUT = (10, 30)

IP_POOL_FILE = "node_pool.js"
CURRENT_FILE = "current_ip.txt"
OUTPUT_FILE = "output.m3u"

# VLC UA（很多IPTV对白名单放行）
HEADERS = {
    "User-Agent": "VLC/3.0.18 LibVLC/3.0.18"
}


# ================== 获取M3U ==================
def fetch_m3u(ip):

    schemes = ["http", "https"]

    for scheme in schemes:

        url = f"{scheme}://{ip}/"

        try:

            print(f"\n尝试获取M3U: {url}")

            r = requests.get(
                url,
                timeout=TIMEOUT,
                headers=HEADERS,
                verify=False,
                allow_redirects=True
            )

            print(f"状态码: {r.status_code}")

            if r.status_code != 200:
                continue

            text = r.text.strip()

            # 判断是否为M3U
            if "#EXTM3U" in text and "#EXTINF" in text:

                print("✅ M3U获取成功")

                return text

            else:

                print("❌ 返回内容不是M3U")

        except Exception as e:

            print(f"获取失败: {e}")

    return None


# ================== 提取第一个频道 ==================
def get_first_channel(m3u_text):

    lines = m3u_text.splitlines()

    for line in lines:

        line = line.strip()

        if line.startswith("http"):
            return line

    return None


# ================== 测试频道是否可播放 ==================
def test_channel(url):

    print(f"测试频道: {url}")

    try:

        r = requests.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            headers=HEADERS,
            verify=False,
            allow_redirects=True
        )

        print(f"频道状态码: {r.status_code}")

        # IPTV常见状态
        if r.status_code not in [200, 206]:
            return False

        # 尝试读取真实数据
        for chunk in r.iter_content(1024):

            if chunk:

                print("✅ 检测到流数据")

                return True

        print("❌ 没有读取到流数据")

        return False

    except Exception as e:

        print(f"频道检测失败: {e}")

        return False


# ================== 读取文件 ==================
def read_list(file):

    try:

        with open(file, "r", encoding="utf-8") as f:
            return [i.strip() for i in f if i.strip()]

    except:

        return []


# ================== 写入文件 ==================
def write_file(file, content):

    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


# ================== 优选IP ==================
def pick_ip(pool):

    random.shuffle(pool)

    for ip in pool:

        print("\n==============================")
        print(f"测试候选IP: {ip}")

        # 1️⃣ 获取M3U
        m3u = fetch_m3u(ip)

        if not m3u:

            print("❌ 获取M3U失败")

            continue

        # 2️⃣ 获取第一个频道
        first_url = get_first_channel(m3u)

        if not first_url:

            print("❌ 没有频道地址")

            continue

        # 3️⃣ 测试频道
        if test_channel(first_url):

            print("✅ IP有效")

            return ip, m3u

        else:

            print("❌ 第一个频道无法播放")

    return None, None


# ================== 主逻辑 ==================
def main():

    pool = read_list(IP_POOL_FILE)

    current = read_list(CURRENT_FILE)

    current_ip = current[0] if current else None

    print(f"当前IP: {current_ip}")

    # ================== 检测当前IP ==================
    if current_ip:

        print("\n检测当前IP...")

        # 1️⃣ 获取M3U
        m3u = fetch_m3u(current_ip)

        if m3u:

            # 2️⃣ 获取第一个频道
            first_url = get_first_channel(m3u)

            if first_url:

                # 3️⃣ 测试频道
                if test_channel(first_url):

                    print("✔ 当前IP可用")

                    write_file(OUTPUT_FILE, m3u)

                    return

                else:

                    print("❌ 第一个频道不可播放")

            else:

                print("❌ 没找到频道地址")

        else:

            print("❌ 获取M3U失败")

        print("❌ 当前IP失效，准备切换")

    # ================== 重新优选 ==================
    new_ip, m3u = pick_ip(pool)

    if new_ip:

        write_file(CURRENT_FILE, new_ip)

        write_file(OUTPUT_FILE, m3u)

        print(f"\n✔ 已切换IP: {new_ip}")

    else:

        print("\n❌ 没有找到可用IP")


# ================== 启动 ==================
if __name__ == "__main__":
    main()
