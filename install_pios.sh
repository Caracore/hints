#!/bin/bash
#
# Hints installation script for Raspberry Pi OS (PiOS)
# Supports: Pi 500+, Pi 5, Pi 4 (ARM64/aarch64)
# Compositors: wayfire (Bookworm), labwc (Trixie+), X11/openbox
#

set -e

UV_INSTALLATION_PATH=$(mktemp -d)
BIN_DIR=""

print_header() {
  echo ""
  echo "####################################"
  echo "$1"
  echo "####################################"
  echo ""
}

check_raspberry_pi() {
  if [ ! -f /sys/firmware/devicetree/base/model ]; then
    echo "⚠️  This script is designed for Raspberry Pi. Proceeding anyway..."
    return
  fi

  MODEL=$(cat /sys/firmware/devicetree/base/model | tr -d '\0')
  echo "🍓 Detected: $MODEL"

  ARCH=$(uname -m)
  if [ "$ARCH" != "aarch64" ]; then
    echo "⚠️  Architecture is $ARCH. ARM64 (aarch64) is recommended for best compatibility."
  fi
}

install_system_dependencies() {
  print_header "Installing system dependencies for PiOS"

  sudo apt update && \
  sudo apt install -y \
    git \
    gcc \
    cmake \
    pkg-config \
    python3-dev \
    python3-numpy \
    libgirepository1.0-dev \
    libcairo2-dev \
    libdbus-1-dev \
    gir1.2-gtk-4.0 \
    at-spi2-core

  if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    print_header "Installing Wayland dependencies"
    sudo apt install -y \
      libgtk-layer-shell0 \
      grim
  fi
}

install_uv() {
  print_header "Installing UV (temporary)"

  curl -LsSf https://astral.sh/uv/install.sh | UV_NO_MODIFY_PATH=1 UV_INSTALL_DIR=$UV_INSTALLATION_PATH sh
  sudo chown -R $USER $($UV_INSTALLATION_PATH/uv tool dir)
  BIN_DIR=$($UV_INSTALLATION_PATH/uv tool dir --bin)
}

install_hints() {
  print_header "Installing hints"

  HINTS_EXPECTED_BIN_DIR="$BIN_DIR" $UV_INSTALLATION_PATH/uv tool install --force git+https://github.com/Caracore/hints@pios-support
  $UV_INSTALLATION_PATH/uv tool update-shell
}

cleanup() {
  rm -rf $UV_INSTALLATION_PATH
}

show_wayfire_keybinding_help() {
  if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    COMPOSITOR=$(ps -e -o comm | grep -m 1 -o -E -e '^wayfire$' -e '^labwc$' 2>/dev/null || true)

    if [ "$COMPOSITOR" = "wayfire" ]; then
      echo ""
      echo "📝 Wayfire keybinding setup:"
      echo "   Add to ~/.config/wayfire.ini under [command]:"
      echo ""
      echo "   binding_hints = <super> KEY_J"
      echo "   command_hints = $BIN_DIR/hints"
      echo ""
      echo "   binding_hints_scroll = <super> KEY_K"
      echo "   command_hints_scroll = $BIN_DIR/hints -m scroll"
      echo ""
    elif [ "$COMPOSITOR" = "labwc" ]; then
      echo ""
      echo "📝 labwc keybinding setup:"
      echo "   Add to ~/.config/labwc/rc.xml under <keyboard>:"
      echo ""
      echo '   <keybind key="W-j">'
      echo '     <action name="Execute" command="'$BIN_DIR'/hints" />'
      echo '   </keybind>'
      echo '   <keybind key="W-k">'
      echo '     <action name="Execute" command="'$BIN_DIR'/hints -m scroll" />'
      echo '   </keybind>'
      echo ""
    fi
  fi
}

greet() {
  echo ""
  echo "🌟 Installation complete! To setup hints, run:"
  echo "sudo env XDG_SESSION_TYPE=$XDG_SESSION_TYPE env XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP $BIN_DIR/hints --setup"
  echo ""
  show_wayfire_keybinding_help
}

# Main
check_raspberry_pi
install_system_dependencies
install_uv
install_hints
cleanup
greet
