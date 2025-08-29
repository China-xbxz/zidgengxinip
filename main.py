import requests
import ipaddress
import json
import concurrent.futures

# ========== 获取IP列表 ==========
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


# ========== 根据IP获取地理位置 ==========
def get_location(ip):
    # 1. pconline
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

    # 2. ip-api
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5)
        data = response.json()
        if data['status'] == 'success':
            return data.get('country', data.get('countryCode'))
    except:
        pass

    # 3. ipinfo.io
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()
        if "country" in data:
            return data["country"]
        if "region" in data:
            return data["region"]
    except:
        pass

    # 4. ip.sb
    try:
        response = requests.get(f"https://api.ip.sb/geoip/{ip}", timeout=5)
        data = response.json()
        if "country" in data:
            return data["country"]
    except:
        pass

    # 5. ipapi.co
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        data = response.json()
        if "country_name" in data:
            return data["country_name"]
    except:
        pass

    # 都失败，返回默认
    return "火星⭐"


# 固定端口 443
def get_fixed_port():
    return 443


# ========== 处理单个IP ==========
def process_ip(line):
    line = line.strip()
    if not line:
        return None

    # 已经是 "IP#位置"
    if "#" in line:
        try:
            ip, location = line.split("#", 1)
            ipaddress.ip_address(ip)  # 校验 IP
            port = get_fixed_port()
            if not location.strip():
                location = "火星⭐"
            return f"{ip}:{port}#{location}"
        except:
            return line

    # 可能是 "IP PORT COUNTRY"
    parts = line.split()
    ip = parts[0]

    try:
        ipaddress.ip_address(ip)  # 校验IP（支持 IPv4/IPv6）
        location = get_location(ip) or "火星⭐"
        port = get_fixed_port()
        return f"{ip}:{port}#{location}"
    except ValueError:
        return line


# ========== 自动识别并转换 ==========
def convert_ips(input_urls, output_files, max_workers=10):
    for input_url, output_file in zip(input_urls, output_files):
        ips = get_ips_from_url(input_url)

        results = set()  # 用 set 自动去重

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_ip, line) for line in ips]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.add(result)  # set 去重

        # 写文件
        with open(output_file, 'w', encoding="utf-8") as f:
            f.write("\n".join(sorted(results)))  # 排序后写入

        print(f"✅ 已保存 {len(results)} 条去重结果到 {output_file}")


if __name__ == "__main__":
    input_urls = [
        "https://ipdb.api.030101.xyz/?type=bestproxy&country=true",
        "https://ipdb.api.030101.xyz/?type=bestcf",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestproxy.txt",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestcf.txt"
    ]
    output_files = ["bestproxy.txt", "bestcf.txt", "best.txt", "cf.txt"]
    convert_ips(input_urls, output_files, max_workers=20)
