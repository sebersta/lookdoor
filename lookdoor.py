import json
import requests
import base64
import urllib.parse
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

PHONE_NUMBER = ''
PASSWORD = ''

def MD5(msg):
    import hashlib
    return(hashlib.md5(msg.encode('utf-8')).hexdigest())

def encrypt(key, msg):
    cipher = Cipher(algorithms.AES(str.encode(key)), modes.ECB())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    msg = padder.update(str.encode(msg)) + padder.finalize()
    ct = encryptor.update(msg) + encryptor.finalize()
    return base64.b64encode(ct)

def login():
    resp = requests.post('https://api.lookdoor.cn:443/func/hjapp/user/v2/getPasswordAesKey.json?')
    cookie = resp.headers['set-cookie']
    regex = re.compile(r'Max-Age=1800, (.*); Path')
    match = regex.search(cookie)
    cookie=match.group(1)
    aes_key = resp.json()['data']['aesKey']
    print(aes_key)
    password_md5 = MD5(PASSWORD)
    password_encypted = urllib.parse.quote_plus(encrypt(aes_key, password_md5))
    
    url = f'https://api.lookdoor.cn:443/func/hjapp/user/v2/login.json?password={password_encypted}&deviceId=&loginNumber={PHONE_NUMBER}&equipmentFlag=1'
    requests.post(url, headers={'cookie': cookie})
    
def unlock(door_number): 
    url = f'https://api.lookdoor.cn/func/hjapp/house/v1/getEquipAccessListNew.json'
    resp = requests.post(url, headers={'cookie': cookie})
    print(resp.json())
    equipment_id = resp.json()['data'][door_number]['id'] 
    
    url = f'https://api.lookdoor.cn:443/func/hjapp/house/v1/pushOpenDoorBySn.json?equipmentId={equipment_id}'
    resp = requests.post(url, headers={'cookie': cookie})
    print(resp.json())
    return resp.json()


def main():
    login()
    unlock(0) # 若账号绑定多个门，则需要修改这里的door_number来指定开哪个门。
    #unlock(1) # 也可以同时打开多个门。

if __name__ == "__main__":
    main()
