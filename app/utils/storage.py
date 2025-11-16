import os
import uuid
from abc import ABC, abstractmethod
from werkzeug.utils import secure_filename
from app.utils.config import config

class StorageInterface(ABC):
    """
    文件存储接口，定义了文件存储的基本操作
    """
    
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

class LocalStorage(StorageInterface):
    """
    本地文件存储实现
    """
    
    def __init__(self, base_path=None):
        """
        初始化本地存储
        
        :param base_path: 存储根目录，默认为配置文件中的 storage.local_path 或项目下的uploads目录
        """
        # 从配置文件中获取存储路径
        config_path = config.get('storage', 'local_path', None)
        
        # 优先级：参数 > 配置文件 > 默认值
        self.base_path = base_path or config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
        
        # 创建根目录
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
    
    def save_file(self, file, directory=None, filename=None, suffix=None):
        """
        保存文件到本地存储
        
        :param file: 文件对象或BytesIO对象
        :param directory: 存储目录
        :param filename: 保存的文件名，如果为None则自动生成
        :param suffix: 文件名后缀
        :return: 保存后的文件路径
        """
        # 构建完整存储路径
        storage_path = os.path.join(self.base_path, directory) if directory else self.base_path
        
        # 创建目录
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
        
        # 生成文件名
        if filename:
            # 使用安全的文件名
            filename = secure_filename(filename)
        else:
            # 自动生成唯一文件名
            filename = f"{uuid.uuid4().hex}{suffix if suffix else ''}"
        
        # 完整文件路径
        file_path = os.path.join(storage_path, filename)
        
        # 保存文件
        if hasattr(file, 'save'):
            # Werkzeug FileStorage对象
            file.save(file_path)
        else:
            # BytesIO对象或类似文件对象
            with open(file_path, 'wb') as f:
                file.seek(0)
                f.write(file.read())
        
        return file_path
    
    def get_file(self, file_id):
        """
        根据文件路径获取文件内容
        
        :param file_id: 文件完整路径
        :return: 文件内容
        """
        if os.path.exists(file_id):
            with open(file_id, 'rb') as f:
                return f.read()
        return None
    
    def open_file(self, file_id, mode='rb'):
        """
        打开文件并返回文件对象
        
        :param file_id: 文件完整路径
        :param mode: 打开模式
        :return: 文件对象
        """
        return open(file_id, mode)
    
    def delete_file(self, file_id):
        """
        删除本地文件
        
        :param file_id: 文件完整路径
        :return: 是否删除成功
        """
        if os.path.exists(file_id):
            os.remove(file_id)
            return True
        return False
    
    def get_file_path(self, file_id):
        """
        获取文件完整路径
        
        :param file_id: 文件完整路径
        :return: 文件完整路径
        """
        return file_id

# 创建存储实例工厂函数
def create_storage():
    """
    根据配置文件自动选择存储类型
    :return: 存储实例
    """
    storage_type = config.get('storage', 'type', 'local')
    
    if storage_type == 'local':
        base_path = config.get('storage', 'local_path', None)
        return LocalStorage(base_path=base_path)
    # 这里可以添加其他存储类型的支持
    # elif storage_type == 's3':
    #     from app.utils.s3_storage import S3Storage
    #     bucket_name = config.get('storage', 's3_bucket')
    #     region_name = config.get('storage', 's3_region')
    #     access_key = config.get('storage', 's3_access_key')
    #     secret_key = config.get('storage', 's3_secret_key')
    #     return S3Storage(bucket_name, region_name, access_key, secret_key)
    else:
        raise ValueError(f"不支持的存储类型: {storage_type}")

# 创建全局存储实例
storage = create_storage()
