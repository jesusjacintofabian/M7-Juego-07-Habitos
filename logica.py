# ============================================================
# M7: EL DESAFÍO DEL EQUIPO - REGLAS DEL JUEGO
# Funciones de puntaje, insignias, cartas, victoria y récords.
# No dibuja nada: la interfaz (mision7_gui.py) solo las llama.
# Autor: Jesús Jacinto Fabián
# ============================================================

import json
import os
import random
from datetime import datetime

import contenido as C

SIN_MULTIPLICADOR = {"mult": 1, "castigo": 1}


def nuevo_jugador(nombre, color):
    return {
        "nombre": nombre, "color": color,
        "nivel": 1, "puntos": 0,
        "liderazgo": 50, "comunicacion": 50, "empatia": 50, "productividad": 50,
        "insignias": [], "racha": 0, "optimas": 0,
    }


def promedio(j):
    return round(sum(j[h] for h in C.HABILIDADES) / len(C.HABILIDADES))


def instantanea(j):
    """Copia de los valores actuales (para animar las barras)."""
    return {k: j[k] for k in list(C.HABILIDADES) + ["puntos"]}


def aplicar_efectos(j, efectos, puntos, config):
    """Aplica cambios según la dificultad. Las habilidades quedan entre
    0 y 100 y los puntos nunca bajan de 0. Devuelve los cambios reales."""
    cambios = []
    for hab, valor in efectos.items():
        if valor < 0:
            valor = int(round(valor * config["castigo"]))
        antes = j[hab]
        j[hab] = max(0, min(100, antes + valor))
        if j[hab] != antes:
            cambios.append((hab, j[hab] - antes))
    if puntos > 0:
        puntos = int(round(puntos * config["mult"]))
    elif puntos < 0:
        puntos = int(round(puntos * config["castigo"]))
    antes = j["puntos"]
    j["puntos"] = max(0, antes + puntos)
    if j["puntos"] != antes:
        cambios.append(("puntos", j["puntos"] - antes))
    return cambios


def dar_insignia(j, nombre):
    if nombre in j["insignias"]:
        return False
    j["insignias"].append(nombre)
    return True


def comprobar_nivel(j):
    nuevo = j["puntos"] // 100 + 1
    if nuevo > j["nivel"]:
        j["nivel"] = nuevo
        return True
    return False


def resolver_decision(j, mision, opcion, config):
    """opcion = None significa que se agotó el tiempo."""
    r = {"calidad": "tiempo", "cambios": [], "bono": 0, "insignias": [],
         "subio": False, "mensaje": "", "mejor": None}
    if opcion is None:
        r["mensaje"] = "¡Se acabó el tiempo! La indecisión le costó al equipo."
        r["cambios"] = aplicar_efectos(j, {"productividad": -10}, 0, config)
    else:
        r["calidad"] = opcion["calidad"]
        r["mensaje"] = opcion["mensaje"]
        r["cambios"] = aplicar_efectos(j, opcion["efectos"], opcion["puntos"], config)

    if r["calidad"] == "optima":
        j["optimas"] += 1
        j["racha"] += 1
        if dar_insignia(j, mision["insignia"]):
            r["insignias"].append(mision["insignia"])
        if j["racha"] >= 2:
            r["bono"] = min(20, 5 * (j["racha"] - 1))
            j["puntos"] += r["bono"]
        if j["racha"] == 3 and dar_insignia(j, "Racha Imparable"):
            r["insignias"].append("Racha Imparable")
    else:
        j["racha"] = 0
        r["mejor"] = next(o["texto"] for o in mision["opciones"]
                          if o["calidad"] == "optima")
    r["subio"] = comprobar_nivel(j)
    return r


def sacar_carta():
    tipo = random.choices(["reto", "bonificacion", "penalizacion"],
                          weights=[40, 30, 30])[0]
    if tipo == "bonificacion":
        return tipo, random.choice(C.CARTAS_BONIFICACION)
    if tipo == "penalizacion":
        return tipo, random.choice(C.CARTAS_PENALIZACION)
    return tipo, None


def resolver_carta(j, carta, config):
    _, efectos, puntos = carta
    cambios = aplicar_efectos(j, efectos, puntos, config)
    return cambios, comprobar_nivel(j)


def pregunta_al_azar(clave):
    return random.choice(C.PREGUNTAS[clave])


def resolver_reto(j, nivel, acierto, config):
    insignias = []
    if acierto:
        cambios = aplicar_efectos(j, {}, nivel["gana"], config)
        if nivel["clave"] == "dificil" and dar_insignia(j, "Mente Brillante"):
            insignias.append("Mente Brillante")
    else:
        cambios = aplicar_efectos(j, {}, -nivel["pierde"], SIN_MULTIPLICADOR)
    return cambios, insignias, comprobar_nivel(j)


def finalizar(j):
    if j["optimas"] == 7 and dar_insignia(j, "Maestro de los 7 Hábitos"):
        return ["Maestro de los 7 Hábitos"]
    return []


def evaluar(j):
    """Devuelve (misión cumplida, rango, promedio)."""
    prom = promedio(j)
    cumplida = j["puntos"] >= C.META_PUNTOS and prom >= C.PROMEDIO_MINIMO
    if cumplida and prom >= 75:
        rango = "Líder Altamente Efectivo"
    elif cumplida:
        rango = "Líder Efectivo"
    elif j["puntos"] >= C.META_PUNTOS * 0.6:
        rango = "Líder en Formación"
    else:
        rango = "Equipo en Riesgo"
    return cumplida, rango, prom


def habilidad_debil(j):
    return min(C.HABILIDADES, key=lambda h: j[h])


def clave_podio(j):
    return (j["puntos"], promedio(j), len(j["insignias"]))


def ordenar_podio(jugadores):
    orden = sorted(jugadores, key=clave_podio, reverse=True)
    empatados = [j for j in orden if clave_podio(j) == clave_podio(orden[0])]
    return orden, empatados


# ============================================================
# RÉCORDS (archivo JSON con los 10 mejores puntajes)
# ============================================================

def cargar_records(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, list) else []
    except (OSError, ValueError):
        return []


def borrar_records(ruta):
    """Elimina el archivo de récords. Devuelve True si se pudo."""
    try:
        if os.path.exists(ruta):
            os.remove(ruta)
        return True
    except OSError:
        return False


def guardar_record(ruta, j, config):
    _, rango, _ = evaluar(j)
    records = cargar_records(ruta)
    records.append({"nombre": j["nombre"], "puntos": j["puntos"],
                    "dificultad": config["nombre"], "rango": rango,
                    "fecha": datetime.now().strftime("%d/%m/%Y")})
    records.sort(key=lambda r: r.get("puntos", 0), reverse=True)
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(records[:10], f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # si no se puede guardar, el juego continúa
