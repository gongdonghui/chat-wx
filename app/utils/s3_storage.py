import boto3
from botocore.exceptions import ClientError
from app.utils.storage import StorageInterface
from werkzeug.utils import secure_filename
import uuid

class S3Storage(StorageInterface):
    """
    S3文件存储实现
    """
    
    def __init__(self, bucket_name, region_name=None, access_key=None, secret_key=None):
        """
        初始化S3存储
        
        :param bucket_name: S3存储桶名称
        :param region_name: S3区域
        :param access_key: AWS访问密钥
        :param secret_key: AWS秘密密钥
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.access_key = access_key
        self.secret_key = secret_key
        
        # 创建S3客户端
        self.s3 = boto3.client(
            's3',
            region_name=region_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # 确保存储桶存在
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        确保S3存储桶存在
        """
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # 创建存储桶
                if self.region_name == 'us-east-1':
                    self.s3.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={
                            'LocationConstraint': self.region_name
                        }
                    )
            else:
                raise
    
    def save_file(self, file, directory=None, filename=None, suffix=None):
        """
        保存文件到S3存储
        
        :param file: 文件对象或BytesIO对象
        :param directory: 存储目录
        :param filename: 保存的文件名，如果为None则自动生成
        :param suffix: 文件名后缀
        :return: 文件的S3键
        """
        # 生成文件名
        if filename:
            filename = secure_filename(filename)
        else:
            filename = f"{uuid.uuid4().hex}{suffix if suffix else ''}"
        
        # 构建S3键
        if directory:
            key = f"{directory}/{filename}"
        else:
            key = filename
        
        # 保存文件
        if hasattr(file, 'save'):
            # Werkzeug FileStorage对象
            file.seek(0)
            self.s3.upload_fileobj(file, self.bucket_name, key)
        else:
            # BytesIO对象或类似文件对象
            file.seek(0)
            self.s3.upload_fileobj(file, self.bucket_name, key)
        
        return key
    
    def get_file(self, file_id):
        """
        根据文件键获取文件内容
        
        :param file_id: 文件的S3键
        :return: 文件内容
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_id)
            return response['Body'].read()
        except ClientError as e:
            return None
    
    def delete_file(self, file_id):
        """
        删除S3中的文件
        
        :param file_id: 文件的S3键
        :return: 是否删除成功
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_id)
            return True
        except ClientError as e:
            return False
    
    def get_file_path(self, file_id):
        """
        获取文件的S3 URL
        
        :param file_id: 文件的S3键
        :return: 文件的S3 URL
        """
        return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_id}"
    
    def get_file_url(self, file_id, expires_in=3600):
        """
        获取文件的预签名URL
        
        :param file_id: 文件的S3键
        :param expires_in: URL有效期（秒）
        :return: 预签名URL
        """
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_id},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            return None
