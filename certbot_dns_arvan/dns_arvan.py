import logging
import requests
import zope.interface
from certbot import errors, interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    description = 'Obtain certificates using a DNS TXT record (if you are using ArvanCloud for DNS).'

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='ArvanCloud credentials INI file.')

    def _setup_credentials(self):
        self._configure_file('credentials', 'ArvanCloud credentials INI file')
        self.credentials = self._configure_credentials(
            'credentials',
            'ArvanCloud credentials INI file',
            {
                'key': 'API Key for ArvanCloud account'
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_arvan_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_arvan_client().del_txt_record(domain, validation_name, validation)

    def _get_arvan_client(self):
        return _ArvanClient(self.credentials.conf('key'))

class _ArvanClient(object):
    def __init__(self, apikey):
        clean_key = apikey.replace("apikey", "").replace("Apikey", "").replace("APIKEY", "").strip()
        self.apikey = f"Apikey {clean_key}"
        self.api_url = "https://napi.arvancloud.ir/cdn/4.0/domains"

    def _get_headers(self):
        return {
            "Authorization": self.apikey,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _find_domain(self, domain_name):
        try:
            page = 1
            domains_list = []
            while True:
                res = requests.get(f"{self.api_url}?page={page}", headers=self._get_headers(), timeout=15)
                if res.status_code != 200:
                    raise errors.PluginError(f"ArvanCloud API Error: {res.status_code}")
                
                json_data = res.json()
                domains_list.extend(json_data.get('data', []))
                
                meta = json_data.get('meta', {})
                if meta.get('current_page', 1) >= meta.get('last_page', 1):
                    break
                page += 1
                
            parts = domain_name.split('.')
            
            for i in range(len(parts) - 1):
                candidate = ".".join(parts[i:])
                for d in domains_list:
                    if d['name'] == candidate:
                        return candidate
        except Exception as e:
            raise errors.PluginError(f"Error finding domain: {e}")

        raise errors.PluginError(f"Domain {domain_name} not found in ArvanCloud account.")

    def add_txt_record(self, domain, validation_name, validation):
        root_domain = self._find_domain(domain)
        if validation_name == root_domain:
             relative_name = "@"
        else:
             suffix = "." + root_domain
             if validation_name.endswith(suffix):
                 relative_name = validation_name[:-len(suffix)]
             else:
                 relative_name = validation_name

        data = {
            "type": "txt", "name": relative_name, "cloud": False, "ttl": 120,
            "value": {"text": validation}
        }
        
        res = requests.post(f"{self.api_url}/{root_domain}/dns-records", headers=self._get_headers(), json=data)
        if res.status_code != 201:
             if "already exists" not in res.text.lower():
                 raise errors.PluginError(f"Error adding TXT record: {res.text}")

    def del_txt_record(self, domain, validation_name, validation):
        try:
            root_domain = self._find_domain(domain)
            if validation_name == root_domain:
                 relative_name = "@"
            else:
                 suffix = "." + root_domain
                 if validation_name.endswith(suffix):
                     relative_name = validation_name[:-len(suffix)]
                 else:
                     relative_name = validation_name

            res = requests.get(f"{self.api_url}/{root_domain}/dns-records", headers=self._get_headers(), params={"type": "txt", "search": relative_name})
            if res.status_code == 200:
                for record in res.json().get('data', []):
                    if record['type'] == 'txt' and record['name'] == relative_name:
                        requests.delete(f"{self.api_url}/{root_domain}/dns-records/{record['id']}", headers=self._get_headers())
        except:
            pass