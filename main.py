import sys
import csv
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass

@dataclass
class Tarea:
    id: str
    duracion: int
    categoria: str

@dataclass
class Recurso:
    id: str
    categorias_soportadas: Set[str]
    tiempo_disponible: int = 0  

def cargar_datos(ruta_tareas: str = 'tareas.txt', ruta_recursos: str = 'recursos.txt') -> Tuple[List[Tarea], List[Recurso]]:
    """Lee los archivos de entrada y retorna las listas de objetos."""
    tareas: List[Tarea] = []
    recursos: List[Recurso] = []
    
    try:
       
        with open(ruta_tareas, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    tareas.append(Tarea(row[0].strip(), int(row[1].strip()), row[2].strip()))
                    
       
        with open(ruta_recursos, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    id_r = row[0].strip()
                    categorias = {cat.strip() for cat in row[1:]}
                    recursos.append(Recurso(id_r, categorias))
                    
    except FileNotFoundError as e:
        print(f"Error: No se encontró el archivo {e.filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer los datos: {e}")
        sys.exit(1)
        
    return tareas, recursos

    # hacer estrategia LTP (Longest Task First) para minimizar el makespan

    tareas_ordenadas = sorted(tareas, key=lambda x: x.duracion, reverse=True)
    
    asignaciones: List[str] = []
    
    for t in tareas_ordenadas:
        # Filtrar recursos que soportan la categoría de la tarea
        recursos_compatibles = [r for r in recursos if t.categoria in r.categorias_soportadas]
        
        if not recursos_compatibles:
            print(f"Advertencia: No hay recursos compatibles para la tarea {t.id} ({t.categoria})")
            continue
            
        # De los compatibles, elegir el que esté libre más temprano (minimiza tiempo de espera)
        recurso_elegido = min(recursos_compatibles, key=lambda r: r.tiempo_disponible)
        
        inicio = recurso_elegido.tiempo_disponible
        fin = inicio + t.duracion
        
        # Guardar resultado (ID Tarea, ID Recurso, Inicio, Fin)
        asignaciones.append(f"{t.id},{recurso_elegido.id},{inicio},{fin}")
        
        # Actualizar disponibilidad del recurso (Exclusividad)
        recurso_elegido.tiempo_disponible = fin
        
    return asignaciones


def guardar_resultados(ruta: str, resultado: List[str]) -> int:
    makespan_max = 0
    with open(ruta, 'w', encoding='utf-8') as f:
        for linea in resultado:
            f.write(linea + "\n")
            # Extraer el tiempo de fin para calcular el makespan
            tiempo_fin = int(linea.split(',')[-1])
            if tiempo_fin > makespan_max:
                makespan_max = tiempo_fin
    return makespan_max
    
def main() -> None:
    # El programa debe recibir el makespan_objetivo como argumento
    if len(sys.argv) < 2:
        print("Uso: python main.py <makespan_objetivo>")
        return

    try:
        makespan_objetivo = float(sys.argv[1])
    except ValueError:
        print("Error: El makespan objetivo debe ser un número.")
        return

    # Cargar y Resolver
    tareas, recursos = cargar_datos()
    resultado = resolver_scheduling(tareas, recursos)
    
    # Escribir output.txt (CSV sin encabezados, sin espacios innecesarios)
    try:
        # Escribir output.txt usando la nueva función
        makespan_final = guardar_resultados('output.txt', resultado)
        
        print(f"Planificación completada.")
        print(f"Makespan obtenido: {makespan_final}")
        if makespan_final <= makespan_objetivo:
            print("¡Objetivo cumplido!")
        else:
            print(f"Aviso: El makespan ({makespan_final}) es mayor al objetivo ({makespan_objetivo}).")
            
    except Exception as e:
        print(f"Error al escribir el archivo de salida: {e}")

if __name__ == "__main__":
    main()