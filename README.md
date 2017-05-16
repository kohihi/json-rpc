# json-rpc
### **server**
1. 要收到客户端的消息，首先要开一个连接用与接收消息，先写一个类，这个类的方法用于创建连接，接收消息。
```python
import socket
class Server():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind_listen(self, port):
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(5)

    def accept_receive_close(self):
        (client_socket, address) = self.sock.accept()
        msg = client_socket.recv(1024)
        self.on_msg(msg)
        client_socket.close()
```
这里有一个`no_msg()`方法放在后面实现，作用就是解析这份消息，并调用对应方法。

2. 收到的消息是 json 格式的，要解析处理，这个类的方法用于处理 json 数据。
```
import json
class JSONRpc():
    # 储存 json 数据
    def __init__(self):
        self.data = None

    # 解析 json ，并用 utf-8 储存
    def from_data(self, data):
        self.data = json.loads(data.decode('utf-8'))

    # 把 name 和 args 取出，用 getattr 获取方法，调用
    def call_method(self):
        method_name = self.data['method_name']
        method_args = self.data['method_args']
        method_kwargs = self.data['method_kwargs']

        getattr(self, method_name)(*method_args, **method_kwargs)
```
前面说`on_msg()`方法就是解析消息，调用函数，`from_data()`和`call_method()`这两个函数都是给`on_msg()`用的。

3. RPCServer类，它继承上面两个类，把方法整合起来，实现rpc server 的功能。
```python
class RPCServer(tcpserver.Server, jsondecode.JSONRpc, rpcstub.RPCStub):
    def __init__(self):
        super(RPCServer, self).__init__()

    def loop(self):
        self.bind_listen(4000)
        while True:
            self.accept_receive_close()

    def on_msg(self, data):
        self.from_data(data)
        self.call_method()
```
上面没提到的 `rpcstub.RPCStub`就是包含服务端实际要被调用的方法的类。继承了它，`getattr(self, method_name)`就能找到对应的函数了。

4. 跑起来
```python
s = rpcserver.RPCServer()
s.loop()
```
`s.loop()`调用了`bind_listen(4000)`,连接被创建在4000端口，这是个死循环，一直保持监听。

一旦收到消息，调用`on_msg(msg)`。

`on_msg`调用`from_data(data)`解析 json，`call_method()`调用客户端想调用的函数（在`RPCStub`这个类里）。

server 的逻辑就是以上这样。


### **client**
客户端要实现的就是想办法把规定格式的 json 发送到 server 。
1. 创建连接
```
import socket
class Client():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, data):
        self.sock.send(data)
```
`connect()`接收两个参数，主机和端口，这个就看服务器是怎样的设置了，主机是服务端的 ip，端口就是服务端绑定 rpc 的端口，就是上面的 4000.

`send()`接收一个参数 data，data就是要发送的 json。

2. 把调用的 method_name 与 参数转成 json 格式的数据，发送。
```python
import json
class RPCStub():
    def __getattr__(self, item):
        def _(*args, **kwargs):
            d = {"method_name": item, 'method_args': args, 'method_kwargs': kwargs}
            self.send(json.dumps(d).encode('utf-8'))

        setattr(self, item, _)
        return _
```
这里用到了 python 的一个魔法方法`__getattr__()`.

最终要实现的效果是在客户端实例化一个 `RPCClient()` 对象`c`，需要远程调用什么方法，就像在本地一样，直接`c.method_name()`就可以。

所以用`__getattr__()`来接住这种 调用“不存在的方法”(miss method)的动作，并加以处理。

处理方式就是把方法名、参数转成一段 json 格式的数据，然后 send 到服务端。

`RPCStub()`这个类就是一个描述器了，关于描述器，这个玩意儿我也是看了几篇文章才大概明白，不在这里展开说(吹)了。

3. 整合
```python
class RPCClient(client.Client, rpcstub.RPCStub):
    pass
```
`RPCClient()`继承`Client()`和`RPCStub()`，这样就可以实现如下操作：
```python
c = RPCClient()
c.connect('127.0.0.1', 4000)
c.foo(1, 2, 3)
```
server 有什么方法，直接调就可以。

这里我的 server 和 client 是在一台电脑上的，所以 `host=127.0.0.1`。

server 上有一个叫 foo() 的函数，需要三个参数，直接`c.foo(1,2,3)`就可以让 server 执行 `foo(1,2,3)`。
