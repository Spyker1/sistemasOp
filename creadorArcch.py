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

    def encontrar_particion_libre(self, tamaño):
        for particion in self.particiones:
            if particion.espacio_libre >= tamaño:
                return particion
        return None

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

    def crear_directorio(self, nombre):
        self.archivos.append(Directorio(nombre))

    def __str__(self):
        return f"Partición {self.nombre}: Tamaño {self.tamaño}, Espacio libre {self.espacio_libre}"

class Archivo:
    def __init__(self, nombre, contenido):
        self.nombre = nombre
        self.contenido = contenido

class Directorio(Archivo):
    def __init__(self, nombre):
        super().__init__(nombre, [])
        self.archivos = []

    def agregar_archivo(self, archivo):
        self.archivos.append(archivo)

def main():
    disco = DiscoDuro(1000)
    disco.crear_particion("Partición1", 500)

    # Función para crear directorios
    def mkdir(directorio_actual, ruta):
        partes = ruta.split("/")
        for parte in partes:
            encontrado = False
            for archivo in directorio_actual.archivos:
                if isinstance(archivo, Directorio) and archivo.nombre == parte:
                    directorio_actual = archivo
                    encontrado = True
                    break
            if not encontrado:
                nuevo_directorio = Directorio(parte)
                directorio_actual.agregar_archivo(nuevo_directorio)
                directorio_actual = nuevo_directorio

    # Crear directorios usando ambos formatos
    raiz = Directorio("raiz")
    disco.particiones[0].archivos.append(raiz)

    print("Creando directorios usando formato FAT:")
    mkdir(raiz, "documentos/fotos")
    mkdir(raiz, "videos")
    print("\nEstructura de directorios:")
    print(raiz.archivos)

    print("\nCreando directorios usando formato EXT:")
    directorio_raiz = raiz
    mkdir(directorio_raiz, "musica")
    mkdir(directorio_raiz, "trabajo/textos")
    print("\nEstructura de directorios:")
    print(directorio_raiz.archivos)

    # Crear archivos en los directorios
    raiz.archivos[0].agregar_archivo(Archivo("foto1.jpg", "contenido de foto1.jpg"))
    raiz.archivos[1].agregar_archivo(Archivo("video1.mp4", "contenido de video1.mp4"))
    directorio_raiz.archivos[0].agregar_archivo(Archivo("cancion1.mp3", "contenido de cancion1.mp3"))
    directorio_raiz.archivos[1].agregar_archivo(Archivo("documento1.txt", "contenido de documento1.txt"))
    
    print("\nEstructura de archivos:")
    print("Fotos:", raiz.archivos[0].archivos)
    print("Videos:", raiz.archivos[1].archivos)
    print("Música:", directorio_raiz.archivos[0].archivos)
    print("Trabajo:", directorio_raiz.archivos[1].archivos)

if __name__ == "__main__":
    main()