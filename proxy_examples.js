// JavaScript 代理模式示例

// 1. 传统代理模式
class RealSubject {
    request() {
        return "RealSubject: 处理请求";
    }
}

class Proxy {
    constructor(realSubject) {
        this.realSubject = realSubject;
    }
    
    request() {
        if (this.checkAccess()) {
            const result = this.realSubject.request();
            this.logAccess();
            return result;
        }
        return "Proxy: 访问被拒绝";
    }
    
    checkAccess() {
        console.log("Proxy: 检查访问权限");
        return true;
    }
    
    logAccess() {
        console.log("Proxy: 记录访问日志");
    }
}

// 2. ES6 Proxy 对象 - 强大的元编程工具
const target = {
    name: "张三",
    age: 25
};

const proxyHandler = {
    // 拦截属性访问
    get(target, property, receiver) {
        console.log(`访问属性: ${property}`);
        if (property === 'secret') {
            return "这是机密信息";
        }
        return Reflect.get(target, property, receiver);
    },
    
    // 拦截属性设置
    set(target, property, value, receiver) {
        console.log(`设置属性: ${property} = ${value}`);
        if (property === 'age' && value < 0) {
            throw new Error("年龄不能为负数");
        }
        return Reflect.set(target, property, value, receiver);
    },
    
    // 拦截函数调用
    apply(target, thisArg, argumentsList) {
        console.log(`调用函数，参数: ${argumentsList}`);
        return target.apply(thisArg, argumentsList);
    }
};

const proxyObject = new Proxy(target, proxyHandler);

// 3. 缓存代理
class CacheProxy {
    constructor(service) {
        this.service = service;
        this.cache = new Map();
    }
    
    getData(key) {
        if (this.cache.has(key)) {
            console.log(`从缓存返回: ${key}`);
            return this.cache.get(key);
        }
        
        console.log(`从服务获取: ${key}`);
        const result = this.service.getData(key);
        this.cache.set(key, result);
        return result;
    }
}

class ExpensiveService {
    getData(key) {
        // 模拟耗时操作
        return `数据_${key}`;
    }
}

// 4. 函数代理 - 装饰器模式
function createFunctionProxy(fn, beforeHook, afterHook) {
    return new Proxy(fn, {
        apply(target, thisArg, argumentsList) {
            beforeHook && beforeHook(argumentsList);
            const result = target.apply(thisArg, argumentsList);
            afterHook && afterHook(result);
            return result;
        }
    });
}

// 使用示例
console.log("=== 传统代理模式 ===");
const realSubject = new RealSubject();
const proxy = new Proxy(realSubject);
console.log(proxy.request());

console.log("\n=== ES6 Proxy 对象 ===");
console.log(proxyObject.name);  // 触发 get 拦截器
proxyObject.age = 30;           // 触发 set 拦截器
console.log(proxyObject.secret); // 访问不存在的属性

console.log("\n=== 缓存代理 ===");
const service = new ExpensiveService();
const cacheProxy = new CacheProxy(service);
console.log(cacheProxy.getData("user1")); // 第一次访问
console.log(cacheProxy.getData("user1")); // 第二次访问（缓存）

console.log("\n=== 函数代理 ===");
const originalFunction = (x, y) => x + y;
const proxiedFunction = createFunctionProxy(
    originalFunction,
    (args) => console.log(`调用前: 参数 ${args}`),
    (result) => console.log(`调用后: 结果 ${result}`)
);
console.log(proxiedFunction(3, 4));