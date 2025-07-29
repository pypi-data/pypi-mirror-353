"""
Classmate - 教室管理系统
"""

__author__ = "linmy"
__email__ = "wzlinmiaoyan@163.com"

from .server import run as _run

def run(host='0.0.0.0', port=5000, password=None):
    """
    启动 Classmate 服务器
    
    参数:
        host (str): 服务器主机地址，默认为 '0.0.0.0'
        port (int): 服务器端口，默认为 5000
        password (str): 教师模式密码，默认为 '123456'
    """
    _run(host=host, port=port, password=password)

__all__ = ['run']