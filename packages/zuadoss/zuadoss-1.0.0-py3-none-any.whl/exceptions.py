"""
ZUAD OSS 异常模块
"""


class ZuadOSSError(Exception):
    """
    ZUAD OSS 基础异常类
    """
    
    def __init__(self, message: str, status_code: int = None, error_code: str = None, 
                 request_id: str = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            status_code: HTTP状态码
            error_code: 错误代码
            request_id: 请求ID
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
    
    def __str__(self):
        return f"{self.error_code}: {self.message}" if self.error_code else self.message


class NoSuchBucket(ZuadOSSError):
    """存储桶不存在异常"""
    
    def __init__(self, bucket_name: str, request_id: str = None):
        message = f"The specified bucket does not exist: {bucket_name}"
        super().__init__(message, 404, "NoSuchBucket", request_id)
        self.bucket_name = bucket_name


class NoSuchKey(ZuadOSSError):
    """对象不存在异常"""
    
    def __init__(self, key: str, request_id: str = None):
        message = f"The specified key does not exist: {key}"
        super().__init__(message, 404, "NoSuchKey", request_id)
        self.key = key


class AccessDenied(ZuadOSSError):
    """访问被拒绝异常"""
    
    def __init__(self, message: str = "Access Denied", request_id: str = None):
        super().__init__(message, 403, "AccessDenied", request_id)


class InvalidAccessKeyId(ZuadOSSError):
    """无效的访问密钥ID异常"""
    
    def __init__(self, access_key_id: str, request_id: str = None):
        message = f"The OSS Access Key Id you provided does not exist in our records: {access_key_id}"
        super().__init__(message, 403, "InvalidAccessKeyId", request_id)
        self.access_key_id = access_key_id


class SignatureDoesNotMatch(ZuadOSSError):
    """签名不匹配异常"""
    
    def __init__(self, message: str = "The request signature we calculated does not match the signature you provided", 
                 request_id: str = None):
        super().__init__(message, 403, "SignatureDoesNotMatch", request_id)


class RequestTimeTooSkewed(ZuadOSSError):
    """请求时间偏差过大异常"""
    
    def __init__(self, message: str = "The difference between the request time and the current time is too large", 
                 request_id: str = None):
        super().__init__(message, 403, "RequestTimeTooSkewed", request_id)


class InvalidArgument(ZuadOSSError):
    """无效参数异常"""
    
    def __init__(self, argument_name: str, argument_value: str = None, request_id: str = None):
        if argument_value:
            message = f"Invalid argument: {argument_name}={argument_value}"
        else:
            message = f"Invalid argument: {argument_name}"
        super().__init__(message, 400, "InvalidArgument", request_id)
        self.argument_name = argument_name
        self.argument_value = argument_value


class BucketAlreadyExists(ZuadOSSError):
    """存储桶已存在异常"""
    
    def __init__(self, bucket_name: str, request_id: str = None):
        message = f"The requested bucket name is not available: {bucket_name}"
        super().__init__(message, 409, "BucketAlreadyExists", request_id)
        self.bucket_name = bucket_name


class BucketNotEmpty(ZuadOSSError):
    """存储桶非空异常"""
    
    def __init__(self, bucket_name: str, request_id: str = None):
        message = f"The bucket you tried to delete is not empty: {bucket_name}"
        super().__init__(message, 409, "BucketNotEmpty", request_id)
        self.bucket_name = bucket_name


class InvalidBucketName(ZuadOSSError):
    """无效存储桶名称异常"""
    
    def __init__(self, bucket_name: str, request_id: str = None):
        message = f"The specified bucket is not valid: {bucket_name}"
        super().__init__(message, 400, "InvalidBucketName", request_id)
        self.bucket_name = bucket_name


class TooManyBuckets(ZuadOSSError):
    """存储桶数量超限异常"""
    
    def __init__(self, message: str = "You have attempted to create more buckets than allowed", 
                 request_id: str = None):
        super().__init__(message, 400, "TooManyBuckets", request_id)


class EntityTooLarge(ZuadOSSError):
    """实体过大异常"""
    
    def __init__(self, message: str = "Your proposed upload exceeds the maximum allowed object size", 
                 request_id: str = None):
        super().__init__(message, 400, "EntityTooLarge", request_id)


class InvalidPartOrder(ZuadOSSError):
    """无效分片顺序异常"""
    
    def __init__(self, message: str = "The list of parts was not in ascending order", 
                 request_id: str = None):
        super().__init__(message, 400, "InvalidPartOrder", request_id)


class InvalidPart(ZuadOSSError):
    """无效分片异常"""
    
    def __init__(self, message: str = "One or more of the specified parts could not be found", 
                 request_id: str = None):
        super().__init__(message, 400, "InvalidPart", request_id)


class NoSuchUpload(ZuadOSSError):
    """分片上传不存在异常"""
    
    def __init__(self, upload_id: str, request_id: str = None):
        message = f"The specified multipart upload does not exist: {upload_id}"
        super().__init__(message, 404, "NoSuchUpload", request_id)
        self.upload_id = upload_id


class NetworkError(ZuadOSSError):
    """网络错误异常"""
    
    def __init__(self, message: str = "Network error occurred", original_error: Exception = None):
        super().__init__(message, None, "NetworkError", None)
        self.original_error = original_error


class ServerError(ZuadOSSError):
    """服务器错误异常"""
    
    def __init__(self, message: str = "Internal server error", status_code: int = 500, 
                 request_id: str = None):
        super().__init__(message, status_code, "InternalError", request_id) 