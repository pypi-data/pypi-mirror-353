"""
全局配置文件
包含Redis连接配置和其他系统设置
"""

# Redis配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 2
REDIS_PASSWORD = 'xxxxxxxxxxx'
REDIS_CONNECTIONS = 3
REDIS_DECODE_RESPONSES = True
REDIS_HEALTH_CHECK_INTERVAL = 60

# 服务配置
SERVICE_CHECK_INTERVAL = 60  # 服务检查间隔（秒）

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = 'adspowerclean.log'  # 日志文件名
