import json
import requests
import base64
import urllib.parse
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

PHONE_NUMBER = '在引号中填入手机号'
PASSWORD = '在引号中填入密码'


def MD5(msg):                   #将密码编码
    import hashlib
    return(hashlib.md5(msg.encode('utf-8')).hexdigest())


def encrypt(key, msg):          #模拟守望领域APP的方式进行AES加密
    cipher = Cipher(algorithms.AES(str.encode(key)), modes.ECB())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    msg = padder.update(str.encode(msg)) + padder.finalize()
    ct = encryptor.update(msg) + encryptor.finalize()
    return base64.b64encode(ct)


def login():                    
    key_resp = requests.post('https://api.lookdoor.cn:443/func/hjapp/user/v2/getPasswordAesKey.json?') #获取cookie, 获取AES密钥
    global cookie
    cookie = key_resp.headers['set-cookie']
    regex = re.compile(r'Max-Age=1800, (.*); Path')
    match = regex.search(cookie)
    cookie = match.group(1)
    aes_key = key_resp.json()['data']['aesKey']
    
    password_md5 = MD5(PASSWORD)
    password_encypted = urllib.parse.quote_plus(encrypt(aes_key, password_md5))             #加密密码
    login_url = f'https://api.lookdoor.cn:443/func/hjapp/user/v2/login.json?password={password_encypted}&deviceId=&loginNumber={PHONE_NUMBER}&equipmentFlag=1'
    requests.post(login_url, headers={'cookie': cookie})
    
    doorquery_url = f'https://api.lookdoor.cn/func/hjapp/house/v1/getEquipAccessListNew.json'         #查询门的ID
    global doorquery_resp
    doorquery_resp = requests.post(doorquery_url, headers={'cookie': cookie})


def unlock(door_number): 
    equipment_id = doorquery_resp.json()['data'][door_number]['id'] 
    unlock_url = f'https://api.lookdoor.cn:443/func/hjapp/house/v1/pushOpenDoorBySn.json?equipmentId={equipment_id}'       #发送开门请求
    unlock_resp = requests.post(unlock_url, headers={'cookie': cookie})
    # print(unlock_resp.json()) 
    return unlock_resp.json()


def main():
    login()
    unlock(0) # 若账号绑定多个门，则需要修改这里的door_number来指定开哪个门。
    #unlock(1) # 也可以同时打开多个门。

if __name__ == "__main__":
    main()
