import threading
import time
import random

class Filosofo(threading.Thread):
    def __init__(self, id, palillo_izq, palillo_der, ronda_dur):
        threading.Thread.__init__(self)
        self.id = id
        self.palillo_izq = palillo_izq
        self.palillo_der = palillo_der
        self.ronda_dur = ronda_dur
        self.vivo = True

    def run(self):
        while self.vivo:
            self.pensar()
            self.comer()

    def pensar(self):
        print(f"Filósofo {self.id} está pensando...")
        time.sleep(random.uniform(1, 3))  # Tiempo aleatorio pensando

    def comer(self):
        print(f"Filósofo {self.id} está intentando comer...")
        if self.tomar_palillos():
            print(f"Filósofo {self.id} está comiendo.")
            time.sleep(random.uniform(1, 2))  # Tiempo aleatorio comiendo
            self.soltar_palillos()
        else:
            print(f"Filósofo {self.id} no pudo comer y muere.")
            self.vivo = False

    def tomar_palillos(self):
        if self.palillo_izq.acquire(blocking=False):
            if self.palillo_der.acquire(blocking=False):
                return True
            else:
                self.palillo_izq.release()
        return False

    def soltar_palillos(self):
        self.palillo_izq.release()
        self.palillo_der.release()

def simular_filosofos(num_filosofos, duracion_ronda):
    palillos = [threading.Lock() for _ in range(num_filosofos)]
    filosofos = [Filosofo(i, palillos[i], palillos[(i + 1) % num_filosofos], duracion_ronda) for i in range(num_filosofos)]

    for filosofo in filosofos:
        filosofo.start()

    while any(filosofo.vivo for filosofo in filosofos):
        time.sleep(duracion_ronda)
        for filosofo in filosofos:
            if not filosofo.vivo:
                continue
            print(f"Filósofo {filosofo.id} no ha comido en esta ronda y muere.")
            filosofo.vivo = False
            filosofo.join()  # Esperar a que termine el hilo del filósofo muerto

    print("Todos los filósofos han muerto.")

if __name__ == "__main__":
    num_filosofos = 5
    duracion_ronda = 6  # Duración de cada ronda en segundos

    simular_filosofos(num_filosofos, duracion_ronda)
