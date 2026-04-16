import requests
import random

TIMEOUT = 8  # ⚠️ 提高超时，避免误判慢源

IP_POOL_FILE = "node_pool.js"
CURRENT_FILE = "current_ip.txt"
OUTPUT_FILE = "output.m3u"


# ================== 获取M3U ==================
def fetch_m3u(ip):
    url = f"http://{ip}/"

    try:
        r = requests.get(
            url,
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if r.status_code != 200:
            return None

        text = r.text.strip()

        if "#EXTM3U" in text and "#EXTINF" in text:
            return text

    except Exception as e:
        print(f"获取M3U失败: {e}")

    return None


# ================== 检测第一个频道 ==================
def first_channel_ok(m3u_text):
    try:
        lines = m3u_text.splitlines()

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()

                    print(f"测试频道: {url}")

                    # ---- 方式1：HEAD ----
                    try:
                        r = requests.head(url, timeout=TIMEOUT)
                        if r.status_code in [200, 206]:
                            return True
                    except:
                        pass

                    # ---- 方式2：GET（流模式）----
                    try:
                        r = requests.get(
                            url,
                            timeout=TIMEOUT,
                            stream=True,
                            headers={"User-Agent": "Mozilla/5.0"}
                        )
                        if r.status_code in [200, 206]:
                            return True
                    except:
                        pass

                    return False

        return False

    except Exception as e:
        print(f"频道检测失败: {e}")
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
        print(f"\n测试候选IP: {ip}")

        m3u = fetch_m3u(ip)

        if not m3u:
            print("  ❌ 无M3U")
            continue

        # ⚠️ 宽松策略：先认为可用
        if first_channel_ok(m3u):
            print("  ✅ 频道可用")
            return ip, m3u
        else:
            print("  ⚠️ 频道检测失败，但M3U存在（可能误判）")

            # 👉 fallback：只要M3U存在也可用（防误杀）
            return ip, m3u

    return None, None


# ================== 主逻辑 ==================
def main():
    pool = read_list(IP_POOL_FILE)
    current = read_list(CURRENT_FILE)

    current_ip = current[0] if current else None

    print(f"当前IP: {current_ip}")

    # ================== 检测当前 ==================
    if current_ip:
        print("\n检测当前IP...")

        m3u = fetch_m3u(current_ip)

        if m3u:
            if first_channel_ok(m3u):
                print("✔ 当前IP完全可用")
                write_file(OUTPUT_FILE, m3u)
                return
            else:
                print("⚠️ 当前IP频道检测失败，但可能仍可用")

                # 👉 宽松模式（关键！）
                write_file(OUTPUT_FILE, m3u)
                return

        print("❌ 当前IP失效，准备切换")

    # ================== 优选 ==================
    new_ip, m3u = pick_ip(pool)

    if new_ip:
        write_file(CURRENT_FILE, new_ip)   # ✔ 自动覆盖（清空+写入）
        write_file(OUTPUT_FILE, m3u)

        print(f"\n✔ 已切换IP: {new_ip}")

    else:
        print("\n❌ 没有找到可用IP")


if __name__ == "__main__":
    main()
