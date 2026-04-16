import requests
import re

TIMEOUT = 5

def has_iptv_source(ip):
    url = f"http://{ip}/"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        text = r.text

        if "#EXTM3U" not in text:
            return False

        pattern = r'#EXTINF.*?\n(https?|rtp)://'
        return re.search(pattern, text) is not None
    except:
        return False


def read_list(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return [i.strip() for i in f if i.strip()]
    except:
        return []


def write_file(file, content):
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    ip_pool = read_list("有源IP.txt")
    current = read_list("current_ip.txt")

    current_ip = current[0] if current else ""

    print(f"当前IP: {current_ip}")

    if current_ip and has_iptv_source(current_ip):
        print("当前IP可用")
        return

    print("开始寻找新IP...")

    for ip in ip_pool:
        if has_iptv_source(ip):
            print(f"找到新IP: {ip}")
            write_file("current_ip.txt", ip)
            return

    print("没有可用IP")


if __name__ == "__main__":
    main()
