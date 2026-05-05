class Personi:

    def __init__(self,emri,vitiLindjes,gjinia):
        self.emri=emri
        self.vitiLindjes = vitiLindjes
        self.gjinia = gjinia

    def prezantimi(self):
        print(f"une jame: {self.emri}, kam lindur ne vitin: {self.vitiLindjes}")

    def sayHi(self):
        print(f"pershendetje nga: {self.emri}")