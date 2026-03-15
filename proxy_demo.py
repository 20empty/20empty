#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理模式综合演示程序
展示代理模式在实际应用中的多种用法
"""

import time
import threading
from functools import wraps
from typing import Any, Dict, Optional
import json

# 1. 智能缓存代理
class SmartCacheProxy:
    """智能缓存代理，支持TTL和LRU策略"""
    
    def __init__(self, target, max_size: int = 100, ttl: int = 300):
        self._target = target
        self._cache: Dict[str, Dict] = {}
        self._access_order = []
        self._max_size = max_size
        self._ttl = ttl
        self._lock = threading.RLock()
    
    def __getattr__(self, name: str) -> Any:
        if hasattr(self._target, name):
            attr = getattr(self._target, name)
            if callable(attr):
                return self._create_cached_method(name, attr)
            return attr
        raise AttributeError(f"'{type(self._target).__name__}' object has no attribute '{name}'")
    
    def _create_cached_method(self, method_name: str, method):
        @wraps(method)
        def cached_method(*args, **kwargs):
            # 创建缓存键
            cache_key = self._create_cache_key(method_name, args, kwargs)
            
            with self._lock:
                # 检查缓存
                if cache_key in self._cache:
                    cache_entry = self._cache[cache_key]
                    
                    # 检查TTL
                    if time.time() - cache_entry['timestamp'] < self._ttl:
                        print(f"🎯 缓存命中: {method_name}")
                        self._update_access_order(cache_key)
                        return cache_entry['value']
                    else:
                        print(f"⏰ 缓存过期: {method_name}")
                        del self._cache[cache_key]
                        self._access_order.remove(cache_key)
                
                # 缓存未命中，调用原方法
                print(f"🔍 缓存未命中，调用原方法: {method_name}")
                result = method(*args, **kwargs)
                
                # 存储到缓存
                self._store_in_cache(cache_key, result)
                return result
        
        return cached_method
    
    def _create_cache_key(self, method_name: str, args, kwargs) -> str:
        """创建缓存键"""
        key_data = {
            'method': method_name,
            'args': args,
            'kwargs': kwargs
        }
        return json.dumps(key_data, sort_keys=True, default=str)
    
    def _store_in_cache(self, key: str, value: Any):
        """存储到缓存，实现LRU策略"""
        # 如果缓存满了，删除最少使用的项
        if len(self._cache) >= self._max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
            print(f"🗑️  LRU淘汰: {oldest_key[:50]}...")
        
        self._cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        self._access_order.append(key)
    
    def _update_access_order(self, key: str):
        """更新访问顺序"""
        self._access_order.remove(key)
        self._access_order.append(key)
    
    def cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'cache_size': len(self._cache),
            'max_size': self._max_size,
            'ttl': self._ttl,
            'keys': list(self._cache.keys())
        }

# 2. 安全访问代理
class SecurityProxy:
    """安全访问代理，提供权限控制和审计日志"""
    
    def __init__(self, target, user_permissions: Dict[str, list]):
        self._target = target
        self._user_permissions = user_permissions
        self._current_user = None
        self._audit_log = []
    
    def login(self, username: str) -> bool:
        """用户登录"""
        if username in self._user_permissions:
            self._current_user = username
            self._log_action("LOGIN", f"用户 {username} 登录成功")
            return True
        self._log_action("LOGIN_FAILED", f"用户 {username} 登录失败")
        return False
    
    def logout(self):
        """用户登出"""
        if self._current_user:
            self._log_action("LOGOUT", f"用户 {self._current_user} 登出")
            self._current_user = None
    
    def __getattr__(self, name: str) -> Any:
        if not self._current_user:
            raise PermissionError("请先登录")
        
        if hasattr(self._target, name):
            # 检查权限
            if not self._check_permission(name):
                self._log_action("ACCESS_DENIED", f"用户 {self._current_user} 访问 {name} 被拒绝")
                raise PermissionError(f"用户 {self._current_user} 没有权限访问 {name}")
            
            attr = getattr(self._target, name)
            if callable(attr):
                return self._create_secure_method(name, attr)
            
            self._log_action("ATTRIBUTE_ACCESS", f"用户 {self._current_user} 访问属性 {name}")
            return attr
        
        raise AttributeError(f"'{type(self._target).__name__}' object has no attribute '{name}'")
    
    def _check_permission(self, method_name: str) -> bool:
        """检查用户权限"""
        user_perms = self._user_permissions.get(self._current_user, [])
        return method_name in user_perms or 'all' in user_perms
    
    def _create_secure_method(self, method_name: str, method):
        @wraps(method)
        def secure_method(*args, **kwargs):
            self._log_action("METHOD_CALL", 
                           f"用户 {self._current_user} 调用方法 {method_name}")
            try:
                result = method(*args, **kwargs)
                self._log_action("METHOD_SUCCESS", 
                               f"用户 {self._current_user} 成功执行 {method_name}")
                return result
            except Exception as e:
                self._log_action("METHOD_ERROR", 
                               f"用户 {self._current_user} 执行 {method_name} 出错: {e}")
                raise
        
        return secure_method
    
    def _log_action(self, action: str, details: str):
        """记录审计日志"""
        log_entry = {
            'timestamp': time.time(),
            'action': action,
            'user': self._current_user,
            'details': details
        }
        self._audit_log.append(log_entry)
        print(f"🔒 [{action}] {details}")
    
    def get_audit_log(self) -> list:
        """获取审计日志"""
        return self._audit_log.copy()

# 3. 示例业务类
class DatabaseService:
    """模拟数据库服务"""
    
    def __init__(self):
        self._data = {
            'users': ['张三', '李四', '王五'],
            'products': ['商品A', '商品B', '商品C']
        }
    
    def get_users(self):
        """获取用户列表（耗时操作）"""
        print("📊 正在从数据库获取用户列表...")
        time.sleep(1)  # 模拟耗时
        return self._data['users'].copy()
    
    def get_products(self):
        """获取产品列表（耗时操作）"""
        print("📊 正在从数据库获取产品列表...")
        time.sleep(1)  # 模拟耗时
        return self._data['products'].copy()
    
    def add_user(self, username: str):
        """添加用户（敏感操作）"""
        print(f"📊 正在添加用户: {username}")
        self._data['users'].append(username)
        return f"用户 {username} 添加成功"
    
    def delete_user(self, username: str):
        """删除用户（高危操作）"""
        print(f"📊 正在删除用户: {username}")
        if username in self._data['users']:
            self._data['users'].remove(username)
            return f"用户 {username} 删除成功"
        return f"用户 {username} 不存在"

def main():
    """主演示程序"""
    print("=" * 60)
    print("🎭 代理模式综合演示")
    print("=" * 60)
    
    # 创建原始服务
    db_service = DatabaseService()
    
    # 1. 演示缓存代理
    print("\n1️⃣  缓存代理演示")
    print("-" * 30)
    
    cached_service = SmartCacheProxy(db_service, max_size=5, ttl=10)
    
    # 第一次调用 - 缓存未命中
    print("第一次调用 get_users:")
    users1 = cached_service.get_users()
    print(f"结果: {users1}")
    
    # 第二次调用 - 缓存命中
    print("\n第二次调用 get_users:")
    users2 = cached_service.get_users()
    print(f"结果: {users2}")
    
    # 显示缓存统计
    print(f"\n缓存统计: {cached_service.cache_stats()}")
    
    # 2. 演示安全代理
    print("\n\n2️⃣  安全代理演示")
    print("-" * 30)
    
    # 定义用户权限
    permissions = {
        'admin': ['all'],  # 管理员有所有权限
        'user': ['get_users', 'get_products'],  # 普通用户只能查询
        'guest': ['get_users']  # 访客只能查看用户
    }
    
    secure_service = SecurityProxy(cached_service, permissions)
    
    # 未登录访问
    print("未登录状态访问:")
    try:
        secure_service.get_users()
    except PermissionError as e:
        print(f"❌ {e}")
    
    # 普通用户登录
    print("\n普通用户登录:")
    secure_service.login('user')
    print(f"✅ 用户数据: {secure_service.get_users()}")
    
    # 尝试执行敏感操作
    print("\n普通用户尝试执行敏感操作:")
    try:
        secure_service.add_user('新用户')
    except PermissionError as e:
        print(f"❌ {e}")
    
    # 管理员登录
    print("\n管理员登录:")
    secure_service.logout()
    secure_service.login('admin')
    print(f"✅ {secure_service.add_user('管理员添加的用户')}")
    
    # 显示审计日志
    print("\n📋 审计日志:")
    for log in secure_service.get_audit_log()[-5:]:  # 显示最后5条
        timestamp = time.strftime('%H:%M:%S', time.localtime(log['timestamp']))
        print(f"  [{timestamp}] {log['action']}: {log['details']}")

if __name__ == "__main__":
    main()