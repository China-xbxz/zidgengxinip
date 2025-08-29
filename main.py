import requests
import ipaddress
import concurrent.futures

# ========== 获取IP列表 ==========
def get_ips_from_url(url):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.text.splitlines()
        else:
            print(f"❌ 获取 {url} 失败, 状态码: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ 请求 {url} 出错: {e}")
    return []

# ========== 获取IP地理位置（只使用免费API） ==========
def get_location(ip):
    apis = [
        lambda ip: requests.get(f"https://api.ip.sb/geoip/{ip}", timeout=5).json().get("country"),
        lambda ip: requests.get(f"https://ipinfo.io/{ip}/country", timeout=5).text.strip(),
        lambda ip: requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5).json().get("country"),
        lambda ip: requests.get(f"https://ipapi.co/{ip}/country_name/", timeout=5).text.strip(),
        lambda ip: requests.get(f"https://ipwhois.app/json/{ip}", timeout=5).json().get("country"),
        lambda ip: requests.get(f"https://freegeoip.app/json/{ip}", timeout=5).json().get("country_name"),
        lambda ip: requests.get(f"https://ipgeo-api.hf.space/{ip}", timeout=5).json().get("country")
    ]
    for api in apis:
        try:
            country = api(ip)
            if country:
                return country
        except:
            continue
    return "火星⭐"

# ========== 固定端口 ==========
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
            ipaddress.ip_address(ip)
            port = get_fixed_port()
            if not location.strip() or location == "火星⭐":
                location = get_location(ip)
            return f"{ip}:{port}#{location}"
        except:
            return line

    # 处理普通 IP
    parts = line.split()
    ip = parts[0]
    try:
        ipaddress.ip_address(ip)
        location = get_location(ip)
        port = get_fixed_port()
        return f"{ip}:{port}#{location}"
    except ValueError:
        return line

# ========== 主转换函数 ==========
def convert_ips(input_urls, output_files, max_workers=20):
    for input_url, output_file in zip(input_urls, output_files):
        ips = get_ips_from_url(input_url)
        results = set()
        failed = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_ip, line): line for line in ips}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result and "火星⭐" in result:
                    failed.add(result)
                if result:
                    results.add(result)

        # 写入最终结果
        with open(output_file, 'w', encoding="utf-8") as f:
            f.write("\n".join(sorted(results)))
        print(f"✅ 已保存 {len(results)} 条结果到 {output_file}")

        # 写入失败文件
        if failed:
            with open("failed.txt", 'a', encoding="utf-8") as f:
                f.write("\n".join(sorted(failed)) + "\n")
            print(f"⚠️ {len(failed)} 条定位失败已记录到 failed.txt")

# ========== 主程序 ==========
if __name__ == "__main__":
    input_urls = [
        "https://ipdb.api.030101.xyz/?type=bestproxy&country=true",
        "https://ipdb.api.030101.xyz/?type=bestcf",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestproxy.txt",
        "https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestcf.txt"
    ]
    output_files = ["bestproxy.txt", "bestcf.txt", "best.txt", "cf.txt"]
    convert_ips(input_urls, output_files, max_workers=20)
