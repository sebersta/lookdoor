import json
import requests
import base64
import urllib.parse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

phone_number = ''
password_md5 = '' # plaintext passwords work too
equipment_id = ''
# equipment_id1 = ''

def encrypt(key, msg):
    cipher = Cipher(algorithms.AES(str.encode(key)), modes.ECB())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    msg = padder.update(str.encode(msg)) + padder.finalize()
    ct = encryptor.update(msg) + encryptor.finalize()
    return base64.b64encode(ct)

def main():
    key_resp = requests.post('https://api.lookdoor.cn:443/func/hjapp/user/v2/getPasswordAesKey.json?')
    cookie = key_resp.headers['set-cookie']
    aes_key = key_resp.json()['data']['aesKey']
    password_encypted = urllib.parse.quote_plus(encrypt(aes_key, password_md5))
    login_url = f'https://api.lookdoor.cn:443/func/hjapp/user/v2/login.json?password={password_encypted}&deviceId=&loginNumber={phone_number}&equipmentFlag=1'
    login_resp=requests.post(login_url, headers={'cookie': cookie, 'Connection': 'keep-alive'})
    
    unlock_url = f'https://api.lookdoor.cn:443/func/hjapp/house/v1/pushOpenDoorBySn.json?equipmentId={equipment_id}'
    unlock_resp = requests.post(unlock_url, headers={'cookie': cookie})
    print(unlock_resp.json())

if __name__ == "__main__":
    main()
