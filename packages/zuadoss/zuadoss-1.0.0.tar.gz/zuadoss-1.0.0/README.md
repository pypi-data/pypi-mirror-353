# ZUAD OSS Python SDK

🚀 **ZUAD OSS Python SDK** 是一个兼容OSS接口的对象存储Python客户端SDK，为ZUAD OSS服务提供完整的Python API支持。

## ✨ 特性

- 🔄 **完全兼容OSS SDK接口** - 无缝迁移，零学习成本
- 📦 **完整的对象存储功能** - 支持上传、下载、删除、列举等所有基本操作
- 🔧 **分片上传支持** - 支持大文件的分片上传和断点续传
- 🔐 **安全认证** - 支持访问密钥认证和预签名URL
- 📊 **丰富的元数据支持** - 支持自定义HTTP头部和对象元数据
- 🌐 **HTTP范围请求** - 支持部分内容下载
- 🛡️ **完善的异常处理** - 详细的错误信息和异常类型
- 📝 **类型提示支持** - 完整的类型注解，IDE友好

## 📦 安装

```bash
# 从源码安装
git clone <repository-url>
cd zuadoss
pip install -e .

# 或者直接安装依赖
pip install requests
```

## 🚀 快速开始

### 基本使用

```python
import zuadoss
from zuadoss import Auth, Bucket

# 初始化OSS客户端（兼容标准OSS接口）
auth = Auth('your_access_key_id', 'your_access_key_secret')
bucket = Bucket(auth, 'http://localhost:8000', 'your-bucket-name')

# 创建存储桶
bucket.create_bucket(permission='private')

# 上传对象
result = bucket.put_object('test.txt', 'Hello, ZUAD OSS!')
print(f"上传成功，ETag: {result.etag}")

# 从本地文件上传（兼容标准OSS接口）
result = bucket.put_object_from_file('upload.txt', '/path/to/local/file.txt')
print(f"文件上传成功，ETag: {result.etag}")

# 下载对象
obj = bucket.get_object('test.txt')
content = obj.content.decode('utf-8')
print(f"下载内容: {content}")

# 列举对象
objects = bucket.list_objects()
for obj in objects.object_list:
    print(f"对象: {obj.key}, 大小: {obj.size}")

# 删除对象
bucket.delete_object('test.txt')
```

### 高级功能

```python
# 带自定义头部的上传
headers = {
    'Content-Type': 'text/plain; charset=utf-8',
    'x-oss-meta-author': 'ZUAD OSS Team',
    'x-oss-meta-description': '自定义元数据'
}
bucket.put_object('custom.txt', '内容', headers=headers)

# 范围下载
obj = bucket.get_object('large-file.txt', byte_range=(0, 1023))  # 下载前1KB

# 分片上传
upload_result = bucket.init_multipart_upload('large-file.txt')
upload_id = upload_result.upload_id

# 上传分片
parts = []
for i, chunk in enumerate(file_chunks, 1):
    part_result = bucket.upload_part('large-file.txt', upload_id, i, chunk)
    parts.append(zuadoss.PartInfo(part_number=i, etag=part_result.etag))

# 完成分片上传
bucket.complete_multipart_upload('large-file.txt', upload_id, parts)

# 生成预签名URL
import time
expires = int(time.time()) + 3600  # 1小时后过期
signed_url = bucket.sign_url('GET', 'test.txt', expires)
```

## 📚 API 参考

### Auth 类

```python
auth = Auth(access_key_id, access_key_secret)
```

认证类，用于生成请求签名。

### Bucket 类

```python
bucket = Bucket(auth, endpoint, bucket_name, is_cname=False)
```

存储桶操作类，提供所有对象存储功能。

#### 存储桶操作

- `create_bucket(permission='private')` - 创建存储桶
- `delete_bucket()` - 删除存储桶
- `bucket_exists()` - 检查存储桶是否存在
- `get_bucket_info()` - 获取存储桶信息

#### 对象操作

- `put_object(key, data, headers=None)` - 上传对象
- `put_object_from_file(key, filename, headers=None)` - 从本地文件上传对象
- `get_object(key, byte_range=None, headers=None)` - 下载对象
- `delete_object(key)` - 删除对象
- `object_exists(key)` - 检查对象是否存在
- `get_object_meta(key)` - 获取对象元数据
- `list_objects(prefix='', delimiter='', marker='', max_keys=1000)` - 列举对象

#### 分片上传

- `init_multipart_upload(key, headers=None)` - 初始化分片上传
- `upload_part(key, upload_id, part_number, data)` - 上传分片
- `complete_multipart_upload(key, upload_id, parts)` - 完成分片上传
- `abort_multipart_upload(key, upload_id)` - 取消分片上传

#### 其他功能

- `sign_url(method, key, expires, headers=None, params=None)` - 生成预签名URL

## 🔧 配置选项

### 连接配置

```python
bucket = Bucket(
    auth=auth,
    endpoint='http://localhost:8000',
    bucket_name='my-bucket',
    is_cname=False,           # 是否使用CNAME
    connect_timeout=60,       # 连接超时时间（秒）
    read_timeout=120          # 读取超时时间（秒）
)
```

### 自定义HTTP会话

```python
import requests

session = requests.Session()
session.proxies = {'http': 'http://proxy:8080'}

bucket = Bucket(auth, endpoint, bucket_name, session=session)
```

## 🛡️ 异常处理

SDK提供了完善的异常处理机制：

```python
try:
    bucket.get_object('non-existent-key')
except zuadoss.NoSuchKey as e:
    print(f"对象不存在: {e.key}")
except zuadoss.AccessDenied as e:
    print(f"访问被拒绝: {e.message}")
except zuadoss.ZuadOSSError as e:
    print(f"OSS错误: {e.error_code} - {e.message}")
    print(f"状态码: {e.status_code}")
    print(f"请求ID: {e.request_id}")
```

### 异常类型

- `ZuadOSSError` - 基础异常类
- `NoSuchBucket` - 存储桶不存在
- `NoSuchKey` - 对象不存在
- `AccessDenied` - 访问被拒绝
- `InvalidAccessKeyId` - 无效的访问密钥ID
- `SignatureDoesNotMatch` - 签名不匹配
- `BucketAlreadyExists` - 存储桶已存在
- `BucketNotEmpty` - 存储桶非空
- `NetworkError` - 网络错误
- `ServerError` - 服务器错误

## 🔄 从阿里云OSS迁移

ZUAD OSS SDK与阿里云OSS SDK接口完全兼容，迁移只需要修改导入和初始化：

```python
# 阿里云OSS
import oss2
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)

# ZUAD OSS
import zuadoss
auth = zuadoss.Auth(access_key_id, access_key_secret)
bucket = zuadoss.Bucket(auth, endpoint, bucket_name)

# 其他API调用完全相同！
```

## 📝 示例代码

查看 `example.py` 文件获取完整的使用示例。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [ZUAD OSS 服务端](../README.md)
- [阿里云OSS Python SDK](https://github.com/aliyun/aliyun-oss-python-sdk)

---

**ZUAD OSS** - 企业级对象存储解决方案 🚀 