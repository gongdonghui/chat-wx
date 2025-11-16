import os
import configparser

class Config:
    """
    配置管理类
    """
    
    def __init__(self, config_file='config.ini'):
        """
        初始化配置
        
        :param config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
    
    def get(self, section, key, default=None):
        """
        获取配置值
        
        :param section: 配置 section
        :param key: 配置 key
        :param default: 默认值
        :return: 配置值
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def getint(self, section, key, default=None):
        """
        获取整数配置值
        
        :param section: 配置 section
        :param key: 配置 key
        :param default: 默认值
        :return: 整数配置值
        """
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def getfloat(self, section, key, default=None):
        """
        获取浮点数配置值
        
        :param section: 配置 section
        :param key: 配置 key
        :param default: 默认值
        :return: 浮点数配置值
        """
        try:
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def getboolean(self, section, key, default=None):
        """
        获取布尔配置值
        
        :param section: 配置 section
        :param key: 配置 key
        :param default: 默认值
        :return: 布尔配置值
        """
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def has_section(self, section):
        """
        检查是否存在指定 section
        
        :param section: 配置 section
        :return: 是否存在
        """
        return self.config.has_section(section)
    
    def has_option(self, section, key):
        """
        检查是否存在指定 option
        
        :param section: 配置 section
        :param key: 配置 key
        :return: 是否存在
        """
        return self.config.has_option(section, key)
    
    def set(self, section, key, value):
        """
        设置配置值
        
        :param section: 配置 section
        :param key: 配置 key
        :param value: 配置值
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
    
    def save(self):
        """
        保存配置到文件
        """
        with open(self.config_file, 'w') as f:
            self.config.write(f)

# 创建全局配置实例
config = Config()
