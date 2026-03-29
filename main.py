import sys
import csv
import time
from typing import List, Set, Tuple, Dict
from dataclasses import dataclass
from collections import defaultdict

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
                
    return tareas, recursos

# 🔥 MEJORA CLAVE: mapa categoría → recursos
def mapear_recursos_por_categoria(recursos: List[Recurso]) -> Dict[str, List[Recurso]]:
    mapa = defaultdict(list)
    for r in recursos:
        for cat in r.categorias_soportadas:
            mapa[cat].append(r)
    return mapa

def resolver_scheduling(tareas: List[Tarea], mapa_recursos: Dict[str, List[Recurso]]) -> Tuple[List[str], int]:
    asignaciones: List[str] = []
    makespan_max = 0

    for t in tareas:
        usables = mapa_recursos.get(t.categoria, [])
        
        if not usables:
            raise Exception(f"Tarea sin recurso compatible: {t.id}")

        # elegir recurso más libre
        elegido = min(usables, key=lambda r: r.tiempo_disponible)

        inicio = elegido.tiempo_disponible
        fin = inicio + t.duracion

        elegido.tiempo_disponible = fin
        makespan_max = max(makespan_max, fin)

        asignaciones.append(f"{t.id},{elegido.id},{inicio},{fin}")

    return asignaciones, makespan_max

def guardar_resultados(ruta: str, resultado: List[str]) -> None:
    with open(ruta, 'w', encoding='utf-8') as f:
        for linea in resultado:
            f.write(linea + "\n")

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

    # 🔥 ordenar tareas (LPT)
    tareas_ordenadas = sorted(tareas, key=lambda x: x.duracion, reverse=True)

    # 🔥 crear mapa eficiente
    mapa_recursos = mapear_recursos_por_categoria(recursos)

    resultado, makespan_final = resolver_scheduling(tareas_ordenadas, mapa_recursos)

    guardar_resultados('output.txt', resultado)
    
    print(f"Planificación completada.")
    print(f"Makespan obtenido: {makespan_final}")
    
    if makespan_final <= makespan_objetivo:
        print("¡Objetivo cumplido!")
    else:
        print(f"Aviso: El makespan ({makespan_final}) es mayor al objetivo ({makespan_objetivo}).")

    fin_tiempo = time.time()      
    tiempo_total = fin_tiempo - inicio_tiempo
    print(f"Tiempo de ejecución: {tiempo_total:.4f} segundos")

if __name__ == "__main__":
    main()