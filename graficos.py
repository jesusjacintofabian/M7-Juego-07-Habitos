# ============================================================
# M7: EL DESAFÍO DEL EQUIPO - GRÁFICOS
# Todo se dibuja con código usando Pygame: personajes, reloj de
# arena, íconos, flechas, botones y paneles. No se usan
# imágenes externas.
# Autor: Jesús Jacinto Fabián
# ============================================================

import math
import random
from functools import lru_cache

import pygame

ANCHO, ALTO = 1280, 720

# ------------------------------------------------------------
# Paleta de colores
# ------------------------------------------------------------
FONDO_1 = (18, 28, 50)
FONDO_2 = (36, 56, 96)
PANEL = (250, 251, 254)
PANEL_2 = (237, 241, 248)
LINEA = (214, 220, 232)
TEXTO = (28, 34, 48)
TEXTO_SUAVE = (96, 106, 126)
TEXTO_CLARO = (200, 210, 230)
BLANCO = (255, 255, 255)
PRIMARIO = (52, 120, 246)
ACENTO = (255, 184, 28)
EXITO = (34, 160, 100)
PELIGRO = (220, 66, 66)
ADVERTENCIA = (236, 142, 30)
MORADO = (124, 86, 214)
GRIS = (150, 158, 172)
ARENA = (232, 186, 92)


def aclarar(c, f):
    return tuple(min(255, int(v + (255 - v) * f)) for v in c[:3])


def oscurecer(c, f):
    return tuple(max(0, int(v * (1 - f))) for v in c[:3])


def mezcla(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------
# Texto
# ------------------------------------------------------------
_fuentes = {}
_cache_texto = {}
NOMBRES_FUENTE = "dejavusans,ubuntu,notosans,liberationsans,freesans"


def fuente(tam, negrita=False):
    clave = (tam, negrita)
    if clave not in _fuentes:
        _fuentes[clave] = pygame.font.SysFont(NOMBRES_FUENTE, tam, bold=negrita)
    return _fuentes[clave]


def render(txt, tam, color, negrita=False):
    clave = (txt, tam, color, negrita)
    s = _cache_texto.get(clave)
    if s is None:
        if len(_cache_texto) > 3000:
            _cache_texto.clear()
        s = fuente(tam, negrita).render(txt, True, color)
        _cache_texto[clave] = s
    return s


def texto(surf, txt, pos, tam=22, color=TEXTO, negrita=False, ancla="topleft"):
    s = render(str(txt), tam, color, negrita)
    r = s.get_rect(**{ancla: pos})
    surf.blit(s, r)
    return r


@lru_cache(maxsize=512)
def envolver(txt, tam, ancho, negrita=False):
    f = fuente(tam, negrita)
    lineas = []
    for parrafo_txt in txt.split("\n"):
        actual = ""
        for palabra in parrafo_txt.split(" "):
            prueba = palabra if not actual else actual + " " + palabra
            if f.size(prueba)[0] <= ancho:
                actual = prueba
            else:
                if actual:
                    lineas.append(actual)
                actual = palabra
        lineas.append(actual)
    return tuple(lineas)


def alto_linea(tam, negrita=False, interlineado=1.25):
    return int(fuente(tam, negrita).get_linesize() * interlineado)


def parrafo(surf, txt, pos, ancho, tam=22, color=TEXTO, negrita=False,
            interlineado=1.25, max_chars=None, centrado=False):
    """Dibuja texto con salto de línea automático. Devuelve la y final."""
    x, y = pos
    paso = alto_linea(tam, negrita, interlineado)
    restante = max_chars
    for linea in envolver(txt, tam, ancho, negrita):
        if restante is not None:
            if restante <= 0:
                break
            if len(linea) > restante:
                linea = linea[:restante]
            restante -= len(linea) + 1
        if centrado:
            texto(surf, linea, (x + ancho // 2, y), tam, color, negrita, "midtop")
        else:
            texto(surf, linea, (x, y), tam, color, negrita)
        y += paso
    return y


def alto_parrafo(txt, ancho, tam=22, negrita=False, interlineado=1.25):
    return len(envolver(txt, tam, ancho, negrita)) * alto_linea(tam, negrita, interlineado)


# ------------------------------------------------------------
# Superficies cacheadas (sombras, capas transparentes, fondo)
# ------------------------------------------------------------
_cache_sup = {}


def _sombra(w, h, radio, alfa=55):
    clave = ("sombra", w, h, radio, alfa)
    if clave not in _cache_sup:
        s = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
        for k, a in ((10, alfa // 3), (6, alfa // 2), (3, alfa)):
            pygame.draw.rect(s, (0, 0, 0, a), (12 - k // 2, 12 - k // 2 + 4,
                                               w + k, h + k), border_radius=radio + k)
        _cache_sup[clave] = s
    return _cache_sup[clave]


def capa(color_alfa, tam=(ANCHO, ALTO)):
    clave = ("capa", color_alfa, tam)
    if clave not in _cache_sup:
        s = pygame.Surface(tam, pygame.SRCALPHA)
        s.fill(color_alfa)
        _cache_sup[clave] = s
    return _cache_sup[clave]


def elipse_alfa(surf, color_alfa, rect):
    rect = pygame.Rect(rect)
    clave = ("elipse", color_alfa, rect.size)
    if clave not in _cache_sup:
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(s, color_alfa, (0, 0, *rect.size))
        _cache_sup[clave] = s
    surf.blit(_cache_sup[clave], rect.topleft)


def fondo(surf):
    if "fondo" not in _cache_sup:
        s = pygame.Surface((ANCHO, ALTO))
        for y in range(ALTO):
            pygame.draw.line(s, mezcla(FONDO_1, FONDO_2, y / ALTO), (0, y), (ANCHO, y))
        deco = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        rnd = random.Random(7)
        for _ in range(14):
            r = rnd.randint(40, 180)
            pygame.draw.circle(deco, (255, 255, 255, rnd.randint(6, 14)),
                               (rnd.randint(0, ANCHO), rnd.randint(0, ALTO)), r)
        # cuadrícula tenue
        for x in range(0, ANCHO, 40):
            pygame.draw.line(deco, (255, 255, 255, 6), (x, 0), (x, ALTO))
        for y in range(0, ALTO, 40):
            pygame.draw.line(deco, (255, 255, 255, 6), (0, y), (ANCHO, y))
        s.blit(deco, (0, 0))
        _cache_sup["fondo"] = s
    surf.blit(_cache_sup["fondo"], (0, 0))


def panel(surf, rect, color=PANEL, radio=18, sombra=True, borde=None, grosor=2):
    rect = pygame.Rect(rect)
    if sombra:
        surf.blit(_sombra(rect.w, rect.h, radio), (rect.x - 12, rect.y - 12))
    pygame.draw.rect(surf, color, rect, border_radius=radio)
    if borde:
        pygame.draw.rect(surf, borde, rect, grosor, border_radius=radio)
    return rect


def pastilla(surf, txt, pos, color, tam=16, color_texto=BLANCO, ancla="topleft"):
    s = render(txt, tam, color_texto, True)
    r = pygame.Rect(0, 0, s.get_width() + 22, s.get_height() + 8)
    setattr(r, ancla, pos)
    pygame.draw.rect(surf, color, r, border_radius=r.h // 2)
    surf.blit(s, s.get_rect(center=r.center))
    return r


def barra(surf, rect, valor, color, maximo=100):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surf, (222, 227, 237), rect, border_radius=rect.h // 2)
    v = max(0.0, min(float(valor), maximo))
    w = int(rect.w * v / maximo)
    if w > 0:
        pygame.draw.rect(surf, color, (rect.x, rect.y, max(w, rect.h), rect.h),
                         border_radius=rect.h // 2)


# ------------------------------------------------------------
# Íconos y flechas (vectoriales)
# ------------------------------------------------------------

def _rotar(puntos, centro, ang):
    cx, cy = centro
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c)
            for x, y in puntos]


def flecha(surf, centro, tam, color, direccion="der"):
    cx, cy = centro
    s = tam / 2
    pts = [(cx - s, cy - s * 0.28), (cx + s * 0.05, cy - s * 0.28),
           (cx + s * 0.05, cy - s * 0.75), (cx + s, cy),
           (cx + s * 0.05, cy + s * 0.75), (cx + s * 0.05, cy + s * 0.28),
           (cx - s, cy + s * 0.28)]
    ang = {"der": 0, "abajo": math.pi / 2, "izq": math.pi, "arriba": -math.pi / 2}[direccion]
    pygame.draw.polygon(surf, color, _rotar(pts, centro, ang))


def triangulo(surf, centro, tam, color, direccion="der"):
    cx, cy = centro
    s = tam / 2
    pts = [(cx - s * 0.6, cy - s), (cx + s * 0.8, cy), (cx - s * 0.6, cy + s)]
    ang = {"der": 0, "abajo": math.pi / 2, "izq": math.pi, "arriba": -math.pi / 2}[direccion]
    pygame.draw.polygon(surf, color, _rotar(pts, centro, ang))


def estrella(surf, centro, r, color, puntas=5, interior=0.45):
    cx, cy = centro
    pts = []
    for i in range(puntas * 2):
        rr = r if i % 2 == 0 else r * interior
        a = -math.pi / 2 + i * math.pi / puntas
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pygame.draw.polygon(surf, color, pts)


def corazon(surf, centro, tam, color):
    cx, cy = centro
    r = tam * 0.27
    pygame.draw.circle(surf, color, (int(cx - r * 0.95), int(cy - r * 0.4)), int(r))
    pygame.draw.circle(surf, color, (int(cx + r * 0.95), int(cy - r * 0.4)), int(r))
    pygame.draw.polygon(surf, color, [(cx - r * 1.9, cy - r * 0.15),
                                      (cx + r * 1.9, cy - r * 0.15),
                                      (cx, cy + tam * 0.45)])


def icono(surf, tipo, centro, tam, color):
    cx, cy = centro
    s = tam / 2
    g = max(2, int(tam / 10))
    if tipo == "liderazgo":           # corona
        pts = [(cx - s, cy + s * 0.6), (cx - s, cy - s * 0.5), (cx - s * 0.45, cy),
               (cx, cy - s * 0.8), (cx + s * 0.45, cy), (cx + s, cy - s * 0.5),
               (cx + s, cy + s * 0.6)]
        pygame.draw.polygon(surf, color, pts)
    elif tipo == "comunicacion":      # globo de diálogo
        pygame.draw.rect(surf, color, (cx - s, cy - s * 0.8, 2 * s, s * 1.3),
                         border_radius=int(s * 0.4))
        pygame.draw.polygon(surf, color, [(cx - s * 0.5, cy + s * 0.4),
                                          (cx - s * 0.6, cy + s), (cx, cy + s * 0.4)])
    elif tipo == "empatia":
        corazon(surf, centro, tam, color)
    elif tipo == "productividad":     # rayo
        pts = [(cx + s * 0.2, cy - s), (cx - s * 0.6, cy + s * 0.15), (cx - s * 0.05, cy + s * 0.15),
               (cx - s * 0.25, cy + s), (cx + s * 0.6, cy - s * 0.2), (cx + s * 0.05, cy - s * 0.2)]
        pygame.draw.polygon(surf, color, pts)
    elif tipo in ("puntos", "trofeo"):
        pygame.draw.rect(surf, color, (cx - s * 0.6, cy - s * 0.85, s * 1.2, s * 0.95),
                         border_bottom_left_radius=int(s * 0.6),
                         border_bottom_right_radius=int(s * 0.6))
        pygame.draw.circle(surf, color, (int(cx - s * 0.62), int(cy - s * 0.45)), int(s * 0.32), g)
        pygame.draw.circle(surf, color, (int(cx + s * 0.62), int(cy - s * 0.45)), int(s * 0.32), g)
        pygame.draw.rect(surf, color, (cx - s * 0.12, cy + s * 0.05, s * 0.24, s * 0.45))
        pygame.draw.rect(surf, color, (cx - s * 0.5, cy + s * 0.5, s, s * 0.32),
                         border_radius=3)
    elif tipo == "estrella":
        estrella(surf, centro, s, color)
    elif tipo == "medalla":
        pygame.draw.polygon(surf, oscurecer(color, 0.25), [(cx - s * 0.55, cy - s), (cx - s * 0.1, cy - s),
                                                          (cx + s * 0.15, cy - s * 0.1), (cx - s * 0.3, cy - s * 0.1)])
        pygame.draw.polygon(surf, oscurecer(color, 0.25), [(cx + s * 0.55, cy - s), (cx + s * 0.1, cy - s),
                                                          (cx - s * 0.15, cy - s * 0.1), (cx + s * 0.3, cy - s * 0.1)])
        pygame.draw.circle(surf, color, (int(cx), int(cy + s * 0.3)), int(s * 0.62))
        estrella(surf, (cx, cy + s * 0.3), s * 0.36, aclarar(color, 0.55))
    elif tipo == "check":
        pygame.draw.lines(surf, color, False, [(cx - s * 0.7, cy), (cx - s * 0.2, cy + s * 0.55),
                                               (cx + s * 0.75, cy - s * 0.55)], max(3, g + 1))
    elif tipo == "x":
        w = max(3, g + 1)
        pygame.draw.line(surf, color, (cx - s * 0.6, cy - s * 0.6), (cx + s * 0.6, cy + s * 0.6), w)
        pygame.draw.line(surf, color, (cx + s * 0.6, cy - s * 0.6), (cx - s * 0.6, cy + s * 0.6), w)
    elif tipo == "alerta":
        pygame.draw.polygon(surf, color, [(cx, cy - s), (cx + s, cy + s * 0.8), (cx - s, cy + s * 0.8)])
        pygame.draw.rect(surf, BLANCO, (cx - g / 2 - 1, cy - s * 0.35, g + 2, s * 0.65))
        pygame.draw.circle(surf, BLANCO, (int(cx), int(cy + s * 0.55)), g)
    elif tipo == "libro":
        pygame.draw.polygon(surf, color, [(cx - s, cy - s * 0.7), (cx - s * 0.08, cy - s * 0.5),
                                          (cx - s * 0.08, cy + s * 0.85), (cx - s, cy + s * 0.65)])
        pygame.draw.polygon(surf, color, [(cx + s, cy - s * 0.7), (cx + s * 0.08, cy - s * 0.5),
                                          (cx + s * 0.08, cy + s * 0.85), (cx + s, cy + s * 0.65)])
    elif tipo == "bombilla":
        pygame.draw.circle(surf, color, (int(cx), int(cy - s * 0.25)), int(s * 0.62))
        pygame.draw.rect(surf, color, (cx - s * 0.3, cy + s * 0.2, s * 0.6, s * 0.4))
        pygame.draw.rect(surf, oscurecer(color, 0.3), (cx - s * 0.28, cy + s * 0.65, s * 0.56, s * 0.25),
                         border_radius=3)
    elif tipo == "mapa":
        pts = [(cx - s, cy - s * 0.7), (cx - s * 0.35, cy - s * 0.9), (cx + s * 0.35, cy - s * 0.7),
               (cx + s, cy - s * 0.9), (cx + s, cy + s * 0.7), (cx + s * 0.35, cy + s * 0.9),
               (cx - s * 0.35, cy + s * 0.7), (cx - s, cy + s * 0.9)]
        pygame.draw.polygon(surf, color, pts, g)
        pygame.draw.line(surf, color, (cx - s * 0.35, cy - s * 0.9), (cx - s * 0.35, cy + s * 0.7), g)
        pygame.draw.line(surf, color, (cx + s * 0.35, cy - s * 0.7), (cx + s * 0.35, cy + s * 0.9), g)
    elif tipo == "info":
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(s), g)
        pygame.draw.rect(surf, color, (cx - g / 2, cy - s * 0.15, g, s * 0.65))
        pygame.draw.circle(surf, color, (int(cx), int(cy - s * 0.45)), max(2, g // 1))
    elif tipo == "salir":
        pygame.draw.rect(surf, color, (cx - s, cy - s * 0.85, s * 1.1, s * 1.7), g, border_radius=3)
        flecha(surf, (cx + s * 0.35, cy), s * 1.2, color, "der")
    elif tipo == "musica":
        pygame.draw.circle(surf, color, (int(cx - s * 0.45), int(cy + s * 0.55)), int(s * 0.32))
        pygame.draw.circle(surf, color, (int(cx + s * 0.55), int(cy + s * 0.35)), int(s * 0.32))
        pygame.draw.line(surf, color, (cx - s * 0.15, cy + s * 0.55), (cx - s * 0.15, cy - s * 0.75), g)
        pygame.draw.line(surf, color, (cx + s * 0.85, cy + s * 0.35), (cx + s * 0.85, cy - s * 0.95), g)
        pygame.draw.line(surf, color, (cx - s * 0.15, cy - s * 0.75), (cx + s * 0.85, cy - s * 0.95), g + 2)
    elif tipo == "pantalla":
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x0, y0 = cx + dx * s * 0.85, cy + dy * s * 0.85
            pygame.draw.line(surf, color, (x0, y0), (x0 - dx * s * 0.5, y0), g)
            pygame.draw.line(surf, color, (x0, y0), (x0, y0 - dy * s * 0.5), g)
    elif tipo == "pausa":
        pygame.draw.rect(surf, color, (cx - s * 0.6, cy - s * 0.7, s * 0.4, s * 1.4), border_radius=2)
        pygame.draw.rect(surf, color, (cx + s * 0.2, cy - s * 0.7, s * 0.4, s * 1.4), border_radius=2)
    elif tipo == "fuego":
        pts = [(cx, cy - s), (cx + s * 0.55, cy - s * 0.1), (cx + s * 0.6, cy + s * 0.45),
               (cx, cy + s), (cx - s * 0.6, cy + s * 0.45), (cx - s * 0.5, cy - s * 0.15),
               (cx - s * 0.2, cy + s * 0.05)]
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.circle(surf, aclarar(color, 0.55), (int(cx), int(cy + s * 0.45)), int(s * 0.32))
    elif tipo == "reloj":
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(s), g)
        pygame.draw.line(surf, color, (cx, cy), (cx, cy - s * 0.6), g)
        pygame.draw.line(surf, color, (cx, cy), (cx + s * 0.45, cy + s * 0.2), g)
    elif tipo == "carta":
        pygame.draw.rect(surf, color, (cx - s * 0.7, cy - s, s * 1.4, s * 2), g, border_radius=4)
        estrella(surf, centro, s * 0.4, color)
    elif tipo == "usuarios":
        for dx, k in ((-0.45, 0.85), (0.45, 0.85), (0, 1.0)):
            pygame.draw.circle(surf, color, (int(cx + dx * s), int(cy - s * 0.35)), int(s * 0.3 * k))
            pygame.draw.ellipse(surf, color, (cx + dx * s - s * 0.5 * k, cy + s * 0.05, s * k, s * 0.8))
    elif tipo == "candado":
        pygame.draw.rect(surf, color, (cx - s * 0.6, cy - s * 0.1, s * 1.2, s * 0.95), border_radius=3)
        pygame.draw.arc(surf, color, (cx - s * 0.42, cy - s * 0.85, s * 0.84, s * 1.3), 0, math.pi, g)
    elif tipo == "dados":
        pygame.draw.rect(surf, color, (cx - s * 0.8, cy - s * 0.8, s * 1.6, s * 1.6), g, border_radius=5)
        for dx, dy in ((-0.4, -0.4), (0, 0), (0.4, 0.4)):
            pygame.draw.circle(surf, color, (int(cx + dx * s), int(cy + dy * s)), max(2, g))
    elif tipo in ("altavoz", "altavoz_on"):
        pygame.draw.rect(surf, color, (cx - s * 0.9, cy - s * 0.3, s * 0.45, s * 0.6))
        pygame.draw.polygon(surf, color, [(cx - s * 0.5, cy - s * 0.3), (cx, cy - s * 0.8),
                                          (cx, cy + s * 0.8), (cx - s * 0.5, cy + s * 0.3)])
        ondas = (0.45, 0.8) if tipo == "altavoz_on" else (0.45,)
        for k in ondas:
            pygame.draw.arc(surf, color, (cx - s * k, cy - s * k, s * k * 2, s * k * 2),
                            -math.pi / 3, math.pi / 3, g)
    elif tipo == "objetivo":
        for k in (1.0, 0.62, 0.25):
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(s * k), g if k < 1 else g)


# ------------------------------------------------------------
# Botones
# ------------------------------------------------------------

class Boton:
    """estilo: 'solido' (relleno), 'claro' (blanco con borde),
    'opcion' (tarjeta de respuesta con número)."""

    def __init__(self, rect, txt, color=PRIMARIO, estilo="solido", flecha=None,
                 icono=None, tam=22, pulso=False, numero=None, dato=None, radio=14):
        self.rect = pygame.Rect(rect)
        self.txt = txt
        self.color = color
        self.estilo = estilo
        self.flecha = flecha        # "der" o "izq"
        self.icono = icono
        self.tam = tam
        self.pulso = pulso
        self.numero = numero
        self.dato = dato
        self.radio = radio
        self.activo = True
        self.foco = False
        self.visible = True
        self.marca = None           # "correcta", "incorrecta" o "elegida"
        self.hover = 0.0
        self._sobre = False

    def actualizar(self, dt, mouse):
        self._sobre = self.visible and self.rect.collidepoint(mouse)
        objetivo = 1.0 if self.activo and (self._sobre or self.foco) else 0.0
        self.hover += (objetivo - self.hover) * min(1.0, dt * 14)

    def clic(self, pos):
        return self.visible and self.activo and self.rect.collidepoint(pos)

    def dibujar(self, surf, t=0.0):
        if not self.visible:
            return
        r = self.rect.move(0, -int(2 * self.hover))
        if self.estilo == "opcion":
            self._dibujar_opcion(surf, r, t)
            return
        if self.estilo == "solido":
            base = self.color if self.activo else (150, 158, 172)
            pygame.draw.rect(surf, oscurecer(base, 0.32), r.move(0, 4), border_radius=self.radio)
            pygame.draw.rect(surf, aclarar(base, 0.14 * self.hover), r, border_radius=self.radio)
            ct = BLANCO
        else:
            pygame.draw.rect(surf, oscurecer(PANEL_2, 0.12), r.move(0, 4), border_radius=self.radio)
            pygame.draw.rect(surf, mezcla(PANEL, aclarar(self.color, 0.85), self.hover), r,
                             border_radius=self.radio)
            pygame.draw.rect(surf, mezcla(LINEA, self.color, self.hover), r, 2, border_radius=self.radio)
            ct = TEXTO if self.activo else GRIS

        if self.pulso and self.activo:
            k = (math.sin(t * 4) + 1) / 2
            pygame.draw.rect(surf, aclarar(self.color, 0.4), r.inflate(6 + 6 * k, 6 + 6 * k),
                             2, border_radius=self.radio + 4)
        if self.foco:
            pygame.draw.rect(surf, ACENTO, r.inflate(10, 10), 3, border_radius=self.radio + 5)

        # contenido centrado: [icono] [flecha izq] texto [flecha der]
        st = render(self.txt, self.tam, ct, True)
        piezas = st.get_width()
        tam_i = int(self.tam * 1.1)
        if self.icono:
            piezas += tam_i + 12
        if self.flecha:
            piezas += tam_i + 10
        x = r.centerx - piezas // 2
        color_icono = ct if self.estilo == "solido" else self.color
        if self.flecha == "izq":
            flecha(surf, (x + tam_i // 2, r.centery), tam_i, color_icono, "izq")
            x += tam_i + 10
        if self.icono:
            icono(surf, self.icono, (x + tam_i // 2, r.centery), tam_i, color_icono)
            x += tam_i + 12
        surf.blit(st, st.get_rect(midleft=(x, r.centery)))
        x += st.get_width() + 10
        if self.flecha == "der":
            desliz = int(3 * self.hover + (2 * math.sin(t * 5) if self.pulso else 0))
            flecha(surf, (x + tam_i // 2 + desliz, r.centery), tam_i, color_icono, "der")

    def _dibujar_opcion(self, surf, r, t):
        colores = {"correcta": EXITO, "incorrecta": PELIGRO, "elegida": PRIMARIO}
        acento = colores.get(self.marca, self.color)
        fondo_c = PANEL if self.activo or self.marca else (244, 246, 250)
        if self.marca:
            fondo_c = aclarar(acento, 0.88)
        else:
            fondo_c = mezcla(fondo_c, aclarar(self.color, 0.9), self.hover)
        pygame.draw.rect(surf, oscurecer(PANEL_2, 0.14), r.move(0, 4), border_radius=self.radio)
        pygame.draw.rect(surf, fondo_c, r, border_radius=self.radio)
        borde = acento if (self.marca or self.hover > 0.05) else LINEA
        pygame.draw.rect(surf, mezcla(LINEA, borde, max(self.hover, 1.0 if self.marca else 0)),
                         r, 3 if (self.marca or self.hover > 0.5) else 2, border_radius=self.radio)
        if self.foco and not self.marca:
            pygame.draw.rect(surf, ACENTO, r.inflate(10, 10), 3, border_radius=self.radio + 5)
        # círculo con número o símbolo
        cx, cy = r.x + 34, r.centery
        pygame.draw.circle(surf, acento if (self.activo or self.marca) else GRIS, (cx, cy), 19)
        if self.marca == "correcta":
            icono(surf, "check", (cx, cy), 20, BLANCO)
        elif self.marca == "incorrecta":
            icono(surf, "x", (cx, cy), 18, BLANCO)
        elif self.numero is not None:
            texto(surf, str(self.numero), (cx, cy), 20, BLANCO, True, "center")
        # texto en varias líneas
        ancho = r.w - 108
        lineas = envolver(self.txt, self.tam, ancho)
        paso = alto_linea(self.tam, False, 1.2)
        y = r.centery - paso * len(lineas) // 2
        color_t = TEXTO if (self.activo or self.marca) else GRIS
        for linea in lineas:
            texto(surf, linea, (r.x + 66, y), self.tam, color_t)
            y += paso
        # flecha de "elegir" al pasar el ratón
        if self.activo and not self.marca and self.hover > 0.05:
            col = mezcla(fondo_c, self.color, self.hover)
            flecha(surf, (r.right - 26 + int(3 * self.hover), cy), 20, col, "der")


class Navegador:
    """Permite usar el teclado (flechas, TAB, ENTER, números) y el ratón
    sobre una lista de botones."""

    def __init__(self, botones, horizontal=False, numeros=True):
        self.botones = botones
        self.horizontal = horizontal
        self.numeros = numeros
        self.i = -1

    def poner(self, i):
        self.i = i
        for k, b in enumerate(self.botones):
            b.foco = (k == i)

    def mover(self, d):
        n = len(self.botones)
        if not n:
            return
        i = self.i
        for _ in range(n):
            i = (i + d) % n if i >= 0 else (0 if d > 0 else n - 1)
            if self.botones[i].activo and self.botones[i].visible:
                break
        self.poner(i)

    def evento(self, ev):
        if ev.tipo == "mover":
            for k, b in enumerate(self.botones):
                if b.visible and b.activo and b.rect.collidepoint(ev.pos):
                    self.poner(k)
        elif ev.tipo == "clic":
            for b in self.botones:
                if b.clic(ev.pos):
                    return b
        elif ev.tipo == "tecla":
            sig = pygame.K_RIGHT if self.horizontal else pygame.K_DOWN
            ant = pygame.K_LEFT if self.horizontal else pygame.K_UP
            if ev.tecla in (sig, pygame.K_TAB):
                self.mover(1)
            elif ev.tecla == ant:
                self.mover(-1)
            elif ev.tecla in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if 0 <= self.i < len(self.botones):
                    b = self.botones[self.i]
                    if b.activo and b.visible:
                        return b
            elif self.numeros and ev.texto and ev.texto.isdigit():
                k = int(ev.texto) - 1
                if 0 <= k < len(self.botones):
                    b = self.botones[k]
                    if b.activo and b.visible:
                        self.poner(k)
                        return b
        return None


# ------------------------------------------------------------
# Personajes (estilo plano semiprofesional)
# ------------------------------------------------------------

def personaje(surf, cx, base, esc, datos, expr="neutral", t=0.0, hablando=False):
    piel = datos["piel"]
    pelo = datos["pelo"]
    ropa = datos["ropa"]
    piel_os = oscurecer(piel, 0.14)
    fase = (cx * 0.013) % 6.28
    base = base + math.sin(t * 2.0 + fase) * 2.2 * esc

    def E(v):
        return v * esc

    # sombra en el piso
    elipse_alfa(surf, (0, 0, 0, 45), (cx - E(78), base - E(10), E(156), E(22)))

    # torso (se calcula primero para ubicar la cabeza)
    torso = pygame.Rect(0, 0, E(136), E(84))
    torso.midbottom = (cx, base)
    cuello = pygame.Rect(0, 0, E(28), E(26))
    cuello.midbottom = (cx, torso.top + E(14))
    hx, hy = cx, cuello.top - E(40)
    hw, hh = E(76), E(88)
    estilo = datos["estilo"]
    if estilo == "largo":   # pelo largo detrás de los hombros
        pygame.draw.rect(surf, oscurecer(pelo, 0.1), (hx - hw / 2 - E(10), hy - hh / 2 + E(8),
                                                      hw + E(20), hh * 1.15), border_radius=int(E(30)))
    rad = int(E(50))
    pygame.draw.rect(surf, ropa, torso, border_top_left_radius=rad, border_top_right_radius=rad,
                     border_bottom_left_radius=int(E(10)), border_bottom_right_radius=int(E(10)))
    # cuello
    pygame.draw.rect(surf, piel_os, cuello, border_radius=int(E(8)))
    tipo = datos.get("tipo_ropa", "camiseta")
    top = torso.top
    if tipo == "blazer":
        pygame.draw.polygon(surf, (245, 247, 250), [(cx - E(20), top + E(4)), (cx, top + E(40)),
                                                    (cx + E(20), top + E(4))])
        pygame.draw.polygon(surf, oscurecer(ropa, 0.25), [(cx - E(24), top + E(3)), (cx - E(4), top + E(42)),
                                                          (cx - E(30), top + E(30))])
        pygame.draw.polygon(surf, oscurecer(ropa, 0.25), [(cx + E(24), top + E(3)), (cx + E(4), top + E(42)),
                                                          (cx + E(30), top + E(30))])
    elif tipo == "camisa":
        pygame.draw.polygon(surf, piel_os, [(cx - E(13), top + E(2)), (cx, top + E(20)),
                                            (cx + E(13), top + E(2))])
        pygame.draw.polygon(surf, aclarar(ropa, 0.35), [(cx - E(26), top + E(2)), (cx - E(2), top + E(22)),
                                                        (cx - E(18), top + E(16))])
        pygame.draw.polygon(surf, aclarar(ropa, 0.35), [(cx + E(26), top + E(2)), (cx + E(2), top + E(22)),
                                                        (cx + E(18), top + E(16))])
        for k in range(3):
            pygame.draw.circle(surf, aclarar(ropa, 0.5), (int(cx), int(top + E(34 + k * 16))), max(1, int(E(2.5))))
    elif tipo == "sueter":
        pygame.draw.ellipse(surf, piel_os, (cx - E(17), top - E(4), E(34), E(18)))
        pygame.draw.ellipse(surf, oscurecer(ropa, 0.2), (cx - E(20), top - E(6), E(40), E(22)), max(2, int(E(4))))
        for k in (-1, 1):
            pygame.draw.line(surf, oscurecer(ropa, 0.12), (cx + k * E(36), top + E(30)),
                             (cx + k * E(36), base - E(6)), max(1, int(E(2))))
    else:
        pygame.draw.ellipse(surf, piel_os, (cx - E(16), top - E(6), E(32), E(20)))

    # cabeza
    if estilo == "mono":
        pygame.draw.circle(surf, oscurecer(pelo, 0.06), (int(hx), int(hy - hh / 2 - E(6))), int(E(19)))
    # orejas
    for k in (-1, 1):
        pygame.draw.ellipse(surf, piel_os, (hx + k * hw / 2 - E(9), hy - E(4), E(18), E(24)))
    pygame.draw.ellipse(surf, piel, (hx - hw / 2, hy - hh / 2, hw, hh))
    # pelo (casquete) y frente
    if estilo == "rizado":
        for k in range(9):
            a = math.pi + k * math.pi / 8
            pygame.draw.circle(surf, pelo, (int(hx + math.cos(a) * hw * 0.47),
                                            int(hy - hh * 0.08 + math.sin(a) * hh * 0.5)), int(E(15)))
    pygame.draw.ellipse(surf, pelo, (hx - hw / 2 - E(3), hy - hh / 2 - E(5), hw + E(6), hh * 0.6))
    frente = (hx - hw * 0.42, hy - hh * 0.17, hw * 0.84, hh * 0.65)
    if estilo == "corto":
        frente = (hx - hw * 0.43, hy - hh * 0.2, hw * 0.86, hh * 0.68)
    pygame.draw.ellipse(surf, piel, frente)
    if estilo == "corto":    # pequeño flequillo lateral
        pygame.draw.polygon(surf, pelo, [(hx - hw * 0.40, hy - hh * 0.14), (hx + hw * 0.18, hy - hh * 0.27),
                                         (hx - hw * 0.12, hy - hh * 0.09)])
    if estilo == "largo":    # mechones que caen a los lados
        for k in (-1, 1):
            pygame.draw.ellipse(surf, pelo, (hx + k * hw * 0.47 - E(7), hy - hh * 0.25, E(14), hh * 0.5))

    # ojos
    ey = hy + hh * 0.06
    ex = hw * 0.2
    parpadeo = ((t + fase) % 4.2) < 0.12
    ojo_c = (40, 40, 52)
    for k in (-1, 1):
        x = hx + k * ex
        if parpadeo or expr == "cansado":
            yy = ey + (E(2) if expr == "cansado" else 0)
            pygame.draw.line(surf, ojo_c, (x - E(6), yy), (x + E(6), yy), max(2, int(E(2.5))))
        else:
            alto_ojo = E(12) if expr == "sorprendido" else E(10)
            pygame.draw.ellipse(surf, ojo_c, (x - E(4.5), ey - alto_ojo / 2, E(9), alto_ojo))
            pygame.draw.circle(surf, BLANCO, (int(x + E(1.5)), int(ey - E(2))), max(1, int(E(1.6))))
    # cejas según expresión: (desplazamiento interior, exterior)
    cejas = {"neutral": (0, 0), "feliz": (-3, -1), "preocupado": (-6, 2),
             "molesto": (4, -4), "sorprendido": (-7, -6), "cansado": (2, 2)}
    di, de = cejas.get(expr, (0, 0))
    cy0 = ey - E(14)
    grosor = max(2, int(E(3)))
    for k in (-1, 1):
        x_in, x_out = hx + k * E(6), hx + k * E(23)
        pygame.draw.line(surf, oscurecer(pelo, 0.2), (x_in, cy0 + E(di)), (x_out, cy0 + E(de)), grosor)
    # rubor
    if expr == "feliz":
        for k in (-1, 1):
            elipse_alfa(surf, (235, 120, 120, 70), (hx + k * E(25) - E(8), ey + E(9), E(16), E(9)))
    # boca
    my = hy + hh * 0.3
    bc = (120, 50, 50)
    if hablando and int(t * 9) % 2 == 0:
        pygame.draw.ellipse(surf, bc, (hx - E(7), my - E(5), E(14), E(11)))
    elif expr == "feliz":
        pygame.draw.arc(surf, bc, (hx - E(13), my - E(12), E(26), E(18)), math.pi * 1.1, math.pi * 1.9, max(2, int(E(3))))
    elif expr == "preocupado":
        pygame.draw.arc(surf, bc, (hx - E(9), my - E(1), E(18), E(12)), math.pi * 0.15, math.pi * 0.85, max(2, int(E(2.5))))
    elif expr == "molesto":
        pygame.draw.arc(surf, bc, (hx - E(12), my - E(1), E(24), E(14)), math.pi * 0.1, math.pi * 0.9, max(2, int(E(3))))
    elif expr == "sorprendido":
        pygame.draw.ellipse(surf, bc, (hx - E(6), my - E(6), E(12), E(14)))
    elif expr == "cansado":
        pygame.draw.line(surf, bc, (hx - E(8), my + E(2)), (hx + E(8), my), max(2, int(E(2.5))))
    else:
        pygame.draw.line(surf, bc, (hx - E(8), my), (hx + E(8), my), max(2, int(E(2.5))))
    # lentes
    if datos.get("lentes"):
        lc = (46, 50, 62)
        for k in (-1, 1):
            pygame.draw.circle(surf, lc, (int(hx + k * ex), int(ey)), int(E(11)), max(2, int(E(2))))
        pygame.draw.line(surf, lc, (hx - ex + E(11), ey), (hx + ex - E(11), ey), max(2, int(E(2))))
    return (hx, hy - hh / 2)   # punta de la cabeza (para colocar globos)


def globo(surf, rect, cola_x, nombre=None, color_nombre=PRIMARIO):
    """Globo de diálogo con cola hacia abajo y etiqueta con el nombre."""
    rect = pygame.Rect(rect)
    panel(surf, rect, BLANCO, 20)
    cola_x = max(rect.x + 40, min(rect.right - 40, cola_x))
    pygame.draw.polygon(surf, BLANCO, [(cola_x - 16, rect.bottom - 2), (cola_x + 16, rect.bottom - 2),
                                       (cola_x + 2, rect.bottom + 22)])
    if nombre:
        pastilla(surf, nombre, (rect.x + 22, rect.y - 13), color_nombre, 16)


# ------------------------------------------------------------
# Reloj de arena
# ------------------------------------------------------------

def reloj_arena(surf, centro, alto, fraccion, t, urgente=False):
    """fraccion = tiempo restante (1.0 lleno arriba, 0.0 vacío)."""
    fraccion = max(0.0, min(1.0, fraccion))
    cx, cy = centro
    h = alto
    w = h * 0.62
    top, bot = cy - h / 2, cy + h / 2
    cuello = w * 0.08
    madera = PELIGRO if urgente and int(t * 4) % 2 == 0 else (128, 92, 56)
    vidrio = [(cx - w / 2, top + 4), (cx + w / 2, top + 4), (cx + cuello, cy),
              (cx + w / 2, bot - 4), (cx - w / 2, bot - 4), (cx - cuello, cy)]
    pygame.draw.polygon(surf, (226, 238, 250), vidrio)
    mitad = h / 2 - 6
    # arena de arriba (se vacía)
    if fraccion > 0:
        hs = mitad * math.sqrt(fraccion)
        hw = cuello + (w / 2 - cuello) * (hs / mitad)
        pygame.draw.polygon(surf, ARENA, [(cx - hw, cy - hs), (cx + hw, cy - hs),
                                          (cx + cuello, cy), (cx - cuello, cy)])
    # arena de abajo (se llena)
    if fraccion < 1:
        hb = mitad * (1 - math.sqrt(fraccion)) * 0.75
        hwb = cuello + (w / 2 - cuello) * (1 - hb / mitad)
        pico = min(10, hb * 0.6)
        pygame.draw.polygon(surf, oscurecer(ARENA, 0.06),
                            [(cx - w / 2 + 3, bot - 5), (cx + w / 2 - 3, bot - 5),
                             (cx + hwb, bot - 5 - hb), (cx, bot - 5 - hb - pico),
                             (cx - hwb, bot - 5 - hb)])
        if 0 < fraccion:
            # chorro de arena con granos en movimiento
            y_fin = bot - 5 - hb - pico
            pygame.draw.line(surf, ARENA, (cx, cy), (cx, y_fin), 2)
            for k in range(4):
                yy = cy + ((t * 90 + k * 14) % max(1, (y_fin - cy)))
                pygame.draw.circle(surf, oscurecer(ARENA, 0.15), (int(cx), int(yy)), 2)
    pygame.draw.polygon(surf, (110, 130, 160), vidrio, 2)
    # marcos de madera
    for y in (top - 4, bot - 4):
        pygame.draw.rect(surf, madera, (cx - w / 2 - 8, y, w + 16, 9), border_radius=4)
    for k in (-1, 1):
        pygame.draw.line(surf, madera, (cx + k * (w / 2 + 3), top + 4), (cx + k * (w / 2 + 3), bot - 4), 3)


# ------------------------------------------------------------
# Confeti
# ------------------------------------------------------------

class Confeti:
    COLORES = [PRIMARIO, ACENTO, EXITO, PELIGRO, MORADO, (22, 170, 190)]

    def __init__(self):
        self.p = []

    def lanzar(self, n=140):
        for _ in range(n):
            self.p.append([random.uniform(0, ANCHO), random.uniform(-300, -10),
                           random.uniform(-40, 40), random.uniform(80, 200),
                           random.choice(self.COLORES), random.uniform(6, 11),
                           random.uniform(0, 6.28), random.uniform(3, 8)])

    def actualizar(self, dt):
        for q in self.p:
            q[0] += q[2] * dt + math.sin(q[6]) * 20 * dt
            q[1] += q[3] * dt
            q[6] += q[7] * dt
        self.p = [q for q in self.p if q[1] < ALTO + 20]

    def dibujar(self, surf):
        for x, y, _, _, c, s, rot, _ in self.p:
            w = max(1, abs(math.cos(rot)) * s)
            pygame.draw.rect(surf, c, (x - w / 2, y - s / 3, w, s * 0.66))
