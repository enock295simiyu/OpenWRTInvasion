#!/usr/bin/env bash


set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color


install_dependancies() {

echo -e "${GREEN}=== Python Installer ===${NC}"

# Check if Python is already installed
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}Python is already installed: $(python3 --version)${NC}"
    exit 0
fi

# Detect package manager
if command -v apt >/dev/null 2>&1; then
    PKG_MANAGER="apt"
    INSTALL_CMD="apt update && apt install -y python3 python3-pip"
elif command -v dnf >/dev/null 2>&1; then
    PKG_MANAGER="dnf"
    INSTALL_CMD="sudo dnf install -y python3 python3-pip"
elif command -v yum >/dev/null 2>&1; then
    PKG_MANAGER="yum"
    INSTALL_CMD="sudo yum install -y python3 python3-pip"
elif command -v pacman >/dev/null 2>&1; then
    PKG_MANAGER="pacman"
    INSTALL_CMD="sudo pacman -Sy --noconfirm python python-pip"
elif command -v zypper >/dev/null 2>&1; then
    PKG_MANAGER="zypper"
    INSTALL_CMD="sudo zypper install -y python3 python3-pip"
else
    echo -e "${RED}No supported package manager found.${NC}"
    echo "Supported managers: apt, dnf, yum, pacman, zypper"
    exit 1
fi

echo -e "${GREEN}Using package manager: ${PKG_MANAGER}${NC}"
echo -e "${GREEN}Installing Python 3...${NC}"
eval "$INSTALL_CMD"

# Verify installation
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}Python installed successfully: $(python3 --version)${NC}"
else
    echo -e "${RED}Python installation failed.${NC}"
    exit 1
fi

# Optional: upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
python3 -m pip install --upgrade pip

echo -e "${GREEN}Installation complete.${NC}"

}

setup_virtualenv() {
    local VENV_DIR=${1:-venv}
    local REQUIREMENTS_FILE=${2:-requirements.txt}

    echo "=== Setting up Python Virtual Environment ==="

    # Ensure Python is available
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python3 is not installed. Please install it first."
        return 1
    fi

    # Create virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment in '$VENV_DIR'..."
        python3 -m venv "$VENV_DIR"
    else
        echo "Virtual environment already exists in '$VENV_DIR'."
    fi

    # Activate the virtual environment
    echo "Activating virtual environment..."
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    echo "Upgrading pip..."
    python -m pip install --upgrade pip

    # Install dependencies if requirements.txt exists
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "Installing dependencies from $REQUIREMENTS_FILE..."
        pip install -r "$REQUIREMENTS_FILE"
    else
        echo "No requirements.txt found. Skipping dependency installation."
    fi

    echo "✅ Virtual environment setup complete."
}

download_repo_zip() {
    local REPO_URL=$1
    local TARGET_DIR=${2:-repo}

    apt install -y unzip curl

    echo "=== Downloading Repository ZIP ==="

    if [ -z "$REPO_URL" ]; then
        echo "❌ Error: Repository URL is required."
        echo "Usage: download_repo_zip <repo_url> [target_dir]"
        return 1
    fi

    # Derive the ZIP download link if it's a GitHub repo
    if [[ "$REPO_URL" == *"github.com"* ]]; then
        # Normalize GitHub URL (handle both https://github.com/user/repo and .git URLs)
        ZIP_URL=$(echo "$REPO_URL" | sed -E 's|\.git$||')/archive/refs/heads/master.zip
    else
        echo "❌ Unsupported repository host. Currently only supports GitHub."
        return 1
    fi

    # Create target directory
    mkdir -p "$TARGET_DIR"

    # Download and extract
    TMP_ZIP="/tmp/repo.zip"
    echo "Downloading ZIP from: $ZIP_URL"

    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$TMP_ZIP" "$ZIP_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$TMP_ZIP" "$ZIP_URL"
    else
        echo "❌ Neither curl nor wget found. Please install one of them."
        return 1
    fi

    echo "Extracting files to: $TARGET_DIR"
    unzip -q "$TMP_ZIP" -d "$TARGET_DIR"

    # Move extracted files out of the auto-created folder (GitHub adds repo-main/)
    local INNER_DIR
    INNER_DIR=$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)
    if [ -n "$INNER_DIR" ]; then
        mv "$INNER_DIR"/* "$TARGET_DIR"/
        rm -rf "$INNER_DIR"
    fi

    rm -f "$TMP_ZIP"
    echo "✅ Repository extracted successfully into '$TARGET_DIR'"
}

main () {
  download_repo_zip "https://github.com/enock295simiyu/OpenWRTInvasion.git" "openwrt_install"
  cd openwrt_install
  install_dependancies
  setup_virtualenv venv requirements.txt
  python nochwired_install.py
}

main

