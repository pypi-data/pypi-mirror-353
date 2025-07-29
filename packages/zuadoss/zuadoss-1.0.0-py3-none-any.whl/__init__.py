"""
ZUAD OSS Python SDK

一个兼容OSS接口的对象存储Python客户端SDK
"""

__version__ = "1.0.0"
__author__ = "ZUAD OSS Team"

from .auth import Auth
from .bucket import Bucket
from .exceptions import (
    ZuadOSSError,
    NoSuchBucket,
    NoSuchKey,
    AccessDenied,
    InvalidAccessKeyId,
    SignatureDoesNotMatch,
    RequestTimeTooSkewed,
    InvalidArgument,
    BucketAlreadyExists,
    BucketNotEmpty,
    InvalidBucketName,
    TooManyBuckets,
    EntityTooLarge,
    InvalidPartOrder,
    InvalidPart,
    NoSuchUpload,
    NetworkError,
    ServerError
)
from .models import (
    ObjectInfo,
    BucketInfo,
    ListObjectsResult,
    ListBucketsResult,
    PutObjectResult,
    GetObjectResult,
    DeleteObjectResult,
    MultipartUploadResult,
    PartInfo,
    InitMultipartUploadResult,
    UploadPartResult,
    CompleteMultipartUploadResult
)

__all__ = [
    'Auth',
    'Bucket', 
    'ZuadOSSError',
    'NoSuchBucket',
    'NoSuchKey',
    'AccessDenied',
    'InvalidAccessKeyId',
    'SignatureDoesNotMatch',
    'RequestTimeTooSkewed',
    'InvalidArgument',
    'BucketAlreadyExists',
    'BucketNotEmpty',
    'InvalidBucketName',
    'TooManyBuckets',
    'EntityTooLarge',
    'InvalidPartOrder',
    'InvalidPart',
    'NoSuchUpload',
    'NetworkError',
    'ServerError',
    'ObjectInfo',
    'BucketInfo',
    'ListObjectsResult',
    'ListBucketsResult',
    'PutObjectResult',
    'GetObjectResult',
    'DeleteObjectResult',
    'MultipartUploadResult',
    'PartInfo',
    'InitMultipartUploadResult',
    'UploadPartResult',
    'CompleteMultipartUploadResult'
] 