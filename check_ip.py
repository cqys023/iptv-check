import requests
import subprocess
import re
import urllib3

urllib3.disable_warnings()

TIMEOUT = (10, 20)

FFMPEG_PATH = "ffmpeg"

HEADERS = {
    "User-Agent": "VLC/3.0.18 LibVLC/3.0.18"
}


# ================== 获取M3U ==================
def fetch_m3u(ip):

    url = f"http://{ip}/"

    try:
        r = requests.get(
            url,
            timeout=TIMEOUT,
            headers=HEADERS,
            verify=False,
            allow_redirects=True
        )

        if r.status_code != 200:
            return None

        text = r.text.strip()

        if "#EXTINF" in text and "http" in text:
            return text

    except:
        pass

    return None


# ================== 提取第一个频道 ==================
def get_first_url(m3u):

    for line in m3u.splitlines():
        if line.startswith("http"):
            return line

    return None


# ================== ffmpeg检测分辨率 ==================
def get_resolution(url):

    cmd = [
        FFMPEG_PATH,
        "-i", url,
        "-t", "5",
        "-f", "null",
        "-"
    ]

    try:
        result = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            timeout=15
        ).decode(errors="ignore")

        match = re.search(r"(\d{3,4})x(\d{3,4})", result)

        if match:
            return int(match.group(1)), int(match.group(2))

    except:
        pass

    return None, None


# ================== 判断是否高清 ==================
def is_hd(width, height):

    if not width:
        return False

    if width >= 1280 and height >= 720:
        return True

    return False


# ================== 测试频道 ==================
def test_channel(url):

    print(f"\n测试频道: {url}")

    width, height = get_resolution(url)

    if not width:
        print("❌ 无法获取分辨率")
        return False

    print(f"分辨率: {width}x{height}")

    if is_hd(width, height):
        print("✅ 高清源")
        return True

    else:
        print("❌ 非高清源")
        return False


# ================== 主检测 ==================
def check_ip(ip):

    print(f"\n检测IP: {ip}")

    m3u = fetch_m3u(ip)

    if not m3u:
        print("❌ M3U获取失败")
        return False

    url = get_first_url(m3u)

    if not url:
        print("❌ 无频道")
        return False

    return test_channel(url)


# ================== 示例 ==================
ip = "78962588856486165751857.iepose.cn"

if check_ip(ip):
    print("\n✔ 可用高清源")
else:
    print("\n❌ 不符合高清")
