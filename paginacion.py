import random

class Pagina:
    def __init__(self, numero_pagina):
        self.numero_pagina = numero_pagina
        self.en_memoria = False

class MemoriaFisica:
    def __init__(self, tamano_memoria, tamano_pagina):
        self.tamano_memoria = tamano_memoria
        self.tamano_pagina = tamano_pagina
        self.paginas = [Pagina(i) for i in range(tamano_memoria // tamano_pagina)]

    def solicitar_memoria(self, numero_pagina):
        if not self.paginas[numero_pagina].en_memoria:
            print(f"Solicitando página {numero_pagina} a disco...")
            self.paginas[numero_pagina].en_memoria = True
            print(f"Página {numero_pagina} cargada en memoria física.")
        else:
            print(f"Página {numero_pagina} ya está en memoria física.")

    def liberar_memoria(self, numero_pagina):
        if self.paginas[numero_pagina].en_memoria:
            print(f"Liberando página {numero_pagina} de memoria física.")
            self.paginas[numero_pagina].en_memoria = False
        else:
            print(f"Página {numero_pagina} no está en memoria física.")

def main():
    tamano_memoria = 1024  # Tamaño de la memoria física en bytes
    tamano_pagina = 64     # Tamaño de cada página en bytes
    memoria = MemoriaFisica(tamano_memoria, tamano_pagina)

    for _ in range(10):  # Simulación de solicitudes y liberaciones aleatorias
        numero_pagina = random.randint(0, tamano_memoria // tamano_pagina - 1)
        operacion = random.choice(["solicitar", "liberar"])

        if operacion == "solicitar":
            memoria.solicitar_memoria(numero_pagina)
        else:
            memoria.liberar_memoria(numero_pagina)

if __name__ == "__main__":
    main()
