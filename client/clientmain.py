import rpcclient

c = rpcclient.RPCClient()
c.connect('127.0.0.1', 4000)
c.foo(1, 2, 3)