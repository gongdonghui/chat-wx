# 文件存储系统

## 概述

本项目实现了一个统一的文件存储系统，支持本地存储和S3存储，并提供了一致的接口供业务代码使用。

## 功能特性

- 统一的文件存储接口
- 支持本地存储和S3存储
- 支持配置文件配置
- 支持文件的保存、读取、删除等操作
- 支持文件的自动命名
- 支持目录结构

## 安装和配置

### 安装依赖

```bash
pip install boto3  # 如果需要使用S3存储
```

### 配置文件

配置文件位于 `config.ini`，示例配置如下：

```ini
[storage]
# 存储类型：local 或 s3
type = local

# 本地存储路径
local_path = /path/to/uploads

# S3存储配置（可选）
s3_bucket = your-s3-bucket
s3_region = us-east-1
s3_access_key = your-access-key
s3_secret_key = your-secret-key
```

## 接口定义

### StorageInterface

```python
class StorageInterface(ABC):
    @abstractmethod
    def save_file(self, file, directory=None, filename=None, suffix=None):
        """
        保存文件到存储系统
        
        :param file: 文件对象或BytesIO对象
        :param directory: 存储目录
        :param filename: 保存的文件名，如果为None则自动生成
        :param suffix: 文件名后缀
        :return: 保存后的文件路径或唯一标识符
        """
        pass
    
    @abstractmethod
    def get_file(self, file_id):
        """
        根据文件标识符获取文件
        
        :param file_id: 文件唯一标识符
        :return: 文件对象或文件路径
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_id):
        """
        删除存储系统中的文件
        
        :param file_id: 文件唯一标识符
        :return: 是否删除成功
        """
        pass
    
    @abstractmethod
    def get_file_path(self, file_id):
        """
        获取文件的完整路径
        
        :param file_id: 文件唯一标识符
        :return: 文件完整路径
        """
        pass
```

## 使用示例

### 本地存储

```python
from app.utils.storage import storage
from io import BytesIO

# 保存文件
file = BytesIO(b'Test content')
file_path = storage.save_file(file, directory='test', suffix='.txt')

# 读取文件
content = storage.get_file(file_path)

# 删除文件
storage.delete_file(file_path)
```

### S3存储

```python
from app.utils.s3_storage import S3Storage
from io import BytesIO

# 创建S3存储实例
s3_storage = S3Storage(
    bucket_name='your-s3-bucket',
    region_name='us-east-1',
    access_key='your-access-key',
    secret_key='your-secret-key'
)

# 保存文件
file = BytesIO(b'Test content')
file_key = s3_storage.save_file(file, directory='test', suffix='.txt')

# 读取文件
content = s3_storage.get_file(file_key)

# 获取文件URL
file_url = s3_storage.get_file_url(file_key)

# 删除文件
storage.delete_file(file_key)
```

## 业务集成

在app/api/rag.py和tasks/meeting.py中已经使用了新的存储系统，例如：

### 保存音频文件

```python
from app.utils.storage import storage

# 保存文件
file_path = storage.save_file(file, directory='audio', suffix='.wav')

# 读取文件
content = storage.get_file(file_path)

# 删除文件
storage.delete_file(file_path)
```

### 保存背景知识文件

```python
from app.utils.storage import storage

# 保存文件
temp_path = storage.save_file(file, directory='background', suffix=os.path.splitext(file.filename)[1].lower())
```

## 扩展支持

可以通过实现StorageInterface接口来支持更多的存储类型，例如：

- FTP存储
- SFTP存储
- 云存储服务（如阿里云OSS、腾讯云COS等）

## 注意事项

1. 使用S3存储时需要安装boto3库
2. 配置文件中的S3密钥需要妥善保管
3. 本地存储的路径需要确保有写入权限
4. 自动生成的文件名是唯一的UUID
5. 文件后缀应该包含点号（如`.txt`）
