#!/usr/bin/env python3
"""
ZUAD OSS Python SDK 使用示例

这个示例展示了如何使用ZUAD OSS SDK进行基本的对象存储操作，
接口设计完全兼容阿里云OSS SDK。
"""

import zuadoss
from zuadoss import Auth, Bucket
import time
import os

# 配置信息
OSS_ACCESS_KEY_ID = "your_access_key_id"
OSS_ACCESS_KEY_SECRET = "your_access_key_secret"
OSS_ENDPOINT = "http://localhost:8000"  # ZUAD OSS服务端点
OSS_BUCKET_NAME = "test-bucket"

def main():
    """主函数"""
    print("🚀 ZUAD OSS Python SDK 使用示例")
    print("=" * 50)
    
    # 1. 初始化OSS客户端（与阿里云OSS完全相同的接口）
    print("1. 初始化OSS客户端...")
    auth = Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    bucket = Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
    print("✅ OSS客户端初始化成功")
    
    try:
        # 2. 创建存储桶
        print("\n2. 创建存储桶...")
        try:
            bucket.create_bucket(permission='private')
            print(f"✅ 存储桶 '{OSS_BUCKET_NAME}' 创建成功")
        except zuadoss.BucketAlreadyExists:
            print(f"ℹ️  存储桶 '{OSS_BUCKET_NAME}' 已存在")
        
        # 3. 检查存储桶是否存在
        print("\n3. 检查存储桶是否存在...")
        exists = bucket.bucket_exists()
        print(f"✅ 存储桶存在状态: {exists}")
        
        # 4. 获取存储桶信息
        print("\n4. 获取存储桶信息...")
        bucket_info = bucket.get_bucket_info()
        print(f"✅ 存储桶信息:")
        print(f"   - 名称: {bucket_info.name}")
        print(f"   - 创建时间: {bucket_info.creation_date}")
        print(f"   - 地区: {bucket_info.location}")
        print(f"   - 权限: {bucket_info.acl}")
        print(f"   - 对象数量: {bucket_info.object_count}")
        print(f"   - 总大小: {bucket_info.total_size} 字节")
        
        # 5. 上传对象
        print("\n5. 上传对象...")
        test_content = "Hello, ZUAD OSS! 这是一个测试文件。🎉"
        test_key = "test/hello.txt"
        
        result = bucket.put_object(test_key, test_content)
        print(f"✅ 对象上传成功:")
        print(f"   - 键名: {test_key}")
        print(f"   - ETag: {result.etag}")
        
        # 5.1 从本地文件上传（兼容阿里云OSS接口）
        print("\n5.1 从本地文件上传...")
        
        # 创建测试文件
        local_test_file = "temp_test_file.txt"
        with open(local_test_file, 'w', encoding='utf-8') as f:
            f.write("这是从本地文件上传的内容 📁")
        
        try:
            file_key = "test/uploaded-from-file.txt"
            file_result = bucket.put_object_from_file(file_key, local_test_file)
            print(f"✅ 从本地文件上传成功:")
            print(f"   - 键名: {file_key}")
            print(f"   - ETag: {file_result.etag}")
            
            # 验证上传内容
            downloaded = bucket.get_object(file_key)
            print(f"   - 验证内容: {downloaded.content.decode('utf-8')}")
            
            # 清理文件
            bucket.delete_object(file_key)
            
        finally:
            # 删除临时文件
            if os.path.exists(local_test_file):
                os.remove(local_test_file)
        
        # 6. 检查对象是否存在
        print("\n6. 检查对象是否存在...")
        obj_exists = bucket.object_exists(test_key)
        print(f"✅ 对象存在状态: {obj_exists}")
        
        # 7. 获取对象元数据
        print("\n7. 获取对象元数据...")
        obj_meta = bucket.get_object_meta(test_key)
        print(f"✅ 对象元数据:")
        print(f"   - 键名: {obj_meta.key}")
        print(f"   - 大小: {obj_meta.size} 字节")
        print(f"   - 最后修改时间: {obj_meta.last_modified}")
        print(f"   - ETag: {obj_meta.etag}")
        print(f"   - 内容类型: {obj_meta.content_type}")
        
        # 8. 下载对象
        print("\n8. 下载对象...")
        obj_result = bucket.get_object(test_key)
        downloaded_content = obj_result.content.decode('utf-8')
        print(f"✅ 对象下载成功:")
        print(f"   - 内容: {downloaded_content}")
        print(f"   - 大小: {obj_result.content_length} 字节")
        
        # 9. 列举对象
        print("\n9. 列举对象...")
        list_result = bucket.list_objects(prefix="test/")
        print(f"✅ 对象列表 (前缀: test/):")
        for obj in list_result.object_list:
            print(f"   - {obj.key} ({obj.size} 字节, {obj.last_modified})")
        
        # 10. 分片上传示例
        print("\n10. 分片上传示例...")
        large_key = "test/large-file.txt"
        large_content = "这是一个大文件的内容。" * 1000  # 模拟大文件
        
        # 初始化分片上传
        init_result = bucket.init_multipart_upload(large_key)
        upload_id = init_result.upload_id
        print(f"✅ 分片上传初始化成功, Upload ID: {upload_id}")
        
        # 上传分片
        part_size = 1024  # 1KB per part
        parts = []
        part_number = 1
        
        for i in range(0, len(large_content.encode('utf-8')), part_size):
            part_data = large_content.encode('utf-8')[i:i+part_size]
            part_result = bucket.upload_part(large_key, upload_id, part_number, part_data)
            
            parts.append(zuadoss.PartInfo(
                part_number=part_number,
                etag=part_result.etag
            ))
            
            print(f"   - 分片 {part_number} 上传成功, ETag: {part_result.etag}")
            part_number += 1
        
        # 完成分片上传
        complete_result = bucket.complete_multipart_upload(large_key, upload_id, parts)
        print(f"✅ 分片上传完成:")
        print(f"   - 键名: {complete_result.key}")
        print(f"   - ETag: {complete_result.etag}")
        
        # 11. 生成预签名URL
        print("\n11. 生成预签名URL...")
        expires = int(time.time()) + 3600  # 1小时后过期
        signed_url = bucket.sign_url('GET', test_key, expires)
        print(f"✅ 预签名URL生成成功:")
        print(f"   - URL: {signed_url}")
        print(f"   - 过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires))}")
        
        # 12. 删除对象
        print("\n12. 删除对象...")
        bucket.delete_object(test_key)
        print(f"✅ 对象 '{test_key}' 删除成功")
        
        bucket.delete_object(large_key)
        print(f"✅ 对象 '{large_key}' 删除成功")
        
        print("\n🎉 所有操作完成！")
        
    except zuadoss.ZuadOSSError as e:
        print(f"❌ OSS操作失败: {e}")
        print(f"   - 错误代码: {e.error_code}")
        print(f"   - 状态码: {e.status_code}")
        print(f"   - 请求ID: {e.request_id}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def advanced_example():
    """高级功能示例"""
    print("\n" + "=" * 50)
    print("🔧 高级功能示例")
    print("=" * 50)
    
    # 初始化客户端
    auth = Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    bucket = Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
    
    try:
        # 1. 带自定义头部的上传
        print("1. 带自定义头部的上传...")
        custom_headers = {
            'Content-Type': 'text/plain; charset=utf-8',
            'x-oss-meta-author': 'ZUAD OSS Team',
            'x-oss-meta-description': '这是一个带自定义元数据的文件'
        }
        
        result = bucket.put_object(
            'test/custom-headers.txt',
            '带自定义头部的文件内容',
            headers=custom_headers
        )
        print(f"✅ 自定义头部上传成功, ETag: {result.etag}")
        
        # 2. 范围下载
        print("\n2. 范围下载...")
        range_result = bucket.get_object('test/custom-headers.txt', byte_range=(0, 10))
        print(f"✅ 范围下载成功: {range_result.content.decode('utf-8')}")
        
        # 3. 列举所有对象
        print("\n3. 列举所有对象...")
        all_objects = bucket.list_objects()
        print(f"✅ 存储桶中共有 {len(all_objects.object_list)} 个对象:")
        for obj in all_objects.object_list:
            print(f"   - {obj.key}")
        
        # 清理
        bucket.delete_object('test/custom-headers.txt')
        print("\n✅ 清理完成")
        
    except zuadoss.ZuadOSSError as e:
        print(f"❌ 高级功能操作失败: {e}")

if __name__ == "__main__":
    print("请先配置正确的访问密钥和端点信息！")
    print("然后取消注释下面的代码行来运行示例：")
    print()
    print("# main()")
    print("# advanced_example()")
    
    # 取消注释下面的行来运行示例
    # main()
    # advanced_example() 