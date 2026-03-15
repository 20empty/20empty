// Java 代理模式示例

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;

// 1. 静态代理
interface Subject {
    String request();
}

class RealSubject implements Subject {
    @Override
    public String request() {
        return "RealSubject: 处理请求";
    }
}

class StaticProxy implements Subject {
    private RealSubject realSubject;
    
    public StaticProxy(RealSubject realSubject) {
        this.realSubject = realSubject;
    }
    
    @Override
    public String request() {
        if (checkAccess()) {
            String result = realSubject.request();
            logAccess();
            return result;
        }
        return "Proxy: 访问被拒绝";
    }
    
    private boolean checkAccess() {
        System.out.println("Proxy: 检查访问权限");
        return true;
    }
    
    private void logAccess() {
        System.out.println("Proxy: 记录访问日志");
    }
}

// 2. 动态代理
class DynamicProxyHandler implements InvocationHandler {
    private Object target;
    
    public DynamicProxyHandler(Object target) {
        this.target = target;
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("动态代理: 调用方法 " + method.getName());
        
        // 前置处理
        long startTime = System.currentTimeMillis();
        
        // 调用真实对象的方法
        Object result = method.invoke(target, args);
        
        // 后置处理
        long endTime = System.currentTimeMillis();
        System.out.println("动态代理: 方法执行耗时 " + (endTime - startTime) + "ms");
        
        return result;
    }
}

// 3. 缓存代理
interface DataService {
    String getData(String key);
}

class ExpensiveDataService implements DataService {
    @Override
    public String getData(String key) {
        System.out.println("从数据库获取数据: " + key);
        try {
            Thread.sleep(1000); // 模拟耗时操作
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "数据_" + key;
    }
}

class CacheProxy implements DataService {
    private DataService dataService;
    private Map<String, String> cache = new HashMap<>();
    
    public CacheProxy(DataService dataService) {
        this.dataService = dataService;
    }
    
    @Override
    public String getData(String key) {
        if (cache.containsKey(key)) {
            System.out.println("从缓存返回数据: " + key);
            return cache.get(key);
        }
        
        String result = dataService.getData(key);
        cache.put(key, result);
        return result;
    }
}

public class ProxyExamples {
    public static void main(String[] args) {
        System.out.println("=== 静态代理 ===");
        RealSubject realSubject = new RealSubject();
        StaticProxy staticProxy = new StaticProxy(realSubject);
        System.out.println(staticProxy.request());
        
        System.out.println("\n=== 动态代理 ===");
        Subject dynamicProxy = (Subject) Proxy.newProxyInstance(
            Subject.class.getClassLoader(),
            new Class[]{Subject.class},
            new DynamicProxyHandler(realSubject)
        );
        System.out.println(dynamicProxy.request());
        
        System.out.println("\n=== 缓存代理 ===");
        DataService expensiveService = new ExpensiveDataService();
        DataService cacheProxy = new CacheProxy(expensiveService);
        
        // 第一次访问
        System.out.println(cacheProxy.getData("user1"));
        // 第二次访问（从缓存）
        System.out.println(cacheProxy.getData("user1"));
    }
}