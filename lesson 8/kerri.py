class Kerri:

    def __init__(self,emri,viti,modeli,kilometrat,prejardhja):
        self.emri=emri
        self.viti = viti
        self.modeli = modeli
        self.kilometrat = kilometrat
        self.prejardhja = prejardhja

    def rriteShpejtesine(self):
        print("shpejtesia e kerrit eshte duke u rritur")

    def ndalu(self):
        print("stooop")

    def info(self):
        print(f"{self.emri}, eshte nje veture mjaft luksoze dhe eshte prodhuar ne vitin : {self.viti}, dhe eshte i prodhuar ne : {self.prejardhja}")