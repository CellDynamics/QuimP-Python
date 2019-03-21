import json


class Parser:
    level = 0

    def __init__(self, qjson):
        self.root = qjson
        self.keys = self.root.keys()
        self.types = [type(self.root.get(x)) for x in self.keys]
        Parser.level += 1
        self.decode()

    def decode(self):
        for k, t in zip(self.keys, self.types):
            print('Key {} type {} level {}'.format(k, t, Parser.level))
            if t == dict:
                self.parser = Parser(self.root.get(k))
            elif t == list:
                if type(self.root.get(k)[0]) == dict:
                    self.parser = Parser(self.root.get(k)[0])

            # else:
            #     print('Key {} type {} level {}'.format(self.root, self.types, Parser.level))


with open('Stack.QCONF') as js:
    qjson = json.load(js)
    p = Parser(qjson)
