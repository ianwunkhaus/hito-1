import sys
import csv
import time
from typing import List, Set, Tuple
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

def resolver_scheduling(tareas: List[Tarea], recursos: List[Recurso]) -> List[str]:
    asignaciones: List[str] = []

    for t in tareas:
        usables = [r for r in recursos if t.categoria in r.categorias_soportadas]
        
        if not usables:
            raise Exception(f"Tarea sin recurso compatible: {t.id}")

        elegido = min(usables, key=lambda r: r.tiempo_disponible)
        inicio = elegido.tiempo_disponible
        fin = inicio + t.duracion

        elegido.tiempo_disponible = fin
        asignaciones.append(f"{t.id},{elegido.id},{inicio},{fin}")

    return asignaciones

def guardar_resultados(ruta: str, resultado: List[str]) -> int:
    makespan_max = 0

    with open(ruta, 'w', encoding='utf-8') as f:
        for linea in resultado:
            f.write(linea + "\n")
            tiempo_fin = int(linea.split(',')[-1])
            if tiempo_fin > makespan_max:
                makespan_max = tiempo_fin

    return makespan_max

def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python main.py <makespan_objetivo>")
        return

    try:
        makespan_objetivo = float(sys.argv[1])
    except ValueError:
        print("Error: El makespan objetivo debe ser un número.")
        return

    inicio_tiempo = time.time()
    
    tareas, recursos = cargar_datos()

    # 🔥 LPT (ordenar antes de asignar)
    tareas_ordenadas = sorted(tareas, key=lambda x: x.duracion, reverse=True)

    resultado = resolver_scheduling(tareas_ordenadas, recursos)

    try:
        makespan_final = guardar_resultados('output.txt', resultado)
        
        print(f"Planificación completada.")
        print(f"Makespan obtenido: {makespan_final}")
        
        if makespan_final <= makespan_objetivo:
            print("¡Objetivo cumplido!")
        else:
            print(f"Aviso: El makespan ({makespan_final}) es mayor al objetivo ({makespan_objetivo}).")

    except Exception as e:
        print(f"Error al escribir el archivo de salida: {e}")

    fin_tiempo = time.time()      
    tiempo_total = fin_tiempo - inicio_tiempo
    print(f"Tiempo de ejecución: {tiempo_total:.4f} segundos")

if __name__ == "__main__":
    main()