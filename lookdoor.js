const request = require('request');
const crypto = require('crypto');
const querystring = require('querystring');

const phone_number = '';
const password_md5 = ''; // plaintext passwords work too
const equipment_id = '';

const encrypt = (key, msg) => {
    const cipher = crypto.createCipheriv('aes-128-ecb', key, '');
    const padder = crypto.createCipheriv('aes-128-ecb', key, '');
    let ct = cipher.update(padder.update(msg, 'utf8', 'hex'), 'hex', 'base64');
    ct += cipher.final('base64');
    return ct;
}

const main = async () => {
    const key_resp = await request('https://api.lookdoor.cn:443/func/hjapp/user/v2/getPasswordAesKey.json?');
    const cookie = key_resp.headers['set-cookie'];
    const aes_key = key_resp.body.data.aesKey;
    const password_encypted = querystring.escape(encrypt(aes_key, password_md5));
    const login_url = `https://api.lookdoor.cn:443/func/hjapp/user/v2/login.json?password=${password_encypted}&deviceId=&loginNumber=${phone_number}&equipmentFlag=1`;
    const login_resp = await request(login_url, {headers: {'cookie': cookie, 'Connection': 'keep-alive'}});
    
    const unlock_url = `https://api.lookdoor.cn:443/func/hjapp/house/v1/pushOpenDoorBySn.json?equipmentId=${equipment_id}`;
    const unlock_resp = await request(unlock_url, {headers: {'cookie': cookie}});
    return unlock_resp.body.message;
}

main().then(console.log);
