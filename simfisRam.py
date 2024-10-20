class Memory:
    def __init__(self, size):
        self.size = size
        self.memory = [None] * size

    def allocate(self, size, pid):
        for i in range(self.size):
            if self.memory[i] is None:
                if self.check_space(i, size):
                    for j in range(i, i + size):
                        self.memory[j] = pid
                    return i
        return -1

    def check_space(self, start, size):
        for i in range(start, start + size):
            if i >= self.size or self.memory[i] is not None:
                return False
        return True

    def deallocate(self, start, size):
        for i in range(start, start + size):
            self.memory[i] = None

    def print_memory(self):
        print("Estado de la memoria:")
        for i in range(self.size):
            print(f"Bloqueado {i}: {'Asignada' if self.memory[i] is not None else 'Libre'}")


import time
import random

def external_program(memory, num_processes, max_memory_size, max_runtime):
    for pid in range(num_processes):
        memory_size = random.randint(1, max_memory_size)
        print(f"Proceso {pid} Solicitud de tamaño de memoria: {memory_size}")
        allocated_block = memory.allocate(memory_size, pid)
        if allocated_block != -1:
            print(f"Memoria asignada en el bloque {allocated_block}")
            time.sleep(random.randint(1, max_runtime))
            memory.deallocate(allocated_block, memory_size)
            print(f"Memoria liberada para el proceso {pid}")
        else:
            print("Error en la asignación de memoria. No hay espacio disponible.")
        memory.print_memory()

memory_size = 20
num_processes = 5
max_memory_size = 5
max_runtime = 5

memory = Memory(memory_size)
external_program(memory, num_processes, max_memory_size, max_runtime)
