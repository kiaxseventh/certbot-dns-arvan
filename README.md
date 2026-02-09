# ArvanCloud DNS Authenticator Plugin for Certbot

This plugin automates the process of completing a ``dns-01`` challenge by creating, and subsequently removing, TXT records using the ArvanCloud API.

## Installation

```bash
pip install certbot-dns-arvan


Usage
To use this plugin, you will need to create a configuration file containing your ArvanCloud API key.

Create a file named arvan.ini (or any name you prefer) with the following content:

Ini, TOML
dns_arvan_key = Apikey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Run certbot using the following command:

Bash
certbot certonly \
  --authenticator dns-arvan \
  --dns-arvan-credentials /path/to/arvan.ini \
  -d example.com