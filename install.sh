#!/usr/bin/env bash
# smart-training-mcp install script
#
# Creates symlinks for all skills into ~/.agents/skills/
# Optionally sets up the Intervals.icu MCP server (Python + .env).
#
# Usage:
#   bash install.sh              # Interactive setup
#   bash install.sh --force      # Remove existing links before creating
#   bash install.sh --skip-mcp   # Skip MCP server setup entirely
#
# Windows users: use install.ps1 instead (PowerShell).
#   .\install.ps1

set -e

FORCE=false
SKIP_MCP=false
for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=true ;;
    --skip-mcp) SKIP_MCP=true ;;
  esac
done

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.agents/skills"
ENV_EXAMPLE="$REPO_DIR/intervals-icu/.env.example"
ENV_FILE="$REPO_DIR/intervals-icu/.env"
ICU_DIR="$REPO_DIR/intervals-icu"

mkdir -p "$SKILLS_DIR"

link() {
  local src="$1"
  local name="$2"
  local dest="${SKILLS_DIR}/${name}"
  if [ "$FORCE" = true ] || [ -e "$dest" ] || [ -L "$dest" ]; then
    rm -rf "$dest"
  fi
  ln -sf "$src" "$dest"
  echo "  [ok] $name"
}

echo ""
echo "Installing skills to $SKILLS_DIR"
echo "(works for Claude Code and OpenCode)"
echo ""

echo "-- smart-training-mcp skills --"
for name in running-training intervals-icu cycling-training hypertrophy-training schoenfeld-hypertrophy sbs-training rp-training rp-diet program-creation assessment; do
  link "$REPO_DIR/skills/$name" "$name"
done

echo ""
echo "----------------------------------------"
count=$(ls "$SKILLS_DIR" | wc -l | tr -d ' ')
echo "$count skills in $SKILLS_DIR"

# --- MCP server setup ---
if [ "$SKIP_MCP" = true ]; then
  echo ""
  echo "MCP server setup skipped (--skip-mcp)."
  echo ""
  echo "  * Claude Code: skills and agents load automatically"
  echo "  * OpenCode:    skills and agents load automatically"
  echo ""
  exit 0
fi

echo ""
echo "----------------------------------------"
echo "Intervals.icu MCP server setup"
echo "----------------------------------------"
echo ""
echo "To connect to Intervals.icu, you need your API key and athlete ID."
echo "Find them at: intervals.icu -> Settings -> Developer Settings"
echo ""

# Step 1: Ask for credentials
read -p "Enter your Intervals.icu API key: " api_key
if [ -z "$api_key" ]; then
  echo ""
  echo "[!] No API key provided -- skipping MCP setup."
  echo "    You can set it up later by running this script again"
  echo "    or by manually editing intervals-icu/.env"
  echo ""
  echo "  * Claude Code: skills and agents load automatically"
  echo "  * OpenCode:    skills and agents load automatically"
  echo ""
  exit 0
fi

read -p "Enter your Intervals.icu athlete ID (e.g. i123456): " athlete_id
if [ -z "$athlete_id" ]; then
  echo ""
  echo "[!] No athlete ID provided -- skipping MCP setup."
  echo "    You can set it up later by running this script again"
  echo "    or by manually editing intervals-icu/.env"
  echo ""
  echo "  * Claude Code: skills and agents load automatically"
  echo "  * OpenCode:    skills and agents load automatically"
  echo ""
  exit 0
fi

# Step 2: Write .env file
cp "$ENV_EXAMPLE" "$ENV_FILE"
sed -i.bak "s|API_KEY=your_intervals_api_key_here|API_KEY=$api_key|" "$ENV_FILE"
sed -i.bak "s|ATHLETE_ID=i123456|ATHLETE_ID=$athlete_id|" "$ENV_FILE"
rm -f "$ENV_FILE.bak"
echo "[ok] Written intervals-icu/.env"

# Step 3: Set env vars persistently (shell profile) and for current session
PROFILE_FILE=""
if [ -f "$HOME/.zshrc" ]; then
  PROFILE_FILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  PROFILE_FILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
  PROFILE_FILE="$HOME/.bash_profile"
elif [ -f "$HOME/.profile" ]; then
  PROFILE_FILE="$HOME/.profile"
fi

if [ -n "$PROFILE_FILE" ]; then
  sed -i.bak '/^export API_KEY=/d; /^export ATHLETE_ID=/d' "$PROFILE_FILE" 2>/dev/null
  rm -f "${PROFILE_FILE}.bak"
  echo "" >> "$PROFILE_FILE"
  echo "export API_KEY=\"$api_key\"" >> "$PROFILE_FILE"
  echo "export ATHLETE_ID=\"$athlete_id\"" >> "$PROFILE_FILE"
  echo "[ok] Added API_KEY and ATHLETE_ID to $PROFILE_FILE"
fi
export API_KEY="$api_key"
export ATHLETE_ID="$athlete_id"
echo "[ok] Set API_KEY and ATHLETE_ID (persistent + current session)"

# Step 4: Check Python and install MCP server
find_python() {
  if command -v python3 &>/dev/null; then echo "python3"
  elif command -v python &>/dev/null; then echo "python"
  else echo ""
  fi
}

PYCMD=$(find_python)

if [ -z "$PYCMD" ]; then
  echo ""
  echo "Python not found."

  if [[ "$(uname -s)" == "Darwin" ]]; then
    if command -v brew &>/dev/null; then
      echo "Installing Python via Homebrew..."
      brew install python@3.12 2>/dev/null
      PYCMD=$(find_python)
      if [ -n "$PYCMD" ]; then
        echo "[ok] Python installed via Homebrew"
      fi
    else
      echo "[!] Homebrew not found -- install it from https://brew.sh"
      echo "    Then: brew install python@3.12"
    fi
  elif [[ "$(uname -s)" == "Linux" ]]; then
    if command -v apt-get &>/dev/null && (command -v sudo &>/dev/null || [ "$(id -u)" -eq 0 ]); then
      echo "Installing Python via apt-get..."
      if [ "$(id -u)" -eq 0 ]; then
        apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv 2>/dev/null
      else
        sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-pip python3-venv 2>/dev/null
      fi
      PYCMD=$(find_python)
      if [ -n "$PYCMD" ]; then
        echo "[ok] Python installed via apt-get"
      fi
    elif command -v dnf &>/dev/null; then
      echo "Installing Python via dnf..."
      if [ "$(id -u)" -eq 0 ]; then
        dnf install -y python3 python3-pip 2>/dev/null
      else
        sudo dnf install -y python3 python3-pip 2>/dev/null
      fi
      PYCMD=$(find_python)
      if [ -n "$PYCMD" ]; then
        echo "[ok] Python installed via dnf"
      fi
    elif command -v pacman &>/dev/null; then
      echo "Installing Python via pacman..."
      if [ "$(id -u)" -eq 0 ]; then
        pacman -S --noconfirm python python-pip 2>/dev/null
      else
        sudo pacman -S --noconfirm python python-pip 2>/dev/null
      fi
      PYCMD=$(find_python)
      if [ -n "$PYCMD" ]; then
        echo "[ok] Python installed via pacman"
      fi
    else
      echo "[!] No supported package manager found."
      echo "    Install Python 3.12+ manually, then run:"
      echo "    cd intervals-icu && pip install ."
    fi
  else
    echo "[!] Unsupported OS -- install Python 3.12+ manually, then run:"
    echo "    cd intervals-icu && pip install ."
  fi
fi

if [ -n "$PYCMD" ]; then
  echo ""
  echo "Found Python: $PYCMD"
  echo "Installing intervals-icu MCP server..."
  if (cd "$ICU_DIR" && $PYCMD -m pip install -e . --quiet 2>/dev/null); then
    echo "[ok] Installed intervals-icu MCP server"
  else
    echo "[!] pip install failed -- you can run it manually:"
    echo "    cd intervals-icu && pip install ."
  fi

  # Step 5: Configure Antigravity CLI if installed
  if command -v agy &> /dev/null; then
    agy mcp add intervals-icu intervals-mcp > /dev/null 2>&1 || true
    echo "[ok] Configured Intervals.icu in Antigravity CLI (agy)"
  fi
fi

echo ""
echo "----------------------------------------"
echo "Setup complete!"
echo ""
echo "  * Claude Code: skills and agents load automatically"
echo "  * OpenCode:    skills and agents load automatically"
echo "  * Antigravity: MCP server registered (agy mcp)"
echo "  * Intervals.icu: API key and athlete ID configured"
echo ""
