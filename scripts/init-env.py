#!/usr/bin/env python3
"""Interactive local setup; never send credentials to a remote API or print them."""
import getpass,os,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from sabi_ray.profiles import domain,validate_secret

def main():
    output=pathlib.Path(__file__).resolve().parents[1]/'.env'
    if output.exists():raise ValueError('.env already exists; refusing overwrite')
    host=domain(input('Public TLS domain (no https://): '))
    username=input('Owner username [owner]: ').strip() or 'owner'
    if not re.fullmatch(r'[A-Za-z0-9_]{3,32}',username):raise ValueError('Use 3-32 letters/digits/underscores')
    password=validate_secret(getpass.getpass('Initial password (not displayed): '))
    if any(c in password for c in "'\"\r\n\x00"):
        raise ValueError('For this local env-file helper, use no quotes or line breaks in the password')
    if password!=getpass.getpass('Repeat password: '):raise ValueError('Passwords do not match')
    content=f"PUBLIC_DOMAIN={host}\nSABI_ADMIN_USER={username}\nSABI_INITIAL_PASSWORD='{password}'\nSABI_PROFILES=vless-ws,trojan-ws,vmess-ws\nSABI_CONTROL_ONLY=false\nSABI_ADVANCED=\nDEPLOY_MODE=docker\nPORT=8080\n"
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:f.write(content)
    print('Created private .env (0600). Save your password securely; no password was printed. Read docs/fa/02-vps-install.md.')
if __name__=='__main__':
    try:main()
    except (ValueError,OSError) as e:print('Setup stopped:',str(e),file=sys.stderr);sys.exit(1)
