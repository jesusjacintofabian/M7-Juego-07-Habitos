# ============================================================
# M7: EL DESAFÍO DEL EQUIPO - CONTENIDO DEL JUEGO
# Aquí están todos los datos: misiones, preguntas, cartas,
# personajes e insignias. Para ampliar el juego basta con
# agregar elementos a estas listas, sin tocar la lógica.
# Autor: Jesús Jacinto Fabián
# ============================================================

META_PUNTOS = 250          # puntos mínimos para cumplir la misión
PROMEDIO_MINIMO = 60       # promedio mínimo de habilidades
MAX_JUGADORES = 4

# clave: (nombre visible, color RGB)
HABILIDADES = {
    "liderazgo": ("Liderazgo", (52, 120, 246)),
    "comunicacion": ("Comunicación", (22, 170, 190)),
    "empatia": ("Empatía", (222, 84, 120)),
    "productividad": ("Productividad", (40, 167, 105)),
}

DIFICULTADES = [
    {"nombre": "Aprendiz", "mult": 1.0, "castigo": 0.5, "tiempo": None,
     "pistas": True,
     "detalles": ["Sin límite de tiempo", "Pistas en cada misión",
                  "Castigos a la mitad", "Puntos x1"]},
    {"nombre": "Líder", "mult": 1.25, "castigo": 1.0, "tiempo": 30,
     "pistas": False,
     "detalles": ["30 segundos por decisión", "Sin pistas",
                  "Castigos normales", "Puntos x1.25"]},
    {"nombre": "Líder Experto", "mult": 1.5, "castigo": 1.5, "tiempo": 15,
     "pistas": False,
     "detalles": ["15 segundos por decisión", "Sin pistas",
                  "Castigos x1.5", "Puntos x1.5"]},
]

# Reto Relámpago: el jugador decide cuánto arriesgar
NIVELES_RETO = [
    {"clave": "facil", "nombre": "Fácil", "gana": 10, "pierde": 0},
    {"clave": "medio", "nombre": "Medio", "gana": 20, "pierde": 10},
    {"clave": "dificil", "nombre": "Difícil", "gana": 40, "pierde": 20},
]


# ============================================================
# PERSONAJES (se dibujan con código en graficos.py)
# ============================================================

PERSONAJES = {
    "elena": {"nombre": "Prof. Elena", "piel": (233, 190, 160),
              "pelo": (140, 134, 130), "estilo": "mono", "ropa": (44, 62, 102),
              "tipo_ropa": "blazer", "lentes": True},
    "carlos": {"nombre": "Carlos", "piel": (196, 142, 104),
               "pelo": (38, 30, 28), "estilo": "corto", "ropa": (46, 120, 190),
               "tipo_ropa": "camisa", "lentes": False},
    "sofia": {"nombre": "Sofía", "piel": (242, 206, 178),
              "pelo": (122, 72, 42), "estilo": "largo", "ropa": (196, 78, 110),
              "tipo_ropa": "camiseta", "lentes": False},
    "diego": {"nombre": "Diego", "piel": (150, 104, 76),
              "pelo": (28, 22, 22), "estilo": "rizado", "ropa": (60, 140, 96),
              "tipo_ropa": "sueter", "lentes": True},
    "ana": {"nombre": "Ana", "piel": (214, 164, 124),
            "pelo": (52, 36, 32), "estilo": "mono", "ropa": (228, 146, 44),
            "tipo_ropa": "camiseta", "lentes": False},
}

EQUIPO = ["carlos", "sofia", "diego", "ana"]


# ============================================================
# LAS 7 MISIONES (una por hábito)
# calidad: "optima" (aplica el hábito), "regular" o "mala"
# escena: personajes en pantalla; hablante: índice del que habla
# ============================================================

MISIONES = [
    {
        "habito": "Hábito 1: Ser proactivo",
        "corto": "Tomar la iniciativa en lugar de esperar.",
        "narracion": "Tu equipo acaba de recibir un proyecto. Nadie ha "
                     "comenzado a organizar el trabajo.",
        "escena": ["carlos", "elena", "sofia"], "hablante": 1,
        "dialogo": "Tienen solo 30 días para entregar el proyecto final. "
                   "El tiempo empieza a correr desde hoy.",
        "pista": "Una persona proactiva no espera: toma la iniciativa.",
        "opciones": [
            {"texto": "Esperar a que alguien tome la iniciativa.",
             "efectos": {"productividad": -5, "liderazgo": -5}, "puntos": 5,
             "mensaje": "Decidiste esperar... y nadie se movió.",
             "calidad": "mala"},
            {"texto": "Organizar al equipo y proponer un plan de trabajo.",
             "efectos": {"liderazgo": 10, "comunicacion": 5, "productividad": 10},
             "puntos": 25, "mensaje": "¡Tomaste la iniciativa! El equipo ya "
                                      "tiene un plan.", "calidad": "optima"},
            {"texto": "Hacer todo el proyecto tú solo.",
             "efectos": {"productividad": 5, "comunicacion": -10, "empatia": -5},
             "puntos": 10, "mensaje": "Avanzaste, pero el equipo quedó fuera.",
             "calidad": "regular"},
            {"texto": "Esperar hasta que falten pocos días.",
             "efectos": {"productividad": -10, "liderazgo": -5}, "puntos": 0,
             "mensaje": "El equipo perdió un tiempo valioso.", "calidad": "mala"},
        ],
        "insignia": "Líder Proactivo",
        "leccion": "Ser proactivo es hacerte responsable de tus acciones y "
                   "actuar dentro de tu círculo de influencia, en lugar de "
                   "esperar a que las circunstancias decidan por ti.",
    },
    {
        "habito": "Hábito 2: Comenzar con un fin en mente",
        "corto": "Tener claro el objetivo antes de avanzar.",
        "narracion": "El equipo trabaja, pero cada persona hace una tarea "
                     "distinta y algunos no conocen el objetivo final.",
        "escena": ["carlos", "sofia"], "hablante": 1,
        "dialogo": "Ya terminé tres pantallas del diseño... pero, ¿qué es "
                   "exactamente lo que vamos a entregar?",
        "pista": "Antes de avanzar, todos deben saber hacia dónde van.",
        "opciones": [
            {"texto": "Continuar trabajando sin cambiar nada.",
             "efectos": {"productividad": -5}, "puntos": 5,
             "mensaje": "El equipo sigue desorientado.", "calidad": "mala"},
            {"texto": "Definir claramente el objetivo junto con el equipo.",
             "efectos": {"liderazgo": 5, "comunicacion": 10, "productividad": 10},
             "puntos": 25, "mensaje": "¡Ahora todos reman hacia la misma meta!",
             "calidad": "optima"},
            {"texto": "Decidir tú solo las tareas de cada uno.",
             "efectos": {"liderazgo": 5, "comunicacion": -5}, "puntos": 10,
             "mensaje": "Hay orden, pero el equipo no se siente parte.",
             "calidad": "regular"},
            {"texto": "Cancelar todas las tareas actuales.",
             "efectos": {"productividad": -10}, "puntos": 0,
             "mensaje": "Se perdió todo el trabajo hecho.", "calidad": "mala"},
        ],
        "insignia": "Visión Compartida",
        "leccion": "Comenzar con un fin en mente significa visualizar el "
                   "resultado esperado antes de empezar, para que cada "
                   "esfuerzo apunte a la misma meta.",
    },
    {
        "habito": "Hábito 3: Poner primero lo primero",
        "corto": "Priorizar lo importante sobre lo urgente o fácil.",
        "narracion": "El equipo tiene muchas tareas pendientes, pero solo "
                     "algunas son realmente importantes.",
        "escena": ["diego", "ana"], "hablante": 0,
        "dialogo": "Tenemos veinte tareas en la lista y no sé por dónde "
                   "empezar. ¡Todo parece urgente!",
        "pista": "Lo importante va antes que lo fácil o lo urgente.",
        "opciones": [
            {"texto": "Hacer primero las tareas más fáciles.",
             "efectos": {"productividad": -5}, "puntos": 5,
             "mensaje": "Avanzaste, pero lo importante sigue pendiente.",
             "calidad": "mala"},
            {"texto": "Priorizar las tareas importantes del proyecto.",
             "efectos": {"productividad": 15, "liderazgo": 5}, "puntos": 25,
             "mensaje": "¡Prioridades claras! El proyecto avanza firme.",
             "calidad": "optima"},
            {"texto": "Hacer varias tareas al mismo tiempo.",
             "efectos": {"productividad": 5, "comunicacion": -5}, "puntos": 10,
             "mensaje": "Hubo avance, pero con mucho desorden.",
             "calidad": "regular"},
            {"texto": "Dejar todas las tareas para el último día.",
             "efectos": {"productividad": -15}, "puntos": 0,
             "mensaje": "El equipo entró en modo emergencia.", "calidad": "mala"},
        ],
        "insignia": "Maestro de Prioridades",
        "leccion": "Poner primero lo primero es organizar el tiempo según la "
                   "importancia y no solo la urgencia: lo importante y no "
                   "urgente es donde se construyen los buenos resultados.",
    },
    {
        "habito": "Hábito 4: Pensar ganar/ganar",
        "corto": "Buscar acuerdos donde todos se beneficien.",
        "narracion": "Carlos y Ana quieren liderar la misma parte del "
                     "proyecto. Ambos tienen buenas ideas.",
        "escena": ["carlos", "ana"], "hablante": 0,
        "dialogo": "Yo debería liderar el módulo principal. Mi propuesta "
                   "es la mejor.",
        "pista": "Busca una salida en la que nadie tenga que perder.",
        "opciones": [
            {"texto": "Elegir a uno y excluir al otro.",
             "efectos": {"empatia": -10, "comunicacion": -5}, "puntos": 5,
             "mensaje": "Uno ganó, el otro se desmotivó.", "calidad": "mala"},
            {"texto": "Buscar una solución que beneficie a ambos.",
             "efectos": {"empatia": 10, "comunicacion": 10, "liderazgo": 5},
             "puntos": 30, "mensaje": "¡Solución ganar/ganar! Ambos lideran "
                                      "una parte.", "calidad": "optima"},
            {"texto": "Ignorar el conflicto.",
             "efectos": {"empatia": -5, "productividad": -5}, "puntos": 0,
             "mensaje": "El conflicto sigue creciendo.", "calidad": "mala"},
            {"texto": "Decidir tú quién tiene la razón.",
             "efectos": {"liderazgo": 5, "empatia": -10}, "puntos": 10,
             "mensaje": "Se resolvió rápido, pero alguien quedó molesto.",
             "calidad": "regular"},
        ],
        "insignia": "Mediador",
        "leccion": "Pensar ganar/ganar es buscar acuerdos donde todas las "
                   "partes se beneficien; en un equipo, si uno pierde, a la "
                   "larga pierden todos.",
    },
    {
        "habito": "Hábito 5: Buscar primero entender",
        "corto": "Escuchar con empatía antes de responder.",
        "narracion": "Diego está molesto. Siente que sus aportes no se "
                     "toman en cuenta.",
        "escena": ["diego"], "hablante": 0,
        "dialogo": "Siento que nadie escucha mis ideas en este equipo. "
                   "¿Para qué sigo proponiendo cosas?",
        "pista": "Antes de hablar, escucha.",
        "opciones": [
            {"texto": "Decirle que deje de quejarse.",
             "efectos": {"empatia": -15, "comunicacion": -10}, "puntos": 0,
             "mensaje": "La situación empeoró.", "calidad": "mala"},
            {"texto": "Escucharlo con atención antes de responder.",
             "efectos": {"empatia": 15, "comunicacion": 15}, "puntos": 30,
             "mensaje": "¡Escucha activa! Diego vuelve a sentirse parte.",
             "calidad": "optima"},
            {"texto": "Ignorarlo y seguir trabajando.",
             "efectos": {"empatia": -10}, "puntos": 0,
             "mensaje": "Diego perdió la motivación.", "calidad": "mala"},
            {"texto": "Decirle de inmediato cómo debe trabajar.",
             "efectos": {"liderazgo": 5, "empatia": -10}, "puntos": 5,
             "mensaje": "Diste instrucciones, pero no lo escuchaste.",
             "calidad": "regular"},
        ],
        "insignia": "Escucha Activa",
        "leccion": "Busca primero entender, luego ser entendido: escuchar "
                   "con empatía genera confianza y evita malentendidos.",
    },
    {
        "habito": "Hábito 6: Sinergizar",
        "corto": "Combinar las fortalezas de todos.",
        "narracion": "Tu equipo tiene habilidades diferentes: Carlos "
                     "programa, Sofía diseña y Diego investiga.",
        "escena": ["carlos", "sofia", "diego"], "hablante": 1,
        "dialogo": "Cada uno sabe hacer algo distinto. ¿Cómo nos "
                   "organizamos para la siguiente entrega?",
        "pista": "El todo puede ser mayor que la suma de las partes.",
        "opciones": [
            {"texto": "Que todos hagan lo mismo al mismo tiempo.",
             "efectos": {"productividad": -5}, "puntos": 5,
             "mensaje": "Se desaprovecharon los talentos.", "calidad": "mala"},
            {"texto": "Aprovechar las fortalezas de cada integrante.",
             "efectos": {"liderazgo": 10, "comunicacion": 10,
                         "productividad": 15, "empatia": 5},
             "puntos": 35, "mensaje": "¡Sinergia total! El resultado supera "
                                      "lo esperado.", "calidad": "optima"},
            {"texto": "Elegir solamente al mejor miembro.",
             "efectos": {"empatia": -10, "comunicacion": -5}, "puntos": 5,
             "mensaje": "Los demás se sintieron excluidos.",
             "calidad": "regular"},
            {"texto": "Que cada uno trabaje por su cuenta.",
             "efectos": {"productividad": -10}, "puntos": 0,
             "mensaje": "Las partes no encajaron al final.", "calidad": "mala"},
        ],
        "insignia": "Equipo Sinérgico",
        "leccion": "Sinergizar es combinar las diferencias del equipo para "
                   "lograr resultados que nadie conseguiría por separado.",
    },
    {
        "habito": "Hábito 7: Afilar la sierra",
        "corto": "Renovarse para rendir a largo plazo.",
        "narracion": "El equipo lleva varios días trabajando sin descanso y "
                     "el cansancio empieza a notarse.",
        "escena": ["carlos", "sofia", "diego"], "hablante": 0,
        "dialogo": "Llevamos cinco días sin parar... ya no rindo igual y "
                   "estoy cometiendo errores.",
        "pista": "Un equipo agotado rinde menos. Renovarse también es trabajar.",
        "opciones": [
            {"texto": "Continuar trabajando sin descanso.",
             "efectos": {"productividad": -15}, "puntos": 5,
             "mensaje": "El cansancio bajó el rendimiento.", "calidad": "mala"},
            {"texto": "Organizar una pausa y luego revisar el progreso.",
             "efectos": {"productividad": 15, "empatia": 10, "liderazgo": 10},
             "puntos": 35, "mensaje": "¡El equipo recuperó la energía!",
             "calidad": "optima"},
            {"texto": "Cancelar el proyecto.",
             "efectos": {"productividad": -20}, "puntos": 0,
             "mensaje": "La misión terminó antes de tiempo.", "calidad": "mala"},
            {"texto": "Dejar que cada uno decida qué hacer.",
             "efectos": {"empatia": 5}, "puntos": 10,
             "mensaje": "Algunos descansaron, otros no.", "calidad": "regular"},
        ],
        "insignia": "Equipo Equilibrado",
        "leccion": "Afilar la sierra es renovarse en lo físico, lo mental, lo "
                   "social/emocional y lo espiritual para mantener el "
                   "rendimiento a largo plazo.",
    },
]


# ============================================================
# INSIGNIAS
# ============================================================

INSIGNIAS = [
    ("Líder Proactivo", "Aplicaste el hábito 1"),
    ("Visión Compartida", "Aplicaste el hábito 2"),
    ("Maestro de Prioridades", "Aplicaste el hábito 3"),
    ("Mediador", "Aplicaste el hábito 4"),
    ("Escucha Activa", "Aplicaste el hábito 5"),
    ("Equipo Sinérgico", "Aplicaste el hábito 6"),
    ("Equipo Equilibrado", "Aplicaste el hábito 7"),
    ("Racha Imparable", "3 decisiones efectivas seguidas"),
    ("Mente Brillante", "Acertaste un reto difícil"),
    ("Maestro de los 7 Hábitos", "Las 7 decisiones efectivas"),
]


# ============================================================
# BANCO DE PREGUNTAS DEL RETO RELÁMPAGO
# (pregunta, [opciones], índice de la correcta)
# ============================================================

PREGUNTAS = {
    "facil": [
        ("¿Quién escribió «Los 7 hábitos de la gente altamente efectiva»?",
         ["Stephen Covey", "Peter Drucker", "Steve Jobs"], 0),
        ("¿Qué hábito consiste en tomar la iniciativa?",
         ["Afilar la sierra", "Ser proactivo", "Sinergizar"], 1),
        ("¿Qué significa «sinergizar»?",
         ["Competir dentro del equipo", "Trabajar solo para ir más rápido",
          "Lograr juntos más que por separado"], 2),
        ("«Afilar la sierra» se refiere a...",
         ["Renovarse y cuidar de uno mismo", "Trabajar sin parar",
          "Corregir los errores de otros"], 0),
        ("Escuchar antes de responder corresponde al hábito...",
         ["Poner primero lo primero", "Buscar primero entender",
          "Ser proactivo"], 1),
    ],
    "medio": [
        ("¿Qué hábitos forman la «victoria privada»?",
         ["Los hábitos 1, 2 y 3", "Los hábitos 4, 5 y 6",
          "Solo el hábito 7"], 0),
        ("¿Qué hábitos forman la «victoria pública»?",
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
        ("¿Qué dimensiones se renuevan al «afilar la sierra»?",
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
# CARTAS DE EVENTO: (texto, efectos, puntos)
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
    ("El chat del grupo se llenó de mensajes sin orden.",
     {"comunicacion": -5}, -5),
]

CONSEJOS = {
    "liderazgo": "Practica los hábitos 1 y 2: toma la iniciativa y define metas claras.",
    "comunicacion": "Practica los hábitos 5 y 6: escucha y coordina al equipo.",
    "empatia": "Practica los hábitos 4 y 5: busca acuerdos y comprende al otro.",
    "productividad": "Practica los hábitos 3 y 7: prioriza y cuida la energía del equipo.",
}
