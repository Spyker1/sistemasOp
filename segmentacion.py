import random

class Segmento:
    def __init__(self, base, limite):
        self.base = base
        self.limite = limite

class Memoria:
    def __init__(self, tamano):
        self.tamano = tamano
        self.segmentos = []

    def asignar_segmento(self, limite):
        base = random.randint(0, self.tamano - limite)
        segmento = Segmento(base, limite)
        self.segmentos.append(segmento)
        return segmento

    def liberar_segmento(self, segmento):
        self.segmentos.remove(segmento)

    def es_direccion_valida(self, direccion):
        for seg in self.segmentos:
            if seg.base <= direccion < seg.base + seg.limite:
                return True
        return False

def main():
    tamano_memoria = 1000
    memoria = Memoria(tamano_memoria)

    while True:
        accion = input("Ingrese 'asignar' para asignar memoria, 'liberar' para liberar memoria, o 'salir' para terminar: ")

        if accion == 'salir':
            break
        elif accion == 'asignar':
            limite = int(input("Ingrese el tamaño de la memoria a asignar: "))
            segmento = memoria.asignar_segmento(limite)
            print(f"Memoria asignada: base={segmento.base}, limite={segmento.limite}")
        elif accion == 'liberar':
            base = int(input("Ingrese la dirección base del segmento a liberar: "))
            for seg in memoria.segmentos:
                if seg.base == base:
                    memoria.liberar_segmento(seg)
                    print("Memoria liberada.")
                    break
            else:
                print("Segmento no encontrado.")
        else:
            print("Acción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()
