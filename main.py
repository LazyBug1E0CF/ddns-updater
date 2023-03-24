import json
import os
from threading import Timer

import requests
from abc import ABC, abstractmethod
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest


class DDNSProvider(ABC):
    @abstractmethod
    def update_dns(self, ip, *domains):
        pass


class Ali(DDNSProvider):
    def __init__(self, access_key, access_secret):
        self.key = access_key
        self.secret = access_secret
        self.client = AcsClient(self.key, self.secret)

    def update_dns(self, ip, *domains):
        for domain in domains:
            request = DescribeSubDomainRecordsRequest()
            request.set_accept_format("json")
            request.set_SubDomain(domain)
            resp = self.client.do_action_with_exception(request)
            domain_info = json.loads(resp)
            if domain_info["TotalCount"] == 0:
                # 域名记录不存在，创建之
                print(f"域名[{domain}]的记录不存在，准备添加")
                self.add(domain.split(".", maxsplit=1)[1], domain.split(".")[0], "A", ip)
                print(f"域名[{domain}]记录添加成功，当前ip -> {ip}")
            elif domain_info["TotalCount"] == 1:
                # 有唯一一条记录，更新之
                origin = domain_info['DomainRecords']['Record'][0]['Value']
                if origin.strip() != ip.strip():
                    print(
                        f"域名[{domain}]的记录已存在，准备更新，原ip -> {domain_info['DomainRecords']['Record'][0]['Value']}")
                    self.update(domain_info["DomainRecords"]["Record"][0]["RecordId"], domain.split(".")[0], "A", ip)
                    print(f"域名[{domain}]记录更新成功，当前ip -> {ip}")
                else:
                    print(f"域名[{domain}]的记录未发生变化，无需更新，ip -> {origin}")
            elif domain_info["TotalCount"] > 1:
                # 同时存在多条记录，这是有问题的，全部删除，创建之
                print(f"域名[{domain}]同时存在多条记录，将全部删除，再添加新记录")
                self.delete(domain.split(".", maxsplit=1)[1], domain.split(".")[0])
                self.add(domain.split(".", maxsplit=1)[1], domain.split(".")[0], "A", ip)
                print()

    def add(self, domain, rr, type, value):
        request = AddDomainRecordRequest()
        request.set_accept_format("json")
        request.set_DomainName(domain)
        request.set_RR(rr)
        request.set_Type(type)
        request.set_Value(value)
        self.client.do_action_with_exception(request)

    def update(self, record_id, rr, type, value):
        request = UpdateDomainRecordRequest()
        request.set_accept_format("json")
        request.set_RecordId(record_id)
        request.set_RR(rr)
        request.set_Type(type)
        request.set_Value(value)
        self.client.do_action_with_exception(request)

    def delete(self, domain, rr):
        request = DeleteSubDomainRecordsRequest()
        request.set_accept_format("json")
        request.set_DomainName(domain)
        request.set_RR(rr)
        self.client.do_action_with_exception(request)


ip_server = os.environ.get("IP_SERVER")
ddns_provider = os.environ.get("DDNS_PROVIDER", default="ali")
key = os.environ.get("ACCESS_KEY")
secret = os.environ.get("ACCESS_SECRET")
domains_str = os.environ.get("DOMAINS")
interval = os.environ.get("INTERVAL", default="5")


def main():
    do_job()


def do_job():
    ip = get_ip()
    if ip is not None:
        update_dns(ip.strip())
        Timer(int(interval) * 60, do_job).start()
    else:
        print("未能获取到ip，15秒后重试")
        Timer(15, do_job).start()


def get_ip():
    resp = requests.get(ip_server)
    if resp is None or resp.status_code != 200:
        print("获取ip地址失败")
    return resp.text


def update_dns(ip):
    provider = None
    if ddns_provider == "ali":
        provider = Ali(key, secret)
    provider.update_dns(ip, domains_str)


if __name__ == "__main__":
    main()
