#!/bin/zsh
set -euo pipefail
PROJECT_DIR="${0:A:h:h}"
# Override when Unreal is installed outside the default Epic Games directory.
ENGINE_ROOT="${UNREAL_ENGINE_ROOT:-/Users/Shared/Epic Games/UE_5.8}"
BUILD_SCRIPT="$ENGINE_ROOT/Engine/Build/BatchFiles/Mac/Build.sh"
if [[ ! -f "$BUILD_SCRIPT" ]]; then
  print -u2 -- "Unreal build script not found: $BUILD_SCRIPT"
  print -u2 -- "Set UNREAL_ENGINE_ROOT to the root of your Unreal Engine 5.8 installation."
  exit 1
fi
"$BUILD_SCRIPT" ToyPrototypeEditor Mac Development "-Project=$PROJECT_DIR/ToyPrototype.uproject" -WaitMutex -NoHotReloadFromIDE -MaxParallelActions=2
