"""
ZUAD OSS 认证模块
"""

import hashlib
import hmac
import base64
import time
from urllib.parse import quote
from typing import Optional


class Auth:
    """
    ZUAD OSS 认证类，兼容阿里云OSS的Auth接口
    """
    
    def __init__(self, access_key_id: str, access_key_secret: str):
        """
        初始化认证对象
        
        Args:
            access_key_id: 访问密钥ID
            access_key_secret: 访问密钥Secret
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
    
    def _sign_string(self, string_to_sign: str) -> str:
        """
        对字符串进行签名
        
        Args:
            string_to_sign: 待签名的字符串
            
        Returns:
            签名结果
        """
        signature = base64.b64encode(
            hmac.new(
                self.access_key_secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        return signature
    
    def _build_canonical_string(self, method: str, resource: str, headers: dict, 
                               params: Optional[dict] = None) -> str:
        """
        构建规范化字符串（匹配服务器端签名算法）
        
        Args:
            method: HTTP方法
            resource: 资源路径
            headers: HTTP头部
            params: 查询参数
            
        Returns:
            规范化字符串
        """
        # 使用简化的签名算法，与服务器端保持一致
        # string_to_sign = f"{method}\n{content_md5}\n{content_type}\n{date}\n{path}"
        
        # 创建小写的headers字典，与服务器端保持一致
        lower_headers = {k.lower(): v for k, v in headers.items()}
        
        content_md5 = lower_headers.get('content-md5', '')
        content_type = lower_headers.get('content-type', '')
        date = lower_headers.get('date', '')
        
        # 简化的签名算法，只包含基本字段
        string_to_sign = f"{method}\n{content_md5}\n{content_type}\n{date}\n{resource}"
        
        return string_to_sign
    
    def sign_request(self, method: str, url: str, headers: dict, 
                    params: Optional[dict] = None) -> str:
        """
        对请求进行签名
        
        Args:
            method: HTTP方法
            url: 请求URL
            headers: HTTP头部
            params: 查询参数
            
        Returns:
            Authorization头部值
        """
        # 从URL中提取资源路径
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        resource = parsed_url.path
        
        # 构建规范化字符串
        string_to_sign = self._build_canonical_string(method, resource, headers, params)
        
        # 生成签名
        signature = self._sign_string(string_to_sign)
        
        # 返回Authorization头部
        return f"OSS {self.access_key_id}:{signature}"
    
    def sign_url(self, method: str, url: str, expires: int, headers: Optional[dict] = None,
                params: Optional[dict] = None) -> str:
        """
        生成预签名URL
        
        Args:
            method: HTTP方法
            url: 基础URL
            expires: 过期时间戳
            headers: HTTP头部
            params: 查询参数
            
        Returns:
            预签名URL
        """
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        
        # 添加过期时间
        headers['Date'] = str(expires)
        
        # 从URL中提取资源路径
        from urllib.parse import urlparse, parse_qs, urlencode
        parsed_url = urlparse(url)
        resource = parsed_url.path
        
        # 合并查询参数
        existing_params = parse_qs(parsed_url.query)
        for key, values in existing_params.items():
            if values:
                params[key] = values[0]
        
        # 构建规范化字符串
        string_to_sign = self._build_canonical_string(method, resource, headers, params)
        
        # 生成签名
        signature = self._sign_string(string_to_sign)
        
        # 构建预签名URL
        params.update({
            'OSSAccessKeyId': self.access_key_id,
            'Expires': str(expires),
            'Signature': signature
        })
        
        query_string = urlencode(params)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        return f"{base_url}?{query_string}" 