import datetime
import random
import time
import pickle
from threading import Thread
from tabulate import tabulate
from colorama import init, Fore, Style
import matplotlib.pyplot as plt  # Librería para gráficos (Instalar con `pip install matplotlib`)

init(autoreset=True)

# Definiendo las clases para usuarios y grupos
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.groups = []

class Group:
    def __init__(self, name):
        self.name = name
        self.members = []

class UserManager:
    def __init__(self):
        self.users = {}
        self.groups = {}
        self.current_user = None

    def add_user(self, username, password):
        if username in self.users:
            print(f"{Fore.RED}Error: El usuario {username} ya existe.")
            return
        user = User(username, password)
        self.users[username] = user
        print(f"{Fore.GREEN}Usuario {username} creado exitosamente.")
    
    def add_group(self, groupname):
        if groupname in self.groups:
            print(f"{Fore.RED}Error: El grupo {groupname} ya existe.")
            return
        group = Group(groupname)
        self.groups[groupname] = group
        print(f"{Fore.GREEN}Grupo {groupname} creado exitosamente.")
    
    def add_user_to_group(self, username, groupname):
        if username not in self.users:
            print(f"{Fore.RED}Error: El usuario {username} no existe.")
            return
        if groupname not in self.groups:
            print(f"{Fore.RED}Error: El grupo {groupname} no existe.")
            return
        user = self.users[username]
        group = self.groups[groupname]
        user.groups.append(groupname)
        group.members.append(username)
        print(f"{Fore.GREEN}Usuario {username} agregado al grupo {groupname} exitosamente.")
    
    def authenticate(self, username, password):
        if username not in self.users or self.users[username].password != password:
            print(f"{Fore.RED}Error: Autenticación fallida.")
            return
        self.current_user = self.users[username]
        print(f"{Fore.GREEN}Usuario {username} autenticado exitosamente.")

    def switch_user(self, username):
        if username not in self.users:
            print(f"{Fore.RED}Error: El usuario {username} no existe.")
            return
        self.current_user = self.users[username]
        print(f"{Fore.GREEN}Cambiado a usuario {username}.")

    def save_state(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
        print(f"{Fore.GREEN}Estado de usuarios guardado exitosamente.")

    @staticmethod
    def load_state(filename):
        try:
            with open(filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Archivo de estado de usuarios no encontrado. Se creará uno nuevo.")
            return UserManager()

# Definiendo las clases para el sistema de archivos
class Block:
    def __init__(self, size):
        self.size = size
        self.data = None
        self.free = True

class File:
    def __init__(self, name, size, created_at, owner, group, permissions="rw-r--"):
        self.name = name
        self.size = size
        self.created_at = created_at
        self.owner = owner
        self.group = group
        self.permissions = permissions
        self.blocks = []
        self.content = ""

class Directory:
    def __init__(self, name):
        self.name = name
        self.files = {}
        self.subdirectories = {}

class FileSystem:
    def __init__(self, num_blocks, block_size, user_manager, memory_limit, max_memory_limit, format="FAT"):
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.blocks = [Block(block_size) for _ in range(num_blocks)]
        self.root = Directory("/")
        self.current_directory = self.root
        self.user_manager = user_manager
        self.memory_limit = memory_limit  # Límite de memoria en bytes
        self.max_memory_limit = max_memory_limit  # Límite máximo de memoria
        self.used_memory = 0  # Memoria usada actualmente
        self.format = format
    
    def create_file(self, name, size):
        if name in self.current_directory.files:
            print(f"{Fore.RED}Error: El archivo {name} ya existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        num_needed_blocks = -(-size // self.block_size)  # Equivalent to math.ceil(size / block_size)
        free_blocks = [block for block in self.blocks if block.free]
        
        if len(free_blocks) < num_needed_blocks:
            print(f"{Fore.RED}Error: No hay suficiente espacio en disco para crear el archivo.")
            return

        if self.used_memory + num_needed_blocks * self.block_size > self.memory_limit:
            print(f"{Fore.RED}Error: No hay suficiente memoria disponible para crear el archivo.")
            return
        
        created_at = datetime.datetime.now()
        owner = self.user_manager.current_user.username
        group = self.user_manager.current_user.groups[0] if self.user_manager.current_user.groups else ""
        new_file = File(name, size, created_at, owner, group)
        for i in range(num_needed_blocks):
            free_blocks[i].free = False
            new_file.blocks.append(free_blocks[i])
        
        self.current_directory.files[name] = new_file
        self.used_memory += num_needed_blocks * self.block_size  # Actualización de la memoria utilizada
        print(f"{Fore.GREEN}Archivo {name} creado exitosamente el {created_at}.")
    
    def delete_file(self, name):
        if name not in self.current_directory.files:
            print(f"{Fore.RED}Error: El archivo {name} no existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        
        file_to_delete = self.current_directory.files[name]
        if not self.check_permissions(file_to_delete, "w"):
            print(f"{Fore.RED}Error: Permiso denegado.")
            return
        
        for block in file_to_delete.blocks:
            block.free = True
        del self.current_directory.files[name]
        self.used_memory -= len(file_to_delete.blocks) * self.block_size  # Actualización de la memoria utilizada
        print(f"{Fore.GREEN}Archivo {name} eliminado exitosamente.")
    
    def list_files(self):
        if not self.current_directory.files and not self.current_directory.subdirectories:
            print(f"{Fore.YELLOW}No hay archivos ni directorios en el directorio actual.")
            return
        data = []
        for dir_name in self.current_directory.subdirectories:
            data.append([f"{Fore.BLUE}DIR", dir_name, "", "", "", ""])
        for file_name, file in self.current_directory.files.items():
            if file.owner == self.user_manager.current_user.username:
                data.append([f"{Fore.WHITE}ARCHIVO", file_name, file.size, file.created_at, file.owner, file.group, file.permissions])
        print(tabulate(data, headers=[f"{Fore.CYAN}Tipo", f"{Fore.CYAN}Nombre", f"{Fore.CYAN}Tamaño (bytes)", f"{Fore.CYAN}Creado El", f"{Fore.CYAN}Propietario", f"{Fore.CYAN}Grupo", f"{Fore.CYAN}Permisos"], tablefmt="fancy_grid"))
    
    def display_fragmentation(self):
        print(f"{Fore.CYAN}Fragmentación del Disco ({self.format}):")
        for i, block in enumerate(self.blocks):
            print("X" if block.free else "O", end=" ")
            if (i + 1) % 10 == 0:
                print()
        print()

    def visualize_fragmentation(self):
        block_status = ["Libre" if block.free else "Ocupado" for block in self.blocks]
        colors = ['green' if status == "Libre" else 'red' for status in block_status]
        plt.figure(figsize=(10, 5))
        plt.bar(range(self.num_blocks), [1] * self.num_blocks, color=colors)
        plt.xlabel('Bloques')
        plt.ylabel('Estado')
        plt.title('Visualización de la Fragmentación del Disco')
        plt.show()

    def defragment(self):
        used_blocks = [block for block in self.blocks if not block.free]
        
        current_free_index = 0
        for file in self.current_directory.files.values():
            new_blocks = []
            for block in file.blocks:
                while current_free_index < len(self.blocks) and not self.blocks[current_free_index].free:
                    current_free_index += 1
                if current_free_index < len(self.blocks):
                    self.blocks[current_free_index].free = False
                    self.blocks[current_free_index].data = block.data
                    block.free = True
                    new_blocks.append(self.blocks[current_free_index])
                    current_free_index += 1
            file.blocks = new_blocks
        
        # Marcar todos los bloques restantes como libres
        for block in self.blocks:
            if block.free and block not in used_blocks:
                block.data = None
        
        print(f"{Fore.GREEN}Desfragmentación completada exitosamente.")
        self.visualize_fragmentation()
    
    def check_disk_integrity(self):
        errors = 0
        for file in self.current_directory.files.values():
            for block in file.blocks:
                if block.free:
                    errors += 1
                    print(f"{Fore.RED}Error: Bloque libre encontrado en el archivo {file.name}")
        if errors == 0:
            print(f"{Fore.GREEN}Integridad del disco verificada: No se encontraron errores.")
        else:
            print(f"{Fore.RED}Integridad del disco verificada: Se encontraron {errors} errores.")

    def check_bad_sectors(self):
        bad_sectors = 0
        for block in self.blocks:
            if random.choice([True, False]):  # Simulación de sectores defectuosos
                bad_sectors += 1
                block.free = True
                block.data = None
        if bad_sectors == 0:
            print(f"{Fore.GREEN}Verificación de sectores defectuosos: No se encontraron sectores defectuosos.")
        else:
            print(f"{Fore.RED}Verificación de sectores defectuosos: Se encontraron {bad_sectors} sectores defectuosos.")

    def visualize_disk_usage(self):
        used_memory = self.used_memory
        free_memory = self.memory_limit - self.used_memory
        
        labels = ['Usado', 'Libre']
        sizes = [used_memory, free_memory]
        colors = ['#ff9999','#66b3ff']
        explode = (0.1, 0)  
        
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=140)
        plt.axis('equal')  
        plt.title('Uso del Disco')
        plt.show()
    
    def create_directory(self, name):
        if name in self.current_directory.subdirectories:
            print(f"{Fore.RED}Error: El directorio {name} ya existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        new_directory = Directory(name)
        self.current_directory.subdirectories[name] = new_directory
        print(f"{Fore.GREEN}Directorio {name} creado exitosamente.")
    
    def change_directory(self, path):
        if path == "/":
            self.current_directory = self.root
            return
        parts = path.split("/")
        current = self.current_directory if path[0] != "/" else self.root
        for part in parts:
            if not part:
                continue
            if part not in current.subdirectories:
                print(f"{Fore.RED}Error: El directorio {part} no existe.")
                return
            current = current.subdirectories[part]
        self.current_directory = current
        print(f"{Fore.GREEN}Cambiado al directorio {path}")

    def write_file(self, name, content):
        if name not in self.current_directory.files:
            print(f"{Fore.RED}Error: El archivo {name} no existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        file = self.current_directory.files[name]
        if not self.check_permissions(file, "w"):
            print(f"{Fore.RED}Error: Permiso denegado.")
            return
        new_content_size = len(content.encode())
        if self.used_memory - len(file.content.encode()) + new_content_size > self.memory_limit:
            print(f"{Fore.RED}Error: No hay suficiente memoria disponible para escribir el contenido en el archivo.")
            return
        self.used_memory = self.used_memory - len(file.content.encode()) + new_content_size
        file.content = content
        print(f"{Fore.GREEN}Contenido escrito en el archivo {name} exitosamente.")
    
    def read_file(self, name):
        if name not in self.current_directory.files:
            print(f"{Fore.RED}Error: El archivo {name} no existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        file = self.current_directory.files[name]
        if not self.check_permissions(file, "r"):
            print(f"{Fore.RED}Error: Permiso denegado.")
            return
        print(f"{Fore.CYAN}Contenido del archivo {name}:")
        print(file.content)

    def change_permissions(self, name, permissions):
        if name not in self.current_directory.files:
            print(f"{Fore.RED}Error: El archivo {name} no existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        file = self.current_directory.files[name]
        if self.user_manager.current_user.username != file.owner:
            print(f"{Fore.RED}Error: Solo el propietario puede cambiar los permisos.")
            return
        file.permissions = permissions
        print(f"{Fore.GREEN}Permisos del archivo {name} cambiados a {permissions}")

    def check_permissions(self, file, mode):
        user = self.user_manager.current_user
        if user.username == file.owner:
            return mode in file.permissions[:3]
        if any(group in user.groups for group in file.group.split(",")):
            return mode in file.permissions[3:6]
        return mode in file.permissions[6:]
    
    def adjust_memory_limit(self, new_limit):
        if new_limit > self.max_memory_limit:
            print(f"{Fore.RED}Error: No se puede exceder el límite máximo de memoria de {self.max_memory_limit / (1024 * 1024)} MB.")
        elif new_limit < self.used_memory:
            print(f"{Fore.RED}Error: No se puede reducir el límite de memoria por debajo de la memoria actualmente usada ({self.used_memory / (1024 * 1024)} MB).")
        else:
            self.memory_limit = new_limit
            print(f"{Fore.GREEN}Límite de memoria ajustado a {new_limit / (1024 * 1024)} MB.")

    def resize_file(self, name, new_size):
        if name not in self.current_directory.files:
            print(f"{Fore.RED}Error: El archivo {name} no existe.")
            return
        if self.user_manager.current_user is None:
            print(f"{Fore.RED}Error: No hay usuario autenticado.")
            return
        file = self.current_directory.files[name]
        if not self.check_permissions(file, "w"):
            print(f"{Fore.RED}Error: Permiso denegado.")
            return
        
        current_size = file.size
        size_diff = new_size - current_size
        
        if size_diff > 0:  # Incrementar tamaño
            if self.used_memory + size_diff > self.memory_limit:
                print(f"{Fore.RED}Error: No hay suficiente memoria disponible para aumentar el tamaño del archivo.")
                return
            num_needed_blocks = -(-size_diff // self.block_size)
            free_blocks = [block for block in self.blocks if block.free]
            if len(free_blocks) < num_needed_blocks:
                print(f"{Fore.RED}Error: No hay suficiente espacio en disco para aumentar el tamaño del archivo.")
                return
            for i in range(num_needed_blocks):
                free_blocks[i].free = False
                file.blocks.append(free_blocks[i])
        elif size_diff < 0:  # Reducir tamaño
            num_blocks_to_free = -(-abs(size_diff) // self.block_size)
            for i in range(num_blocks_to_free):
                block_to_free = file.blocks.pop()
                block_to_free.free = True
        
        self.used_memory += size_diff
        file.size = new_size
        print(f"{Fore.GREEN}Tamaño del archivo {name} cambiado a {new_size} bytes exitosamente.")

    def save_state(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
        print(f"{Fore.GREEN}Estado del sistema de archivos guardado exitosamente.")

    @staticmethod
    def load_state(filename, user_manager, memory_limit, max_memory_limit, format):
        try:
            with open(filename, 'rb') as file:
                fs = pickle.load(file)
                fs.user_manager = user_manager
                fs.memory_limit = memory_limit
                fs.max_memory_limit = max_memory_limit
                fs.format = format
                return fs
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Archivo de estado del sistema de archivos no encontrado. Se creará uno nuevo.")
            return FileSystem(num_blocks=100, block_size=1024, user_manager=user_manager, memory_limit=memory_limit, max_memory_limit=max_memory_limit, format=format)

# Definiendo las clases para la administración de procesos
class Process:
    def __init__(self, pid, command, cpu_usage, memory_usage, priority=1, nice=0):
        self.pid = pid
        self.command = command
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.priority = priority
        self.nice = nice
        self.execution_time = 0
        self.state = "running"  # Estados posibles: running, paused, terminated, waiting
        self.waiting_time = 0

class ProcessManager:
    def __init__(self, memory_limit, max_memory_limit):
        self.next_pid = 1
        self.processes = []
        self.cpu_time_slice = 1  # Tiempo de CPU asignado a cada proceso en cada ciclo de simulación
        self.memory_limit = memory_limit  # Límite de memoria en bytes
        self.max_memory_limit = max_memory_limit  # Límite máximo de memoria
        self.used_memory = 0  # Memoria usada actualmente
    
    def create_process(self, command, cpu_usage=None, memory_usage=None, priority=1, nice=0):
        if cpu_usage is None:
            cpu_usage = random.randint(1, 10)  # Simulación de uso de CPU entre 1 y 10%
        if memory_usage is None:
            memory_usage = random.randint(10, 100)  # Simulación de uso de memoria entre 10 y 100MB
        
        if self.used_memory + memory_usage > self.memory_limit:
            print(f"{Fore.RED}Error: No hay suficiente memoria disponible para crear el proceso.")
            return
        
        new_process = Process(self.next_pid, command, cpu_usage, memory_usage, priority, nice)
        self.next_pid += 1
        self.processes.append(new_process)
        self.used_memory += memory_usage
        print(f"{Fore.GREEN}Proceso {new_process.pid} creado: {new_process.command}, CPU: {new_process.cpu_usage}%, Memoria: {new_process.memory_usage}MB, Prioridad: {new_process.priority}, Nice: {new_process.nice}")
        return new_process
    
    def initialize_system_processes(self):
        self.create_process("init", priority=0)
        self.create_process("scheduler", priority=0)
        self.create_process("io_manager", priority=0)
        self.create_process("network_manager", priority=0)
        self.create_process("visor", priority=1)

    def list_processes(self):
        if not self.processes:
            print(f"{Fore.YELLOW}No hay procesos en ejecución.")
            return
        data = []
        for process in self.processes:
            state_color = Fore.GREEN if process.state == "running" else (Fore.YELLOW if process.state == "paused" else Fore.RED)
            data.append([process.pid, process.command, process.cpu_usage, process.memory_usage, process.priority, process.nice, process.execution_time, state_color + process.state])
        print(tabulate(data, headers=[f"{Fore.CYAN}PID", f"{Fore.CYAN}Comando", f"{Fore.CYAN}CPU (%)", f"{Fore.CYAN}Memoria (MB)", f"{Fore.CYAN}Prioridad", f"{Fore.CYAN}Nice", f"{Fore.CYAN}Tiempo de Ejecución", f"{Fore.CYAN}Estado"], tablefmt="fancy_grid"))
    
    def simulate_resource_usage(self):
        while True:
            if not self.processes:
                time.sleep(1)
                continue
            for process in self.processes:
                if process.state == "running":
                    process.execution_time += self.cpu_time_slice
                    process.cpu_usage = max(1, min(100, process.cpu_usage + random.randint(-5, 5)))
                    process.memory_usage = max(10, min(1024, process.memory_usage + random.randint(-10, 10)))
            time.sleep(1)
    
    def send_signal(self, pid, signal):
        process = next((p for p in self.processes if p.pid == pid), None)
        if not process:
            print(f"{Fore.RED}Error: Proceso con PID {pid} no encontrado.")
            return
        if signal == "kill":
            process.state = "terminated"
            self.used_memory -= process.memory_usage
            print(f"{Fore.GREEN}Proceso {pid} terminado.")
        elif signal == "pause":
            if process.state == "running":
                process.state = "paused"
                print(f"{Fore.GREEN}Proceso {pid} pausado.")
            else:
                print(f"{Fore.RED}Error: El proceso {pid} no está en ejecución.")
        elif signal == "resume":
            if process.state == "paused":
                process.state = "running"
                print(f"{Fore.GREEN}Proceso {pid} resumido.")
            else:
                print(f"{Fore.RED}Error: El proceso {pid} no está pausado.")
        else:
            print(f"{Fore.RED}Error: Señal desconocida: {signal}")

    def handle_io_event(self, pid, event_duration):
        process = next((p for p in self.processes if p.pid == pid), None)
        if not process:
            print(f"{Fore.RED}Error: Proceso con PID {pid} no encontrado.")
            return
        if process.state == "running":
            process.state = "waiting"
            process.waiting_time = event_duration
            print(f"{Fore.GREEN}Proceso {pid} esperando evento de E/S.")

    def simulate_io_events(self):
        while True:
            if not self.processes:
                time.sleep(1)
                continue
            for process in self.processes:
                if process.state == "waiting":
                    process.waiting_time -= 1
                    if process.waiting_time <= 0:
                        process.state = "running"
                        print(f"{Fore.GREEN}Proceso {process.pid} evento de E/S completado.")
            time.sleep(1)

    def sort_processes(self, sort_key):
        self.processes.sort(key=lambda p: getattr(p, sort_key))
    
    def adjust_memory_limit(self, new_limit):
        if new_limit > self.max_memory_limit:
            print(f"{Fore.RED}Error: No se puede exceder el límite máximo de memoria de {self.max_memory_limit / (1024 * 1024)} MB.")
        elif new_limit < self.used_memory:
            print(f"{Fore.RED}Error: No se puede reducir el límite de memoria por debajo de la memoria actualmente usada ({self.used_memory / (1024 * 1024)} MB).")
        else:
            self.memory_limit = new_limit
            print(f"{Fore.GREEN}Límite de memoria ajustado a {new_limit / (1024 * 1024)} MB.")

    def change_nice(self, pid, new_nice):
        process = next((p for p in self.processes if p.pid == pid), None)
        if not process:
            print(f"{Fore.RED}Error: Proceso con PID {pid} no encontrado.")
            return
        process.nice = new_nice
        print(f"{Fore.GREEN}Valor nice del proceso {pid} cambiado a {new_nice}.")

    def save_state(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
        print(f"{Fore.GREEN}Estado de procesos guardado exitosamente.")

    @staticmethod
    def load_state(filename, memory_limit, max_memory_limit):
        try:
            with open(filename, 'rb') as file:
                pm = pickle.load(file)
                pm.memory_limit = memory_limit
                pm.max_memory_limit = max_memory_limit
                return pm
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Archivo de estado de procesos no encontrado. Se creará uno nuevo.")
            return ProcessManager(memory_limit=memory_limit, max_memory_limit=max_memory_limit)

# Integrando todo en una interfaz de terminal
class Terminal:
    def __init__(self, filesystem, process_manager, user_manager):
        self.filesystem = filesystem
        self.process_manager = process_manager
        self.user_manager = user_manager
        self.resource_thread = Thread(target=self.process_manager.simulate_resource_usage)
        self.resource_thread.daemon = True
        self.resource_thread.start()
        self.io_thread = Thread(target=self.process_manager.simulate_io_events)
        self.io_thread.daemon = True
        self.io_thread.start()
    
    def run(self):
        self.process_manager.initialize_system_processes()
        while True:
            self.show_menu()
            command = input(f"{Fore.CYAN}Seleccione una opción: ").strip()
            self.handle_command(command)
    
    def show_menu(self):
        menu_text = """
        Menú de Opciones:
        1. Crear archivo
        2. Eliminar archivo
        3. Listar archivos y directorios
        4. Mostrar fragmentación del disco
        5. Desfragmentar disco
        6. Verificar integridad del disco
        7. Verificar sectores defectuosos
        8. Visualizar uso del disco
        9. Visualizar fragmentación del disco
        10. Crear directorio
        11. Cambiar directorio
        12. Escribir en archivo
        13. Leer archivo
        14. Cambiar permisos de archivo
        15. Ejecutar proceso
        16. Listar procesos
        17. Matar proceso
        18. Pausar proceso
        19. Resumir proceso
        20. Cambiar prioridad de proceso
        21. Manejar evento de E/S
        22. Agregar usuario
        23. Agregar grupo
        24. Agregar usuario a grupo
        25. Autenticar usuario
        26. Cambiar de usuario
        27. Ajustar límite de memoria
        28. Cambiar tamaño de archivo
        29. Cambiar valor nice de proceso
        30. Mostrar visor de procesos
        31. Ayuda
        32. Salir
        """
        print(menu_text)

    def handle_command(self, command):
        try:
            option = int(command)
        except ValueError:
            print(f"{Fore.RED}Error: Opción inválida.")
            return
        
        if option == 1:
            filename = input(f"{Fore.CYAN}Ingrese el nombre del archivo: ")
            size = int(input(f"{Fore.CYAN}Ingrese el tamaño del archivo: "))
            self.filesystem.create_file(filename, size)
        elif option == 2:
            filename = input(f"{Fore.CYAN}Ingrese el nombre del archivo a eliminar: ")
            self.filesystem.delete_file(filename)
        elif option == 3:
            self.filesystem.list_files()
        elif option == 4:
            self.filesystem.display_fragmentation()
        elif option == 5:
            self.filesystem.defragment()
        elif option == 6:
            self.filesystem.check_disk_integrity()
        elif option == 7:
            self.filesystem.check_bad_sectors()
        elif option == 8:
            self.filesystem.visualize_disk_usage()
        elif option == 9:
            self.filesystem.visualize_fragmentation()
        elif option == 10:
            dirname = input(f"{Fore.CYAN}Ingrese el nombre del directorio: ")
            self.filesystem.create_directory(dirname)
        elif option == 11:
            path = input(f"{Fore.CYAN}Ingrese la ruta del directorio: ")
            self.filesystem.change_directory(path)
        elif option == 12:
            filename = input(f"{Fore.CYAN}Ingrese el nombre del archivo: ")
            content = input(f"{Fore.CYAN}Ingrese el contenido del archivo: ")
            self.filesystem.write_file(filename, content)
        elif option == 13:
            filename = input(f"{Fore.CYAN}Ingrese el nombre del archivo: ")
            self.filesystem.read_file(filename)
        elif option == 14:
            filename = input(f"{Fore.CYAN}Ingrese el nombre del archivo: ")
            permissions = input(f"{Fore.CYAN}Ingrese los permisos del archivo: ")
            self.filesystem.change_permissions(filename, permissions)
        elif option == 15:
            command_str = input(f"{Fore.CYAN}Ingrese el comando a ejecutar: ")
            self.process_manager.create_process(command_str)
        elif option == 16:
            self.process_manager.list_processes()
        elif option == 17:
            pid = int(input(f"{Fore.CYAN}Ingrese el PID del proceso a matar: "))
            self.process_manager.send_signal(pid, "kill")
        elif option == 18:
            pid = int(input(f"{Fore.CYAN}Ingrese el PID del proceso a pausar: "))
            self.process_manager.send_signal(pid, "pause")
        elif option == 19:
            pid = int(input(f"{Fore.CYAN}Ingrese el PID del proceso a resumir: "))
            self.process_manager.send_signal(pid, "resume")
        elif option == 20:
            pid = int(input(f"{Fore.CYAN}Ingrese el PID del proceso: "))
            priority = int(input(f"{Fore.CYAN}Ingrese la nueva prioridad: "))
            process = next((p for p in self.process_manager.processes if p.pid == pid), None)
            if not process:
                print(f"{Fore.RED}Error: Proceso con PID {pid} no encontrado.")
            else:
                process.priority = priority
                print(f"{Fore.GREEN}Prioridad del proceso {pid} cambiada a {priority}.")
        elif option == 21:
            pid = int(input(f"{Fore.CYAN}Ingrese el PID del proceso: "))
            duration = int(input(f"{Fore.CYAN}Ingrese la duración del evento de E/S: "))
            self.process_manager.handle_io_event(pid, duration)
        elif option == 22:
            username = input(f"{Fore.CYAN}Ingrese el nombre del usuario: ")
            password = input(f"{Fore.CYAN}Ingrese la contraseña del usuario: ")
            self.user_manager.add_user(username, password)
        elif option == 23:
            groupname = input(f"{Fore.CYAN}Ingrese el nombre del grupo: ")
            self.user_manager.add_group(groupname)
        elif option == 24:
            username = input(f"{Fore.CYAN}Ingrese el nombre del usuario: ")
            groupname = input(f"{Fore.CYAN}Ingrese el nombre del grupo: ")
            self.user_manager.add_user_to_group(username, groupname)
        elif option == 25:
            username = input(f"{Fore.CYAN}Ingrese el nombre del usuario: ")
            password = input(f"{Fore.CYAN}Ingrese la contraseña del usuario: ")
            self.user_manager.authenticate(username, password)
        elif option == 26:
            username = input(f"{Fore.CYAN}Ingrese el nombre del usuario: ")
            self.user_manager.switch_user(username)
        elif option == 27:
            new_limit = int(input(f"{Fore.CYAN}Ingrese el nuevo límite de memoria en MB: ")) * 1024 * 1024
            self.process_manager.adjust_memory_limit(new_limit)
            self.filesystem.adjust_memory_limit(new_limit)
        elif option == 28:
            filename = input(f"{Fore.CYAN}Ingrese el nombre del archivo: ")
            new_size = int(input(f"{Fore.CYAN}Ingrese el nuevo tamaño del archivo: "))
            self.filesystem.resize_file(filename, new_size)
        elif option == 29:
            pid = int(input(f"{Fore.CYAN}Ingrese el PID del proceso: "))
            new_nice = int(input(f"{Fore.CYAN}Ingrese el nuevo valor nice: "))
            self.process_manager.change_nice(pid, new_nice)
        elif option == 30:
            sort_key = input(f"{Fore.CYAN}Ingrese la clave para ordenar (pid, command, cpu_usage, memory_usage, priority, nice): ")
            self.show_process_view([sort_key])
        elif option == 31:
            self.show_help()
        elif option == 32:
            self.save_state()
            print(f"{Fore.CYAN}Saliendo del terminal.")
            exit()
        else:
            print(f"{Fore.RED}Error: Opción inválida.")
    
    def show_process_view(self, args):
        if len(args) > 0:
            sort_key = args[0]
            if sort_key in ["pid", "command", "cpu_usage", "memory_usage", "priority", "nice"]:
                self.process_manager.sort_processes(sort_key)
                print(f"{Fore.GREEN}Procesos ordenados por {sort_key}.")
            else:
                print(f"{Fore.RED}Error: Clave de ordenación desconocida: {sort_key}")
        self.process_manager.list_processes()
        print(f"{Fore.YELLOW}Para terminar un proceso desde el visor, use el comando 'matar <pid>'.")

    def show_help(self):
        help_text = """
        Comandos disponibles:
        1. Crear archivo
        2. Eliminar archivo
        3. Listar archivos y directorios
        4. Mostrar fragmentación del disco
        5. Desfragmentar disco
        6. Verificar integridad del disco
        7. Verificar sectores defectuosos
        8. Visualizar uso del disco
        9. Visualizar fragmentación del disco
        10. Crear directorio
        11. Cambiar directorio
        12. Escribir en archivo
        13. Leer archivo
        14. Cambiar permisos de archivo
        15. Ejecutar proceso
        16. Listar procesos
        17. Matar proceso
        18. Pausar proceso
        19. Resumir proceso
        20. Cambiar prioridad de proceso
        21. Manejar evento de E/S
        22. Agregar usuario
        23. Agregar grupo
        24. Agregar usuario a grupo
        25. Autenticar usuario
        26. Cambiar de usuario
        27. Ajustar límite de memoria
        28. Cambiar tamaño de archivo
        29. Cambiar valor nice de proceso
        30. Mostrar visor de procesos
        31. Ayuda
        32. Salir
        """
        print(help_text)

    def save_state(self):
        self.filesystem.save_state('filesystem_state.pkl')
        self.process_manager.save_state('process_manager_state.pkl')
        self.user_manager.save_state('user_manager_state.pkl')

# Configuración del simulador
memory_limit = 1024 * 1024 * 10  # 10 MB de límite de memoria
max_memory_limit = 1024 * 1024 * 1000000  # 1000 GB de límite máximo de memoria
user_manager = UserManager.load_state('user_manager_state.pkl')
filesystem = FileSystem.load_state('filesystem_state.pkl', user_manager, memory_limit, max_memory_limit, format="FAT")
process_manager = ProcessManager.load_state('process_manager_state.pkl', memory_limit=memory_limit, max_memory_limit=max_memory_limit)
terminal = Terminal(filesystem, process_manager, user_manager)

# Comentado para no ejecutar en el PCI
terminal.run()
