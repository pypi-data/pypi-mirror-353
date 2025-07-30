#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author: MaJian
@Time: 2024/1/20 17:23
@SoftWare: PyCharm
@Project: mortal
@File: __init__.py
"""
__all__ = ["m_crypt"]
from .crypt_main import m_crypt
"""
可用方法: 
   xxx.aes_ecb: 使用 AES ECB 模式对数据进行加密
      参数: 
         value: 需要加密的字符串
         key: 加密使用的密钥，支持 16/24/32 位
      返回: 加密后的字节数据
   xxx.aes_ecb_decrypt: 使用 AES ECB 模式对数据进行解密
      参数: 
         value: 需要解密的字节数据
         key: 解密使用的密钥，支持 16/24/32 位
      返回: 解密后的字符串
   xxx.aes_cbc: 使用 AES CBC 模式对数据进行加密
      参数: 
         value: 需要加密的字符串
         key: 加密使用的密钥，支持 16/24/32 位
         iv: 初始化向量，仅支持 16 位
      返回: 加密后的字节数据
   xxx.aes_cbc_decrypt: 使用 AES ECB 模式对数据进行解密
      参数: 
         value: 需要解密的字节数据
         key: 解密使用的密钥，支持 16/24/32 位
         iv: 初始化向量，仅支持 16 位
      返回: 解密后的字符串
   xxx.base64: 使用 Base64 编码对数据进行加密
      参数: 
         value: 需要加密的字符串
      返回: 加密后的字符串
   xxx.base64_decrypt: 使用 Base64 解码对数据进行解密
      参数: 
         value: 需要解密的字符串
      返回: 解密后的字符串
   xxx.des: 使用 DES 算法对数据进行加密
      参数: 
         value: 需要加密的字符串
         key: 加密使用的密钥，仅支持 8 位
      返回: 加密后的字节数据
   xxx.des_decrypt: 使用 DES 算法对数据进行解密
      参数: 
         value: 需要解密的字节数据
         key: 解密使用的密钥，仅支持 8 位
      返回: 解密后的字符串
   xxx.md5: 使用 MD5 算法对数据进行加密
      参数: 
         value: 需要加密的字符串
         key: 加密使用的密钥
         fmt: 输出格式，默认为 None，可选 upper、lower
      返回: 加密后的字符串
   xxx.md5_hmac: 使用 HMAC-MD5 算法对数据进行加密
      参数: 
         value: 需要加密的字符串
         key: 加密使用的密钥
      返回: 加密后的字节数据
   xxx.php: 使用 PHP 风格的加密算法对数据进行加密
      参数: 
         value: 需要加密的数据
         key: 加密使用的密钥，支持 1-16 汉字或 1-32 英文
         iv: 初始化向量，仅支持 16 位
         base64s: 是否使用 Base64 编码，默认为 False
      返回: base64s为 True 则返回加密后的字符串，base64s为 False 则返回加密后的字节数据
   xxx.php_decrypt: 使用 PHP 风格的解密算法对数据进行解密
      参数: 
         value: 需要解密的数据
         key: 解密使用的密钥，支持 1-16 汉字或 1-32 英文
         iv: 初始化向量，仅支持 16 位
         base64s: 是否使用 Base64 解码，默认为 False
      返回: 解密后的字符串
   xxx.rsa_keys: 生成 RSA 公钥和私钥对
      参数: 
         length: 默认 2048，可传入 len(text) 自动计算，最高支持 4096
   xxx.rsa: 使用 RSA 算法对数据进行加密
      参数: 
         value: 需要加密的数据，最高约支持 500 字节长度的数据
         pub_key: 公钥，可通过 xxx.m_rsa_keys() 获取
         hexs: 是否使用十六进制编码，默认为 False
      返回: 加密后的字节数据
   xxx.rsa_decrypt: 使用 RSA 算法对数据进行解密
      参数: 
         value: 需要解密的数据
         pri_key: 私钥，可通过 xxx.m_rsa_keys() 获取
         hexs: 是否使用十六进制解码，默认为 False
      返回: 解密后的字符串
   xxx.sha1: 使用 SHA1 算法对数据进行加密
      参数: 
         value: 需要加密的数据
         fmt: 输出格式，默认为 None，可选 upper、lower
      返回: 加密后的字符串
   xxx.sha256: 使用 SHA256 算法对数据进行加密
      参数: 
         value: 需要加密的数据
         fmt: 输出格式，默认为 None，可选 upper、lower
      返回: 加密后的字符串
   xxx.sha384: 使用 SHA384 算法对数据进行加密
      参数: 
         value: 需要加密的数据
         fmt: 输出格式，默认为 None，可选 upper、lower
      返回: 加密后的字符串
   xxx.sha512: 使用 SHA512 算法对数据进行加密
      参数: 
         value: 需要加密的数据
         fmt: 输出格式，默认为 None，可选 upper、lower
      返回: 加密后的字符串
   xxx.token: 生成加密的 Token
      参数: 
         data: 需要加密的数据
         key: 加密使用的密钥，任意字符串
         exp_time: Token 的有效期，默认为 86400 秒（1 天）
         issuer: Token 的发行者，默认为 Mortal
      返回: 加密后的字符串
   xxx.token_decrypt: 解密 Token 并获取原始数据
      参数: 
         token: 需要解密的 Token
         key: 解密使用的密钥，任意字符串
         issuer: Token 的发行者，默认为 Mortal
      返回: 解密后的数据
"""
