#!/usr/bin/env bash
# ============================================================
# Instalador de M7: El Desafío del Equipo (Ubuntu)
# 1) Instala Pygame si no está instalado.
# 2) Crea un acceso directo en el menú de aplicaciones.
# ============================================================
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

if python3 -c "import pygame" 2>/dev/null; then
    echo "✔ Pygame ya está instalado."
else
    echo "Instalando Pygame (te pedirá tu contraseña)..."
    sudo apt update
    sudo apt install -y python3-pygame
fi

chmod +x "$DIR/jugar.sh"
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/mision7.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=M7: El Desafío del Equipo
Comment=Juego serio sobre Los 7 Hábitos de la Gente Altamente Efectiva
Exec=python3 "$DIR/mision7_gui.py"
Path=$DIR
Icon=$DIR/icono.png
Terminal=false
Categories=Game;Education;
DESKTOP

echo "✔ Listo. Busca «M7» en el menú de aplicaciones,"
echo "  o ejecuta:  ./jugar.sh"
