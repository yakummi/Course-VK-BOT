class Iteration:
    def __init__(self, massiv:list):
        self.massiv = massiv

        print(self.massiv)
        print(self.massiv[1])
    def __next__(self):
        for k, v in self.massiv[1]:
            return k, v

test = Iteration([{'id': 'Vanya', 'volk':'no'}, {'id': 'Oleg'}])
print(test.__next__())
print(test.__next__())

