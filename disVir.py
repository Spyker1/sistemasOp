class DiscoDuro:
    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.espacio_libre = capacidad
        self.particiones = []

    def crear_particion(self, nombre, tamaño):
        if tamaño <= self.espacio_libre:
            self.particiones.append(Particion(nombre, tamaño))
            self.espacio_libre -= tamaño
            return True
        else:
            return False

    def mostrar_particiones(self):
        for particion in self.particiones:
            print(particion)

class Particion:
    def __init__(self, nombre, tamaño):
        self.nombre = nombre
        self.tamaño = tamaño
        self.espacio_libre = tamaño
        self.archivos = []

    def almacenar_archivo(self, archivo, tamaño):
        if tamaño <= self.espacio_libre:
            self.archivos.append(archivo)
            self.espacio_libre -= tamaño
            return True
        else:
            return False

    def __str__(self):
        return f"Partición {self.nombre}: Tamaño {self.tamaño}, Espacio libre {self.espacio_libre}"

if __name__ == "__main__":
    # Crear un disco duro de 1000 MB
    disco = DiscoDuro(1000)

    # Crear una partición de 500 MB
    disco.crear_particion("Partición1", 500)

    # Mostrar particiones
    disco.mostrar_particiones()

