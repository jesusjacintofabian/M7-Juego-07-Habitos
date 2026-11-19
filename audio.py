# ============================================================
# M7: EL DESAFÍO DEL EQUIPO - MÚSICA Y SONIDOS
# Toda la música y los efectos son ORIGINALES: se componen y
# sintetizan con código (ondas senoidales, triangulares y ruido)
# usando solo la librería estándar de Python. No se usó ningún
# archivo de audio de terceros.
#
# Los archivos .wav se crean en la carpeta "sonidos" la primera
# vez que se abre el juego. Para regenerarlos:
#     python3 audio.py
# Autor: Jesús Jacinto Fabián
# ============================================================

import array
import math
import os
import random
import wave

FRECUENCIA = 44100          # efectos
FRECUENCIA_MUSICA = 22050   # música de fondo

ARCHIVOS = ["clic", "acierto", "error", "tiempo", "tic", "insignia",
            "nivel", "carta", "victoria", "derrota", "inicio",
            "musica_fondo"]


# ------------------------------------------------------------
# Síntesis básica
# ------------------------------------------------------------

def midi(n):
    """Convierte un número de nota MIDI a frecuencia en Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def nota(freq, dur, vol=0.5, forma="seno", ataque=0.005, liberacion=0.05,
         decaimiento=0.0, vibrato=0.0, desliz=0.0, sr=FRECUENCIA):
    n = int(dur * sr)
    out = [0.0] * n
    na = max(1, int(ataque * sr))
    nl = max(1, int(liberacion * sr))
    fase = 0.0
    dos_pi = 2 * math.pi
    for i in range(n):
        t = i / sr
        f = freq * (1 + desliz * t / dur) if desliz else freq
        if vibrato:
            f *= 1 + 0.012 * math.sin(dos_pi * vibrato * t)
        fase += dos_pi * f / sr
        if forma == "seno":
            v = math.sin(fase)
        elif forma == "suave":
            v = (math.sin(fase) + 0.25 * math.sin(2 * fase)
                 + 0.08 * math.sin(3 * fase))
        elif forma == "triangulo":
            v = 2 / math.pi * math.asin(math.sin(fase))
        else:  # ruido
            v = random.uniform(-1, 1)
        env = 1.0
        if i < na:
            env = i / na
        if i > n - nl:
            env *= (n - i) / nl
        if decaimiento:
            env *= math.exp(-decaimiento * t)
        out[i] = v * env * vol
    return out


def mezclar(destino, fuente, inicio, sr=FRECUENCIA):
    pos = int(inicio * sr)
    fin = min(len(destino), pos + len(fuente))
    for i in range(pos, fin):
        destino[i] += fuente[i - pos]


def suavizar(muestras, factor=0.25):
    """Filtro pasa-bajos sencillo para que el ruido suene más suave."""
    y = 0.0
    for i, x in enumerate(muestras):
        y += factor * (x - y)
        muestras[i] = y
    return muestras


def guardar(ruta, muestras, sr=FRECUENCIA, pico=0.85):
    maximo = max(1e-9, max(abs(x) for x in muestras))
    escala = pico / maximo   # normaliza: todos los sonidos con volumen parejo
    datos = array.array("h", (int(max(-1.0, min(1.0, x * escala)) * 32767)
                              for x in muestras))
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(datos.tobytes())


def secuencia(notas, total, forma="suave", vol=0.45, decaimiento=6.0):
    """notas = [(inicio_seg, frecuencia, duración), ...]"""
    buf = [0.0] * int(total * FRECUENCIA)
    for inicio, f, d in notas:
        mezclar(buf, nota(f, d, vol, forma, decaimiento=decaimiento,
                          liberacion=0.08), inicio)
    return buf


# ------------------------------------------------------------
# Efectos de sonido
# ------------------------------------------------------------

def crear_efectos(carpeta):
    def ruta(nombre):
        return os.path.join(carpeta, nombre + ".wav")

    # Clic de botón: corto y suave
    b = nota(1100, 0.06, 0.45, "seno", decaimiento=55)
    mezclar(b, nota(1650, 0.04, 0.12, "seno", decaimiento=80), 0)
    guardar(ruta("clic"), b)

    # Acierto: arpegio ascendente Do-Mi-Sol
    guardar(ruta("acierto"), secuencia(
        [(0, midi(72), 0.25), (0.08, midi(76), 0.25), (0.16, midi(79), 0.4)], 0.6))

    # Error: dos notas descendentes
    guardar(ruta("error"), secuencia(
        [(0, midi(67), 0.22), (0.16, midi(63), 0.45)], 0.65, vol=0.5,
        decaimiento=4))

    # Tiempo agotado: zumbido grave descendente
    b = nota(196, 0.7, 0.5, "suave", vibrato=7, desliz=-0.3, liberacion=0.2)
    mezclar(b, nota(147, 0.7, 0.3, "suave", desliz=-0.3, liberacion=0.2), 0)
    guardar(ruta("tiempo"), b)

    # Tic del reloj (últimos segundos): golpe tipo bloque de madera
    b = nota(1050, 0.13, 0.6, "seno", ataque=0.001, decaimiento=38)
    mezclar(b, nota(1580, 0.1, 0.35, "seno", ataque=0.001, decaimiento=55), 0)
    mezclar(b, suavizar(nota(0, 0.012, 0.5, "ruido", ataque=0.0005), 0.6), 0)
    guardar(ruta("tic"), b)

    # Insignia: destello brillante
    guardar(ruta("insignia"), secuencia(
        [(0, midi(84), 0.3), (0.07, midi(88), 0.3), (0.14, midi(91), 0.3),
         (0.21, midi(96), 0.5)], 0.75, forma="seno", vol=0.35, decaimiento=7))

    # Subida de nivel: pequeña fanfarria
    guardar(ruta("nivel"), secuencia(
        [(0, midi(67), 0.15), (0.1, midi(72), 0.15), (0.2, midi(76), 0.15),
         (0.3, midi(79), 0.6), (0.3, midi(72), 0.6)], 0.95, decaimiento=3.5))

    # Carta: soplido (ruido filtrado)
    b = suavizar(nota(0, 0.35, 0.6, "ruido", ataque=0.12, liberacion=0.2), 0.08)
    guardar(ruta("carta"), b)

    # Victoria: fanfarria con acorde final
    guardar(ruta("victoria"), secuencia(
        [(0, midi(72), 0.18), (0.14, midi(76), 0.18), (0.28, midi(79), 0.18),
         (0.42, midi(84), 1.1), (0.42, midi(76), 1.1), (0.42, midi(79), 1.1),
         (0.42, midi(60), 1.1)], 1.6, vol=0.35, decaimiento=2.2))

    # Derrota: línea descendente tranquila
    guardar(ruta("derrota"), secuencia(
        [(0, midi(67), 0.3), (0.25, midi(65), 0.3), (0.5, midi(64), 0.3),
         (0.75, midi(62), 0.9), (0.75, midi(55), 0.9)], 1.7, vol=0.4,
        decaimiento=2.5))

    # Inicio de partida: campanita ascendente
    guardar(ruta("inicio"), secuencia(
        [(0, midi(64), 0.4), (0.1, midi(69), 0.4), (0.2, midi(76), 0.7)],
        0.95, forma="seno", vol=0.4, decaimiento=4))


# ------------------------------------------------------------
# Música de fondo: loop tranquilo de 16 compases a 90 BPM
# Progresión Do maj7 - La m7 - Fa maj7 - Sol (sus)
# ------------------------------------------------------------

def crear_musica(carpeta):
    sr = FRECUENCIA_MUSICA
    bpm = 90
    tiempo = 60 / bpm                # duración de una negra
    compas = 4 * tiempo
    acordes = [
        # (pad, bajo, notas del arpegio)
        ([48, 52, 55, 59], 36, [60, 64, 67, 71]),   # Do maj7
        ([45, 48, 52, 55], 45, [57, 60, 64, 69]),   # La m7
        ([41, 45, 48, 52], 41, [57, 60, 65, 69]),   # Fa maj7
        ([43, 47, 50, 52], 43, [59, 62, 67, 71]),   # Sol sus
    ]
    patrones = [[0, 1, 2, 3, 2, 1, 0, 1], [0, 2, 1, 3, 0, 2, 3, 1]]
    compases_total = 16
    total = compases_total * compas
    buf = [0.0] * int(total * sr)

    for c in range(compases_total):
        pad, bajo, arp = acordes[(c // 2) % 4]
        inicio = c * compas
        # Pad suave (dos osciladores ligeramente desafinados)
        if c % 2 == 0:
            for n in pad:
                for desaf in (0.998, 1.002):
                    mezclar(buf, nota(midi(n) * desaf, 2 * compas + 0.4, 0.035,
                                      "seno", ataque=0.7, liberacion=0.8, sr=sr),
                            inicio, sr)
        # Bajo en los tiempos 1 y 3
        for b in (0, 2):
            mezclar(buf, nota(midi(bajo), 2 * tiempo, 0.17, "triangulo",
                              ataque=0.01, liberacion=0.2, decaimiento=1.6, sr=sr),
                    inicio + b * tiempo, sr)
        # Arpegio en corcheas
        patron = patrones[(c // 8) % 2]
        for k, idx in enumerate(patron):
            if c >= 8 and k == 7:
                continue  # pequeña variación rítmica en la segunda vuelta
            altura = arp[idx] + (12 if (c >= 8 and k in (3, 6)) else 0)
            mezclar(buf, nota(midi(altura), 0.55, 0.075, "seno", ataque=0.004,
                              liberacion=0.1, decaimiento=5, sr=sr),
                    inicio + k * tiempo / 2, sr)
        # Percusión muy suave (contratiempos)
        for k in range(4):
            golpe = suavizar(nota(0, 0.05, 0.03, "ruido", ataque=0.001,
                                  decaimiento=70, sr=sr), 0.5)
            mezclar(buf, golpe, inicio + k * tiempo + tiempo / 2, sr)

    guardar(os.path.join(carpeta, "musica_fondo.wav"), buf, sr, pico=0.8)


def generar(carpeta, forzar=False):
    os.makedirs(carpeta, exist_ok=True)
    faltan = [a for a in ARCHIVOS
              if not os.path.exists(os.path.join(carpeta, a + ".wav"))]
    if forzar or any(a != "musica_fondo" for a in faltan):
        crear_efectos(carpeta)
    if forzar or "musica_fondo" in faltan:
        crear_musica(carpeta)


# ------------------------------------------------------------
# Reproductor que usa el juego
# ------------------------------------------------------------

class Audio:
    VOLUMEN_EFECTOS = 0.7
    VOLUMEN_MUSICA = 0.35

    VOLUMEN_VOZ = 1.0
    VOLUMEN_MUSICA_CON_VOZ = 0.08
    EXTENSIONES_VOZ = (".ogg", ".wav", ".mp3")

    def __init__(self, carpeta, carpeta_voz=None):
        import pygame
        self.pg = pygame
        self.carpeta_voz = carpeta_voz
        self.voces = {}
        self.canal_voz = None
        self.voz_actual = None
        self.sonidos = {}
        self.musica_activa = True
        self.ok = False
        try:
            generar(carpeta)
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            for nombre in ARCHIVOS[:-1]:
                s = pygame.mixer.Sound(os.path.join(carpeta, nombre + ".wav"))
                s.set_volume(self.VOLUMEN_EFECTOS)
                self.sonidos[nombre] = s
            pygame.mixer.music.load(os.path.join(carpeta, "musica_fondo.wav"))
            pygame.mixer.music.set_volume(self.VOLUMEN_MUSICA)
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)
            self.canal_voz = pygame.mixer.Channel(0)
            self.ok = True
        except Exception as error:  # sin tarjeta de sonido: juego en silencio
            print("Aviso: no se pudo iniciar el audio:", error)

    def play(self, nombre):
        if self.ok and nombre in self.sonidos:
            self.sonidos[nombre].play()

    # -------- Voz del autor (archivos opcionales en la carpeta "voz") --------

    def _cargar_voz(self, nombre):
        if nombre in self.voces:
            return self.voces[nombre]
        sonido = None
        if self.ok and self.carpeta_voz:
            for ext in self.EXTENSIONES_VOZ:
                ruta = os.path.join(self.carpeta_voz, nombre + ext)
                if os.path.exists(ruta):
                    try:
                        sonido = self.pg.mixer.Sound(ruta)
                        sonido.set_volume(self.VOLUMEN_VOZ)
                    except Exception as error:
                        print(f"Aviso: no se pudo cargar {ruta}:", error)
                    break
        self.voces[nombre] = sonido
        return sonido

    def hay_voz(self, nombre):
        return self._cargar_voz(nombre) is not None

    def hablar(self, nombre):
        """Reproduce una grabación (por ejemplo "mision_3"). Si no existe, no hace nada."""
        sonido = self._cargar_voz(nombre)
        if sonido is None:
            self.detener_voz()      # no dejar sonando la grabación anterior
            return False
        self.canal_voz.stop()
        self.canal_voz.play(sonido)
        self.voz_actual = nombre
        self.pg.mixer.music.set_volume(self.VOLUMEN_MUSICA_CON_VOZ)
        return True

    def detener_voz(self):
        if self.ok and self.canal_voz:
            self.canal_voz.stop()
        self.voz_actual = None
        if self.ok:
            self.pg.mixer.music.set_volume(self.VOLUMEN_MUSICA)

    def hablando(self, nombre=None):
        if not (self.ok and self.canal_voz and self.canal_voz.get_busy()):
            return False
        return nombre is None or nombre == self.voz_actual

    def actualizar(self):
        """Devuelve la música a su volumen normal cuando termina la voz."""
        if self.voz_actual and not self.hablando():
            self.voz_actual = None
            self.pg.mixer.music.set_volume(self.VOLUMEN_MUSICA)

    def iniciar_musica(self):
        if self.ok and self.musica_activa:
            self.pg.mixer.music.play(-1, fade_ms=1500)

    def alternar_musica(self):
        self.musica_activa = not self.musica_activa
        if not self.ok:
            return
        if self.musica_activa:
            self.pg.mixer.music.play(-1, fade_ms=800)
        else:
            self.pg.mixer.music.fadeout(400)


if __name__ == "__main__":
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sonidos")
    generar(destino, forzar=True)
    print("Sonidos generados en:", destino)
