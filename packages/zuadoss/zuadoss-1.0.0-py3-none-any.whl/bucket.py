"""
ZUAD OSS Bucket模块
"""

import json
import time
import hashlib
import mimetypes
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, BinaryIO
from urllib.parse import urljoin, quote
import requests
import os

from .auth import Auth
from .exceptions import *
from .models import *


class Bucket:
    """
    ZUAD OSS 存储桶类，兼容阿里云OSS的Bucket接口
    """
    
    def __init__(self, auth: Auth, endpoint: str, bucket_name: str, 
                 is_cname: bool = False, session: Optional[requests.Session] = None,
                 connect_timeout: int = 60, read_timeout: int = 120):
        """
        初始化存储桶对象
        
        Args:
            auth: 认证对象
            endpoint: OSS服务端点
            bucket_name: 存储桶名称
            is_cname: 是否使用CNAME
            session: HTTP会话对象
            connect_timeout: 连接超时时间
            read_timeout: 读取超时时间
        """
        self.auth = auth
        self.endpoint = endpoint.rstrip('/')
        self.bucket_name = bucket_name
        self.is_cname = is_cname
        self.session = session or requests.Session()
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        
        # 构建基础URL
        if is_cname:
            self.base_url = f"{self.endpoint}"
        else:
            self.base_url = f"{self.endpoint}/api/v1"
    
    def _make_request(self, method: str, path: str, headers: Optional[Dict] = None,
                     params: Optional[Dict] = None, data: Optional[bytes] = None,
                     stream: bool = False) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            path: 请求路径
            headers: HTTP头部
            params: 查询参数
            data: 请求体数据
            stream: 是否流式响应
            
        Returns:
            HTTP响应对象
        """
        if headers is None:
            headers = {}
        
        # 构建完整URL
        if path.startswith('/'):
            url = self.base_url + path
        else:
            url = f"{self.base_url}/{path}"
        
        # 添加默认头部
        # headers.setdefault('Date', time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()))
        headers.setdefault('User-Agent', 'zuadoss-python-sdk/1.0.0')
        
        # 如果有数据，计算Content-MD5
        if data:
            md5_hash = hashlib.md5(data).digest()
            headers['Content-MD5'] = base64.b64encode(md5_hash).decode('utf-8')
            headers.setdefault('Content-Type', 'application/octet-stream')
        
        # 生成签名
        authorization = self.auth.sign_request(method, url, headers, params)
        headers['Authorization'] = authorization
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                stream=stream,
                timeout=(self.connect_timeout, self.read_timeout)
            )
            
            # 检查响应状态
            self._check_response(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", e)
    
    def _check_response(self, response: requests.Response):
        """
        检查响应状态并抛出相应异常
        
        Args:
            response: HTTP响应对象
        """
        if response.status_code < 400:
            return
        
        request_id = response.headers.get('x-oss-request-id')
        
        try:
            error_data = response.json()
            error_code = error_data.get('error_code', 'Unknown')
            message = error_data.get('detail', response.text)
        except:
            error_code = 'Unknown'
            message = response.text or f"HTTP {response.status_code}"
        
        # 根据状态码和错误代码抛出相应异常
        if response.status_code == 404:
            if 'bucket' in message.lower():
                raise NoSuchBucket(self.bucket_name, request_id)
            else:
                raise NoSuchKey(message, request_id)
        elif response.status_code == 403:
            if 'access' in error_code.lower():
                raise InvalidAccessKeyId(self.auth.access_key_id, request_id)
            elif 'signature' in error_code.lower():
                raise SignatureDoesNotMatch(message, request_id)
            else:
                raise AccessDenied(message, request_id)
        elif response.status_code == 409:
            if 'bucket' in message.lower() and 'exist' in message.lower():
                raise BucketAlreadyExists(self.bucket_name, request_id)
            elif 'empty' in message.lower():
                raise BucketNotEmpty(self.bucket_name, request_id)
        elif response.status_code == 400:
            raise InvalidArgument('request', message, request_id)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, request_id)
        else:
            raise ZuadOSSError(message, response.status_code, error_code, request_id)
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """解析日期时间字符串"""
        try:
            # 尝试解析ISO格式
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # 尝试解析时间戳
                return datetime.fromtimestamp(float(date_str))
            except:
                return datetime.now()
    
    # 存储桶操作
    def create_bucket(self, permission: str = 'private') -> None:
        """
        创建存储桶
        
        Args:
            permission: 存储桶权限 (private, public-read, public-read-write)
        """
        data = {
            'name': self.bucket_name,
            'acl': permission
        }
        
        self._make_request('POST', '/buckets/', data=json.dumps(data).encode('utf-8'),
                          headers={'Content-Type': 'application/json'})
    
    def delete_bucket(self) -> None:
        """删除存储桶"""
        self._make_request('DELETE', f'/buckets/{self.bucket_name}')
    
    def bucket_exists(self) -> bool:
        """
        检查存储桶是否存在
        
        Returns:
            存储桶是否存在
        """
        try:
            self._make_request('GET', f'/buckets/{self.bucket_name}')
            return True
        except NoSuchBucket:
            return False
    
    def get_bucket_info(self) -> BucketInfo:
        """
        获取存储桶信息
        
        Returns:
            存储桶信息对象
        """
        response = self._make_request('GET', f'/buckets/{self.bucket_name}')
        data = response.json()
        
        return BucketInfo(
            name=data['name'],
            creation_date=self._parse_datetime(str(data['created_at'])),
            location=data.get('region', 'us-east-1'),
            acl=data.get('acl', 'private'),
            versioning_enabled=data.get('versioning_enabled', False),
            object_count=data.get('object_count', 0),
            total_size=data.get('total_size', 0)
        )
    
    # 对象操作
    def put_object(self, key: str, data: Union[str, bytes, BinaryIO],
                   headers: Optional[Dict] = None, progress_callback=None) -> PutObjectResult:
        """
        上传对象
        
        Args:
            key: 对象键名
            data: 对象数据
            headers: HTTP头部
            progress_callback: 进度回调函数
            
        Returns:
            上传结果
        """
        if headers is None:
            headers = {}
        
        # 处理数据
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif hasattr(data, 'read'):
            data = data.read()
        
        # 自动检测Content-Type
        if 'Content-Type' not in headers:
            content_type, _ = mimetypes.guess_type(key)
            if content_type:
                # 为文本类型添加charset
                if content_type.startswith('text/'):
                    content_type += '; charset=utf-8'
                headers['Content-Type'] = content_type
        
        # 上传对象
        response = self._make_request('PUT', f'/objects/{self.bucket_name}/{quote(key, safe="/")}',
                                    headers=headers, data=data)
        
        result_data = response.json()
        return PutObjectResult(
            etag=result_data.get('etag', ''),
            request_id=response.headers.get('x-oss-request-id')
        )
    
    def put_object_from_file(self, key: str, filename: str, 
                            headers: Optional[Dict] = None, progress_callback=None) -> PutObjectResult:
        """
        从本地文件上传对象（兼容阿里云OSS接口）
        
        Args:
            key: 对象键名
            filename: 本地文件路径
            headers: HTTP头部
            progress_callback: 进度回调函数
            
        Returns:
            上传结果
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"本地文件不存在: {filename}")
        
        if headers is None:
            headers = {}
        
        # 自动检测Content-Type（优先使用文件路径检测）
        if 'Content-Type' not in headers:
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type, _ = mimetypes.guess_type(key)
            if content_type:
                headers['Content-Type'] = content_type
        
        # 读取文件内容
        with open(filename, 'rb') as f:
            file_data = f.read()
        
        # 调用put_object方法
        return self.put_object(key, file_data, headers, progress_callback)
    
    def get_object(self, key: str, byte_range: Optional[tuple] = None,
                   headers: Optional[Dict] = None, progress_callback=None) -> GetObjectResult:
        """
        下载对象
        
        Args:
            key: 对象键名
            byte_range: 字节范围 (start, end)
            headers: HTTP头部
            progress_callback: 进度回调函数
            
        Returns:
            下载结果
        """
        if headers is None:
            headers = {}
        
        # 添加Range头部
        if byte_range:
            start, end = byte_range
            headers['Range'] = f'bytes={start}-{end}'
        
        response = self._make_request('GET', f'/objects/{self.bucket_name}/{quote(key, safe="/")}',
                                    headers=headers, stream=True)
        
        # 读取内容
        content = response.content
        
        return GetObjectResult(
            content=content,
            content_length=len(content),
            content_type=response.headers.get('Content-Type'),
            etag=response.headers.get('ETag'),
            last_modified=self._parse_datetime(response.headers.get('Last-Modified', '')),
            metadata=self._extract_metadata(response.headers),
            request_id=response.headers.get('x-oss-request-id')
        )
    
    def get_object_to_file(self, key: str, filename: str, byte_range: Optional[tuple] = None,
                          headers: Optional[Dict] = None, progress_callback=None) -> None:
        """
        下载对象到本地文件（兼容阿里云OSS接口）
        
        Args:
            key: 对象键名
            filename: 本地文件路径
            byte_range: 字节范围 (start, end)
            headers: HTTP头部
            progress_callback: 进度回调函数
        """
        if headers is None:
            headers = {}
        
        # 添加Range头部
        if byte_range:
            start, end = byte_range
            headers['Range'] = f'bytes={start}-{end}'
        
        response = self._make_request('GET', f'/objects/{self.bucket_name}/{quote(key, safe="/")}',
                                    headers=headers, stream=True)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 写入文件
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    if progress_callback:
                        progress_callback(len(chunk))
    
    def delete_object(self, key: str) -> DeleteObjectResult:
        """
        删除对象
        
        Args:
            key: 对象键名
            
        Returns:
            删除结果
        """
        response = self._make_request('DELETE', f'/objects/{self.bucket_name}/{quote(key, safe="/")}')
        
        return DeleteObjectResult(
            request_id=response.headers.get('x-oss-request-id')
        )
    
    def object_exists(self, key: str) -> bool:
        """
        检查对象是否存在
        
        Args:
            key: 对象键名
            
        Returns:
            对象是否存在
        """
        try:
            self._make_request('GET', f'/objects/{self.bucket_name}/{quote(key, safe="/")}/info')
            return True
        except NoSuchKey:
            return False
    
    def get_object_meta(self, key: str) -> ObjectInfo:
        """
        获取对象元数据
        
        Args:
            key: 对象键名
            
        Returns:
            对象信息
        """
        response = self._make_request('GET', f'/objects/{self.bucket_name}/{quote(key, safe="/")}/info')
        data = response.json()
        
        return ObjectInfo(
            key=data['key'],
            size=data['size'],
            last_modified=self._parse_datetime(str(data['last_modified'])),
            etag=data['etag'],
            content_type=data.get('content_type'),
            metadata=data.get('metadata', {}),
            storage_class=data.get('storage_class', 'Standard')
        )
    
    def list_objects(self, prefix: str = '', delimiter: str = '', marker: str = '',
                    max_keys: int = 1000) -> ListObjectsResult:
        """
        列举对象
        
        Args:
            prefix: 对象键名前缀
            delimiter: 分隔符
            marker: 起始标记
            max_keys: 最大返回数量
            
        Returns:
            列举结果
        """
        params = {
            'prefix': prefix,
            'max_keys': max_keys
        }
        if delimiter:
            params['delimiter'] = delimiter
        if marker:
            params['marker'] = marker
        
        response = self._make_request('GET', f'/objects/{self.bucket_name}/', params=params)
        data = response.json()
        
        result = ListObjectsResult(
            bucket_name=self.bucket_name,
            prefix=prefix,
            marker=marker,
            max_keys=max_keys,
            is_truncated=data.get('is_truncated', False),
            next_marker=data.get('next_marker'),
            delimiter=delimiter
        )
        
        # 添加对象信息
        for obj_data in data.get('contents', []):
            obj_info = ObjectInfo(
                key=obj_data.get('display_name', obj_data['key']),  # 使用显示名称作为key
                size=obj_data['size'],
                last_modified=self._parse_datetime(str(obj_data['last_modified'])),
                etag=obj_data['etag'],
                content_type=obj_data.get('content_type'),
                metadata=obj_data.get('metadata', {}),
                storage_class=obj_data.get('storage_class', 'Standard')
            )
            result.append(obj_info)
        
        # 添加公共前缀
        for prefix in data.get('common_prefixes', []):
            result.append_common_prefix(prefix)
        
        return result
    
    # 分片上传操作
    def init_multipart_upload(self, key: str, headers: Optional[Dict] = None) -> InitMultipartUploadResult:
        """
        初始化分片上传
        
        Args:
            key: 对象键名
            headers: HTTP头部
            
        Returns:
            初始化结果
        """
        if headers is None:
            headers = {}
        
        response = self._make_request('POST', f'/objects/{self.bucket_name}/{quote(key, safe="/")}/multipart',
                                    headers=headers)
        data = response.json()
        
        return InitMultipartUploadResult(
            bucket_name=self.bucket_name,
            key=key,
            upload_id=data['upload_id'],
            request_id=response.headers.get('x-oss-request-id')
        )
    
    def upload_part(self, key: str, upload_id: str, part_number: int, data: bytes) -> UploadPartResult:
        """
        上传分片
        
        Args:
            key: 对象键名
            upload_id: 上传ID
            part_number: 分片号
            data: 分片数据
            
        Returns:
            上传结果
        """
        response = self._make_request('POST', f'/objects/{self.bucket_name}/{quote(key, safe="/")}/multipart/{upload_id}/{part_number}',
                                    data=data)
        data = response.json()
        
        return UploadPartResult(
            part_number=part_number,
            etag=data['etag'],
            request_id=response.headers.get('x-oss-request-id')
        )
    
    def complete_multipart_upload(self, key: str, upload_id: str, 
                                 parts: List[PartInfo]) -> CompleteMultipartUploadResult:
        """
        完成分片上传
        
        Args:
            key: 对象键名
            upload_id: 上传ID
            parts: 分片信息列表
            
        Returns:
            完成结果
        """
        parts_data = [
            {
                'part_number': part.part_number,
                'etag': part.etag
            }
            for part in parts
        ]
        
        data = {
            'upload_id': upload_id,
            'parts': parts_data
        }
        
        response = self._make_request('POST', f'/objects/{self.bucket_name}/{quote(key, safe="/")}/multipart/{upload_id}/complete',
                                    data=json.dumps(data).encode('utf-8'),
                                    headers={'Content-Type': 'application/json'})
        
        result_data = response.json()
        
        return CompleteMultipartUploadResult(
            bucket_name=self.bucket_name,
            key=key,
            etag=result_data['etag'],
            location=f"{self.base_url}/objects/{self.bucket_name}/{quote(key, safe='/')}",
            request_id=response.headers.get('x-oss-request-id')
        )
    
    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        """
        取消分片上传
        
        Args:
            key: 对象键名
            upload_id: 上传ID
        """
        self._make_request('DELETE', f'/objects/{self.bucket_name}/{quote(key, safe="/")}/multipart/{upload_id}')
    
    def _extract_metadata(self, headers: Dict[str, str]) -> Dict[str, str]:
        """从HTTP头部提取用户元数据"""
        metadata = {}
        for key, value in headers.items():
            if key.lower().startswith('x-oss-meta-'):
                metadata[key[11:]] = value  # 移除 'x-oss-meta-' 前缀
        return metadata
    
    # 预签名URL
    def sign_url(self, method: str, key: str, expires: int, headers: Optional[Dict] = None,
                params: Optional[Dict] = None) -> str:
        """
        生成预签名URL
        
        Args:
            method: HTTP方法
            key: 对象键名
            expires: 过期时间戳
            headers: HTTP头部
            params: 查询参数
            
        Returns:
            预签名URL
        """
        url = f"{self.base_url}/objects/{self.bucket_name}/{quote(key, safe="/")}"
        return self.auth.sign_url(method, url, expires, headers, params) 