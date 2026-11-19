# ============================================================
# M7: EL DESAFÍO DEL EQUIPO
# VERSIÓN 3.0 - VERSIÓN DE TERMINAL (respaldo sin interfaz gráfica)
# Juego serio para aprender Los 7 Hábitos de la Gente
# Altamente Efectiva (Stephen Covey) tomando decisiones
# como líder de un equipo universitario.
#
# Universidad Tecnológica de Panamá
# Curso: Sistemas Colaborativos - Dr. Ramfis Miguelena
# Autor: Jesús Jacinto Fabián
# ============================================================

import json
import os
import random
import time
from datetime import datetime

# Activa los colores ANSI en la consola de Windows 10/11
if os.name == "nt":
    os.system("")

# Modo rápido (sin pausas ni limpiar pantalla), útil para pruebas
RAPIDO = os.environ.get("MISION7_RAPIDO") == "1"

ARCHIVO_RECORDS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "records_mision7.json"
)


# ============================================================
# COLORES
# ============================================================

RESET = "\033[0m"
ROJO = "\033[31m"
VERDE = "\033[32m"
AMARILLO = "\033[33m"
AZUL = "\033[34m"
MORADO = "\033[35m"
CYAN = "\033[36m"
BLANCO = "\033[37m"
NEGRITA = "\033[1m"


# ============================================================
# CONFIGURACIÓN GENERAL DEL JUEGO
# ============================================================

META_PUNTOS = 250          # Puntos mínimos para cumplir la misión
PROMEDIO_MINIMO = 60       # Promedio mínimo de habilidades
MAX_JUGADORES = 4

HABILIDADES = {
    "liderazgo": ("🧠", "Liderazgo", AZUL),
    "comunicacion": ("💬", "Comunicación", CYAN),
    "empatia": ("❤️", "Empatía", MORADO),
    "productividad": ("⚡", "Productividad", VERDE),
}

DIFICULTADES = {
    "1": {
        "nombre": "Aprendiz",
        "mult": 1.0,
        "castigo": 0.5,
        "tiempo": None,
        "pistas": True,
        "desc": "Con pistas, castigos a la mitad y sin límite de tiempo.",
    },
    "2": {
        "nombre": "Líder",
        "mult": 1.25,
        "castigo": 1.0,
        "tiempo": 30,
        "pistas": False,
        "desc": "30 segundos por decisión. Puntos x1.25.",
    },
    "3": {
        "nombre": "Líder Experto",
        "mult": 1.5,
        "castigo": 1.5,
        "tiempo": 15,
        "pistas": False,
        "desc": "15 segundos por decisión, castigos x1.5. Puntos x1.5.",
    },
}

# Retos Relámpago: el jugador elige cuánto arriesgar
NIVELES_RETO = {
    "1": {"clave": "facil", "nombre": "Fácil", "gana": 10, "pierde": 0},
    "2": {"clave": "medio", "nombre": "Medio", "gana": 20, "pierde": 10},
    "3": {"clave": "dificil", "nombre": "Difícil", "gana": 40, "pierde": 20},
}


# ============================================================
# CONTENIDO: LAS 7 MISIONES (una por hábito)
# calidad: "optima" (decisión efectiva), "regular" o "mala"
# ============================================================

MISIONES = [
    {
        "habito": "HÁBITO 1: SER PROACTIVO",
        "situacion": (
            "Tu equipo acaba de recibir un proyecto.\n"
            "El profesor informa que solo tienen 30 días.\n"
            "Nadie ha comenzado a organizar el trabajo.\n\n"
            "¿Qué haces?"
        ),
        "pista": "Una persona proactiva no espera: toma la iniciativa.",
        "opciones": [
            {"texto": "Esperar a que alguien tome la iniciativa.",
             "efectos": {"productividad": -5, "liderazgo": -5}, "puntos": 5,
             "mensaje": "Decidiste esperar.", "calidad": "mala"},
            {"texto": "Organizar al equipo y proponer un plan.",
             "efectos": {"liderazgo": 10, "comunicacion": 5, "productividad": 10},
             "puntos": 25, "mensaje": "¡Tomaste la iniciativa!", "calidad": "optima"},
            {"texto": "Hacer todo el proyecto tú solo.",
             "efectos": {"productividad": 5, "comunicacion": -10, "empatia": -5},
             "puntos": 10, "mensaje": "Decidiste hacerlo todo tú solo.",
             "calidad": "regular"},
            {"texto": "Esperar hasta que falten pocos días.",
             "efectos": {"productividad": -10, "liderazgo": -5}, "puntos": 0,
             "mensaje": "El equipo perdió tiempo valioso.", "calidad": "mala"},
        ],
        "insignia": ("Líder Proactivo",
                     "Tomaste la iniciativa para organizar al equipo."),
        "leccion": ("Ser proactivo es hacerte responsable de tus acciones y "
                    "actuar dentro de tu círculo de influencia, en lugar de "
                    "esperar a que las circunstancias decidan por ti."),
    },
    {
        "habito": "HÁBITO 2: COMENZAR CON UN FIN EN MENTE",
        "situacion": (
            "El equipo está trabajando, pero cada persona\n"
            "hace una tarea diferente.\n"
            "Algunos no saben cuál es el objetivo final.\n\n"
            "¿Qué haces?"
        ),
        "pista": "Antes de avanzar, todos deben saber hacia dónde van.",
        "opciones": [
            {"texto": "Continuar trabajando sin cambiar nada.",
             "efectos": {"productividad": -5}, "puntos": 5,
             "mensaje": "El equipo sigue desorientado.", "calidad": "mala"},
            {"texto": "Definir claramente el objetivo con el equipo.",
             "efectos": {"liderazgo": 5, "comunicacion": 10, "productividad": 10},
             "puntos": 25, "mensaje": "¡El equipo encontró un objetivo común!",
             "calidad": "optima"},
            {"texto": "Decidir tú solo las tareas de cada uno.",
             "efectos": {"liderazgo": 5, "comunicacion": -5}, "puntos": 10,
             "mensaje": "Hay orden, pero el equipo no se siente parte.",
             "calidad": "regular"},
            {"texto": "Cancelar todas las tareas actuales.",
             "efectos": {"productividad": -10}, "puntos": 0,
             "mensaje": "El proyecto perdió tiempo.", "calidad": "mala"},
        ],
        "insignia": ("Visión Compartida",
                     "Ayudaste al equipo a trabajar hacia un objetivo común."),
        "leccion": ("Comenzar con un fin en mente significa visualizar el "
                    "resultado esperado antes de empezar, para que cada "
                    "esfuerzo apunte a la misma meta."),
    },
    {
        "habito": "HÁBITO 3: PONER PRIMERO LO PRIMERO",
        "situacion": (
            "El equipo tiene muchas tareas pendientes,\n"
            "pero solo algunas son realmente importantes.\n\n"
            "¿Qué haces?"
        ),
        "pista": "Lo importante va antes que lo fácil o lo urgente.",
        "opciones": [
            {"texto": "Hacer primero las tareas fáciles.",
             "efectos": {"productividad": -5}, "puntos": 5,
             "mensaje": "Avanzaste, pero lo importante sigue pendiente.",
             "calidad": "mala"},
            {"texto": "Priorizar las tareas importantes.",
             "efectos": {"productividad": 15, "liderazgo": 5}, "puntos": 25,
             "mensaje": "¡Priorizaste correctamente!", "calidad": "optima"},
            {"texto": "Hacer varias tareas al mismo tiempo.",
             "efectos": {"productividad": 5, "comunicacion": -5}, "puntos": 10,
             "mensaje": "Hubo avance, pero con desorden.", "calidad": "regular"},
            {"texto": "Dejar las tareas para el último día.",
             "efectos": {"productividad": -15}, "puntos": 0,
             "mensaje": "El equipo entró en modo emergencia.", "calidad": "mala"},
        ],
        "insignia": ("Maestro de Prioridades",
                     "Supiste identificar las tareas más importantes."),
        "leccion": ("Poner primero lo primero es organizar el tiempo según la "
                    "importancia y no solo la urgencia: lo importante y no "
                    "urgente es donde se construyen los buenos resultados."),
    },
    {
        "habito": "HÁBITO 4: PENSAR GANAR/GANAR",
        "situacion": (
            "Dos compañeros quieren liderar una parte\n"
            "importante del proyecto. Ambos tienen buenas ideas.\n\n"
            "¿Qué haces?"
        ),
        "pista": "Busca una salida en la que nadie tenga que perder.",
        "opciones": [
            {"texto": "Elegir a uno y excluir al otro.",
             "efectos": {"empatia": -10, "comunicacion": -5}, "puntos": 5,
             "mensaje": "Uno ganó, el otro se desmotivó.", "calidad": "mala"},
            {"texto": "Buscar una solución que beneficie a ambos.",
             "efectos": {"empatia": 10, "comunicacion": 10, "liderazgo": 5},
             "puntos": 30, "mensaje": "¡Encontraste una solución ganar/ganar!",
             "calidad": "optima"},
            {"texto": "Ignorar el conflicto.",
             "efectos": {"empatia": -5, "productividad": -5}, "puntos": 0,
             "mensaje": "El conflicto continúa.", "calidad": "mala"},
            {"texto": "Decidir tú quién tiene la razón.",
             "efectos": {"liderazgo": 5, "empatia": -10}, "puntos": 10,
             "mensaje": "Se resolvió rápido, pero alguien quedó molesto.",
             "calidad": "regular"},
        ],
        "insignia": ("Mediador",
                     "Resolviste un conflicto buscando beneficio mutuo."),
        "leccion": ("Pensar ganar/ganar es buscar acuerdos donde todas las "
                    "partes se beneficien; en un equipo, si uno pierde, a la "
                    "larga pierden todos."),
    },
    {
        "habito": "HÁBITO 5: BUSCAR PRIMERO ENTENDER",
        "situacion": (
            "Uno de tus compañeros está molesto.\n"
            "Dice que siente que nadie escucha sus ideas.\n\n"
            "¿Qué haces?"
        ),
        "pista": "Antes de hablar, escucha.",
        "opciones": [
            {"texto": "Decirle que deje de quejarse.",
             "efectos": {"empatia": -15, "comunicacion": -10}, "puntos": 0,
             "mensaje": "La situación empeoró.", "calidad": "mala"},
            {"texto": "Escucharlo con atención antes de responder.",
             "efectos": {"empatia": 15, "comunicacion": 15}, "puntos": 30,
             "mensaje": "¡Escuchaste activamente!", "calidad": "optima"},
            {"texto": "Ignorarlo.",
             "efectos": {"empatia": -10}, "puntos": 0,
             "mensaje": "El compañero perdió la motivación.", "calidad": "mala"},
            {"texto": "Decirle de inmediato cómo debe trabajar.",
             "efectos": {"liderazgo": 5, "empatia": -10}, "puntos": 5,
             "mensaje": "Diste instrucciones, pero no lo escuchaste.",
             "calidad": "regular"},
        ],
        "insignia": ("Escucha Activa",
                     "Demostraste que primero intentas comprender."),
        "leccion": ("Busca primero entender, luego ser entendido: escuchar "
                    "con empatía genera confianza y evita malentendidos."),
    },
    {
        "habito": "HÁBITO 6: SINERGIZAR",
        "situacion": (
            "Tu equipo tiene habilidades diferentes:\n"
            "una persona programa, otra diseña y otra investiga.\n\n"
            "¿Qué haces?"
        ),
        "pista": "El todo puede ser mayor que la suma de las partes.",
        "opciones": [
            {"texto": "Dejar que todos hagan lo mismo.",
             "efectos": {"productividad": -5}, "puntos": 5,
             "mensaje": "Se desaprovecharon talentos.", "calidad": "mala"},
            {"texto": "Aprovechar las fortalezas de cada integrante.",
             "efectos": {"liderazgo": 10, "comunicacion": 10,
                         "productividad": 15, "empatia": 5},
             "puntos": 35, "mensaje": "¡El equipo trabajó en sinergia!",
             "calidad": "optima"},
            {"texto": "Elegir solamente al mejor miembro.",
             "efectos": {"empatia": -10, "comunicacion": -5}, "puntos": 5,
             "mensaje": "Los demás se sintieron excluidos.", "calidad": "regular"},
            {"texto": "Que cada uno trabaje por su cuenta.",
             "efectos": {"productividad": -10}, "puntos": 0,
             "mensaje": "El trabajo se volvió demasiado pesado.",
             "calidad": "mala"},
        ],
        "insignia": ("Equipo Sinérgico",
                     "Aprovechaste las fortalezas individuales del equipo."),
        "leccion": ("Sinergizar es combinar las diferencias del equipo para "
                    "lograr resultados que nadie conseguiría por separado."),
    },
    {
        "habito": "HÁBITO 7: AFILAR LA SIERRA",
        "situacion": (
            "El equipo lleva varios días trabajando sin descanso.\n"
            "El cansancio comienza a afectar el proyecto.\n\n"
            "¿Qué haces?"
        ),
        "pista": "Un equipo agotado rinde menos. Renovarse también es trabajar.",
        "opciones": [
            {"texto": "Continuar trabajando sin descanso.",
             "efectos": {"productividad": -15}, "puntos": 5,
             "mensaje": "El cansancio disminuyó el rendimiento.",
             "calidad": "mala"},
            {"texto": "Organizar una pausa y revisar el progreso.",
             "efectos": {"productividad": 15, "empatia": 10, "liderazgo": 10},
             "puntos": 35, "mensaje": "¡El equipo recuperó energía!",
             "calidad": "optima"},
            {"texto": "Cancelar el proyecto.",
             "efectos": {"productividad": -20}, "puntos": 0,
             "mensaje": "La misión terminó antes de tiempo.", "calidad": "mala"},
            {"texto": "Dejar que cada uno decida qué hacer.",
             "efectos": {"empatia": 5}, "puntos": 10,
             "mensaje": "Algunos descansaron, otros no.", "calidad": "regular"},
        ],
        "insignia": ("Equipo Equilibrado",
                     "Comprendiste la importancia de cuidar al equipo."),
        "leccion": ("Afilar la sierra es renovarse en lo físico, mental, "
                    "social/emocional y espiritual para mantener el "
                    "rendimiento a largo plazo."),
    },
]


# ============================================================
# CONTENIDO: BANCO DE PREGUNTAS DEL RETO RELÁMPAGO
# ============================================================

PREGUNTAS = {
    "facil": [
        ("¿Quién escribió 'Los 7 hábitos de la gente altamente efectiva'?",
         ["Stephen Covey", "Peter Drucker", "Steve Jobs"], 0),
        ("¿Qué hábito consiste en tomar la iniciativa?",
         ["Afilar la sierra", "Ser proactivo", "Sinergizar"], 1),
        ("¿Qué significa 'sinergizar'?",
         ["Competir dentro del equipo", "Trabajar solo para ir más rápido",
          "Lograr juntos más que por separado"], 2),
        ("'Afilar la sierra' se refiere a...",
         ["Renovarse y cuidar de uno mismo", "Trabajar sin parar",
          "Corregir los errores de otros"], 0),
        ("Escuchar antes de responder corresponde al hábito...",
         ["Poner primero lo primero", "Buscar primero entender",
          "Ser proactivo"], 1),
    ],
    "medio": [
        ("¿Qué hábitos forman la 'victoria privada'?",
         ["Los hábitos 1, 2 y 3", "Los hábitos 4, 5 y 6",
          "Solo el hábito 7"], 0),
        ("¿Qué hábitos forman la 'victoria pública'?",
         ["Los hábitos 1, 2 y 3", "Los hábitos 4, 5 y 6",
          "Los hábitos 5, 6 y 7"], 1),
        ("La matriz de Covey para priorizar organiza las tareas según...",
         ["Costo y tiempo", "Dificultad y gusto",
          "Importancia y urgencia"], 2),
        ("¿En qué tipo de tareas debe enfocarse una persona efectiva?",
         ["Importantes y no urgentes", "Urgentes y no importantes",
          "Ni urgentes ni importantes"], 0),
        ("Pensar ganar/ganar significa...",
         ["Ganar a toda costa", "Buscar el beneficio mutuo",
          "Ceder siempre para evitar conflictos"], 1),
    ],
    "dificil": [
        ("Según Covey, entre el estímulo y la respuesta existe...",
         ["La libertad de elegir", "Un reflejo automático",
          "La aprobación de los demás"], 0),
        ("¿Cuáles son las dimensiones que se renuevan al 'afilar la sierra'?",
         ["Física, económica, laboral y familiar",
          "Física, mental, social/emocional y espiritual",
          "Mental, académica, digital y social"], 1),
        ("Las personas proactivas concentran su energía en su...",
         ["Círculo de preocupación", "Círculo de confort",
          "Círculo de influencia"], 2),
        ("Covey describe la madurez como el paso de la dependencia a la "
         "independencia y luego a...",
         ["La interdependencia", "La autosuficiencia total",
          "La competencia"], 0),
        ("¿Cuál es el enunciado completo del hábito 5?",
         ["Escuchar solo cuando sea necesario",
          "Busque primero entender, luego ser entendido",
          "Hablar primero para guiar al equipo"], 1),
    ],
}


# ============================================================
# CONTENIDO: CARTAS DE EVENTO (bonificación y penalización)
# ============================================================

CARTAS_BONIFICACION = [
    ("El equipo entregó un avance antes de la fecha.",
     {"productividad": 10}, 15),
    ("Un compañero te agradeció por escucharlo.",
     {"empatia": 10}, 10),
    ("La reunión semanal fue corta y muy clara.",
     {"comunicacion": 10}, 10),
    ("El profesor felicitó la organización del equipo.",
     {"liderazgo": 10}, 15),
    ("El equipo creó un tablero de tareas compartido.",
     {"productividad": 5, "comunicacion": 5}, 10),
]

CARTAS_PENALIZACION = [
    ("Un integrante faltó a la reunión sin avisar.",
     {"comunicacion": -10}, -5),
    ("Se perdió un archivo porque nadie tenía respaldo.",
     {"productividad": -10}, -10),
    ("Un comentario sin tacto generó tensión en el grupo.",
     {"empatia": -10}, -5),
    ("Nadie revisó los acuerdos de la última reunión.",
     {"liderazgo": -5, "productividad": -5}, -5),
    ("El grupo de chat se llenó de mensajes sin orden.",
     {"comunicacion": -5}, -5),
]


# ============================================================
# FUNCIONES DE APOYO (entrada, pantalla, pausas)
# ============================================================

def esperar(segundos):
    if not RAPIDO:
        time.sleep(segundos)


def limpiar():
    if RAPIDO:
        print("\n" + "-" * 56)
    else:
        os.system("cls" if os.name == "nt" else "clear")


def leer(mensaje):
    """input() seguro: si se cierra la entrada, el juego termina ordenado."""
    try:
        return input(mensaje).strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{CYAN}Juego finalizado. ¡Hasta la próxima! 👋{RESET}")
        raise SystemExit


def pausa():
    leer(f"\n{AMARILLO}Presiona ENTER para continuar...{RESET}")


def pedir_opcion(validas, mensaje="Selecciona una opción: "):
    """Repite la pregunta hasta recibir una opción válida."""
    while True:
        opcion = leer(f"\n{CYAN}{mensaje}{RESET}")
        if opcion in validas:
            return opcion
        print(f"{ROJO}Opción inválida. Elige entre: "
              f"{', '.join(validas)}.{RESET}")


def linea(caracter="═", largo=56):
    print(caracter * largo)


def titulo(texto):
    limpiar()
    print(f"{MORADO}{NEGRITA}")
    print("╔" + "═" * 56 + "╗")
    print("║" + texto.center(56) + "║")
    print("╚" + "═" * 56 + "╝")
    print(RESET)


def barra(valor, maximo=100, longitud=20):
    valor = max(0, min(valor, maximo))
    llenado = int((valor / maximo) * longitud)
    color = VERDE if valor >= 60 else (AMARILLO if valor >= 40 else ROJO)
    return f"{color}{'█' * llenado}{BLANCO}{'░' * (longitud - llenado)}{RESET}"


def cuadro(texto, color=AMARILLO):
    print(f"\n{color}{NEGRITA}")
    print("╔" + "═" * 44 + "╗")
    print("║" + texto.center(44) + "║")
    print("╚" + "═" * 44 + "╝")
    print(RESET)


# ============================================================
# JUGADOR
# ============================================================

def nuevo_jugador(nombre):
    return {
        "nombre": nombre,
        "nivel": 1,
        "puntos": 0,
        "liderazgo": 50,
        "comunicacion": 50,
        "empatia": 50,
        "productividad": 50,
        "insignias": [],
        "racha": 0,
        "optimas": 0,
    }


def promedio(jugador):
    return round(sum(jugador[h] for h in HABILIDADES) / len(HABILIDADES))


def aplicar_efectos(jugador, efectos, puntos, config):
    """Aplica cambios a habilidades y puntos según la dificultad.
    Las habilidades quedan entre 0 y 100 y los puntos nunca bajan de 0."""
    cambios = []
    for habilidad, valor in efectos.items():
        if valor < 0:
            valor = int(round(valor * config["castigo"]))
        antes = jugador[habilidad]
        jugador[habilidad] = max(0, min(100, antes + valor))
        real = jugador[habilidad] - antes
        if real != 0:
            icono, nombre, _ = HABILIDADES[habilidad]
            color = VERDE if real > 0 else ROJO
            cambios.append(f"{color}{icono} {nombre} {real:+d}{RESET}")

    if puntos > 0:
        puntos = int(round(puntos * config["mult"]))
    elif puntos < 0:
        puntos = int(round(puntos * config["castigo"]))
    antes = jugador["puntos"]
    jugador["puntos"] = max(0, antes + puntos)
    real = jugador["puntos"] - antes
    if real != 0:
        color = VERDE if real > 0 else ROJO
        cambios.append(f"{color}🏆 Puntos {real:+d}{RESET}")

    if cambios:
        print("   " + "   ".join(cambios))


def dar_insignia(jugador, nombre, descripcion):
    if nombre in jugador["insignias"]:
        return
    jugador["insignias"].append(nombre)
    cuadro("🏆 NUEVA INSIGNIA 🏆")
    print(f"{AMARILLO}★ {NEGRITA}{nombre}{RESET}")
    print(f"{BLANCO}{descripcion}{RESET}")
    esperar(1)


def comprobar_nivel(jugador):
    nuevo = jugador["puntos"] // 100 + 1
    if nuevo > jugador["nivel"]:
        jugador["nivel"] = nuevo
        cuadro("⭐ ¡SUBISTE DE NIVEL! ⭐")
        print(f"{VERDE}{jugador['nombre']} ahora es nivel {nuevo}.{RESET}")
        esperar(1)


def mini_estado(jugador):
    """Resumen corto que se muestra al final de cada turno."""
    linea("─")
    print(f"{NEGRITA}{jugador['nombre']}{RESET}  |  ⭐ Nivel {jugador['nivel']}"
          f"  |  🏆 {jugador['puntos']}/{META_PUNTOS} pts"
          f"  |  🔥 Racha {jugador['racha']}")
    for clave, (icono, nombre, color) in HABILIDADES.items():
        print(f"  {icono} {nombre:<14}{barra(jugador[clave], longitud=15)} "
              f"{jugador[clave]}")
    linea("─")


# ============================================================
# TURNO DE MISIÓN
# ============================================================

def turno_mision(jugador, mision, numero, config):
    titulo(f"🎯 MISIÓN {numero}/7  -  Turno de {jugador['nombre']}")
    print(f"{AMARILLO}{NEGRITA}{mision['habito']}{RESET}")
    linea("─")
    print(mision["situacion"])
    linea("─")

    if config["pistas"]:
        print(f"{CYAN}💡 Pista: {mision['pista']}{RESET}\n")

    # Las opciones se barajan en cada partida (rejugabilidad)
    opciones = mision["opciones"][:]
    random.shuffle(opciones)
    for i, op in enumerate(opciones, 1):
        print(f"  [{i}] {op['texto']}")

    if config["tiempo"]:
        print(f"\n{ROJO}⏱  Tienes {config['tiempo']} segundos para decidir.{RESET}")

    inicio = time.time()
    eleccion = pedir_opcion(["1", "2", "3", "4"])
    duracion = time.time() - inicio

    print()
    if config["tiempo"] and duracion > config["tiempo"]:
        print(f"{ROJO}⏱  ¡Tiempo agotado! ({duracion:.0f} s). "
              f"La indecisión le costó al equipo.{RESET}")
        aplicar_efectos(jugador, {"productividad": -10}, 0, config)
        calidad = "mala"
    else:
        op = opciones[int(eleccion) - 1]
        color = {"optima": VERDE, "regular": AMARILLO, "mala": ROJO}[op["calidad"]]
        print(f"{color}{NEGRITA}{op['mensaje']}{RESET}")
        aplicar_efectos(jugador, op["efectos"], op["puntos"], config)
        calidad = op["calidad"]

    # Racha de decisiones efectivas
    if calidad == "optima":
        jugador["optimas"] += 1
        jugador["racha"] += 1
        dar_insignia(jugador, *mision["insignia"])
        if jugador["racha"] >= 2:
            bono = min(20, 5 * (jugador["racha"] - 1))
            print(f"\n{AMARILLO}🔥 Racha de {jugador['racha']} decisiones "
                  f"efectivas: bono de {bono} puntos.{RESET}")
            aplicar_efectos(jugador, {}, bono, {"mult": 1, "castigo": 1})
        if jugador["racha"] == 3:
            dar_insignia(jugador, "Racha Imparable",
                         "Tomaste 3 decisiones efectivas seguidas.")
    else:
        jugador["racha"] = 0
        mejor = next(o for o in mision["opciones"] if o["calidad"] == "optima")
        print(f"\n{CYAN}La decisión más efectiva era: "
              f"\"{mejor['texto']}\"{RESET}")

    print(f"\n{MORADO}{NEGRITA}📘 LECCIÓN:{RESET} {mision['leccion']}")
    comprobar_nivel(jugador)
    pausa()


# ============================================================
# CARTA DE EVENTO (después de cada misión)
# ============================================================

def carta_evento(jugador, config):
    titulo(f"🃏 CARTA DE EVENTO  -  {jugador['nombre']}")
    tipo = random.choices(
        ["reto", "bonificacion", "penalizacion"], weights=[40, 30, 30]
    )[0]

    if tipo == "bonificacion":
        texto, efectos, puntos = random.choice(CARTAS_BONIFICACION)
        print(f"{VERDE}{NEGRITA}⭐ CARTA DE BONIFICACIÓN{RESET}\n")
        print(texto)
        aplicar_efectos(jugador, efectos, puntos, config)

    elif tipo == "penalizacion":
        texto, efectos, puntos = random.choice(CARTAS_PENALIZACION)
        print(f"{ROJO}{NEGRITA}⚠️  CARTA DE PENALIZACIÓN{RESET}\n")
        print(texto)
        aplicar_efectos(jugador, efectos, puntos, config)

    else:
        reto_relampago(jugador, config)

    comprobar_nivel(jugador)
    mini_estado(jugador)
    pausa()


def hacer_pregunta(pregunta, tiempo=None):
    """Muestra una pregunta y devuelve True si se responde bien a tiempo."""
    enunciado, opciones, correcta = pregunta
    print(f"\n{NEGRITA}{enunciado}{RESET}")
    for i, texto in enumerate(opciones, 1):
        print(f"  [{i}] {texto}")
    if tiempo:
        print(f"{ROJO}⏱  {tiempo} segundos.{RESET}")
    inicio = time.time()
    respuesta = pedir_opcion([str(i) for i in range(1, len(opciones) + 1)],
                             "Tu respuesta: ")
    if tiempo and time.time() - inicio > tiempo:
        print(f"{ROJO}⏱  ¡Tiempo agotado!{RESET}")
        return False
    if int(respuesta) - 1 == correcta:
        print(f"{VERDE}{NEGRITA}✔ ¡Correcto!{RESET}")
        return True
    print(f"{ROJO}✘ Incorrecto. La respuesta era: {opciones[correcta]}{RESET}")
    return False


def reto_relampago(jugador, config):
    print(f"{MORADO}{NEGRITA}⚡ RETO RELÁMPAGO{RESET}\n")
    print("Elige cuánto quieres arriesgar ANTES de ver la pregunta:\n")
    for clave, n in NIVELES_RETO.items():
        pierde = f"pierdes {n['pierde']}" if n["pierde"] else "no pierdes nada"
        print(f"  [{clave}] {n['nombre']:<8} → aciertas +{n['gana']}, "
              f"fallas: {pierde}")
    nivel = NIVELES_RETO[pedir_opcion(["1", "2", "3"])]
    pregunta = random.choice(PREGUNTAS[nivel["clave"]])

    if hacer_pregunta(pregunta, config["tiempo"]):
        aplicar_efectos(jugador, {}, nivel["gana"], config)
        if nivel["clave"] == "dificil":
            dar_insignia(jugador, "Mente Brillante",
                         "Respondiste correctamente un reto difícil.")
    else:
        aplicar_efectos(jugador, {}, -nivel["pierde"], {"mult": 1, "castigo": 1})


# ============================================================
# FINAL DE PARTIDA, RANGOS Y DESEMPATE
# ============================================================

def evaluar(jugador):
    prom = promedio(jugador)
    cumplida = jugador["puntos"] >= META_PUNTOS and prom >= PROMEDIO_MINIMO
    if cumplida and prom >= 75:
        rango = "🏆 LÍDER ALTAMENTE EFECTIVO"
    elif cumplida:
        rango = "⭐ LÍDER EFECTIVO"
    elif jugador["puntos"] >= META_PUNTOS * 0.6:
        rango = "📘 LÍDER EN FORMACIÓN"
    else:
        rango = "⚠️  EQUIPO EN RIESGO"
    return cumplida, rango, prom


CONSEJOS = {
    "liderazgo": "Practica los hábitos 1 y 2: toma la iniciativa y define metas.",
    "comunicacion": "Practica los hábitos 5 y 6: escucha y coordina al equipo.",
    "empatia": "Practica los hábitos 4 y 5: busca acuerdos y comprende al otro.",
    "productividad": "Practica los hábitos 3 y 7: prioriza y cuida la energía.",
}


def resultado_individual(jugador, config):
    if jugador["optimas"] == 7:
        dar_insignia(jugador, "Maestro de los 7 Hábitos",
                     "Tomaste la decisión más efectiva en las 7 misiones.")

    cumplida, rango, prom = evaluar(jugador)
    titulo(f"🏁 RESULTADO DE {jugador['nombre'].upper()}")

    if cumplida:
        print(f"{VERDE}{NEGRITA}✅ ¡MISIÓN CUMPLIDA! El proyecto fue un éxito.{RESET}")
    else:
        print(f"{ROJO}{NEGRITA}❌ MISIÓN NO CUMPLIDA. El equipo necesita "
              f"mejorar.{RESET}")
        print(f"{BLANCO}(Meta: {META_PUNTOS} puntos y promedio de habilidades "
              f"de {PROMEDIO_MINIMO} o más){RESET}")

    print(f"\n{AMARILLO}RANGO:{RESET} {NEGRITA}{rango}{RESET}")
    print(f"{AMARILLO}Dificultad:{RESET} {config['nombre']}")
    print(f"{AMARILLO}Puntos:{RESET} {jugador['puntos']}   "
          f"{AMARILLO}Nivel:{RESET} {jugador['nivel']}   "
          f"{AMARILLO}Promedio:{RESET} {prom}")
    print(f"{AMARILLO}Decisiones efectivas:{RESET} {jugador['optimas']}/7")
    linea()
    for clave, (icono, nombre, _) in HABILIDADES.items():
        print(f"{icono} {nombre:<15}{barra(jugador[clave])} {jugador[clave]}")
    linea()
    print(f"{AMARILLO}🏆 INSIGNIAS ({len(jugador['insignias'])}){RESET}")
    for insignia in jugador["insignias"] or ["Ninguna"]:
        print(f"   ★ {insignia}")

    debil = min(HABILIDADES, key=lambda h: jugador[h])
    print(f"\n{CYAN}💡 Consejo: tu habilidad más baja es "
          f"{HABILIDADES[debil][1]}. {CONSEJOS[debil]}{RESET}")

    guardar_record(jugador, config, rango)
    pausa()


def muerte_subita(empatados):
    """Desempate: preguntas difíciles hasta que solo uno acierte."""
    titulo("⚔️  ¡EMPATE! MUERTE SÚBITA ⚔️")
    print("Los jugadores empatados responderán preguntas difíciles.")
    print("Gana quien sea el único en acertar una ronda.\n")
    vivos = empatados[:]
    for ronda in range(1, 11):
        pregunta = random.choice(PREGUNTAS["dificil"])
        print(f"\n{MORADO}{NEGRITA}--- Ronda {ronda} ---{RESET}")
        aciertan = []
        for j in vivos:
            print(f"\n{AMARILLO}Turno de {j['nombre']}{RESET}")
            if hacer_pregunta(pregunta):
                aciertan.append(j)
        if len(aciertan) == 1:
            return aciertan[0]
        if aciertan:
            vivos = aciertan
        print(f"{CYAN}Nadie quedó solo. Nueva pregunta...{RESET}")
        esperar(1)
    return None  # empate compartido tras 10 rondas


def podio(jugadores):
    clave = lambda j: (j["puntos"], promedio(j), len(j["insignias"]))
    orden = sorted(jugadores, key=clave, reverse=True)
    empatados = [j for j in orden if clave(j) == clave(orden[0])]

    ganador = orden[0]
    if len(empatados) > 1:
        ganador = muerte_subita(empatados)
        if ganador:
            orden.remove(ganador)
            orden.insert(0, ganador)

    titulo("🥇 PODIO FINAL 🥇")
    medallas = ["🥇", "🥈", "🥉", "4️⃣"]
    for i, j in enumerate(orden):
        _, rango, prom = evaluar(j)
        print(f"{medallas[i]} {NEGRITA}{j['nombre']:<14}{RESET} "
              f"{j['puntos']:>4} pts  prom {prom:>3}  {rango}")
    linea()
    if ganador:
        print(f"{VERDE}{NEGRITA}¡{ganador['nombre']} es el mejor líder "
              f"de la partida!{RESET}")
    else:
        print(f"{AMARILLO}{NEGRITA}¡Empate compartido! Todos lideraron "
              f"igual de bien.{RESET}")
    pausa()


# ============================================================
# TABLA DE RÉCORDS (se guarda en un archivo JSON)
# ============================================================

def cargar_records():
    try:
        with open(ARCHIVO_RECORDS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def guardar_record(jugador, config, rango):
    records = cargar_records()
    records.append({
        "nombre": jugador["nombre"],
        "puntos": jugador["puntos"],
        "dificultad": config["nombre"],
        "rango": rango,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
    })
    records.sort(key=lambda r: r["puntos"], reverse=True)
    try:
        with open(ARCHIVO_RECORDS, "w", encoding="utf-8") as f:
            json.dump(records[:10], f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # si no se puede guardar, el juego sigue normalmente


def ver_records():
    titulo("📈 TABLA DE RÉCORDS (TOP 10)")
    records = cargar_records()
    if not records:
        print(f"{BLANCO}Todavía no hay récords. ¡Sé el primero!{RESET}")
    for i, r in enumerate(records, 1):
        print(f"{AMARILLO}{i:>2}.{RESET} {r['nombre']:<14} "
              f"{r['puntos']:>4} pts  {r['dificultad']:<13} {r['fecha']}")
    pausa()


# ============================================================
# PANTALLAS DEL MENÚ
# ============================================================

def como_jugar():
    titulo("📖 CÓMO JUGAR")
    print(f"""{CYAN}{NEGRITA}Objetivo{RESET}
Eres el líder de un equipo universitario que debe terminar
un proyecto. Supera 7 misiones (una por cada hábito de
Stephen Covey) tomando las decisiones más efectivas.

{CYAN}{NEGRITA}Cada ronda tiene dos partes{RESET}
 1. {AMARILLO}Misión:{RESET} lees una situación y eliges 1 de 4 decisiones.
    Cada decisión cambia tus habilidades y tus puntos.
 2. {AMARILLO}Carta de evento:{RESET} sale al azar una carta de
    {VERDE}Bonificación{RESET}, {ROJO}Penalización{RESET} o {MORADO}Reto Relámpago{RESET}.

{CYAN}{NEGRITA}Reto Relámpago (riesgo y recompensa){RESET}
 Fácil +10 / 0   ·   Medio +20 / -10   ·   Difícil +40 / -20

{CYAN}{NEGRITA}Reglas clave{RESET}
 • Los puntos nunca bajan de 0; las habilidades van de 0 a 100.
 • Decisiones efectivas seguidas forman una 🔥 racha con bono.
 • Cada 100 puntos subes de nivel.
 • En dificultad Líder y Experto hay límite de tiempo.

{CYAN}{NEGRITA}Condición de victoria{RESET}
 Llegar a {META_PUNTOS} puntos o más con un promedio de
 habilidades de {PROMEDIO_MINIMO} o más.
 En multijugador gana quien tenga más puntos; si hay empate,
 se define con muerte súbita de preguntas difíciles.""")
    pausa()


def ver_misiones():
    titulo("📜 MAPA DE MISIONES")
    for i, m in enumerate(MISIONES, 1):
        print(f"{AMARILLO}[{i:02d}]{RESET} {CYAN}{m['habito']}{RESET}")
    pausa()


def creditos():
    titulo("🎬 CRÉDITOS")
    print(f"""{NEGRITA}M7: EL DESAFÍO DEL EQUIPO{RESET}

Diseño, programación y contenido:  {CYAN}Jesús Jacinto Fabián{RESET}
Curso:     Sistemas Colaborativos
Profesor:  Dr. Ramfis Miguelena
Universidad Tecnológica de Panamá
Facultad de Ingeniería de Sistemas Computacionales
Licenciatura en Ciberseguridad  ·  II Semestre 2026

Basado en: Covey, S. R. Los 7 hábitos de la gente
altamente efectiva.""")
    pausa()


# ============================================================
# CONFIGURAR Y JUGAR UNA PARTIDA
# ============================================================

def configurar_partida():
    titulo("⚙️  NUEVA PARTIDA")
    print("¿Cuántos jugadores participarán? (1 a 4)")
    print(f"{BLANCO}Con 2 o más se juega por turnos y compiten por el podio.{RESET}")
    cantidad = int(pedir_opcion([str(n) for n in range(1, MAX_JUGADORES + 1)]))

    jugadores = []
    for n in range(1, cantidad + 1):
        nombre = ""
        while not nombre:
            nombre = leer(f"{AMARILLO}Nombre del jugador {n}: {RESET}")
        jugadores.append(nuevo_jugador(nombre[:14]))

    titulo("🎚️  DIFICULTAD")
    for clave, d in DIFICULTADES.items():
        print(f"  [{clave}] {NEGRITA}{d['nombre']:<14}{RESET} {d['desc']}")
    config = DIFICULTADES[pedir_opcion(list(DIFICULTADES))]
    return jugadores, config


def historia(jugadores):
    nombres = ", ".join(j["nombre"] for j in jugadores)
    titulo("📖 HISTORIA")
    print(f"""{CYAN}{nombres}{RESET}: han sido seleccionados para liderar
un equipo universitario.

La misión es completar un proyecto antes de que termine
el tiempo disponible. Pero hay un problema...

El equipo está formado por personas con diferentes
personalidades, habilidades y formas de trabajar.

Cada decisión cambiará el futuro del equipo.

{AMARILLO}¿Podrás convertirlo en un verdadero equipo?{RESET}""")
    pausa()


def jugar():
    jugadores, config = configurar_partida()
    historia(jugadores)

    for numero, mision in enumerate(MISIONES, 1):
        for jugador in jugadores:
            print(f"\n{MORADO}Preparando misión {numero}/7 para "
                  f"{jugador['nombre']}...{RESET}")
            esperar(0.7)
            turno_mision(jugador, mision, numero, config)
            carta_evento(jugador, config)

    for jugador in jugadores:
        resultado_individual(jugador, config)

    if len(jugadores) > 1:
        podio(jugadores)


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu():
    while True:
        titulo("⚡ M7: EL DESAFÍO DEL EQUIPO ⚡")
        print(f"{CYAN}{NEGRITA}Aprende a liderar con Los 7 Hábitos{RESET}\n")
        print(f"{CYAN}[1] 🎮 Nueva partida{RESET}")
        print(f"{AZUL}[2] 📖 Cómo jugar{RESET}")
        print(f"{MORADO}[3] 📜 Mapa de misiones{RESET}")
        print(f"{AMARILLO}[4] 📈 Tabla de récords{RESET}")
        print(f"{BLANCO}[5] 🎬 Créditos{RESET}")
        print(f"{ROJO}[6] 🚪 Salir{RESET}")
        linea()

        opcion = pedir_opcion(["1", "2", "3", "4", "5", "6"])
        if opcion == "1":
            jugar()
        elif opcion == "2":
            como_jugar()
        elif opcion == "3":
            ver_misiones()
        elif opcion == "4":
            ver_records()
        elif opcion == "5":
            creditos()
        else:
            print(f"\n{CYAN}Gracias por jugar. ¡Hasta la próxima! 👋{RESET}")
            break


if __name__ == "__main__":
    menu()
