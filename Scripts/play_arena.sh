#!/bin/zsh
set -euo pipefail
PROJECT_DIR="${0:A:h:h}"
ENGINE_ROOT="${UNREAL_ENGINE_ROOT:-/Users/Shared/Epic Games/UE_5.8}"
"$ENGINE_ROOT/Engine/Binaries/Mac/UnrealEditor" "$PROJECT_DIR/ToyPrototype.uproject" /Game/Toy/Maps/ToyLab -game -windowed -ForceRes -ResX=1280 -ResY=800 '-ExecCmds=r.SetRes 1280x800w' "$@"
