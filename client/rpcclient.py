import client
import rpcstub


class RPCClient(client.Client, rpcstub.RPCStub):
    pass
