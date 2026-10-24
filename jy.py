import json
import random
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

PLAIN_JSON = '{"setLeft":24,"passtime":204,"userresponse":25.85812369116827,"device_id":"","lot_number":"b2dd3c86dcde4fbdafe008dc92c51a75","pow_msg":"1|0|sha256|2026-10-24 10:06:51.176896+08:00|54088bb07d2df3c46b79f80300b0abbe|b2dd3c86dcde4fbdafe008dc92c51a75||43c27177a6c4740e","pow_sign":"0d5d583ab0280e3808c862181b80bcf826e99bbf0748e5939e05cc5aad8191cf","geetest":"captcha","lang":"zh","ep":"123","biht":"1426265548","gee_guard":{"roe":{"aup":"3","sep":"3","egp":"3","auh":"3","rew":"3","snh":"3","res":"3","cdc":"3"}},"dQFB":"BoHp","c866dc":{"08dc92c5":{"d4d6":"6dcde4fb"}},"em":{"ph":0,"cp":0,"ek":"11","wd":1,"nt":0,"si":0,"sc":0},"td_sign":"5f8001cfc3ff84ac29a802bab987710ecab79303e13fcdf65090f1c7bfbb6d46"}'

N_HEX = "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81"
N = int(N_HEX, 16)
E = 65537


def generate_16_char_str():
    def e():
        num = int(65536 * (1 + random.random()))
        return format(num, 'x')[1:]

    return e() + e() + e() + e()


def get_aes_hex(plain_str, key_str):
    iv_str = "0000000000000000"

    key_bytes = key_str.encode('utf-8')
    iv_bytes = iv_str.encode('utf-8')
    plain_bytes = plain_str.encode('utf-8')

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    ciphertext = cipher.encrypt(pad(plain_bytes, AES.block_size))

    return binascii.hexlify(ciphertext).decode()


def get_rsa_hex(hex_str):
    ascii_bytes = [ord(c) for c in hex_str[::-1]]
    pad_length = 32 - 2 - 1 - len(ascii_bytes)

    random_pad = [random.randint(1, 255) for _ in range(pad_length)]
    word_array = [2, 0] + random_pad + ascii_bytes + [0]

    word_array = word_array[1:]

    M = 0
    for word in word_array:
        M = (M << 32) + word

    cipher_int = pow(M, E, N)

    s = hex(cipher_int)[2:]
    if len(s) < 256:
        s = "0" * (256 - len(s)) + s

    return s
def generate_w():
    random_key = generate_16_char_str()
    c_hex = get_aes_hex(PLAIN_JSON, random_key)
    u_hex = get_rsa_hex(random_key)
    w = c_hex + u_hex
    return w


if __name__ == "__main__":
    w_parameter = generate_w()
    print(w_parameter)