# Python 代理模式示例

from abc import ABC, abstractmethod
import time
from typing import Any

# 1. 基础代理模式
class Subject(ABC):
    """抽象主题接口"""
    @abstractmethod
    def request(self) -> str:
        pass

class RealSubject(Subject):
    """真实主题对象"""
    def request(self) -> str:
        return "RealSubject: 处理请求"

class Proxy(Subject):
    """代理对象"""
    def __init__(self, real_subject: RealSubject):
        self._real_subject = real_subject
    
    def request(self) -> str:
        # 在访问前添加额外逻辑
        if self._check_access():
            result = self._real_subject.request()
            self._log_access()
            return result
        return "Proxy: 访问被拒绝"
    
    def _check_access(self) -> bool:
        print("Proxy: 检查访问权限")
        return True
    
    def _log_access(self) -> None:
        print("Proxy: 记录访问日志")

# 2. 缓存代理示例
class ExpensiveService:
    """昂贵的服务操作"""
    def get_data(self, key: str) -> str:
        print(f"正在从数据库获取数据: {key}")
        time.sleep(1)  # 模拟耗时操作
        return f"数据_{key}"

class CacheProxy:
    """缓存代理"""
    def __init__(self, service: ExpensiveService):
        self._service = service
        self._cache = {}
    
    def get_data(self, key: str) -> str:
        if key in self._cache:
            print(f"从缓存返回数据: {key}")
            return self._cache[key]
        
        result = self._service.get_data(key)
        self._cache[key] = result
        return result

# 3. Python 内置代理 - __getattr__
class AttributeProxy:
    """属性代理"""
    def __init__(self, target):
        self._target = target
    
    def __getattr__(self, name: str) -> Any:
        print(f"代理访问属性: {name}")
        return getattr(self._target, name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            print(f"代理设置属性: {name} = {value}")
            setattr(self._target, name, value)

# 使用示例
if __name__ == "__main__":
    print("=== 基础代理模式 ===")
    real_subject = RealSubject()
    proxy = Proxy(real_subject)
    print(proxy.request())
    
    print("\n=== 缓存代理 ===")
    service = ExpensiveService()
    cache_proxy = CacheProxy(service)
    
    # 第一次访问 - 从服务获取
    print(cache_proxy.get_data("user1"))
    # 第二次访问 - 从缓存获取
    print(cache_proxy.get_data("user1"))
    
    print("\n=== 属性代理 ===")
    class Person:
        def __init__(self, name):
            self.name = name
    
    person = Person("张三")
    proxy_person = AttributeProxy(person)
    print(proxy_person.name)  # 代理访问
    proxy_person.age = 25     # 代理设置