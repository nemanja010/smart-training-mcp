#!/usr/bin/env bash
# smart-training-mcp install script
#
# Creates symlinks for all skills into ~/.agents/skills/
# Optionally sets up the Intervals.icu MCP server (Python + .env)
# and the paper-search MCP server (uvx + optional API keys).
#
# Usage:
#   bash install.sh                      # Interactive setup
#   bash install.sh --force              # Remove existing links before creating
#   bash install.sh --skip-mcp           # Skip MCP server setup entirely
#   bash install.sh --skip-intervals     # Set up paper search but skip Intervals.icu
#   bash install.sh --skip-paper-search  # Set up Intervals.icu but skip paper search
#
# Windows users: use install.ps1 instead (PowerShell).
#   .\install.ps1

set -e

FORCE=false
SKIP_MCP=false
SKIP_INTERVALS=false
SKIP_PAPER_SEARCH=false
for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=true ;;
    --skip-mcp) SKIP_MCP=true ;;
    --skip-intervals) SKIP_INTERVALS=true ;;
    --skip-paper-search) SKIP_PAPER_SEARCH=true ;;
  esac
done

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.agents/skills"
ENV_EXAMPLE="$REPO_DIR/intervals-icu/.env.example"
ENV_FILE="$REPO_DIR/intervals-icu/.env"
ICU_DIR="$REPO_DIR/intervals-icu"
PAPER_ENV_EXAMPLE="$REPO_DIR/paper-search/.env.example"
PAPER_ENV_DIR="${HOME}/.config/paper-search-mcp"
PAPER_ENV_FILE="${PAPER_ENV_DIR}/.env"

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

# Same as link(), but into an explicit destination directory (used for .agents/skills).
link_to() {
  local src="$1"
  local name="$2"
  local dest_dir="$3"
  local dest="${dest_dir}/${name}"
  mkdir -p "$dest_dir"
  if [ "$FORCE" = true ] || [ -e "$dest" ] || [ -L "$dest" ]; then
    rm -rf "$dest"
  fi
  ln -sfn "$src" "$dest"
  echo "  [ok] $(basename "$dest_dir")/$name"
}

echo ""
echo "Installing skills to $SKILLS_DIR"
echo "(works for Claude Code and OpenCode)"
echo ""

echo "-- smart-training-mcp skills --"
for name in running-training intervals-icu cycling-training hypertrophy-training schoenfeld-hypertrophy sbs-training rp-training rp-diet program-creation assessment paper-research; do
  link "$REPO_DIR/skills/$name" "$name"
done

echo ""
echo "----------------------------------------"
count=$(ls "$SKILLS_DIR" | wc -l | tr -d ' ')
echo "$count skills in $SKILLS_DIR"

# ---------------------------------------------------------------------------
# Antigravity project-level customizations (.agents/)
#
# Antigravity does NOT read .mcp.json, .opencode/opencode.json, or the global
# ~/.agents/skills/. It discovers skills and MCP servers from .agents/ inside
# the workspace root, so this repo ships its own.
# ---------------------------------------------------------------------------
echo ""
echo "Setting up Antigravity project-level customizations (.agents/)"

AGENTS_SKILLS_DIR="$REPO_DIR/.agents/skills"
for name in running-training intervals-icu cycling-training hypertrophy-training schoenfeld-hypertrophy sbs-training rp-training rp-diet program-creation assessment paper-research; do
  link_to "$REPO_DIR/skills/$name" "$name" "$AGENTS_SKILLS_DIR"
done

# Antigravity plugins: MCP server definitions. These are checked in, so only
# write them when missing (or on --force) to avoid clobbering local edits.
mkdir -p "$REPO_DIR/.agents/plugins/intervals-icu" "$REPO_DIR/.agents/plugins/paper-search"

if [ ! -f "$REPO_DIR/.agents/plugins/intervals-icu/plugin.json" ] || [ "$FORCE" = true ]; then
  cat > "$REPO_DIR/.agents/plugins/intervals-icu/plugin.json" << 'EOF'
{
  "name": "intervals-icu",
  "description": "MCP server integration for Smart Training"
}
EOF
fi

if [ ! -f "$REPO_DIR/.agents/plugins/intervals-icu/mcp_config.json" ] || [ "$FORCE" = true ]; then
  cat > "$REPO_DIR/.agents/plugins/intervals-icu/mcp_config.json" << 'EOF'
{
  "mcpServers": {
    "intervals-icu": {
      "command": "intervals-mcp",
      "args": []
    }
  }
}
EOF
fi
echo "  [ok] .agents/plugins/intervals-icu"

# NOTE: the "mcp<2" pin is REQUIRED -- paper-search-mcp does not constrain its
# `mcp` dependency and mcp 2.x removed mcp.server.fastmcp, which it imports.
if [ ! -f "$REPO_DIR/.agents/plugins/paper-search/plugin.json" ] || [ "$FORCE" = true ]; then
  cat > "$REPO_DIR/.agents/plugins/paper-search/plugin.json" << 'EOF'
{
  "name": "paper-search",
  "description": "MCP server integration for Smart Training"
}
EOF
fi

if [ ! -f "$REPO_DIR/.agents/plugins/paper-search/mcp_config.json" ] || [ "$FORCE" = true ]; then
  cat > "$REPO_DIR/.agents/plugins/paper-search/mcp_config.json" << 'EOF'
{
  "mcpServers": {
    "paper-search": {
      "command": "uvx",
      "args": ["--from", "paper-search-mcp", "--with", "mcp<2", "paper-search-mcp"]
    }
  }
}
EOF
fi
echo "  [ok] .agents/plugins/paper-search"

echo "Antigravity setup: .agents/skills/ + .agents/plugins/ ready."

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

INTERVALS_CONFIGURED=false

setup_intervals_mcp() {
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
  echo "[!] No API key provided -- skipping Intervals.icu MCP setup."
  echo "    Set it up later by running this script again"
  echo "    or by manually editing intervals-icu/.env"
  return 0
fi

read -p "Enter your Intervals.icu athlete ID (e.g. i123456): " athlete_id
if [ -z "$athlete_id" ]; then
  echo ""
  echo "[!] No athlete ID provided -- skipping Intervals.icu MCP setup."
  echo "    Set it up later by running this script again"
  echo "    or by manually editing intervals-icu/.env"
  return 0
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

  INTERVALS_CONFIGURED=true
fi
}

# ---------------------------------------------------------------------------
# paper-search MCP server setup (uvx + optional API keys)
# ---------------------------------------------------------------------------
setup_paper_search_mcp() {
  echo ""
  echo "----------------------------------------"
  echo "Paper search MCP server setup"
  echo "----------------------------------------"
  echo ""

  # Step 1: verify uv (required -- the server is launched via uvx)
  if ! command -v uv &> /dev/null; then
    echo "[!] 'uv' not found -- the paper-search MCP server needs it."
    echo "    Install from https://docs.astral.sh/uv/getting-started/installation/"
    echo "    e.g. curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "    Then re-run: bash install.sh --skip-intervals"
    return 0
  fi
  echo "[ok] Found uv"

  # Step 2: optional API keys -> ~/.config/paper-search-mcp/.env (auto-loaded)
  if [ -f "$PAPER_ENV_FILE" ]; then
    echo "[ok] $PAPER_ENV_FILE already exists (leaving it untouched)"
  else
    mkdir -p "$PAPER_ENV_DIR"
    cp "$PAPER_ENV_EXAMPLE" "$PAPER_ENV_FILE"

    read -p "Unpaywall email for OA lookups (any valid email; blank to skip): " unpaywall_email
    if [ -n "$unpaywall_email" ]; then
      sed -i.bak "s|PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=your_email_here|PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=$unpaywall_email|" "$PAPER_ENV_FILE"
      rm -f "${PAPER_ENV_FILE}.bak"
      echo "[ok] Written $PAPER_ENV_FILE"
      echo "    Add optional keys (CORE, Semantic Scholar, OpenAlex) any time."
    else
      echo "[!] No email -- template written to $PAPER_ENV_FILE"
      echo "    Paper search works keyless; Unpaywall stays disabled until set."
    fi
  fi

  # Step 3: warm the uvx cache so the first MCP call isn't slow
  echo "Pre-downloading paper-search-mcp (first run only)..."
  if uv run --quiet --with "paper-search-mcp" --with "mcp<2" python -c "import paper_search_mcp" >/dev/null 2>&1; then
    echo "[ok] paper-search-mcp ready"
  else
    echo "[!] Could not pre-download -- the first MCP call will do it instead."
  fi

  # Step 4: register with Antigravity CLI if present
  if command -v agy &> /dev/null; then
    agy mcp add paper-search uvx -- --from paper-search-mcp --with "mcp<2" paper-search-mcp > /dev/null 2>&1 || true
    echo "[ok] Configured paper-search in Antigravity CLI (agy)"
  fi

  echo ""
  echo "Paper search is registered in .mcp.json and .opencode/opencode.json."
  echo "Restart your client to load it. Then try:"
  echo '  "Find recent research on taper length before a marathon."'
}

# ---------------------------------------------------------------------------
# Run setup
# ---------------------------------------------------------------------------
if [ "$SKIP_INTERVALS" = true ]; then
  echo ""
  echo "Intervals.icu setup skipped (--skip-intervals)."
else
  setup_intervals_mcp
fi

if [ "$SKIP_PAPER_SEARCH" = true ]; then
  echo ""
  echo "Paper search setup skipped (--skip-paper-search)."
else
  setup_paper_search_mcp
fi

echo ""
echo "----------------------------------------"
echo "Setup complete!"
echo ""
echo "  * Claude Code: skills and agents load automatically"
echo "  * OpenCode:    skills and agents load automatically"
echo "  * Antigravity: skills via .agents/skills/, MCP via .agents/plugins/"
if [ "$INTERVALS_CONFIGURED" = true ]; then
  echo "  * Intervals.icu: API key and athlete ID configured"
fi
if [ "$SKIP_PAPER_SEARCH" != true ]; then
  echo "  * Paper search: academic literature MCP server registered"
fi
echo ""
echo "Restart your client (or run /mcp) to connect the servers."
echo ""
echo "Self-contained: everything resolves inside this folder."
echo ""
