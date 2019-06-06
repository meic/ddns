import json
import requests

IPV4_INFO_URL = 'http://ifconfig.co/json'
CONFIG_FILE = 'config.json'


def get_config():
    return json.load(open(CONFIG_FILE))


def main():
    req = requests.get(url=IPV4_INFO_URL)
    ip = req.json()['ip']

    if not req.ok:
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


if __name__ == '__main__':
    main()