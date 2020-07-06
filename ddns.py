import json
import requests
import smtplib
from dns import resolver

IPV4_INFO_URL = 'http://ifconfig.co/json'
CONFIG_FILE = 'config.json'


def get_config():
    return json.load(open(CONFIG_FILE))


def get_old_ip():
    res = resolver.Resolver()
    res.nameservers = ['1.1.1.1']
    answers = res.query('home.meic.dev')
    for rdata in answers:
        return rdata.address

def send_email(config, ip):
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(
        config['email_from'],
        config['email_to'],
        'Subject: Home IP changed\n\nIP changed to: {ip}'.format(
            ip=ip
        )
    )

def main():
    req = requests.get(url=IPV4_INFO_URL)

    if not req.ok:
        return
    ip = req.json()['ip']
    old_ip = get_old_ip()
    if ip == old_ip:
        return

    config = get_config()

    url = ('https://api.cloudflare.com/client/v4/zones/{zone_identifier}'
           '/dns_records/{identifier}').format(
        zone_identifier=config['zone_id'],
        identifier=config['dns_record_id'],
    )

    req = requests.put(
        url=url,
        headers={
            'X-Auth-Email': config['api_email'],
            'X-Auth-Key': config['api_key'],
        },
        json={
            'type': 'A',
            'name': 'home.meic.dev',
            'content': ip,
            'ttl': 120,
            'proxied': False,
        }
    )

    send_email(config, ip)


if __name__ == '__main__':
    main()
