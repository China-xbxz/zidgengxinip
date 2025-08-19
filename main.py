import requests
import socket
from bs4 import BeautifulSoup

# 从URL获取IP列表
def get_ips_from_url(url):
    try:
        response = requests.get(url)
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
        # 优先尝试 pconline 接口
        response = requests.get(f"http://whois.pconline.com.cn/ipJson.jsp?ip={ip}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            font_element = soup.find("font")
            if font_element is not None:
                font_content = font_element.text
                if '"pro": "' in font_content:
                    return font_content.split('"pro": "')[1].split('"')[0]
                elif '"city": "' in font_content:
                    return font_content.split('"city": "')[1].split('"')[0]
    except Exception as e:
        print(f"Error fetching location for IP {ip} using pconline: {e}")

    # 备用接口 ip-api
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data['status'] == 'success':
            return data['countryCode']
    except Exception as e:
        print(f"Error fetching location for IP {ip} using ip-api.com: {e}")
    return None

# 端口扫描（只扫常见CF/代理端口）
def scan_ports(ip):
    open_ports = []
    for port in [443, 2096, 2053, 2083, 2087, 8443]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip, port))
            s.close()
            if result == 0:
                open_ports.append(port)
        except:
            pass
    if not open_ports:
        open_ports.append(443)  # 默认给443
    return open_ports

# 自动识别并转换
def convert_ips(input_urls, output_files):
    for input_url, output_file in zip(input_urls, output_files):
        ips = get_ips_from_url(input_url)

        with open(output_file, 'w') as f:
            for line in ips:
                line = line.strip()
                if not line:
                    continue

                # 如果是 "IP#位置" 格式
                if "#" in line:
                    try:
                        ip, location = line.split("#", 1)
                        socket.inet_aton(ip)  # 校验IP
                        open_ports = scan_ports(ip)
                        f.write(f"{ip}:{open_ports[0]}#{location}\n")
                    except:
                        f.write(f"{line}\n")
                    continue

                # 如果是 "IP PORT COUNTRY" 格式，只取IP
                parts = line.split()
                ip = parts[0]

                try:
                    socket.inet_aton(ip)  # 校验IP

                    # 获取位置
                    location = get_location(ip)
                    if not location:
                        location = "火星⭐"

                    # 扫描端口
                    open_ports = scan_ports(ip)

                    f.write(f"{ip}:{open_ports[0]}#{location}\n")

                except socket.error:
                    # 非IP直接写原始行
                    f.write(f"{line}\n")
                    continue

if __name__ == "__main__":
    input_urls = [
        "https://ipdb.api.030101.xyz/?type=bestproxy&country=true",
        "https://ipdb.api.030101.xyz/?type=bestcf"
    ]
    output_files = ["bestproxy.txt", "bestcf.txt"]
    convert_ips(input_urls, output_files)
