import requests
import random
import urllib3

# 忽略 HTTPS 证书警告
urllib3.disable_warnings()

TIMEOUT = 8

IP_POOL_FILE = "node_pool.js"
CURRENT_FILE = "current_ip.txt"
OUTPUT_FILE = "output.m3u"


# ================== 获取M3U ==================
def fetch_m3u(ip):

    # 自动尝试 HTTP / HTTPS
    schemes = ["http", "https"]

    for scheme in schemes:

        url = f"{scheme}://{ip}/"

        try:
            print(f"尝试获取M3U: {url}")

            r = requests.get(
                url,
                timeout=TIMEOUT,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                verify=False
            )

            if r.status_code != 200:
                print(f"状态码异常: {r.status_code}")
                continue

            text = r.text.strip()

            # 判断是否为M3U
            if "#EXTM3U" in text and "#EXTINF" in text:
                print("✅ M3U获取成功")
                return text

        except Exception as e:
            print(f"获取失败: {e}")

    return None


# ================== 检测频道 ==================
def test_stream(url):

    try:
        r = requests.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            verify=False
        )

        # 允许更多状态码
        if r.status_code not in [200, 206, 301, 302]:
            return False

        # 读取前1024字节
        for chunk in r.iter_content(1024):
            if chunk:
                return True

        return False

    except Exception as e:
        print(f"检测流失败: {e}")
        return False


# ================== 检测M3U中的频道 ==================
def first_channel_ok(m3u_text):

    try:
        lines = m3u_text.splitlines()

        urls = []

        # 提取所有频道URL
        for line in lines:

            line = line.strip()

            if line.startswith("http"):
                urls.append(line)

        if not urls:
            return False

        # 随机抽取最多3个频道检测
        random.shuffle(urls)

        test_urls = urls[:3]

        for url in test_urls:

            print(f"测试频道: {url}")

            if test_stream(url):
                print("✅ 频道可播放")
                return True

            else:
                print("❌ 频道不可播放")

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

        print("\n========================")
        print(f"测试候选IP: {ip}")

        m3u = fetch_m3u(ip)

        if not m3u:
            print("❌ 无法获取M3U")
            continue

        # 检测频道
        if first_channel_ok(m3u):

            print("✅ IP可用")
            return ip, m3u

        else:

            print("⚠️ 频道检测失败，但M3U存在")

            # 宽松模式
            return ip, m3u

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

        m3u = fetch_m3u(current_ip)

        if m3u:

            if first_channel_ok(m3u):

                print("✔ 当前IP完全可用")

                write_file(OUTPUT_FILE, m3u)

                return

            else:

                print("⚠️ 当前IP频道检测失败，但M3U存在")

                # 宽松模式
                write_file(OUTPUT_FILE, m3u)

                return

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
