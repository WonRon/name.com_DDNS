import requests
from lxml import etree
from apscheduler.schedulers.blocking import BlockingScheduler
import time

# ------------------相关配置------------------ #

isloop=1 #是否循环
acct_name="muhefeng" # name.com的用户名
password="woainiA1" # name.com的密码
domain_name="131394.xyz" # 域名,如name.com
name="desktop.131394.xyz" # 子域名,如login.name.com
create_date="2023-01-01 05:13:22" # 创建时间
id="221444403" # DNS的ID
# ------------------相关配置------------------ #


# 获取ipv6地址
def getIPv6Address():
    text = requests.get('https://v6.ident.me').text
    return text
# 向name.com发包，实现DDNS
def ddns():
    proxies = {
    'http':None,
    'https':None
    }

    # 通过csrf_token登录
    s = requests.Session()
    r = s.get(url="https://www.name.com/account/login", proxies=proxies).text
    html = etree.HTML(r)
    csrf_token = html.xpath('/html/head/meta[9]/@content')[0]
    r = s.post(url="https://www.name.com/account/login", data={
      "acct_name": acct_name,
      "password": password,
      "csrf_token": csrf_token
    }, proxies=proxies,verify=False).status_code
    r = s.get(url="https://www.name.com/account", proxies=proxies).text

    # POST 信息
    update={
        "model_name":"dns",
        "id":id,
        "name":name,
        "type":"AAAA",
        "content":getIPv6Address(),
        "ttl":300,
        # "prio":None,
        "create_date":create_date,
        # "nickname":None
    }
    # 获取域名的信息
    getDomainDetails=s.get(url="https://www.name.com/account/domain/details/"+domain_name,proxies=proxies)

    # 获取更改域名信息的csrf_token
    html = etree.HTML(getDomainDetails.text)
    csrf_token = html.xpath('/html/head/meta[9]/@content')[0]
    # 在header中加入获取的csrf_token
    s.headers.update({"x-csrf-token-auth":csrf_token})
    #更新DNS信息
    r = s.put(url="https://www.name.com/api/v3/domain/"+domain_name+"/dns/"+id,json=update,proxies=proxies).text
    if r=="[]":
        print("=================================\n"+
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+":已更新DNS"+
        "=================================")

ddns()

sched = BlockingScheduler(timezone='Asia/Shanghai')
if isloop:
    # 设置每三小时执行一次更新
    sched.add_job(ddns, 'interval', hours=3)
    sched.start()
