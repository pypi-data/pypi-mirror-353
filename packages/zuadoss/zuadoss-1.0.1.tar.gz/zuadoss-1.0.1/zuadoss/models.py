"""
ZUAD OSS 数据模型模块
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ObjectInfo:
    """对象信息"""
    key: str
    size: int
    last_modified: datetime
    etag: str
    content_type: str = None
    metadata: Dict[str, str] = None
    storage_class: str = "Standard"
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BucketInfo:
    """存储桶信息"""
    name: str
    creation_date: datetime
    location: str = "us-east-1"
    storage_class: str = "Standard"
    acl: str = "private"
    versioning_enabled: bool = False
    object_count: int = 0
    total_size: int = 0


@dataclass
class PartInfo:
    """分片信息"""
    part_number: int
    etag: str
    size: int = None
    last_modified: datetime = None


@dataclass
class MultipartUploadInfo:
    """分片上传信息"""
    upload_id: str
    key: str
    initiated: datetime
    storage_class: str = "Standard"


class ListObjectsResult:
    """列举对象结果"""
    
    def __init__(self, bucket_name: str, prefix: str = None, marker: str = None,
                 max_keys: int = 1000, is_truncated: bool = False,
                 next_marker: str = None, delimiter: str = None):
        self.bucket_name = bucket_name
        self.prefix = prefix or ""
        self.marker = marker or ""
        self.max_keys = max_keys
        self.is_truncated = is_truncated
        self.next_marker = next_marker
        self.delimiter = delimiter
        self.object_list: List[ObjectInfo] = []
        self.common_prefix_list: List[str] = []
    
    def append(self, obj_info: ObjectInfo):
        """添加对象信息"""
        self.object_list.append(obj_info)
    
    def append_common_prefix(self, prefix: str):
        """添加公共前缀"""
        self.common_prefix_list.append(prefix)
    
    @property
    def objects(self):
        """兼容性属性：返回object_list"""
        return self.object_list


class ListBucketsResult:
    """列举存储桶结果"""
    
    def __init__(self, owner_id: str = None, owner_display_name: str = None):
        self.owner_id = owner_id
        self.owner_display_name = owner_display_name
        self.bucket_list: List[BucketInfo] = []
    
    def append(self, bucket_info: BucketInfo):
        """添加存储桶信息"""
        self.bucket_list.append(bucket_info)


class PutObjectResult:
    """上传对象结果"""
    
    def __init__(self, etag: str, request_id: str = None, crc: str = None):
        self.etag = etag
        self.request_id = request_id
        self.crc = crc


class GetObjectResult:
    """获取对象结果"""
    
    def __init__(self, content: bytes, content_length: int, content_type: str = None,
                 etag: str = None, last_modified: datetime = None,
                 metadata: Dict[str, str] = None, request_id: str = None):
        self.content = content
        self.content_length = content_length
        self.content_type = content_type
        self.etag = etag
        self.last_modified = last_modified
        self.metadata = metadata or {}
        self.request_id = request_id
    
    def read(self, size: int = -1) -> bytes:
        """读取内容"""
        if size == -1:
            return self.content
        return self.content[:size]


class DeleteObjectResult:
    """删除对象结果"""
    
    def __init__(self, request_id: str = None, delete_marker: bool = False,
                 version_id: str = None):
        self.request_id = request_id
        self.delete_marker = delete_marker
        self.version_id = version_id


class InitMultipartUploadResult:
    """初始化分片上传结果"""
    
    def __init__(self, bucket_name: str, key: str, upload_id: str, request_id: str = None):
        self.bucket_name = bucket_name
        self.key = key
        self.upload_id = upload_id
        self.request_id = request_id


class UploadPartResult:
    """上传分片结果"""
    
    def __init__(self, part_number: int, etag: str, request_id: str = None, crc: str = None):
        self.part_number = part_number
        self.etag = etag
        self.request_id = request_id
        self.crc = crc


class CompleteMultipartUploadResult:
    """完成分片上传结果"""
    
    def __init__(self, bucket_name: str, key: str, etag: str, location: str = None,
                 request_id: str = None):
        self.bucket_name = bucket_name
        self.key = key
        self.etag = etag
        self.location = location
        self.request_id = request_id


class ListMultipartUploadsResult:
    """列举分片上传结果"""
    
    def __init__(self, bucket_name: str, key_marker: str = None, upload_id_marker: str = None,
                 max_uploads: int = 1000, is_truncated: bool = False,
                 next_key_marker: str = None, next_upload_id_marker: str = None,
                 prefix: str = None, delimiter: str = None):
        self.bucket_name = bucket_name
        self.key_marker = key_marker or ""
        self.upload_id_marker = upload_id_marker or ""
        self.max_uploads = max_uploads
        self.is_truncated = is_truncated
        self.next_key_marker = next_key_marker
        self.next_upload_id_marker = next_upload_id_marker
        self.prefix = prefix or ""
        self.delimiter = delimiter
        self.upload_list: List[MultipartUploadInfo] = []
        self.common_prefix_list: List[str] = []
    
    def append(self, upload_info: MultipartUploadInfo):
        """添加分片上传信息"""
        self.upload_list.append(upload_info)
    
    def append_common_prefix(self, prefix: str):
        """添加公共前缀"""
        self.common_prefix_list.append(prefix)


class ListPartsResult:
    """列举分片结果"""
    
    def __init__(self, bucket_name: str, key: str, upload_id: str,
                 part_number_marker: int = 0, max_parts: int = 1000,
                 is_truncated: bool = False, next_part_number_marker: int = None,
                 storage_class: str = "Standard"):
        self.bucket_name = bucket_name
        self.key = key
        self.upload_id = upload_id
        self.part_number_marker = part_number_marker
        self.max_parts = max_parts
        self.is_truncated = is_truncated
        self.next_part_number_marker = next_part_number_marker
        self.storage_class = storage_class
        self.part_list: List[PartInfo] = []
    
    def append(self, part_info: PartInfo):
        """添加分片信息"""
        self.part_list.append(part_info)


# 兼容性别名，与阿里云OSS SDK保持一致
MultipartUploadResult = CompleteMultipartUploadResult 