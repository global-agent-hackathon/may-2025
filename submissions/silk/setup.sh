#!/bin/bash

set -e


confirm() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

install_nvm() {
    export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        . "$NVM_DIR/nvm.sh"
    elif [ -s "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        . "$NVM_DIR/nvm.sh"
    fi

    if ! command -v nvm &> /dev/null; then
        echo "📦 nvm is not installed."
        if confirm "Would you like to install nvm?"; then
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

            # Load nvm to current shell session
            export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

            echo "✅ nvm has been successfully installed!"
        else
            echo "⏭️ Skipping nvm installation."
        fi
    else
        echo "✅ nvm is already installed."
    fi
}

install_node_with_nvm() {
    export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        . "$NVM_DIR/nvm.sh"
    elif [ -s "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        . "$NVM_DIR/nvm.sh"
    fi

    if ! command -v nvm &> /dev/null; then
        echo "❌ nvm is not installed. Please install nvm first."
        return 1
    fi

    if [ -z "$1" ]; then
        node_version=$(nvm ls-remote --lts | tail -1 | awk '{print $1}')
    else
        node_version="$1"
    fi

    installed_node=$(nvm ls --no-colors | grep -w "v$node_version")

    if [ -n "$installed_node" ]; then
        echo "✅ Node.js version $node_version is already installed."
        nvm use $node_version
    else
        if confirm "Would you like to install Node.js version $node_version using nvm?"; then
            nvm install $node_version
            nvm use $node_version
            echo "✅ Node.js $node_version and npm have been successfully installed with nvm!"
        else
            echo "⏭️ Skipping Node.js installation."
        fi
    fi
}

detect_package_manager() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            echo "apt"
        elif command -v yum &> /dev/null; then
            echo "yum"
        elif command -v dnf &> /dev/null; then
            echo "dnf"
        elif command -v pacman &> /dev/null; then
            echo "pacman"
        elif command -v zypper &> /dev/null; then
            echo "zypper"
        else
            echo "❌ Unsupported Linux package manager"
            return 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            echo "brew"
        else
            echo "❌ Homebrew is not installed"
            return 1
        fi
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "❌ Windows detected. Please install dependencies manually."
        return 1
    else
        echo "❌ Unsupported OS"
        return 1
    fi
}

install_dependency() {
    local package_manager=$1
    local dependency=$2

    if ! command -v $dependency &> /dev/null; then
        echo "📦 $dependency is not installed."
        if confirm "Would you like to install $dependency using $package_manager?"; then
            case $package_manager in
                apt)
                    sudo apt update && sudo apt install -y $dependency
                    ;;
                yum)
                    sudo yum install -y $dependency
                    ;;
                dnf)
                    sudo dnf install -y $dependency
                    ;;
                pacman)
                    sudo pacman -S --noconfirm $dependency
                    ;;
                zypper)
                    sudo zypper install -y $dependency
                    ;;
                brew)
                    export HOMEBREW_NO_AUTO_UPDATE=1
                    brew install $dependency
                    ;;
                *)
                    echo "❌ Unsupported package manager"
                    return 1
                    ;;
            esac
            echo "✅ $dependency has been successfully installed!"
        else
            echo "⏭️ Skipping $dependency installation."
        fi
    else
        echo "✅ $dependency is already installed."
    fi
}

install_python_and_pip() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        REQUIRED_VERSION="3.12" # Changed to 3.12 as per original prompt

        # Check if Python version is at least 3.12
        if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) == "$REQUIRED_VERSION" ]]; then
            echo "✅ Python 3 (version $PYTHON_VERSION) is already installed and meets the required version."
            return 0
        else
            echo "❌ Current Python version ($PYTHON_VERSION) is less than the required 3.12, trying to upgrade/install it..."
        fi
    else
        echo "❌ Python 3 is not installed."
    fi
    echo "⚙️ Attempting to install Python 3.12 or higher..."
    package_manager=$(detect_package_manager)
    if [ $? -eq 0 ]; then
        case $package_manager in
            apt)
                # For Debian/Ubuntu - May need deadsnakes PPA for 3.12 if not in default repos
                echo "💡 For Python 3.12 on Debian/Ubuntu, you might need to add the deadsnakes PPA."
                echo "    (e.g., sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update)"
                sudo apt update
                sudo apt install -y python3.12 python3.12-venv python3-pip
                ;;
            yum|dnf)
                # For CentOS/RHEL/Fedora
                sudo "$package_manager" install -y python3 python3-pip python3-virtualenv
                ;;
            pacman)
                # For Arch Linux
                sudo pacman -Sy --noconfirm python python-pip python-virtualenv
                ;;
            zypper)
                # For OpenSUSE
                sudo zypper install -y python3 python3-pip python3-virtualenv
                ;;
            brew)
                # For macOS using Homebrew
                export HOMEBREW_NO_AUTO_UPDATE=1
                brew install python
                ;;
            *)
                echo "❌ Unsupported package manager: $package_manager"
                return 1
                ;;
        esac
        echo "✅ Python 3, pip, and virtual environment packages have been successfully installed!"
    else
        echo "❌ Package manager detection failed: $package_manager"
    fi

    # Check for pip and venv separately as they might not be included with Python
    if ! command -v pip3 &> /dev/null; then
        echo "📦 pip3 is not installed. Installing..."
        install_dependency $package_manager python3-pip
    fi

    if ! python3 -m venv --help &> /dev/null; then
        echo "📦 venv module is not installed. Installing..."
        install_dependency $package_manager python3-venv
    fi
}

# --- Main Setup Process ---

echo "--- Starting Silk Application Setup ---"


check_and_install_dependencies() {
    install_nvm
    install_node_with_nvm 22.8.0
    install_python_and_pip
}
check_and_install_dependencies

# Ensure PATH is updated for nvm and python
export PATH="$HOME/.local/bin:$PATH" # For Python user installs
# Re-source nvm for current shell to ensure it's in PATH
if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
elif [ -s "$HOME/.nvm/nvm.sh" ]; then
    export NVM_DIR="$HOME/.nvm"
    . "$NVM_DIR/nvm.sh"
fi


# --- Backend Setup ---
echo "--- Setting up Backend ---"
cd backend

# Create and activate virtual environment
echo "Creating and activating Python virtual environment..."
python3 -m venv venv
# Check OS for activation script
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    . venv/Scripts/activate
else
    . venv/bin/activate
fi

# Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, and wheel..."
python3 -m pip install --upgrade pip setuptools wheel

echo "🐍 Using Python: $(which python3)"
echo "🐍 Using pip: $(which pip3)"

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# Set up Environment Variables for Backend
echo "
🔧 Let's set up your backend environment variables (.env file)."
echo "   These will be saved in: $(pwd)/.env"

# GEMINI_API_KEY
read -p "🔑 Enter your **GEMINI API Key** (Get one here: https://aistudio.google.com/app/apikey): " GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ GEMINI_API_KEY not provided. You will need to add it manually to backend/.env for the application to function."
fi

# GEMINI_MODEL
read -p "🤖 Enter the **GEMINI Model** name (e.g., gemini-1.5-flash, gemini-2.0-flash). Default: gemini-2.0-flash: " GEMINI_MODEL
GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.0-flash}

# DB_PATH is hardcoded
DB_PATH="app.db"

# Create a .env file and add the content
echo "📝 Creating .env file with provided environment variables..."
cat <<EOF > .env
GEMINI_MODEL=$GEMINI_MODEL
GEMINI_API_KEY=$GEMINI_API_KEY
DB_PATH=$DB_PATH
EOF
echo "Backend .env file created/updated."

deactivate # Deactivate virtual environment

cd .. # Go back to the project root

# --- Frontend Setup ---
echo "--- Setting up Frontend ---"
cd frontend

echo "Installing Node.js dependencies..."
npm install

echo "Setting up frontend environment variables (.env file)..."
cat <<EOF > .env
VITE_API_URL=http://localhost:8000
EOF
echo "Frontend .env file created/updated."

cd .. # Go back to the project root

echo "
*******************************************
*                                         *
* 🎉 Setup Completed Successfully! 🎉     *
*                                         *
* 🚀 IMPORTANT: Next Steps 🚀             *
*                                         *
* 1. Check your backend/.env:             *
* - Ensure GEMINI_API_KEY is correctly    *
* set if you skipped it during setup.     *
*                                         *
* 2. Install dependencies:                *
* Run the following command in a          *
*  terminal window:                       *
*                                         *
* $ make install                          *
*                                         *
* 3. Start the Application:               *
* Run the following command in a          *
*  terminal window:                       *
*                                         *
* $ make run                              *
*                                         *
*                                         *
*                                         *
* 🎉 You're all set! Happy coding! 🎉     *
*                                         *
*******************************************
"