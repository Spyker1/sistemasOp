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
        self.inodo_map = []  # Mapa de inodos
        self.bloque_map = {}  # Mapa de bloques

    def almacenar_inodo(self, inodo):
        self.inodo_map.append(inodo)

    def __str__(self):
        return f"Partición {self.nombre}: Tamaño {self.tamaño}, Espacio libre {self.espacio_libre}"

class Archivo:
    def __init__(self, nombre, tamaño, datos):
        self.nombre = nombre
        self.tamaño = tamaño
        self.datos = datos  # Datos del archivo

def encontrar_bloques_contiguos(bloques_necesarios, particion):
    bloques_contiguos = []
    espacio_contiguo = 0

    for i, bloque in enumerate(particion.bloque_map):
        if not particion.bloque_map[bloque]:
            espacio_contiguo += 1
            bloques_contiguos.append(bloque)
            if espacio_contiguo == bloques_necesarios:
                return bloques_contiguos
        else:
            espacio_contiguo = 0
            bloques_contiguos = []

    return None

def escribir_inodo_en_disco(inodo, particion):
    particion.almacenar_inodo(inodo)
    print(f"Inodo {inodo['nombre']} almacenado en la partición {particion.nombre}")

def escribir_datos_en_bloques(archivo, bloques_contiguos, particion):
    for i, bloque in enumerate(bloques_contiguos):
        if i < len(archivo.datos):
            particion.bloque_map[bloque] = archivo.datos[i]
            print(f"Dato {archivo.datos[i]} almacenado en el bloque {bloque} de la partición {particion.nombre}")

def actualizar_mapa_de_bits(bloques_contiguos, particion):
    for bloque in bloques_contiguos:
        particion.bloque_map[bloque] = True
        print(f"Bloque {bloque} actualizado en el mapa de bits de la partición {particion.nombre}")

if __name__ == "__main__":
    # Crear un disco duro de 1000 MB
    disco = DiscoDuro(1000)

    # Crear una partición de 500 MB
    disco.crear_particion("Partición1", 500)

    # Mostrar particiones
    disco.mostrar_particiones()

    # Escribir archivos en el disco
    archivo1 = Archivo("documento1.txt", 500, ["datos1", "datos2", "datos3", "datos4"])
    particion = disco.particiones[0]  # Tomamos la primera partición, podrías ajustarlo según tu estructura
    bloques_contiguos = encontrar_bloques_contiguos(len(archivo1.datos), particion)

    if bloques_contiguos:
        inodo = {"nombre": archivo1.nombre, "tamaño": archivo1.tamaño, "bloques": bloques_contiguos}
        escribir_inodo_en_disco(inodo, particion)
        escribir_datos_en_bloques(archivo1, bloques_contiguos, particion)
        actualizar_mapa_de_bits(bloques_contiguos, particion)
    else:
        print("No hay suficiente espacio en disco para almacenar el archivo.")
