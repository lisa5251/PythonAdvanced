from kerri import Kerri

class KerriElektrik(Kerri):

    def __init__(self,emri,viti,modeli,bateria):
        super().__init__(emri,viti,modeli)
        self.bateria=bateria

    def rritjeShpejtesise(self):
        print("kerrit elektrik eshte duke shpejtuar ")

    def mbusheBaterin(self):
        print("mbushe baterin")