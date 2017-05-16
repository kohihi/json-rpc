from server import (
    tcpserver,
    jsondecode,
    rpcstub,
)


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