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