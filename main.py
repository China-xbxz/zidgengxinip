import requests
import ipaddress
import random
import json
import concurrent.futures

# 从URL获取IP列表
def get_ips_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.splitlines()
        else:
            print(f"❌ 获取 {url} 失败, 状态码: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 请求 {url} 出错: {e}")
    return []

# 根据IP获取地理位置
def get_location(ip):
    # pconline接口
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

# 随机端口，可扩展
def get_random_port():
    return random.choice([80, 443, 8443])

# 处理单个IP
def process_ip(line):
    line = line.strip()
    if not line:
        return None

    # 已经是 "IP#位置"
    if "#" in line:
        try:
            ip, location = line.split("#", 1)
            ipaddress.ip_address(ip)  # 校验 IP
            port = get_random_port()
            return f"{ip}:{port}#{location}"
        except:
            return line

    # 可能是 "IP PORT COUNTRY"
    parts = line.split()
    ip = parts[0]

    try:
        ipaddress.ip_address(ip)  # 支持 IPv4/IPv6

        # 获取位置
        location = get_location(ip)
        if not location:
            location = "火星⭐"

        port = get_random_port()
        return f"{ip}:{port}#{location}"

    except ValueError:
        # 非IP，原样返回
        return line

# 自动识别并转换
def convert_ips(input_urls, output_files, max_workers=10):
    for input_url, output_file in zip(input_urls, output_files):
        ips = get_ips_from_url(input_url)

        results = []
        # 多线程查询，加快速度
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_ip, line) for line in ips]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        # 写文件
        with open(output_file, 'w', encoding="utf-8") as f:
            f.write("\n".join(results))

        print(f"✅ 已保存 {len(results)} 条结果到 {output_file}")

if __name__ == "__main__":
    input_urls = [
        "https://ipdb.api.030101.xyz/?type=bestproxy&country=true",
        "https://ipdb.api.030101.xyz/?type=bestcf",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestproxy.txt",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestcf.txt"
    ]
    output_files = ["bestproxy.txt", "bestcf.txt", "best.txt", "cf.txt"]
    convert_ips(input_urls, output_files, max_workers=20)
