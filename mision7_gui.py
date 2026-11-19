#!/usr/bin/env python3
# ============================================================
# M7: EL DESAFÍO DEL EQUIPO
# VERSIÓN 4.0 - INTERFAZ GRÁFICA (Pygame)
#
# Juego serio para aprender Los 7 Hábitos de la Gente
# Altamente Efectiva (Stephen Covey).
#
# Universidad Tecnológica de Panamá
# Curso: Sistemas Colaborativos - Dr. Ramfis Miguelena
# Autor: Jesús Jacinto Fabián
#
# Ejecutar:  python3 mision7_gui.py
# ============================================================

import math
import os
import random

import pygame

import contenido as C
import graficos as G
import logica as L
from audio import Audio
from graficos import ANCHO, ALTO, Boton, Navegador

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_RECORDS = os.path.join(CARPETA, "records_mision7.json")
CARPETA_VOZ = os.path.join(CARPETA, "voz")
COLORES_JUGADOR = [(52, 120, 246), (226, 80, 110), (34, 160, 100), (240, 160, 30)]

# Ánimo inicial de los personajes en cada misión
ANIMO = [["neutral", "neutral", "neutral"], ["preocupado", "preocupado"],
         ["preocupado", "neutral"], ["molesto", "molesto"], ["molesto"],
         ["neutral", "neutral", "neutral"], ["cansado", "cansado", "cansado"]]
REACCION = {"optima": "feliz", "regular": "neutral", "mala": "preocupado",
            "tiempo": "sorprendido"}
POS_PERSONAJES = {1: [320], 2: [215, 425], 3: [150, 320, 490]}


class Ev:
    """Evento simplificado (posición ya convertida a la pantalla base)."""

    def __init__(self, tipo, pos=None, tecla=None, texto=""):
        self.tipo = tipo
        self.pos = pos
        self.tecla = tecla
        self.texto = texto


def es_tecla(ev, *teclas):
    return ev.tipo == "tecla" and ev.tecla in teclas


def limpiar_texto(s):
    """Quita emojis (por ejemplo de récords de la versión de terminal)."""
    return "".join(ch for ch in str(s) if ord(ch) < 0x2190 or 0x2190 <= ord(ch) <= 0x21FF).strip()


# ============================================================
# ELEMENTOS COMUNES DE PANTALLA
# ============================================================

def barra_superior(s, titulo, subtitulo=None, progreso=None, jugador=None):
    pygame.draw.rect(s, (12, 20, 38), (0, 0, ANCHO, 64))
    pygame.draw.line(s, (58, 78, 118), (0, 64), (ANCHO, 64))
    G.texto(s, titulo, (24, 10), 14, G.ACENTO, True)
    if subtitulo:
        G.texto(s, subtitulo, (24, 30), 21, G.BLANCO, True)
    if progreso is not None:
        x0 = 590
        for i in range(7):
            x = x0 + i * 42
            if i < 6:
                col = G.EXITO if i < progreso else (60, 76, 108)
                pygame.draw.line(s, col, (x + 12, 32), (x + 30, 32), 3)
            if i < progreso:
                pygame.draw.circle(s, G.EXITO, (x, 32), 12)
                G.icono(s, "check", (x, 32), 12, G.BLANCO)
            elif i == progreso:
                pygame.draw.circle(s, G.ACENTO, (x, 32), 14)
                G.texto(s, str(i + 1), (x, 32), 15, G.TEXTO, True, "center")
            else:
                pygame.draw.circle(s, (60, 76, 108), (x, 32), 12)
                G.texto(s, str(i + 1), (x, 32), 13, G.TEXTO_CLARO, True, "center")
    if jugador:
        nombre = G.render(jugador["nombre"], 17, G.BLANCO, True)
        x_fin = 1118
        pts = G.render(f"{jugador['puntos']} pts", 14, G.ACENTO, True)
        ancho = max(nombre.get_width(), pts.get_width()) + 56
        r = pygame.Rect(x_fin - ancho, 12, ancho, 42)
        pygame.draw.rect(s, (28, 42, 70), r, border_radius=21)
        pygame.draw.circle(s, jugador["color"], (r.x + 21, r.centery), 15)
        G.texto(s, jugador["nombre"][0].upper(), (r.x + 21, r.centery), 15, G.BLANCO, True, "center")
        s.blit(nombre, (r.x + 44, r.y + 3))
        s.blit(pts, (r.x + 44, r.y + 22))


def hud(s, j, valores=None):
    v = valores or j
    G.panel(s, (20, 650, 1240, 60), G.PANEL, 14, sombra=False)
    pygame.draw.circle(s, j["color"], (54, 680), 19)
    G.icono(s, "estrella", (54, 680), 20, G.BLANCO)
    G.texto(s, f"Nivel {j['nivel']}", (82, 658), 14, G.TEXTO_SUAVE, True)
    G.texto(s, f"{int(v['puntos'])} / {C.META_PUNTOS} pts", (82, 676), 19, G.TEXTO, True)
    if j["racha"] >= 2:
        G.icono(s, "fuego", (248, 680), 22, G.ADVERTENCIA)
        G.texto(s, f"x{j['racha']}", (262, 672), 15, G.ADVERTENCIA, True)
    for i, (clave, (nombre, color)) in enumerate(C.HABILIDADES.items()):
        x = 300 + i * 238
        G.icono(s, clave, (x + 12, 681), 22, color)
        G.texto(s, nombre, (x + 32, 658), 14, G.TEXTO_SUAVE, True)
        G.texto(s, str(int(round(v[clave]))), (x + 222, 658), 14, G.TEXTO, True, "topright")
        G.barra(s, (x + 32, 682, 190, 11), v[clave], color)


def ayuda(s, txt, y=696):
    G.texto(s, txt, (ANCHO // 2, y), 15, G.TEXTO_CLARO, False, "midbottom")


def dibujar_escenario(s, mision, idx_mision, t, expresiones, texto_globo,
                      chars=None, hablando=False):
    G.panel(s, (20, 80, 600, 556), (226, 234, 246), 18)
    pygame.draw.rect(s, (206, 216, 233), (20, 572, 600, 64),
                     border_bottom_left_radius=18, border_bottom_right_radius=18)
    G.icono(s, "info", (46, 108), 22, G.PRIMARIO)
    G.parrafo(s, mision["narracion"], (66, 96), 530, 18, G.TEXTO_SUAVE)
    ids = mision["escena"]
    xs = [20 + x for x in POS_PERSONAJES[len(ids)]]
    h = mision["hablante"]
    quien = C.PERSONAJES[ids[h]]
    G.globo(s, (40, 172, 560, 160), xs[h], quien["nombre"], G.oscurecer(quien["ropa"], 0.1))
    G.parrafo(s, texto_globo, (64, 198), 512, 22, G.TEXTO, max_chars=chars)
    if chars is not None and chars < len(texto_globo):
        G.texto(s, "Clic o ESPACIO para leer rápido", (584, 318), 13, G.TEXTO_SUAVE, False, "bottomright")
    for k, (pid, x) in enumerate(zip(ids, xs)):
        G.personaje(s, x, 618, 1.18, C.PERSONAJES[pid], expresiones[k], t,
                    hablando=(hablando and k == h))


def dibujar_reloj(s, centro, restante, total, t, leido):
    cx, cy = centro
    urgente = restante <= 5
    G.reloj_arena(s, (cx + 52, cy), 80, restante / total, t, urgente)
    color = G.PELIGRO if urgente else G.TEXTO
    G.texto(s, str(max(0, math.ceil(restante))), (cx - 6, cy - 6), 40, color, True, "center")
    G.texto(s, "segundos", (cx - 6, cy + 22), 12, G.TEXTO_SUAVE, True, "center")
    if not leido:
        G.texto(s, "inicia al terminar de leer", (cx + 20, cy + 50), 12, G.TEXTO_SUAVE, False, "center")


def boton_voz(s, juego, centro, nombre, t):
    """Dibuja el altavoz de una grabación: con ondas animadas si está sonando."""
    if not juego.audio.hay_voz(nombre):
        return None
    activo = juego.audio.hablando(nombre)
    r = pygame.Rect(0, 0, 40, 40)
    r.center = centro
    sobre = r.collidepoint(juego.mouse)
    color = G.PRIMARIO if (activo or sobre) else G.TEXTO_SUAVE
    pygame.draw.circle(s, G.aclarar(color, 0.85), r.center, 20)
    tipo = "altavoz_on" if activo and int(t * 3) % 2 == 0 else "altavoz"
    G.icono(s, tipo, r.center, 22, color)
    return r


# ============================================================
# ESCENAS
# ============================================================

class Escena:
    pausable = False

    def __init__(self, juego):
        self.juego = juego
        self.t = 0.0
        self.botones = []

    def evento(self, ev):
        pass

    def actualizar(self, dt):
        self.t += dt
        for b in self.botones:
            b.actualizar(dt, self.juego.mouse)

    def dibujar(self, s):
        pass

    def dibujar_botones(self, s):
        for b in self.botones:
            b.dibujar(s, self.t)


# ------------------------------------------------------------
# Menú principal
# ------------------------------------------------------------

class EscenaMenu(Escena):
    def __init__(self, juego):
        super().__init__(juego)
        x, y, w, h, paso = 90, 292, 340, 54, 64
        self.b_jugar = Boton((x, y, w, h + 6), "Jugar", flecha="der", pulso=True, tam=26)
        datos = [("Cómo jugar", "libro"), ("Mapa de misiones", "mapa"),
                 ("Récords", "trofeo"), ("Créditos", "info"), ("Salir", "salir")]
        self.botones = [self.b_jugar] + [
            Boton((x, y + 14 + paso * (i + 1), w, h), txt, G.PRIMARIO if txt != "Salir" else G.PELIGRO,
                  "claro", icono=ic) for i, (txt, ic) in enumerate(datos)]
        self.nav = Navegador(self.botones)
        self.nav.poner(0)

    def evento(self, ev):
        b = self.nav.evento(ev)
        if not b:
            return
        self.juego.audio.play("clic")
        j = self.juego
        destinos = {"Jugar": EscenaJugadores, "Cómo jugar": EscenaComoJugar,
                    "Mapa de misiones": EscenaMapa, "Récords": EscenaRecords,
                    "Créditos": EscenaCreditos}
        if b.txt == "Salir":
            j.corriendo = False
        else:
            j.cambiar(destinos[b.txt](j))

    def dibujar(self, s):
        G.fondo(s)
        G.elipse_alfa(s, (255, 255, 255, 18), (600, 150, 680, 520))
        G.texto(s, "M7", (86, 92), 86, G.BLANCO, True)
        G.texto(s, "El Desafío del Equipo", (92, 196), 36, G.ACENTO, True)
        G.texto(s, "Aprende a liderar con Los 7 Hábitos de la Gente Altamente Efectiva",
                (94, 248), 17, G.TEXTO_CLARO)
        orden = [("carlos", 690, 1.0), ("sofia", 815, 1.0), ("elena", 940, 1.15),
                 ("diego", 1065, 1.0), ("ana", 1190, 1.0)]
        for pid, x, esc in orden:
            G.personaje(s, x, 640, esc, C.PERSONAJES[pid], "feliz", self.t)
        self.dibujar_botones(s)
        G.texto(s, "↑ ↓ moverte  ·  ENTER elegir  ·  F11 pantalla completa", (940, 700), 15,
                G.TEXTO_CLARO, False, "midbottom")


# ------------------------------------------------------------
# Configuración: jugadores y dificultad
# ------------------------------------------------------------

class EscenaJugadores(Escena):
    def __init__(self, juego):
        super().__init__(juego)
        self.cantidad = 1
        self.nombres = ["", "", "", ""]
        self.campo = 0
        self.b_menos = Boton((496, 182, 66, 66), "", estilo="claro", flecha="izq")
        self.b_mas = Boton((718, 182, 66, 66), "", estilo="claro", flecha="der")
        self.b_volver = Boton((270, 562, 200, 54), "Volver", estilo="claro", flecha="izq")
        self.b_sig = Boton((810, 562, 200, 54), "Siguiente", flecha="der", pulso=True)
        self.botones = [self.b_menos, self.b_mas, self.b_volver, self.b_sig]

    def rect_campo(self, i):
        return pygame.Rect(420, 316 + i * 58, 440, 46)

    def cambiar_cantidad(self, d):
        nueva = max(1, min(C.MAX_JUGADORES, self.cantidad + d))
        if nueva != self.cantidad:
            self.cantidad = nueva
            self.campo = min(self.campo, nueva - 1)
            self.juego.audio.play("clic")

    def siguiente(self):
        self.juego.audio.play("clic")
        jugadores = []
        for i in range(self.cantidad):
            nombre = self.nombres[i].strip() or f"Jugador {i + 1}"
            jugadores.append(L.nuevo_jugador(nombre, COLORES_JUGADOR[i]))
        self.juego.cambiar(EscenaDificultad(self.juego, jugadores))

    def evento(self, ev):
        if ev.tipo == "clic":
            if self.b_menos.clic(ev.pos):
                self.cambiar_cantidad(-1)
            elif self.b_mas.clic(ev.pos):
                self.cambiar_cantidad(1)
            elif self.b_volver.clic(ev.pos):
                self.juego.audio.play("clic")
                self.juego.cambiar(EscenaMenu(self.juego))
            elif self.b_sig.clic(ev.pos):
                self.siguiente()
            for i in range(self.cantidad):
                if self.rect_campo(i).collidepoint(ev.pos):
                    self.campo = i
        elif ev.tipo == "tecla":
            if ev.tecla == pygame.K_ESCAPE:
                self.juego.cambiar(EscenaMenu(self.juego))
            elif ev.tecla == pygame.K_LEFT:
                self.cambiar_cantidad(-1)
            elif ev.tecla == pygame.K_RIGHT:
                self.cambiar_cantidad(1)
            elif ev.tecla in (pygame.K_DOWN, pygame.K_TAB):
                self.campo = (self.campo + 1) % self.cantidad
            elif ev.tecla == pygame.K_UP:
                self.campo = (self.campo - 1) % self.cantidad
            elif ev.tecla == pygame.K_BACKSPACE:
                self.nombres[self.campo] = self.nombres[self.campo][:-1]
            elif ev.tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.campo < self.cantidad - 1:
                    self.campo += 1
                else:
                    self.siguiente()
        elif ev.tipo == "texto":
            actual = self.nombres[self.campo]
            limpio = "".join(ch for ch in ev.texto if ch.isprintable())
            self.nombres[self.campo] = (actual + limpio)[:14]

    def dibujar(self, s):
        G.fondo(s)
        G.panel(s, (240, 84, 800, 552))
        G.texto(s, "¿Cuántos jugadores?", (640, 106), 30, G.TEXTO, True, "midtop")
        G.texto(s, "Con 2 a 4 jugadores se juega por turnos en la misma computadora.",
                (640, 148), 16, G.TEXTO_SUAVE, False, "midtop")
        G.texto(s, str(self.cantidad), (640, 214), 56, G.PRIMARIO, True, "center")
        G.texto(s, "← → para cambiar", (640, 262), 13, G.TEXTO_SUAVE, False, "midtop")
        G.texto(s, "Escribe los nombres (opcional):", (420, 288), 16, G.TEXTO, True)
        for i in range(self.cantidad):
            r = self.rect_campo(i)
            color = COLORES_JUGADOR[i]
            pygame.draw.circle(s, color, (r.x - 30, r.centery), 17)
            G.texto(s, str(i + 1), (r.x - 30, r.centery), 16, G.BLANCO, True, "center")
            activo = (i == self.campo)
            pygame.draw.rect(s, G.BLANCO, r, border_radius=10)
            pygame.draw.rect(s, G.PRIMARIO if activo else G.LINEA, r, 3 if activo else 2, border_radius=10)
            if self.nombres[i]:
                tr = G.texto(s, self.nombres[i], (r.x + 16, r.centery), 20, G.TEXTO, False, "midleft")
                x_cursor = tr.right + 3
            else:
                G.texto(s, f"Jugador {i + 1}", (r.x + 16, r.centery), 20, (170, 176, 190), False, "midleft")
                x_cursor = r.x + 16
            if activo and int(self.t * 2) % 2 == 0:
                pygame.draw.line(s, G.PRIMARIO, (x_cursor, r.y + 11), (x_cursor, r.bottom - 11), 2)
            if activo:
                G.flecha(s, (r.x - 66, r.centery), 22, G.ACENTO, "der")
        self.dibujar_botones(s)
        ayuda(s, "TAB o ↑ ↓ cambiar de casilla   ·   ENTER continuar   ·   ESC volver")


class EscenaDificultad(Escena):
    def __init__(self, juego, jugadores):
        super().__init__(juego)
        self.jugadores = jugadores
        self.sel = 0
        self.tarjetas = [Boton((80 + i * 380, 146, 360, 386), "", G.PRIMARIO, "claro", dato=i, radio=20)
                         for i in range(3)]
        self.b_volver = Boton((80, 572, 200, 54), "Volver", estilo="claro", flecha="izq")
        self.b_ok = Boton((1000, 572, 200, 54), "Comenzar", flecha="der", pulso=True)
        self.botones = self.tarjetas + [self.b_volver, self.b_ok]
        self.nav = Navegador(self.tarjetas, horizontal=True)
        self.nav.poner(0)

    def comenzar(self):
        self.juego.audio.play("inicio")
        self.juego.iniciar_partida(self.jugadores, C.DIFICULTADES[self.sel])

    def evento(self, ev):
        if es_tecla(ev, pygame.K_ESCAPE) or (ev.tipo == "clic" and self.b_volver.clic(ev.pos)):
            self.juego.cambiar(EscenaJugadores(self.juego))
            return
        if ev.tipo == "clic" and self.b_ok.clic(ev.pos):
            self.comenzar()
            return
        if es_tecla(ev, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.sel = max(0, self.nav.i)
            self.comenzar()
            return
        b = self.nav.evento(ev)
        if b:
            self.sel = b.dato
            self.juego.audio.play("clic")
        elif ev.tipo == "tecla" and self.nav.i >= 0:
            self.sel = self.nav.i

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "Elige la dificultad", (640, 78), 34, G.BLANCO, True, "midtop")
        G.texto(s, "Puedes cambiarla en cada partida. Si es tu primera vez, empieza como Aprendiz.",
                (640, 118), 16, G.TEXTO_CLARO, False, "midtop")
        for b in self.tarjetas:
            b.dibujar(s, self.t)
            d = C.DIFICULTADES[b.dato]
            r = b.rect.move(0, -int(2 * b.hover))
            if b.dato == self.sel:
                pygame.draw.rect(s, G.EXITO, r, 4, border_radius=20)
                G.pastilla(s, "Seleccionada", (r.centerx, r.y - 14), G.EXITO, 14, ancla="midtop")
            fr = [1.0, 0.55, 0.25][b.dato]
            G.reloj_arena(s, (r.centerx, r.y + 78), 84, fr, self.t if b.dato else 0)
            G.texto(s, d["nombre"], (r.centerx, r.y + 136), 30, G.TEXTO, True, "midtop")
            for k, det in enumerate(d["detalles"]):
                y = r.y + 196 + k * 40
                G.icono(s, "check", (r.x + 48, y + 11), 16, G.EXITO)
                G.texto(s, det, (r.x + 68, y), 19, G.TEXTO)
            G.texto(s, f"Tecla {b.dato + 1}", (r.centerx, r.bottom - 26), 13, G.TEXTO_SUAVE, True, "center")
        self.b_volver.dibujar(s, self.t)
        self.b_ok.dibujar(s, self.t)
        ayuda(s, "← → elegir   ·   ENTER comenzar   ·   ESC volver")


# ------------------------------------------------------------
# Historia (presentación con la mentora)
# ------------------------------------------------------------

class EscenaHistoria(Escena):
    def __init__(self, juego):
        super().__init__(juego)
        nombres = [j["nombre"] for j in juego.partida.jugadores]
        quien = nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]
        plural = len(nombres) > 1
        self.paginas = [
            f"¡Bienvenido{'s' if plural else ''}, {quien}! Soy la profesora Elena y seré "
            f"{'su' if plural else 'tu'} mentora en esta misión.",
            f"{'Han' if plural else 'Has'} sido seleccionado{'s' if plural else ''} para liderar "
            "un equipo universitario que debe entregar un proyecto en 30 días.",
            "Carlos programa, Sofía diseña, Diego investiga y Ana organiza. Son muy talentosos... "
            "pero también muy diferentes.",
            "En cada misión tomarás una decisión. Las más efectivas aplican uno de Los 7 Hábitos. "
            "¿Podrás convertirlos en un verdadero equipo?",
        ]
        self.pag = 0
        self.chars = 0.0
        self.b_saltar = Boton((60, 596, 200, 52), "Saltar historia", estilo="claro")
        self.b_sig = Boton((1020, 596, 200, 52), "Siguiente", flecha="der", pulso=True)
        self.botones = [self.b_saltar, self.b_sig]

    def avanzar(self):
        txt = self.paginas[self.pag]
        if self.chars < len(txt):
            self.chars = len(txt)
            return
        self.juego.audio.play("clic")
        if self.pag < len(self.paginas) - 1:
            self.pag += 1
            self.chars = 0
        else:
            self.juego.siguiente_turno()

    def evento(self, ev):
        if ev.tipo == "clic" and self.b_saltar.clic(ev.pos):
            self.juego.audio.play("clic")
            self.juego.siguiente_turno()
        elif ev.tipo == "clic" or es_tecla(ev, pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT, pygame.K_KP_ENTER):
            self.avanzar()
        elif es_tecla(ev, pygame.K_ESCAPE):
            self.juego.cambiar(EscenaMenu(self.juego))

    def actualizar(self, dt):
        super().actualizar(dt)
        self.chars = min(len(self.paginas[self.pag]), self.chars + dt * 48)
        ultima = self.pag == len(self.paginas) - 1
        self.b_sig.txt = "¡Comenzar!" if ultima else "Siguiente"

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "LA HISTORIA", (640, 30), 16, G.ACENTO, True, "midtop")
        txt = self.paginas[self.pag]
        hablando = self.chars < len(txt)
        G.personaje(s, 250, 548, 1.45, C.PERSONAJES["elena"], "feliz", self.t, hablando)
        if self.pag >= 2:
            for k, pid in enumerate(C.EQUIPO):
                G.personaje(s, 640 + k * 160, 548, 1.12, C.PERSONAJES[pid],
                            "neutral" if self.pag == 2 else "feliz", self.t)
        G.globo(s, (60, 80, 1160, 170), 250, "Prof. Elena", C.PERSONAJES["elena"]["ropa"])
        G.parrafo(s, txt, (92, 112), 1100, 27, G.TEXTO, max_chars=int(self.chars))
        for i in range(len(self.paginas)):
            col = G.ACENTO if i == self.pag else (90, 106, 140)
            pygame.draw.circle(s, col, (640 - 36 + i * 24, 622), 7 if i == self.pag else 5)
        self.dibujar_botones(s)
        ayuda(s, "Clic, ENTER o → para continuar", 704)


# ------------------------------------------------------------
# Pantalla de cambio de turno (multijugador)
# ------------------------------------------------------------

class EscenaTurno(Escena):
    pausable = True

    def __init__(self, juego):
        super().__init__(juego)
        p = juego.partida
        self.j = p.jugador()
        self.m = C.MISIONES[p.mision_idx]
        self.num = p.mision_idx + 1
        self.b = Boton((540, 470, 200, 56), "¡Estoy listo!", flecha="der", pulso=True)
        self.botones = [self.b]

    def evento(self, ev):
        if (ev.tipo == "clic" and self.b.clic(ev.pos)) or es_tecla(ev, pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            self.juego.audio.play("clic")
            self.juego.cambiar(EscenaMision(self.juego))

    def dibujar(self, s):
        G.fondo(s)
        G.panel(s, (340, 120, 600, 450))
        pygame.draw.circle(s, self.j["color"], (640, 212), 58)
        G.texto(s, self.j["nombre"][0].upper(), (640, 212), 56, G.BLANCO, True, "center")
        G.texto(s, f"Turno de {self.j['nombre']}", (640, 290), 36, G.TEXTO, True, "midtop")
        G.texto(s, f"Misión {self.num} de 7  ·  {self.m['habito']}", (640, 344), 19, G.TEXTO_SUAVE, False, "midtop")
        G.texto(s, f"Pasa la computadora a {self.j['nombre']}.", (640, 390), 18, G.PRIMARIO, True, "midtop")
        G.texto(s, f"{self.j['puntos']} puntos  ·  nivel {self.j['nivel']}", (640, 420), 16, G.TEXTO_SUAVE, False, "midtop")
        self.dibujar_botones(s)
        ayuda(s, "ENTER o clic para empezar   ·   ESC pausa")


# ------------------------------------------------------------
# Misión: situación + 4 decisiones (+ reloj de arena)
# ------------------------------------------------------------

class EscenaMision(Escena):
    pausable = True

    def __init__(self, juego):
        super().__init__(juego)
        p = juego.partida
        self.j = p.jugador()
        self.idx = p.mision_idx
        self.m = C.MISIONES[self.idx]
        self.config = p.config
        self.opciones = random.sample(self.m["opciones"], 4)   # orden distinto cada partida
        self.botones = [Boton((660, 196 + i * 92, 580, 80), o["texto"], self.j["color"], "opcion",
                              numero=i + 1, tam=20, dato=o) for i, o in enumerate(self.opciones)]
        self.nav = Navegador(self.botones)
        self.chars = 0.0
        self.total = len(self.m["dialogo"])
        self.tiempo = self.config["tiempo"]
        self.restante = float(self.tiempo or 0)
        self.elegido = None
        self.espera = 0.0
        self.ultimo_tic = None
        self.resuelto = False

    @property
    def leido(self):
        return self.chars >= self.total

    def evento(self, ev):
        if self.elegido is not None:
            return
        if not self.leido:
            if (ev.tipo == "clic" and pygame.Rect(20, 80, 600, 556).collidepoint(ev.pos)) or es_tecla(ev, pygame.K_SPACE):
                self.chars = self.total
                return
        b = self.nav.evento(ev)
        if b:
            self.elegir(b)

    def elegir(self, b):
        self.chars = self.total
        self.elegido = b
        b.marca = "elegida"
        for o in self.botones:
            o.activo = o is b
            o.foco = False
        self.juego.audio.play("clic")
        self.espera = 0.45

    def resolver(self, opcion):
        if self.resuelto:
            return
        self.resuelto = True
        antes = L.instantanea(self.j)
        r = L.resolver_decision(self.j, self.m, opcion, self.config)
        self.juego.cambiar(EscenaResultado(self.juego, self.m, self.idx, r, antes))

    def actualizar(self, dt):
        super().actualizar(dt)
        self.chars = min(self.total, self.chars + dt * 50)
        if self.elegido is not None:
            self.espera -= dt
            if self.espera <= 0:
                self.resolver(self.elegido.dato)
            return
        if self.tiempo and self.leido:
            self.restante -= dt
            seg = math.ceil(self.restante)
            if seg <= 5 and seg != self.ultimo_tic and self.restante > 0:
                self.ultimo_tic = seg
                self.juego.audio.play("tic")
            if self.restante <= 0:
                self.juego.audio.play("tiempo")
                for o in self.botones:
                    o.activo = False
                self.resolver(None)

    def dibujar(self, s):
        G.fondo(s)
        barra_superior(s, f"MISIÓN {self.idx + 1} DE 7", self.m["habito"], self.idx, self.j)
        dibujar_escenario(s, self.m, self.idx, self.t, ANIMO[self.idx], self.m["dialogo"],
                          int(self.chars), hablando=not self.leido)
        G.panel(s, (640, 80, 620, 556))
        G.texto(s, "¿Qué haces?", (664, 98), 30, G.TEXTO, True)
        G.texto(s, "Haz clic en una opción, o usa ↑ ↓ y ENTER (atajo: 1-4).", (664, 140), 15, G.TEXTO_SUAVE)
        if self.tiempo:
            dibujar_reloj(s, (1150, 134), self.restante, self.tiempo, self.t, self.leido)
        self.dibujar_botones(s)
        if self.config["pistas"]:
            r = pygame.Rect(660, 572, 580, 50)
            pygame.draw.rect(s, (255, 246, 222), r, border_radius=12)
            G.icono(s, "bombilla", (686, r.centery), 24, G.ACENTO)
            G.texto(s, "Pista: " + self.m["pista"], (708, r.centery), 17, (120, 86, 20), True, "midleft")
        hud(s, self.j)


# ------------------------------------------------------------
# Resultado de la decisión + lección del hábito
# ------------------------------------------------------------

class EscenaResultado(Escena):
    pausable = True
    BANNERS = {"optima": ("Decisión efectiva", G.EXITO, "check"),
               "regular": ("Decisión regular", G.ADVERTENCIA, "alerta"),
               "mala": ("Decisión poco efectiva", G.PELIGRO, "x"),
               "tiempo": ("Se acabó el tiempo", G.PELIGRO, "reloj")}

    def __init__(self, juego, mision, idx, r, antes):
        super().__init__(juego)
        self.j = juego.partida.jugador()
        self.m = mision
        self.idx = idx
        self.r = r
        self.antes = antes
        self.despues = L.instantanea(self.j)
        self.valores = dict(antes)
        self.items = list(r["cambios"]) + ([("racha", r["bono"])] if r["bono"] else [])
        self.b = Boton((1030, 568, 210, 54), "Continuar", flecha="der", pulso=True)
        self.botones = [self.b]
        self.nav = Navegador(self.botones)
        self.nav.poner(0)
        if r["calidad"] == "optima":
            juego.audio.play("acierto")
        elif r["calidad"] in ("mala", "regular"):
            juego.audio.play("error")
        for ins in r["insignias"]:
            juego.toast("¡Nueva insignia!", ins, "medalla", G.ACENTO, "insignia")
        if r["subio"]:
            juego.toast("¡Subiste de nivel!", f"{self.j['nombre']} ahora es nivel {self.j['nivel']}",
                        "estrella", G.PRIMARIO, "nivel")

    def evento(self, ev):
        if self.nav.evento(ev):
            self.juego.audio.play("clic")
            self.juego.cambiar(EscenaCarta(self.juego))

    def actualizar(self, dt):
        super().actualizar(dt)
        k = max(0.0, min(1.0, (self.t - 0.3) / 0.9))
        k = 1 - (1 - k) ** 3
        for clave in self.valores:
            self.valores[clave] = self.antes[clave] + (self.despues[clave] - self.antes[clave]) * k

    def dibujar(self, s):
        G.fondo(s)
        barra_superior(s, f"MISIÓN {self.idx + 1} DE 7", self.m["habito"], self.idx, self.j)
        reac = REACCION[self.r["calidad"]]
        dibujar_escenario(s, self.m, self.idx, self.t, [reac] * len(self.m["escena"]), self.r["mensaje"])
        G.panel(s, (640, 80, 620, 556))
        titulo, color, ic = self.BANNERS[self.r["calidad"]]
        pygame.draw.rect(s, color, (640, 80, 620, 74), border_top_left_radius=18, border_top_right_radius=18)
        pygame.draw.circle(s, G.BLANCO, (684, 117), 22)
        G.icono(s, ic, (684, 117), 24, color)
        G.texto(s, titulo, (720, 117), 28, G.BLANCO, True, "midleft")
        G.texto(s, "Así cambió tu equipo:", (664, 168), 16, G.TEXTO_SUAVE, True)
        for i, (clave, delta) in enumerate(self.items):
            if self.t < 0.25 + 0.12 * i:
                continue
            x = 664 + (i % 2) * 290
            y = 196 + (i // 2) * 36
            if clave == "puntos":
                nombre, col, icon = "Puntos", G.ACENTO, "trofeo"
            elif clave == "racha":
                nombre, col, icon = "Bono de racha", G.ADVERTENCIA, "fuego"
            else:
                nombre, col = C.HABILIDADES[clave]
                icon = clave
            G.icono(s, icon, (x + 12, y + 13), 22, col)
            G.texto(s, nombre, (x + 32, y + 2), 18, G.TEXTO)
            G.pastilla(s, f"{delta:+d}", (x + 270, y), G.EXITO if delta > 0 else G.PELIGRO, 15, ancla="topright")
        if not self.items:
            G.texto(s, "Sin cambios esta vez.", (664, 200), 18, G.TEXTO_SUAVE)
        y = 196 + ((len(self.items) + 1) // 2) * 36 + 14
        if self.r["mejor"]:
            alto = 34 + G.alto_parrafo(self.r["mejor"], 540, 18, True)
            pygame.draw.rect(s, (230, 240, 255), (660, y, 580, alto), border_radius=12)
            G.texto(s, "La decisión más efectiva era:", (678, y + 9), 14, G.PRIMARIO, True)
            G.parrafo(s, self.r["mejor"], (678, y + 28), 540, 18, G.TEXTO, True)
            y += alto + 10
        alto_l = 556 - y
        pygame.draw.rect(s, G.PANEL_2, (660, y, 580, alto_l), border_radius=12)
        G.icono(s, "libro", (686, y + 24), 24, G.MORADO)
        G.texto(s, "Lección: " + self.m["habito"], (708, y + 13), 17, G.MORADO, True)
        G.parrafo(s, self.m["leccion"], (680, y + 44), 540, 18, G.TEXTO)
        self.dibujar_botones(s)
        G.texto(s, "ENTER para continuar", (1018, 595), 13, G.TEXTO_SUAVE, False, "midright")
        hud(s, self.j, self.valores)


# ------------------------------------------------------------
# Pregunta (para el Reto Relámpago y el desempate)
# ------------------------------------------------------------

class Pregunta:
    def __init__(self, juego, pregunta, tiempo, x, y, ancho):
        self.juego = juego
        self.enunciado, self.ops, self.correcta = pregunta
        self.x, self.y, self.ancho = x, y, ancho
        self.alto_enunciado = G.alto_parrafo(self.enunciado, ancho - 170, 24, True)
        y0 = y + max(self.alto_enunciado, 70) + 22
        self.botones = [Boton((x, y0 + i * 76, ancho, 64), op, G.MORADO, "opcion", numero=i + 1, tam=20)
                        for i, op in enumerate(self.ops)]
        self.nav = Navegador(self.botones)
        self.tiempo = tiempo
        self.restante = float(tiempo or 0)
        self.ultimo_tic = None
        self.respondida = False
        self.resultado = None
        self.t = 0.0

    def evento(self, ev):
        if self.respondida:
            return
        b = self.nav.evento(ev)
        if b:
            self.responder(self.botones.index(b))

    def responder(self, i):
        self.respondida = True
        for b in self.botones:
            b.activo = False
            b.foco = False
        self.botones[self.correcta].marca = "correcta"
        if i is not None and i != self.correcta:
            self.botones[i].marca = "incorrecta"
        self.resultado = (i == self.correcta)
        if i is None:
            self.juego.audio.play("tiempo")
        else:
            self.juego.audio.play("acierto" if self.resultado else "error")

    def actualizar(self, dt):
        self.t += dt
        for b in self.botones:
            b.actualizar(dt, self.juego.mouse)
        if self.tiempo and not self.respondida:
            self.restante -= dt
            seg = math.ceil(self.restante)
            if seg <= 5 and seg != self.ultimo_tic and self.restante > 0:
                self.ultimo_tic = seg
                self.juego.audio.play("tic")
            if self.restante <= 0:
                self.responder(None)

    def dibujar(self, s):
        G.parrafo(s, self.enunciado, (self.x, self.y), self.ancho - 170, 24, G.TEXTO, True)
        if self.tiempo:
            dibujar_reloj(s, (self.x + self.ancho - 86, self.y + 36), self.restante, self.tiempo, self.t, True)
        for b in self.botones:
            b.dibujar(s, self.t)


# ------------------------------------------------------------
# Carta de evento: bonificación, penalización o reto relámpago
# ------------------------------------------------------------

class EscenaCarta(Escena):
    pausable = True
    TIPOS = {"bonificacion": ("Bonificación", G.EXITO, "estrella"),
             "penalizacion": ("Penalización", G.PELIGRO, "alerta"),
             "reto": ("Reto Relámpago", G.MORADO, "productividad")}

    def __init__(self, juego):
        super().__init__(juego)
        p = juego.partida
        self.j = p.jugador()
        self.idx = p.mision_idx
        self.config = p.config
        self.tipo, self.carta = L.sacar_carta()
        self.estado = "oculta"
        self.anim = 0.0
        self.aplicado = False
        self.cambios = []
        self.antes = L.instantanea(self.j)
        self.valores = dict(self.antes)
        self.t_cambio = 0.0
        self.b_voltear = Boton((540, 562, 200, 54), "Voltear carta", G.MORADO, icono="carta", pulso=True)
        self.b_cont = Boton((1040, 572, 200, 54), "Continuar", flecha="der", pulso=True)
        self.b_cont.visible = False
        self.niveles = [Boton((190 + i * 310, 230, 280, 280), "", G.MORADO, "claro", dato=n, radio=20)
                        for i, n in enumerate(C.NIVELES_RETO)]
        for b in self.niveles:
            b.visible = False
        self.botones = [self.b_voltear, self.b_cont] + self.niveles
        self.nav = Navegador([self.b_voltear])
        self.nav.poner(0)
        self.pregunta = None
        self.nivel = None

    def rect_carta(self):
        return pygame.Rect(490, 104, 300, 420)

    # -- transiciones --
    def voltear(self):
        self.juego.audio.play("carta")
        self.estado = "volteando"
        self.anim = 0.0
        self.b_voltear.visible = False

    def mostrar_continuar(self):
        self.b_cont.visible = True
        self.nav = Navegador([self.b_cont])
        self.nav.poner(0)

    def aplicar(self):
        self.aplicado = True
        if self.tipo == "reto":
            return
        self.antes = L.instantanea(self.j)
        self.cambios, subio = L.resolver_carta(self.j, self.carta, self.config)
        self.despues = L.instantanea(self.j)
        self.t_cambio = self.t
        self.juego.audio.play("acierto" if self.tipo == "bonificacion" else "error")
        if subio:
            self.juego.toast("¡Subiste de nivel!", f"Ahora eres nivel {self.j['nivel']}", "estrella",
                             G.PRIMARIO, "nivel")

    def elegir_nivel(self, b):
        self.juego.audio.play("clic")
        self.nivel = b.dato
        for n in self.niveles:
            n.visible = False
        self.pregunta = Pregunta(self.juego, L.pregunta_al_azar(self.nivel["clave"]),
                                 self.config["tiempo"], 190, 176, 900)
        self.estado = "reto_pregunta"
        self.nav = Navegador([])

    def terminar_reto(self):
        self.antes = L.instantanea(self.j)
        self.cambios, insignias, subio = L.resolver_reto(self.j, self.nivel, self.pregunta.resultado, self.config)
        self.despues = L.instantanea(self.j)
        self.t_cambio = self.t
        for ins in insignias:
            self.juego.toast("¡Nueva insignia!", ins, "medalla", G.ACENTO, "insignia")
        if subio:
            self.juego.toast("¡Subiste de nivel!", f"Ahora eres nivel {self.j['nivel']}", "estrella",
                             G.PRIMARIO, "nivel")
        self.estado = "reto_fin"
        self.mostrar_continuar()

    # -- bucle --
    def evento(self, ev):
        if self.estado == "oculta":
            if ((ev.tipo == "clic" and (self.b_voltear.clic(ev.pos) or self.rect_carta().collidepoint(ev.pos)))
                    or es_tecla(ev, pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)):
                self.voltear()
        elif self.estado == "reto_nivel":
            b = self.nav.evento(ev)
            if b:
                self.elegir_nivel(b)
        elif self.estado == "reto_pregunta":
            self.pregunta.evento(ev)
        elif self.b_cont.visible:
            if self.nav.evento(ev):
                self.juego.audio.play("clic")
                self.juego.turno_terminado()

    def actualizar(self, dt):
        super().actualizar(dt)
        if self.estado == "volteando":
            self.anim += dt / 0.5
            if self.anim >= 0.5 and not self.aplicado:
                self.aplicar()
            if self.anim >= 1:
                self.anim = 1
                if self.tipo == "reto":
                    self.estado = "reto_intro"
                    self.t_intro = self.t
                else:
                    self.estado = "frente"
                    self.mostrar_continuar()
        elif self.estado == "reto_intro" and self.t - self.t_intro > 0.9:
            self.estado = "reto_nivel"
            for b in self.niveles:
                b.visible = True
            self.nav = Navegador(self.niveles, horizontal=True)
            self.nav.poner(0)
        elif self.estado == "reto_pregunta":
            self.pregunta.actualizar(dt)
            if self.pregunta.respondida:
                if not hasattr(self, "t_resp"):
                    self.t_resp = self.t
                elif self.t - self.t_resp > 0.6:
                    self.terminar_reto()
        if self.cambios or self.estado in ("frente", "reto_fin"):
            if hasattr(self, "despues"):
                k = max(0.0, min(1.0, (self.t - self.t_cambio - 0.2) / 0.8))
                k = 1 - (1 - k) ** 3
                for c in self.valores:
                    self.valores[c] = self.antes[c] + (self.despues[c] - self.antes[c]) * k

    # -- dibujo --
    def superficie_carta(self, frente):
        w, h = 300, 420
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        if not frente:
            pygame.draw.rect(sup, (34, 50, 92), (0, 0, w, h), border_radius=22)
            pygame.draw.rect(sup, G.ACENTO, (10, 10, w - 20, h - 20), 3, border_radius=16)
            for k in range(6):
                d = 30 + k * 26
                pygame.draw.polygon(sup, (52, 72, 122), [(w / 2, h / 2 - d), (w / 2 + d * 0.75, h / 2),
                                                         (w / 2, h / 2 + d), (w / 2 - d * 0.75, h / 2)], 2)
            G.estrella(sup, (w / 2, h / 2), 34, G.ACENTO)
            G.texto(sup, "M7", (w / 2, h - 50), 22, G.ACENTO, True, "center")
            return sup
        nombre, color, ic = self.TIPOS[self.tipo]
        pygame.draw.rect(sup, G.BLANCO, (0, 0, w, h), border_radius=22)
        pygame.draw.rect(sup, color, (0, 0, w, 96), border_top_left_radius=22, border_top_right_radius=22)
        pygame.draw.rect(sup, color, (0, 0, w, h), 4, border_radius=22)
        pygame.draw.circle(sup, G.BLANCO, (w // 2, 96), 38)
        G.icono(sup, ic, (w // 2, 96), 40, color)
        G.texto(sup, nombre.upper(), (w // 2, 30), 22, G.BLANCO, True, "center")
        if self.tipo == "reto":
            G.parrafo(sup, "Elige cuánto arriesgar y responde una pregunta sobre Los 7 Hábitos.",
                      (24, 160), w - 48, 19, G.TEXTO, centrado=True)
        else:
            y = G.parrafo(sup, self.carta[0], (24, 152), w - 48, 20, G.TEXTO, True, centrado=True)
            y += 14
            for clave, delta in self.cambios:
                if clave == "puntos":
                    nom, col, icn = "Puntos", G.ACENTO, "trofeo"
                else:
                    (nom, col), icn = C.HABILIDADES[clave], clave
                G.icono(sup, icn, (52, y + 12), 22, col)
                G.texto(sup, nom, (72, y + 2), 18, G.TEXTO)
                G.pastilla(sup, f"{delta:+d}", (w - 28, y), G.EXITO if delta > 0 else G.PELIGRO, 15, ancla="topright")
                y += 36
            if not self.cambios:
                G.texto(sup, "(sin efecto: ya estabas al límite)", (w // 2, y + 6), 14, G.TEXTO_SUAVE, False, "midtop")
        return sup

    def dibujar_carta(self, s):
        r = self.rect_carta()
        if self.estado == "oculta":
            r = r.move(0, int(math.sin(self.t * 2.5) * 5))
            sup = self.superficie_carta(False)
            escala = 1.0
        elif self.estado == "volteando":
            frente = self.anim >= 0.5
            sup = self.superficie_carta(frente)
            escala = abs(math.cos(self.anim * math.pi))
        else:
            sup = self.superficie_carta(True)
            escala = 1.0
        w = max(2, int(r.w * escala))
        if w != r.w:
            sup = pygame.transform.smoothscale(sup, (w, r.h))
        s.blit(G._sombra(w, r.h, 22), (r.centerx - w // 2 - 12, r.y - 12))
        s.blit(sup, (r.centerx - w // 2, r.y))

    def dibujar(self, s):
        G.fondo(s)
        barra_superior(s, f"MISIÓN {self.idx + 1} DE 7  ·  CARTA DE EVENTO",
                       "¡Saca tu carta!", self.idx, self.j)
        if self.estado in ("oculta", "volteando", "frente", "reto_intro"):
            G.texto(s, "Después de cada misión", (90, 150), 18, G.TEXTO_CLARO)
            G.texto(s, "sale una carta al azar:", (90, 176), 18, G.TEXTO_CLARO)
            for k, clave in enumerate(["bonificacion", "penalizacion", "reto"]):
                nombre, color, ic = self.TIPOS[clave]
                y = 226 + k * 58
                pygame.draw.circle(s, color, (110, y + 16), 20)
                G.icono(s, ic, (110, y + 16), 22, G.BLANCO)
                G.texto(s, nombre, (142, y + 4), 20, G.BLANCO, True)
            if self.estado == "oculta":
                G.texto(s, "Haz clic en la carta", (1010, 280), 20, G.BLANCO, True, "midtop")
                G.texto(s, "o presiona ENTER", (1010, 308), 18, G.TEXTO_CLARO, False, "midtop")
                desliz = int(math.sin(self.t * 5) * 6)
                G.flecha(s, (880 + desliz, 300), 46, G.ACENTO, "izq")
            self.dibujar_carta(s)
        else:
            G.panel(s, (140, 84, 1000, 552))
            G.icono(s, "productividad", (186, 126), 32, G.MORADO)
            G.texto(s, "Reto Relámpago", (210, 106), 32, G.MORADO, True)
            if self.estado == "reto_nivel":
                G.texto(s, "Elige cuánto quieres arriesgar ANTES de ver la pregunta.", (190, 160), 19, G.TEXTO)
                for b in self.niveles:
                    b.dibujar(s, self.t)
                    n = b.dato
                    r = b.rect.move(0, -int(2 * b.hover))
                    G.texto(s, n["nombre"], (r.centerx, r.y + 26), 30, G.TEXTO, True, "midtop")
                    for k in range(3):
                        col = G.MORADO if k <= C.NIVELES_RETO.index(n) else G.LINEA
                        pygame.draw.rect(s, col, (r.centerx - 50 + k * 36, r.y + 76, 28, 10), border_radius=5)
                    G.texto(s, "Si aciertas", (r.centerx, r.y + 112), 16, G.TEXTO_SUAVE, True, "midtop")
                    G.texto(s, f"+{n['gana']} pts", (r.centerx, r.y + 134), 30, G.EXITO, True, "midtop")
                    G.texto(s, "Si fallas", (r.centerx, r.y + 182), 16, G.TEXTO_SUAVE, True, "midtop")
                    if n["pierde"]:
                        G.texto(s, f"-{n['pierde']} pts", (r.centerx, r.y + 204), 30, G.PELIGRO, True, "midtop")
                    else:
                        G.texto(s, "No pierdes", (r.centerx, r.y + 210), 22, G.TEXTO_SUAVE, True, "midtop")
                    G.texto(s, f"Tecla {C.NIVELES_RETO.index(n) + 1}", (r.centerx, r.bottom - 22), 13,
                            G.TEXTO_SUAVE, True, "center")
                G.texto(s, "← → moverte   ·   ENTER elegir   ·   o haz clic", (640, 548), 15,
                        G.TEXTO_SUAVE, False, "midtop")
            else:
                G.pastilla(s, f"Nivel {self.nivel['nombre']}: +{self.nivel['gana']} / -{self.nivel['pierde']}",
                           (1110, 108), G.MORADO, 15, ancla="topright")
                self.pregunta.dibujar(s)
                if self.estado == "reto_fin":
                    bien = self.pregunta.resultado
                    delta = sum(d for c, d in self.cambios if c == "puntos")
                    if bien:
                        msg, col = f"¡Correcto!  {delta:+d} puntos", G.EXITO
                    elif self.nivel["pierde"]:
                        msg, col = f"Incorrecto.  {delta:+d} puntos", G.PELIGRO
                    else:
                        msg, col = "Incorrecto, pero en Fácil no pierdes puntos.", G.ADVERTENCIA
                    G.icono(s, "check" if bien else "x", (206, 594), 26, col)
                    G.texto(s, msg, (230, 594), 24, col, True, "midleft")
        self.b_voltear.dibujar(s, self.t)
        self.b_cont.dibujar(s, self.t)
        hud(s, self.j, self.valores)


# ------------------------------------------------------------
# Resumen final de cada jugador
# ------------------------------------------------------------

class EscenaResumen(Escena):
    def __init__(self, juego, i, nuevas):
        super().__init__(juego)
        p = juego.partida
        self.i = i
        self.j = p.jugadores[i]
        self.cumplida, self.rango, self.prom = L.evaluar(self.j)
        ultimo = i == len(p.jugadores) - 1
        if not ultimo:
            txt = "Siguiente jugador"
        elif len(p.jugadores) > 1:
            txt = "Ver podio"
        else:
            txt = "Menú principal"
        self.b = Boton((936, 566, 228, 54), txt, flecha="der", pulso=True)
        self.botones = [self.b]
        self.nav = Navegador(self.botones)
        self.nav.poner(0)
        self.confeti = G.Confeti()
        if self.cumplida:
            self.confeti.lanzar()
            juego.audio.play("victoria")
        else:
            juego.audio.play("derrota")
        for ins in nuevas:
            juego.toast("¡Insignia legendaria!", ins, "medalla", G.ACENTO, "insignia")

    def evento(self, ev):
        if self.nav.evento(ev):
            self.juego.audio.play("clic")
            self.juego.resumen_siguiente(self.i)

    def actualizar(self, dt):
        super().actualizar(dt)
        self.confeti.actualizar(dt)

    def dibujar(self, s):
        G.fondo(s)
        G.panel(s, (100, 70, 1080, 566))
        G.texto(s, f"RESULTADO DE {self.j['nombre'].upper()}", (130, 92), 15, G.TEXTO_SUAVE, True)
        if self.cumplida:
            G.pastilla(s, "¡MISIÓN CUMPLIDA!", (130, 118), G.EXITO, 18)
        else:
            G.pastilla(s, "MISIÓN NO CUMPLIDA", (130, 118), G.PELIGRO, 18)
            G.texto(s, f"Meta: {C.META_PUNTOS} pts y promedio {C.PROMEDIO_MINIMO}+", (350, 124), 14, G.TEXTO_SUAVE)
        color_rango = {"Líder Altamente Efectivo": G.ACENTO, "Líder Efectivo": G.EXITO,
                       "Líder en Formación": G.PRIMARIO, "Equipo en Riesgo": G.PELIGRO}[self.rango]
        G.icono(s, "medalla", (162, 196), 60, color_rango)
        G.texto(s, self.rango, (204, 172), 32, G.TEXTO, True)
        G.texto(s, f"Dificultad: {self.juego.partida.config['nombre']}", (206, 212), 16, G.TEXTO_SUAVE)
        datos = [("Puntos", self.j["puntos"]), ("Nivel", self.j["nivel"]),
                 ("Promedio", self.prom), ("Efectivas", f"{self.j['optimas']}/7")]
        for k, (nom, val) in enumerate(datos):
            r = pygame.Rect(130 + k * 118, 244, 108, 66)
            pygame.draw.rect(s, G.PANEL_2, r, border_radius=12)
            G.texto(s, str(val), (r.centerx, r.y + 8), 26, G.TEXTO, True, "midtop")
            G.texto(s, nom, (r.centerx, r.y + 42), 13, G.TEXTO_SUAVE, True, "midtop")
        for k, (clave, (nom, col)) in enumerate(C.HABILIDADES.items()):
            y = 334 + k * 42
            G.icono(s, clave, (142, y + 14), 22, col)
            G.texto(s, nom, (162, y), 16, G.TEXTO, True)
            G.texto(s, str(self.j[clave]), (590, y), 16, G.TEXTO, True, "topright")
            G.barra(s, (162, y + 22, 428, 11), self.j[clave], col)
        G.texto(s, f"Insignias ({len(self.j['insignias'])}/{len(C.INSIGNIAS)})", (640, 92), 18, G.TEXTO, True)
        for k, (nom, desc) in enumerate(C.INSIGNIAS):
            x = 640 + (k % 2) * 262
            y = 124 + (k // 2) * 72
            tiene = nom in self.j["insignias"]
            r = pygame.Rect(x, y, 252, 62)
            pygame.draw.rect(s, (255, 248, 226) if tiene else G.PANEL_2, r, border_radius=12)
            if tiene:
                G.icono(s, "medalla", (x + 28, y + 30), 34, G.ACENTO)
            else:
                G.icono(s, "candado", (x + 28, y + 31), 24, G.GRIS)
            G.parrafo(s, nom, (x + 52, y + 8), 196, 14, G.TEXTO if tiene else G.GRIS, True, 1.05)
            G.texto(s, desc, (x + 52, y + 42), 11, G.TEXTO_SUAVE if tiene else G.GRIS)
        r = pygame.Rect(130, 510, 790, 100)
        pygame.draw.rect(s, (255, 246, 222), r, border_radius=12)
        G.icono(s, "bombilla", (160, r.y + 30), 28, G.ACENTO)
        debil = L.habilidad_debil(self.j)
        G.texto(s, f"Consejo: tu habilidad más baja es {C.HABILIDADES[debil][0]}.", (184, r.y + 16), 17,
                (120, 86, 20), True)
        G.parrafo(s, C.CONSEJOS[debil], (184, r.y + 44), 720, 17, G.TEXTO)
        self.dibujar_botones(s)
        self.confeti.dibujar(s)


# ------------------------------------------------------------
# Desempate por muerte súbita
# ------------------------------------------------------------

class EscenaDesempate(Escena):
    def __init__(self, juego, empatados, orden):
        super().__init__(juego)
        self.vivos = list(empatados)
        self.orden = orden
        self.ronda = 0
        self.mazo = []
        self.b = Boton((930, 566, 210, 54), "Siguiente", flecha="der", pulso=True)
        self.botones = [self.b]
        self.nueva_ronda()

    def nueva_ronda(self):
        self.ronda += 1
        if not self.mazo:
            self.mazo = list(C.PREGUNTAS["dificil"])
            random.shuffle(self.mazo)
        self.q = self.mazo.pop()
        self.turno = 0
        self.aciertan = []
        self.mensaje = None
        self.preparar()

    def preparar(self):
        self.preg = Pregunta(self.juego, self.q, None, 190, 200, 900)
        self.b.visible = False

    def evento(self, ev):
        if self.b.visible:
            if (ev.tipo == "clic" and self.b.clic(ev.pos)) or es_tecla(ev, pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                self.juego.audio.play("clic")
                self.avanzar()
        else:
            self.preg.evento(ev)

    def avanzar(self):
        if self.mensaje is not None:
            if self.ganador is not None or self.ronda >= 10:
                self.juego.mostrar_podio(self.orden, self.ganador)
            else:
                self.nueva_ronda()
            return
        if self.preg.resultado:
            self.aciertan.append(self.vivos[self.turno])
        self.turno += 1
        if self.turno < len(self.vivos):
            self.preparar()
            return
        self.ganador = None
        if len(self.aciertan) == 1:
            self.ganador = self.aciertan[0]
            self.mensaje = f"¡{self.ganador['nombre']} acertó en solitario y gana el desempate!"
        else:
            if self.aciertan:
                self.vivos = self.aciertan
            if self.ronda >= 10:
                self.mensaje = "Tras 10 rondas sigue el empate: ¡victoria compartida!"
            else:
                self.mensaje = "Nadie quedó solo. ¡Otra ronda con una nueva pregunta!"
        self.b.visible = True

    def actualizar(self, dt):
        super().actualizar(dt)
        if self.mensaje is None:
            self.preg.actualizar(dt)
            if self.preg.respondida:
                self.b.visible = True

    def dibujar(self, s):
        G.fondo(s)
        G.panel(s, (140, 70, 1000, 566))
        G.texto(s, f"MUERTE SÚBITA  ·  RONDA {self.ronda}", (190, 92), 16, G.PELIGRO, True)
        G.texto(s, "Empate en el primer lugar: gana quien acierte en solitario.", (190, 116), 17, G.TEXTO_SUAVE)
        if self.mensaje:
            G.parrafo(s, self.mensaje, (190, 260), 900, 30, G.TEXTO, True, centrado=True)
        else:
            j = self.vivos[self.turno]
            G.pastilla(s, f"Turno de {j['nombre']}", (190, 150), j["color"], 18)
            self.preg.dibujar(s)
            G.texto(s, "Haz clic en una respuesta o usa las teclas 1 a 3.", (190, 560), 15, G.TEXTO_SUAVE)
        self.dibujar_botones(s)


# ------------------------------------------------------------
# Podio final (multijugador)
# ------------------------------------------------------------

class EscenaPodio(Escena):
    def __init__(self, juego, orden, ganador):
        super().__init__(juego)
        self.orden = orden
        self.ganador = ganador
        self.b_menu = Boton((80, 600, 230, 54), "Menú principal", estilo="claro", flecha="izq")
        self.b_otra = Boton((970, 600, 230, 54), "Jugar otra vez", flecha="der", pulso=True)
        self.botones = [self.b_menu, self.b_otra]
        self.nav = Navegador(self.botones, horizontal=True)
        self.nav.poner(1)
        self.confeti = G.Confeti()
        self.confeti.lanzar(180)
        juego.audio.play("victoria")

    def evento(self, ev):
        b = self.nav.evento(ev)
        if b is self.b_menu or es_tecla(ev, pygame.K_ESCAPE):
            self.juego.cambiar(EscenaMenu(self.juego))
        elif b is self.b_otra:
            self.juego.cambiar(EscenaJugadores(self.juego))

    def actualizar(self, dt):
        super().actualizar(dt)
        self.confeti.actualizar(dt)
        if int(self.t) % 4 == 3 and len(self.confeti.p) < 30:
            self.confeti.lanzar(60)

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "PODIO FINAL", (640, 70), 40, G.BLANCO, True, "midtop")
        if self.ganador:
            G.texto(s, f"¡{self.ganador['nombre']} es quien mejor lideró la partida!", (640, 122), 22,
                    G.ACENTO, True, "midtop")
        else:
            G.texto(s, "¡Empate compartido! Lideraron igual de bien.", (640, 122), 22, G.ACENTO, True, "midtop")
        lugares = [(640, 230, G.ACENTO), (380, 160, (190, 196, 210)), (900, 110, (205, 140, 90))]
        for k, j in enumerate(self.orden[:3]):
            x, h, col = lugares[k]
            base = 570
            r = pygame.Rect(x - 110, base - h, 220, h)
            pygame.draw.rect(s, col, r, border_top_left_radius=14, border_top_right_radius=14)
            G.texto(s, str(k + 1), (x, r.y + 16), 46, G.BLANCO, True, "midtop")
            G.texto(s, f"{j['puntos']} pts", (x, r.y + 74), 20, G.BLANCO, True, "midtop")
            cy = r.y - 96 + int(math.sin(self.t * 2 + k) * 4)
            pygame.draw.circle(s, G.BLANCO, (x, cy), 48)
            pygame.draw.circle(s, j["color"], (x, cy), 43)
            G.texto(s, j["nombre"][0].upper(), (x, cy), 44, G.BLANCO, True, "center")
            G.texto(s, j["nombre"], (x, cy + 54), 20, G.BLANCO, True, "midtop")
            if k == 0:
                G.icono(s, "liderazgo", (x, cy - 70), 48, G.ACENTO)
        if len(self.orden) > 3:
            j = self.orden[3]
            G.texto(s, f"4.º lugar: {j['nombre']} ({j['puntos']} pts)", (640, 584), 18, G.TEXTO_CLARO, True, "midtop")
        self.dibujar_botones(s)
        self.confeti.dibujar(s)


# ------------------------------------------------------------
# Pantallas informativas del menú
# ------------------------------------------------------------

class EscenaInfo(Escena):
    """Base con botón Volver y tecla ESC."""

    def __init__(self, juego):
        super().__init__(juego)
        self.b_volver = Boton((80, 600, 200, 54), "Volver", estilo="claro", flecha="izq")
        self.botones = [self.b_volver]

    def volver(self):
        self.juego.audio.play("clic")
        self.juego.cambiar(EscenaMenu(self.juego))

    def evento(self, ev):
        if es_tecla(ev, pygame.K_ESCAPE, pygame.K_BACKSPACE) or (ev.tipo == "clic" and self.b_volver.clic(ev.pos)):
            self.volver()


class EscenaComoJugar(EscenaInfo):
    PAGINAS = [
        ("El objetivo", "Eres el líder de un equipo universitario que debe terminar un proyecto. "
                        "Supera 7 misiones, una por cada hábito de Stephen Covey, tomando las "
                        "decisiones más efectivas para tu equipo."),
        ("Las misiones", "En cada misión lees una situación y eliges 1 de 4 decisiones: con el ratón, "
                         "con las flechas ↑ ↓ y ENTER, o con las teclas 1 a 4. Cada decisión cambia "
                         "tu liderazgo, comunicación, empatía y productividad. Después verás la lección "
                         "del hábito."),
        ("El reloj de arena", "En las dificultades Líder y Líder Experto tienes un tiempo límite. El reloj "
                              "empieza cuando terminas de leer. En los últimos 5 segundos escucharás un "
                              "tic-tac. Si se acaba el tiempo, el equipo pierde productividad."),
        ("Cartas de evento", "Después de cada misión volteas una carta al azar: Bonificación (premio), "
                             "Penalización (castigo) o Reto Relámpago. En el reto eliges cuánto arriesgar "
                             "ANTES de ver la pregunta: Fácil +10/0, Medio +20/-10, Difícil +40/-20."),
        ("Puntos, rachas e insignias", "Las decisiones efectivas seguidas forman una racha con bono de puntos. "
                                       "Cada 100 puntos subes de nivel. Hay 10 insignias por descubrir. "
                                       "Los puntos nunca bajan de 0 y las habilidades van de 0 a 100."),
        ("Cómo se gana", f"Cumples la misión si terminas con {C.META_PUNTOS} puntos o más y un promedio "
                         f"de habilidades de {C.PROMEDIO_MINIMO} o más. En multijugador gana quien tenga "
                         "más puntos; si hay empate, se define con muerte súbita de preguntas difíciles."),
    ]

    def __init__(self, juego):
        super().__init__(juego)
        self.pag = 0
        self.r_voz = None
        self.voz_iniciada = False
        self.b_ant = Boton((720, 600, 200, 54), "Anterior", estilo="claro", flecha="izq")
        self.b_sig = Boton((1000, 600, 200, 54), "Siguiente", flecha="der", pulso=True)
        self.botones += [self.b_ant, self.b_sig]

    def mover(self, d):
        nueva = self.pag + d
        if nueva >= len(self.PAGINAS):
            self.volver()
        elif nueva >= 0:
            self.pag = nueva
            self.juego.audio.play("clic")
            self.juego.audio.hablar(f"como_jugar_{self.pag + 1}")

    def evento(self, ev):
        if ev.tipo == "clic" and self.r_voz and self.r_voz.collidepoint(ev.pos):
            self.juego.audio.hablar(f"como_jugar_{self.pag + 1}")
            return
        if es_tecla(ev, pygame.K_r):
            self.juego.audio.hablar(f"como_jugar_{self.pag + 1}")
            return
        super().evento(ev)
        if (ev.tipo == "clic" and self.b_sig.clic(ev.pos)) or es_tecla(ev, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE):
            self.mover(1)
        elif (ev.tipo == "clic" and self.b_ant.clic(ev.pos)) or es_tecla(ev, pygame.K_LEFT):
            self.mover(-1)

    def actualizar(self, dt):
        super().actualizar(dt)
        if not self.voz_iniciada and self.t > 0.3:     # tras la transición de entrada
            self.voz_iniciada = True
            self.juego.audio.hablar("como_jugar_1")
        self.b_ant.activo = self.pag > 0
        self.b_sig.txt = "Entendido" if self.pag == len(self.PAGINAS) - 1 else "Siguiente"

    def ilustracion(self, s, r):
        cx, cy = r.center
        p = self.pag
        if p == 0:
            for k, pid in enumerate(C.EQUIPO):
                G.personaje(s, r.x + 70 + k * 100, r.bottom - 30, 0.82, C.PERSONAJES[pid], "feliz", self.t)
            G.icono(s, "trofeo", (cx, r.y + 90), 90, G.ACENTO)
        elif p == 1:
            for k in range(4):
                b = pygame.Rect(r.x + 40, r.y + 70 + k * 78, r.w - 80, 60)
                activo = k == int(self.t) % 4
                pygame.draw.rect(s, (230, 240, 255) if activo else G.BLANCO, b, border_radius=12)
                pygame.draw.rect(s, G.PRIMARIO if activo else G.LINEA, b, 3 if activo else 2, border_radius=12)
                pygame.draw.circle(s, G.PRIMARIO, (b.x + 30, b.centery), 16)
                G.texto(s, str(k + 1), (b.x + 30, b.centery), 16, G.BLANCO, True, "center")
                pygame.draw.rect(s, G.LINEA, (b.x + 60, b.centery - 6, b.w - 120, 12), border_radius=6)
                if activo:
                    G.flecha(s, (b.right - 26, b.centery), 22, G.PRIMARIO, "der")
        elif p == 2:
            fr = 1 - (self.t % 8) / 8
            G.reloj_arena(s, (cx, cy), 260, fr, self.t, fr < 0.3)
        elif p == 3:
            for k, (col, ic) in enumerate([(G.EXITO, "estrella"), (G.PELIGRO, "alerta"), (G.MORADO, "productividad")]):
                ang = (k - 1) * 0.28
                c = pygame.Surface((130, 180), pygame.SRCALPHA)
                pygame.draw.rect(c, G.BLANCO, (0, 0, 130, 180), border_radius=14)
                pygame.draw.rect(c, col, (0, 0, 130, 180), 4, border_radius=14)
                pygame.draw.rect(c, col, (0, 0, 130, 46), border_top_left_radius=14, border_top_right_radius=14)
                G.icono(c, ic, (65, 104), 50, col)
                c = pygame.transform.rotozoom(c, -math.degrees(ang), 1)
                s.blit(c, c.get_rect(center=(cx + (k - 1) * 110, cy + abs(k - 1) * 20)))
        elif p == 4:
            G.icono(s, "fuego", (cx - 110, cy - 40), 90, G.ADVERTENCIA)
            G.icono(s, "medalla", (cx + 10, cy - 40), 100, G.ACENTO)
            G.icono(s, "estrella", (cx + 130, cy - 40), 90, G.PRIMARIO)
            G.texto(s, "Racha  ·  Insignias  ·  Nivel", (cx, cy + 70), 18, G.TEXTO_SUAVE, True, "midtop")
        else:
            G.icono(s, "trofeo", (cx, cy - 60), 120, G.ACENTO)
            G.texto(s, f"{C.META_PUNTOS} pts", (cx, cy + 40), 44, G.TEXTO, True, "midtop")
            G.texto(s, f"+ promedio {C.PROMEDIO_MINIMO}", (cx, cy + 96), 22, G.TEXTO_SUAVE, True, "midtop")

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "CÓMO JUGAR", (640, 30), 16, G.ACENTO, True, "midtop")
        G.panel(s, (80, 70, 1120, 500))
        r = pygame.Rect(110, 100, 460, 440)
        pygame.draw.rect(s, G.PANEL_2, r, border_radius=16)
        self.ilustracion(s, r)
        titulo, cuerpo = self.PAGINAS[self.pag]
        G.texto(s, f"{self.pag + 1} / {len(self.PAGINAS)}", (610, 112), 15, G.TEXTO_SUAVE, True)
        self.r_voz = boton_voz(s, self.juego, (1150, 120), f"como_jugar_{self.pag + 1}", self.t)
        if self.r_voz:
            G.texto(s, "Escuchar (R)", (1124, 120), 13, G.TEXTO_SUAVE, True, "midright")
        G.texto(s, titulo, (610, 136), 34, G.TEXTO, True)
        G.parrafo(s, cuerpo, (610, 196), 560, 22, G.TEXTO, interlineado=1.4)
        for i in range(len(self.PAGINAS)):
            col = G.ACENTO if i == self.pag else (90, 106, 140)
            pygame.draw.circle(s, col, (520 + i * 24, 627), 7 if i == self.pag else 5)
        self.dibujar_botones(s)
        ayuda(s, "← → cambiar de página   ·   ESC volver", 714)


class EscenaMapa(EscenaInfo):
    def __init__(self, juego):
        super().__init__(juego)
        self.sobre = None
        self.rects = []
        for i in range(len(C.MISIONES)):
            fila, col = divmod(i, 4)
            ancho = 280
            x0 = 60 if fila == 0 else 60 + ancho // 2 + 10
            self.rects.append(pygame.Rect(x0 + col * (ancho + 20), 110 + fila * 236, ancho, 216))
        self.con_voz = any(juego.audio.hay_voz(f"mision_{i + 1}") for i in range(len(C.MISIONES)))

    def evento(self, ev):
        if ev.tipo in ("mover", "clic"):
            actual = next((i for i, r in enumerate(self.rects) if r.collidepoint(ev.pos)), None)
            if actual is not None and (actual != self.sobre or ev.tipo == "clic"):
                self.juego.audio.hablar(f"mision_{actual + 1}")
            self.sobre = actual
        super().evento(ev)

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "MAPA DE MISIONES", (640, 26), 34, G.BLANCO, True, "midtop")
        G.texto(s, "Una misión por cada uno de Los 7 Hábitos de Stephen Covey", (640, 70), 16,
                G.TEXTO_CLARO, False, "midtop")
        for i, m in enumerate(C.MISIONES):
            fila, col = divmod(i, 4)
            ancho = 280
            x0 = 60 if fila == 0 else 60 + ancho // 2 + 10
            r = self.rects[i]
            G.panel(s, r)
            if i == self.sobre:
                pygame.draw.rect(s, G.ACENTO, r.inflate(8, 8), 4, border_radius=22)
            if self.juego.audio.hay_voz(f"mision_{i + 1}"):
                activo = self.juego.audio.hablando(f"mision_{i + 1}")
                tipo = "altavoz_on" if activo and int(self.t * 3) % 2 == 0 else "altavoz"
                G.icono(s, tipo, (r.right - 26, r.bottom - 30), 20, G.PRIMARIO if activo else G.GRIS)
            pygame.draw.circle(s, G.PRIMARIO, (r.x + 36, r.y + 36), 22)
            G.texto(s, str(i + 1), (r.x + 36, r.y + 36), 20, G.BLANCO, True, "center")
            nombre = m["habito"].split(": ", 1)[1]
            G.parrafo(s, nombre, (r.x + 68, r.y + 20), r.w - 84, 19, G.TEXTO, True, 1.1)
            G.parrafo(s, m["corto"], (r.x + 20, r.y + 84), r.w - 40, 16, G.TEXTO_SUAVE)
            G.icono(s, "medalla", (r.x + 34, r.bottom - 32), 30, G.ACENTO)
            G.texto(s, m["insignia"], (r.x + 56, r.bottom - 40), 15, G.TEXTO, True)
            if i < 6 and col < 3:
                G.flecha(s, (r.right + 10, r.centery), 18, G.ACENTO, "der")
        if self.con_voz:
            G.texto(s, "Pasa el cursor sobre una misión para escuchar su explicación.", (640, 614), 16,
                    G.TEXTO_CLARO, True, "midtop")
        self.dibujar_botones(s)


class EscenaRecords(EscenaInfo):
    def __init__(self, juego):
        super().__init__(juego)
        self.records = L.cargar_records(RUTA_RECORDS)
        self.b_limpiar = Boton((900, 600, 300, 54), "Limpiar registros", G.PELIGRO, "claro", icono="x")
        self.b_limpiar.activo = bool(self.records)
        self.b_no = Boton((450, 400, 170, 54), "Cancelar", estilo="claro", flecha="izq")
        self.b_si = Boton((660, 400, 170, 54), "Sí, borrar", G.PELIGRO)
        self.botones.append(self.b_limpiar)
        self.confirmando = False
        self.nav_conf = Navegador([self.b_no, self.b_si], horizontal=True)
        self.mensaje = None
        self.t_mensaje = 0.0

    def evento(self, ev):
        if self.confirmando:
            b = self.nav_conf.evento(ev)
            if b is self.b_si:
                ok = L.borrar_records(RUTA_RECORDS)
                self.records = [] if ok else self.records
                self.b_limpiar.activo = bool(self.records)
                self.mensaje = "Registros borrados." if ok else "No se pudo borrar el archivo."
                self.t_mensaje = self.t
                self.juego.audio.play("error" if not ok else "clic")
                self.confirmando = False
            elif b is self.b_no or es_tecla(ev, pygame.K_ESCAPE):
                self.juego.audio.play("clic")
                self.confirmando = False
            return
        if ev.tipo == "clic" and self.b_limpiar.clic(ev.pos) or es_tecla(ev, pygame.K_DELETE) and self.records:
            self.juego.audio.play("clic")
            self.confirmando = True
            self.nav_conf.poner(0)
            return
        super().evento(ev)

    def actualizar(self, dt):
        super().actualizar(dt)
        if self.confirmando:
            for b in (self.b_no, self.b_si):
                b.actualizar(dt, self.juego.mouse)

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "TABLA DE RÉCORDS", (640, 26), 34, G.BLANCO, True, "midtop")
        G.panel(s, (180, 86, 920, 490))
        cols = [(214, "#"), (260, "Jugador"), (520, "Puntos"), (640, "Dificultad"), (800, "Rango"), (1000, "Fecha")]
        for x, txt in cols:
            G.texto(s, txt, (x, 106), 15, G.TEXTO_SUAVE, True)
        pygame.draw.line(s, G.LINEA, (200, 132), (1080, 132), 2)
        if not self.records:
            G.texto(s, "Todavía no hay récords. ¡Juega una partida y sé el primero!", (640, 300), 20,
                    G.TEXTO_SUAVE, True, "center")
        for k, rec in enumerate(self.records[:10]):
            y = 144 + k * 42
            if k % 2 == 0:
                pygame.draw.rect(s, G.PANEL_2, (196, y - 6, 888, 38), border_radius=8)
            if k < 3:
                G.icono(s, "medalla", (220, y + 12), 24, [G.ACENTO, (180, 186, 200), (205, 140, 90)][k])
            else:
                G.texto(s, str(k + 1), (220, y + 2), 17, G.TEXTO, True, "midtop")
            G.texto(s, limpiar_texto(rec.get("nombre", ""))[:16], (260, y + 2), 18, G.TEXTO, True)
            G.texto(s, str(rec.get("puntos", 0)), (520, y + 2), 18, G.TEXTO, True)
            G.texto(s, limpiar_texto(rec.get("dificultad", "")), (640, y + 3), 16, G.TEXTO)
            rango = limpiar_texto(rec.get("rango", ""))
            if rango.isupper():
                rango = rango.capitalize()
            G.texto(s, rango[:26], (800, y + 3), 15, G.TEXTO)
            G.texto(s, rec.get("fecha", ""), (1000, y + 3), 15, G.TEXTO_SUAVE)
        self.dibujar_botones(s)
        if self.mensaje and self.t - self.t_mensaje < 2.5:
            G.pastilla(s, self.mensaje, (640, 612), G.EXITO if "borrados" in self.mensaje else G.PELIGRO,
                       16, ancla="midtop")
        if self.records:
            ayuda(s, "ESC volver   ·   SUPR limpiar registros", 714)
        if self.confirmando:
            s.blit(G.capa((8, 12, 24, 180)), (0, 0))
            G.panel(s, (400, 220, 480, 260))
            G.icono(s, "alerta", (640, 268), 44, G.PELIGRO)
            G.texto(s, "¿Borrar todos los récords?", (640, 300), 26, G.TEXTO, True, "midtop")
            G.texto(s, "Esta acción no se puede deshacer.", (640, 340), 16, G.TEXTO_SUAVE, False, "midtop")
            self.b_no.dibujar(s, self.t)
            self.b_si.dibujar(s, self.t)


class EscenaCreditos(EscenaInfo):
    LINEAS = [
        ("Diseño, programación, ilustraciones y audio", "Jesús Jacinto Fabián"),
        ("Curso", "Sistemas Colaborativos  ·  Dr. Ramfis Miguelena"),
        ("Institución", "Universidad Tecnológica de Panamá  ·  FISC  ·  Lic. en Ciberseguridad"),
        ("Contenido educativo", "Basado en «Los 7 hábitos de la gente altamente efectiva» de Stephen R. Covey"),
        ("Ilustraciones", "Dibujadas con código (Pygame), sin imágenes de terceros"),
        ("Música y efectos", "Compuestos y sintetizados con código en audio.py (obra original)"),
        ("Tecnologías", "Python 3  ·  Pygame (licencia LGPL)  ·  fuente DejaVu Sans (licencia libre)"),
        ("Versión", "4.0  ·  II Semestre 2026"),
    ]

    def dibujar(self, s):
        G.fondo(s)
        G.texto(s, "CRÉDITOS", (640, 26), 34, G.BLANCO, True, "midtop")
        G.panel(s, (160, 86, 960, 490))
        G.texto(s, "M7: EL DESAFÍO DEL EQUIPO", (640, 112), 26, G.PRIMARIO, True, "midtop")
        for k, (a, b) in enumerate(self.LINEAS):
            y = 168 + k * 48
            G.texto(s, a, (200, y), 14, G.TEXTO_SUAVE, True)
            G.texto(s, b, (200, y + 18), 18, G.TEXTO)
        self.dibujar_botones(s)


# ============================================================
# CONTROLADOR PRINCIPAL
# ============================================================

class Partida:
    def __init__(self, jugadores, config):
        self.jugadores = jugadores
        self.config = config
        self.mision_idx = 0
        self.jugador_idx = 0

    def jugador(self):
        return self.jugadores[self.jugador_idx]


class Juego:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption("M7: El Desafío del Equipo")
        icono_v = pygame.Surface((64, 64), pygame.SRCALPHA)
        G.icono(icono_v, "medalla", (32, 32), 60, G.ACENTO)
        pygame.display.set_icon(icono_v)
        self.ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        self.base = pygame.Surface((ANCHO, ALTO))
        self.velo = pygame.Surface((ANCHO, ALTO))
        self.velo.fill((10, 16, 30))
        self.reloj = pygame.time.Clock()
        self.audio = Audio(os.path.join(CARPETA, "sonidos"), CARPETA_VOZ)
        self.mouse = (0, 0)
        self.escala, self.offset = 1.0, (0, 0)
        self.corriendo = True
        self.pantalla_completa = False
        self.partida = None
        self.pausa = False
        self.toasts = []
        self.toast_actual = None
        self.fade = 1.0
        self.b_pausa_seguir = Boton((490, 330, 300, 56), "Continuar", flecha="der", pulso=True)
        self.b_pausa_menu = Boton((490, 404, 300, 56), "Salir al menú", G.PELIGRO, "claro", icono="salir")
        self.nav_pausa = Navegador([self.b_pausa_seguir, self.b_pausa_menu])
        self.globales = {"musica": pygame.Rect(1180, 14, 36, 36),
                         "pantalla": pygame.Rect(1228, 14, 36, 36),
                         "pausa": pygame.Rect(1180 - 48, 14, 36, 36)}
        self.escena = EscenaMenu(self)
        self.audio.iniciar_musica()

    # -- navegación general --
    def cambiar(self, escena):
        self.audio.detener_voz()
        self.escena = escena
        self.fade = 1.0

    def toast(self, titulo, txt, icono="medalla", color=G.ACENTO, sonido="insignia"):
        self.toasts.append({"titulo": titulo, "txt": txt, "icono": icono, "color": color,
                            "sonido": sonido, "t": 0.0})

    # -- flujo de la partida --
    def iniciar_partida(self, jugadores, config):
        self.partida = Partida(jugadores, config)
        self.cambiar(EscenaHistoria(self))

    def siguiente_turno(self):
        p = self.partida
        if p.mision_idx >= len(C.MISIONES):
            self.fin_partida()
        elif len(p.jugadores) > 1:
            self.cambiar(EscenaTurno(self))
        else:
            self.cambiar(EscenaMision(self))

    def turno_terminado(self):
        p = self.partida
        p.jugador_idx += 1
        if p.jugador_idx >= len(p.jugadores):
            p.jugador_idx = 0
            p.mision_idx += 1
        self.siguiente_turno()

    def fin_partida(self):
        p = self.partida
        self.nuevas_finales = []
        for j in p.jugadores:
            self.nuevas_finales.append(L.finalizar(j))
            L.guardar_record(RUTA_RECORDS, j, p.config)
        self.cambiar(EscenaResumen(self, 0, self.nuevas_finales[0]))

    def resumen_siguiente(self, i):
        p = self.partida
        if i + 1 < len(p.jugadores):
            self.cambiar(EscenaResumen(self, i + 1, self.nuevas_finales[i + 1]))
        elif len(p.jugadores) > 1:
            orden, empatados = L.ordenar_podio(p.jugadores)
            if len(empatados) > 1:
                self.cambiar(EscenaDesempate(self, empatados, orden))
            else:
                self.mostrar_podio(orden, orden[0])
        else:
            self.cambiar(EscenaMenu(self))

    def mostrar_podio(self, orden, ganador):
        if ganador is not None:
            orden = [ganador] + [j for j in orden if j is not ganador]
        self.cambiar(EscenaPodio(self, orden, ganador))

    # -- ventana --
    def alternar_pantalla(self):
        self.pantalla_completa = not self.pantalla_completa
        if self.pantalla_completa:
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

    def a_base(self, pos):
        return ((pos[0] - self.offset[0]) / self.escala, (pos[1] - self.offset[1]) / self.escala)

    # -- bucle principal --
    def procesar(self, e):
        if e.type == pygame.QUIT:
            self.corriendo = False
            return
        ev = None
        if e.type == pygame.MOUSEMOTION:
            self.mouse = self.a_base(e.pos)
            ev = Ev("mover", self.mouse)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.mouse = self.a_base(e.pos)
            if self.clic_global(self.mouse):
                return
            ev = Ev("clic", self.mouse)
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_F11:
                self.alternar_pantalla()
                return
            if e.key in (pygame.K_ESCAPE, pygame.K_p) and (self.pausa or self.escena.pausable):
                self.alternar_pausa()
                return
            ev = Ev("tecla", tecla=e.key, texto=e.unicode)
        elif e.type == pygame.TEXTINPUT:
            ev = Ev("texto", texto=e.text)
        if ev is None:
            return
        if self.pausa:
            b = self.nav_pausa.evento(ev)
            if b is self.b_pausa_seguir:
                self.alternar_pausa()
            elif b is self.b_pausa_menu:
                self.pausa = False
                self.partida = None
                self.audio.play("clic")
                self.cambiar(EscenaMenu(self))
        else:
            self.escena.evento(ev)

    def alternar_pausa(self):
        self.pausa = not self.pausa
        self.audio.play("clic")
        if self.pausa:
            self.nav_pausa.poner(0)

    def clic_global(self, pos):
        if self.globales["musica"].collidepoint(pos):
            self.audio.alternar_musica()
            return True
        if self.globales["pantalla"].collidepoint(pos):
            self.alternar_pantalla()
            return True
        if self.globales["pausa"].collidepoint(pos) and (self.escena.pausable or self.pausa):
            self.alternar_pausa()
            return True
        return False

    def actualizar(self, dt):
        if self.pausa:
            for b in (self.b_pausa_seguir, self.b_pausa_menu):
                b.actualizar(dt, self.mouse)
        else:
            self.escena.actualizar(dt)
        self.fade = max(0.0, self.fade - dt * 4)
        self.audio.actualizar()
        if self.toast_actual is None and self.toasts:
            self.toast_actual = self.toasts.pop(0)
            self.audio.play(self.toast_actual["sonido"])
        if self.toast_actual:
            self.toast_actual["t"] += dt
            if self.toast_actual["t"] > 2.8:
                self.toast_actual = None

    def dibujar_globales(self, s):
        items = [("musica", "Música"), ("pantalla", "Pantalla completa (F11)")]
        if self.escena.pausable or self.pausa:
            items.append(("pausa", "Pausa (ESC)"))
        for clave, ayuda_txt in items:
            r = self.globales[clave]
            sobre = r.collidepoint(self.mouse)
            pygame.draw.circle(s, (58, 80, 124) if sobre else (34, 50, 84), r.center, 18)
            G.icono(s, clave, r.center, 18, G.BLANCO)
            if clave == "musica" and not self.audio.musica_activa:
                pygame.draw.line(s, G.PELIGRO, (r.x + 6, r.bottom - 6), (r.right - 6, r.y + 6), 3)
            if sobre:
                G.pastilla(s, ayuda_txt, (r.right, r.bottom + 6), (20, 28, 46), 13, ancla="topright")

    def dibujar_toast(self, s):
        ta = self.toast_actual
        if not ta:
            return
        t = ta["t"]
        k = min(1.0, t / 0.3) if t < 2.4 else max(0.0, 1 - (t - 2.4) / 0.4)
        k = 1 - (1 - k) ** 3
        r = pygame.Rect(0, 0, 430, 58)
        r.midtop = (640, int(-64 + 67 * k))
        G.panel(s, r, G.BLANCO, 14, borde=ta["color"], grosor=3)
        pygame.draw.circle(s, aclarar_suave(ta["color"]), (r.x + 32, r.centery), 22)
        G.icono(s, ta["icono"], (r.x + 32, r.centery), 28, ta["color"])
        G.texto(s, ta["titulo"], (r.x + 64, r.y + 8), 14, ta["color"], True)
        G.texto(s, ta["txt"], (r.x + 64, r.y + 26), 20, G.TEXTO, True)

    def dibujar_pausa(self, s):
        s.blit(G.capa((8, 12, 24, 180)), (0, 0))
        G.panel(s, (440, 200, 400, 300))
        G.icono(s, "pausa", (640, 248), 40, G.PRIMARIO)
        G.texto(s, "Juego en pausa", (640, 278), 28, G.TEXTO, True, "midtop")
        self.b_pausa_seguir.dibujar(s, 0)
        self.b_pausa_menu.dibujar(s, 0)
        G.texto(s, "Si sales al menú se pierde la partida.", (640, 470), 13, G.TEXTO_SUAVE, False, "midtop")

    def dibujar(self):
        s = self.base
        self.escena.dibujar(s)
        self.dibujar_globales(s)
        if self.pausa:
            self.dibujar_pausa(s)
        self.dibujar_toast(s)
        if self.fade > 0:
            self.velo.set_alpha(int(255 * self.fade))
            s.blit(self.velo, (0, 0))
        ventana = pygame.display.get_surface()
        tam = ventana.get_size()
        if tam == (ANCHO, ALTO):
            self.escala, self.offset = 1.0, (0, 0)
            ventana.blit(s, (0, 0))
        else:
            self.escala = min(tam[0] / ANCHO, tam[1] / ALTO)
            w, h = int(ANCHO * self.escala), int(ALTO * self.escala)
            self.offset = ((tam[0] - w) // 2, (tam[1] - h) // 2)
            ventana.fill((0, 0, 0))
            ventana.blit(pygame.transform.smoothscale(s, (w, h)), self.offset)
        pygame.display.flip()

    def ejecutar(self):
        while self.corriendo:
            dt = min(0.05, self.reloj.tick(60) / 1000)
            for e in pygame.event.get():
                self.procesar(e)
            self.actualizar(dt)
            if self.corriendo:
                self.dibujar()
        pygame.quit()


def aclarar_suave(c):
    return G.aclarar(c, 0.85)


if __name__ == "__main__":
    Juego().ejecutar()
