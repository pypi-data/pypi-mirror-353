import httpx
import time
import random
from typing import List, Optional, Dict, Union, Literal
import logging
import socket
from urllib.parse import urlparse
from twisted.internet import defer, threads, reactor
from twisted.internet.defer import inlineCallbacks, returnValue
import functools

logger = logging.getLogger(__name__)

class AdsPowerAPI:
    def __init__(self, base_url: str = "http://local.adspower.net:50325"):
    # def __init__(self, base_url: str = "http://127.0.0.1:50325"):
        self.base_url = base_url
        self.endpoints = {
            "start_browser": "/api/v1/browser/start",
            "close_browser": "/api/v1/browser/stop",
            "create_browser": "/api/v1/user/create",
            "get_browser_list": "/api/v1/user/list",
            "get_group_list": "/api/v1/group/list",
            "create_group": "/api/v1/group/create",
            "delete_browser": "/api/v1/user/delete"
        }
        self._network_cache = {}
        self._cache_ttl = 30  # 缓存有效期30秒

    def _get_cached_network_status(self, key: str) -> Optional[bool]:
        """
        从缓存中获取网络状态
        
        Args:
            key: 缓存键名
            
        Returns:
            Optional[bool]: 如果缓存存在且未过期返回状态，否则返回None
        """
        if key in self._network_cache:
            status, timestamp = self._network_cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return status
            else:
                del self._network_cache[key]
        return None

    def _set_cached_network_status(self, key: str, status: bool):
        """
        设置网络状态缓存
        
        Args:
            key: 缓存键名
            status: 状态值
        """
        self._network_cache[key] = (status, time.time())

    def _check_single_url(self, url: str, timeout: int = 5) -> bool:
        """
        同步检查单个URL的可访问性
        这个方法会被 deferToThread 包装成异步调用
        
        Args:
            url: 要检查的URL
            timeout: 超时时间（秒）
            
        Returns:
            bool: URL是否可访问
        """
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.head(url)
                return response.status_code == 200
        except Exception:
            return False

    @inlineCallbacks
    def check_network_connectivity(self, url: str, timeout: int = 5):
        """
        使用Twisted的异步机制检查网络连通性
        
        这个方法使用了 @inlineCallbacks 装饰器，允许我们使用 yield 来处理异步操作
        而不需要写回调函数。每个 yield 表达式会暂停函数执行，直到异步操作完成。
        
        Args:
            url: 要检查的目标URL
            timeout: 超时时间（秒）
            
        Returns:
            Deferred[bool]: 返回一个Deferred对象，最终解析为布尔值
        """
        # 先检查缓存
        cache_key = f"network_status_{url}"
        cached_status = self._get_cached_network_status(cache_key)
        if cached_status is not None:
            returnValue(cached_status)

        try:
            # 使用Twisted的线程池并发检查多个URL
            test_urls = [
                "https://www.google.com",
                "https://www.bing.com",
                url
            ]
            
            # 将同步函数包装成异步
            check_func = functools.partial(self._check_single_url, timeout=timeout)
            # 并发执行检查
            results = []
            for test_url in test_urls:
                # threads.deferToThread 会在线程池中执行同步函数
                # yield 会等待每个检查完成
                result = yield threads.deferToThread(check_func, test_url)
                results.append(result)

            # 如果能访问通用网站但不能访问目标网站，可能是被封
            status = True
            if any(results[:2]) and not results[2]:
                status = False

            # 更新缓存
            self._set_cached_network_status(cache_key, status)
            returnValue(status)

        except Exception as e:
            logger.warning(f"网络连通性检查失败: {e}")
            returnValue(False)

    def _request(self, method: str, endpoint: str, params: dict = None, json: dict = None, timeout: int = 60,
                 retries: int = 3) -> dict:
        url = f"{self.base_url}{endpoint}"
        for attempt in range(retries):
            try:
                response = httpx.request(method, url, params=params, json=json, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                time.sleep(1)  # 保证调用频率符合限制
                return data
            except httpx.ReadTimeout:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise
        return None

    def get_group_list(self) -> List[dict]:
        resp = self._request("GET", self.endpoints["get_group_list"])
        return resp.get("data", {}).get("list", [])

    def get_or_create_group_by_name(self, group_name: str = "spider") -> str:
        """
        根据组名获取或创建组
        
        Args:
            group_name: 组名，默认为"spider"
            
        Returns:
            str: 组ID
        """
        # 先查找是否存在同名组
        groups = self.get_group_list()
        for group in groups:
            if group.get("group_name") == group_name:
                return str(group["group_id"])
        
        # 不存在则创建新组
        resp = self._request("POST", self.endpoints["create_group"], json={"group_name": group_name})
        return str(resp["data"]["group_id"])

    def get_or_create_random_group(self) -> str:
        groups = self.get_group_list()
        if groups:
            return str(random.choice(groups)["group_id"])
        else:
            group_name = f"auto_{int(time.time())}"
            resp = self._request("POST", self.endpoints["create_group"], json={"group_name": group_name})
            return str(resp["data"]["group_id"])

    def create_browser(self, group_id: str, name: Optional[str] = None, proxy_config: Optional[dict] = None,
                       fingerprint_config: Optional[dict] = None) -> dict:
        payload = {
            "group_id": group_id,
            "name": name or f"auto_profile_{int(time.time())}",
            "user_proxy_config": proxy_config or {"proxy_soft": "no_proxy"},
            "fingerprint_config": fingerprint_config or { # https://localapi-doc-en.adspower.com/docs/Awy6Dg
                "browser_kernel_config": {"type": "chrome", "version": "131"},
                # "browser_kernel_config": {"type": "chrome", "version": "ua_auto"},
                "random_ua": {"ua_version": [], "ua_system_version": ["Windows 10"]}
            }
        }
        return self._request("POST", self.endpoints["create_browser"], json=payload)

    def start_browser(self, user_id: str) -> dict:
        if not user_id:
            raise ValueError("user_id 不可为空")
        return self._request("GET", self.endpoints["start_browser"], params={"user_id": user_id})

    def close_browser(self, user_id: str) -> dict:
        return self._request("GET", self.endpoints["close_browser"], params={"user_id": user_id})

    def delete_browser(self, user_ids: List[str]) -> dict:
        return self._request("POST", self.endpoints["delete_browser"], json={"user_ids": user_ids})

    def get_opened_user_ids(self) -> set:
        resp = self._request("GET", "/api/v1/browser/local-active")
        # logger.info(f'opened resp:{resp}')
        if resp and resp.get("code") == 0:
            return set(item["user_id"] for item in resp["data"].get("list", []))
        return set()

    def is_browser_active(self, user_id: str) -> bool:
        try:
            local_users = self.get_opened_user_ids()
            logger.info(f'local_users:{local_users}')
            return user_id in local_users
        except Exception as e:
            logger.warning(f"使用 local-active 检查失败，降级为 /active: {e}")
            resp = self._request("GET", "/api/v1/browser/active", params={"user_id": user_id})
            return resp.get("code") == 0 and resp.get("data", {}).get("status") == "Active"

    def get_browser_list(self, group_id: Optional[str] = None) -> List[dict]:
        params = {"group_id": group_id} if group_id else {}
        resp = self._request("GET", self.endpoints["get_browser_list"], params=params)
        return resp.get("data", {}).get("list", [])

    @inlineCallbacks
    def is_profile_blocked(self, user_id: str, target_url: str):
        """
        异步检查profile是否被封
        
        Args:
            user_id: profile ID
            target_url: 目标URL
            
        Returns:
            Deferred[bool]: 返回一个Deferred对象，最终解析为布尔值
                           True表示被封，False表示正常
        """
        try:
            # 先检查浏览器是否正常运行
            if not self.is_browser_active(user_id):
                returnValue(False)
                
            # 检查网络连通性
            # yield 会等待 check_network_connectivity 完成
            status = yield self.check_network_connectivity(target_url)
            returnValue(not status)
                
        except Exception as e:
            logger.error(f"检查profile状态失败: {e}")
            returnValue(True)  # 如有异常，保守起见认为被封

def test_network_check():
    """
    测试网络检测功能
    
    这个测试展示了如何在Twisted环境中使用这些异步方法
    """
    api = AdsPowerAPI()
    
    @inlineCallbacks
    def run_test():
        try:
            # 测试可访问的URL
            logger.info("测试 google.com ...")
            result = yield api.check_network_connectivity("https://www.google.com")
            logger.info(f"Google可访问性: {result}")
            
            # 测试不可访问的URL
            logger.info("测试无效URL...")
            result = yield api.check_network_connectivity("https://invalid.example.com")
            logger.info(f"无效URL可访问性: {result}")
            
            # 测试缓存
            logger.info("测试缓存...")
            result1 = yield api.check_network_connectivity("https://www.google.com")
            result2 = yield api.check_network_connectivity("https://www.google.com")
            logger.info(f"缓存测试结果: {result1 == result2}")
            
        except Exception as e:
            logger.error(f"测试过程中出错: {e}")
        finally:
            reactor.stop()
    
    # 启动测试
    reactor.callWhenRunning(run_test)
    reactor.run()

def test_profile_block_check():
    """
    测试profile封禁检测功能
    """
    api = AdsPowerAPI()
    
    @inlineCallbacks
    def run_test():
        try:
            # 创建一个测试profile
            group_id = api.get_or_create_random_group()
            profile = api.create_browser(group_id)
            user_id = profile.get("data", {}).get("id")
            
            if not user_id:
                logger.error("创建profile失败")
                reactor.stop()
                return
                
            logger.info(f"创建测试profile: {user_id}")
            
            # 测试profile状态检查
            logger.info("检查profile状态...")
            result = yield api.is_profile_blocked(user_id, "https://www.google.com")
            logger.info(f"Profile状态检查结果: {'已封禁' if result else '正常'}")
            
            # 清理测试profile
            api.delete_browser([user_id])
            logger.info("测试完成，已清理测试profile")
            
        except Exception as e:
            logger.error(f"测试过程中出错: {e}")
        finally:
            reactor.stop()
    
    # 启动测试
    reactor.callWhenRunning(run_test)
    reactor.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    logger.info("=== 开始网络检测测试 ===")
    test_network_check()
    
    logger.info("\n=== 开始profile状态检测测试 ===")
    test_profile_block_check()
