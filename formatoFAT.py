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
        self.tabla_asignacion = [0] * (tamaño // 10)  # Cada clúster tiene un tamaño de 10 MB
        self.archivos = []

    def almacenar_archivo(self, archivo, tamaño):
        clusters_necesarios = tamaño // 10 + (1 if tamaño % 10 != 0 else 0)
        clusters_disponibles = sum(1 for cluster in self.tabla_asignacion if cluster == 0)

        if clusters_necesarios <= clusters_disponibles:
            # Buscar clústeres libres para el archivo
            clusters_libres = [i for i, cluster in enumerate(self.tabla_asignacion) if cluster == 0]
            inicio = clusters_libres[0]
            fin = inicio + clusters_necesarios - 1

            # Asignar clústeres del archivo en la tabla de asignación
            for i in range(inicio, fin + 1):
                self.tabla_asignacion[i] = 1

            # Guardar el archivo en la partición
            self.archivos.append((archivo, inicio, fin))
            self.espacio_libre -= tamaño
            return True
        else:
            return False

    def defragmentar(self):
        # Reorganizar archivos en clústeres contiguos
        archivos_ordenados = sorted(self.archivos, key=lambda x: x[1])  # Ordenar por el inicio del clúster
        nueva_tabla_asignacion = [0] * len(self.tabla_asignacion)

        nuevo_inicio = 0
        for archivo, inicio, fin in archivos_ordenados:
            nuevo_fin = nuevo_inicio + (fin - inicio)
            nueva_tabla_asignacion[nuevo_inicio:nuevo_fin + 1] = [1] * (nuevo_fin - nuevo_inicio + 1)
            self.archivos[self.archivos.index((archivo, inicio, fin))] = (archivo, nuevo_inicio, nuevo_fin)
            nuevo_inicio = nuevo_fin + 1

        # Actualizar la tabla de asignación
        self.tabla_asignacion = nueva_tabla_asignacion

    def __str__(self):
        return f"Partición {self.nombre}: Tamaño {self.tamaño} MB, Espacio libre {self.espacio_libre} MB"

if __name__ == "__main__":
    # Crear un disco duro de 1000 MB
    disco = DiscoDuro(1000)

    # Crear una partición de 500 MB
    disco.crear_particion("Partición1", 500)

    # Escribir archivos en la partición
    disco.particiones[0].almacenar_archivo("archivo1.txt", 50)
    disco.particiones[0].almacenar_archivo("archivo2.txt", 70)
    disco.particiones[0].almacenar_archivo("archivo3.txt", 90)

    # Mostrar particiones y archivos
    disco.mostrar_particiones()
    for particion in disco.particiones:
        print(f"Archivos en {particion.nombre}:")
        for archivo, inicio, fin in particion.archivos:
            print(f"- {archivo}: Clústeres {inicio} a {fin}")

    # Ejecutar defragmentación
    print("\nEjecutando defragmentación...")
    disco.particiones[0].defragmentar()

    # Mostrar particiones y archivos después de la defragmentación
    print("\nParticiones después de la defragmentación:")
    disco.mostrar_particiones()
    for particion in disco.particiones:
        print(f"Archivos en {particion.nombre}:")
        for archivo, inicio, fin in particion.archivos:
            print(f"- {archivo}: Clústeres {inicio} a {fin}")
