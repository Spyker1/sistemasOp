import random

class Filosofo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.comida = 0
        self.sin_comer = 0

    def comer(self):
        self.comida += 1
        self.sin_comer = 0

    def pensar(self):
        self.sin_comer += 1
        if self.sin_comer >= 3:  # Si un filósofo pasa 3 rondas sin comer, muere
            return True
        return False

filosofos = [Filosofo("Filósofo " + str(i+1)) for i in range(5)]

rondas = 0
while True:
    rondas += 1
    print(f"Ronda {rondas}:")
    for filosofo in filosofos:
        if random.random() < 0.5:  # 50% de probabilidad de comer en cada ronda
            filosofo.comer()
            print(f"{filosofo.nombre} está comiendo.")
        else:
            if filosofo.pensar():
                print(f"{filosofo.nombre} ha muerto de hambre.")
                filosofos.remove(filosofo)
            else:
                print(f"{filosofo.nombre} está pensando.")

    if len(filosofos) == 0:  # Si todos los filósofos han muerto, termina la simulación
        print("Todos los filósofos han muerto.")
        break

print("La cena ha terminado.")
