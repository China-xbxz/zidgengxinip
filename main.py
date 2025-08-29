import requests
import socket
import random
import json

# 从URL获取IP列表
def get_ips_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.splitlines()
        else:
            print(f"Failed to fetch IPs from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching IPs from {url}: {e}")
    return []

# 根据IP获取地理位置
def get_location(ip):
    try:
        response = requests.get(f"http://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true", timeout=5)
        if response.status_code == 200:
            data = json.loads(response.text)
            if "pro" in data and data["pro"]:
                return data["pro"]
            elif "city" in data and data["city"]:
                return data["city"]
    except:
        pass

    # 备用接口 ip-api
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data['status'] == 'success':
            return data['countryCode']
    except:
        pass

    return "火星⭐"

# 固定端口（可扩展为多个端口随机）
def get_random_port():
    return 443

# 自动识别并转换
def convert_ips(input_urls, output_files):
    for input_url, output_file in zip(input_urls, output_files):
        ips = get_ips_from_url(input_url)

        with open(output_file, 'w', encoding="utf-8") as f:
            for line in ips:
                line = line.strip()
                if not line:
                    continue

                # 如果是 "IP#位置" 格式
                if "#" in line:
                    try:
                        ip, location = line.split("#", 1)
                        socket.inet_aton(ip)  # 校验IP
                        port = get_random_port()
                        f.write(f"{ip}:{port}#{location}\n")
                    except:
                        f.write(f"{line}\n")
                    continue

                # 如果是 "IP PORT COUNTRY" 格式，只取IP
                parts = line.split()
                ip = parts[0]

                try:
                    socket.inet_aton(ip)  # 校验IPv4

                    # 获取位置
                    location = get_location(ip)
                    if not location:
                        location = "未知"

                    # 固定端口
                    port = get_random_port()

                    f.write(f"{ip}:{port}#{location}\n")

                except socket.error:
                    # 非IP直接写原始行
                    f.write(f"{line}\n")
                    continue

if __name__ == "__main__":
    input_urls = [
        "https://ipdb.api.030101.xyz/?type=bestproxy&country=true",
        "https://ipdb.api.030101.xyz/?type=bestcf",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestproxy.txt"
    ]
    output_files = ["bestproxy.txt", "bestcf.txt", "best.txt"]
    convert_ips(input_urls, output_files)
