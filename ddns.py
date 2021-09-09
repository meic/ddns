import json
import requests
import smtplib
from dns import resolver


class Ddns:
    IPV4_INFO_URL = "http://ifconfig.co/json"
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.config = json.load(open(self.CONFIG_FILE))

    def get_old_ip(self):
        res = resolver.Resolver()
        res.nameservers = ["1.1.1.1"]
        answers = res.resolve(self.config["hostname"])
        for rdata in answers:
            return rdata.address

    def send_email(self, ip):
        smtp = smtplib.SMTP("localhost")
        smtp.sendmail(
            self.config["email_from"],
            self.config["email_to"],
            "Subject: Home IP changed\n\nIP changed to: {ip}".format(ip=ip),
        )

    def run(self):
        req = requests.get(url=self.IPV4_INFO_URL)

        if not req.ok:
            return
        ip = req.json()["ip"]
        old_ip = self.get_old_ip()
        if ip == old_ip:
            return

        url = (
            "https://api.cloudflare.com/client/v4/zones/{zone_identifier}"
            "/dns_records/{identifier}"
        ).format(
            zone_identifier=self.config["zone_id"],
            identifier=self.config["dns_record_id"],
        )

        req = requests.put(
            url=url,
            headers={
                "X-Auth-Email": self.config["api_email"],
                "X-Auth-Key": self.config["api_key"],
            },
            json={
                "type": "A",
                "name": self.config["hostname"],
                "content": ip,
                "ttl": 120,
                "proxied": False,
            },
        )

        self.send_email(ip)


if __name__ == "__main__":
    Ddns().run()
