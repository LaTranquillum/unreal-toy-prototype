"""Run real Unreal AI/physics and check fresh machine-readable results."""
from pathlib import Path
import json
import subprocess
import sys
import time

project = Path(__file__).resolve().parents[1]
engine = Path('/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd')
report = project / 'Saved/Verification/runtime.json'
started = time.time()
run = subprocess.run([
    str(engine), str(project/'ToyPrototype.uproject'), '/Game/Toy/Maps/ToyLab',
    '-game', '-ToyVerify', '-unattended', '-nosound', '-nullrhi',
    '-UseFixedTimeStep', '-FPS=60', f'-abslog={project}/Saved/Verification/runtime.log',
], timeout=300)
if not report.exists() or report.stat().st_mtime < started:
    sys.exit('FAIL: Unreal did not write a fresh verification report')
data = json.loads(report.read_text())
checks = ['wandering_pass','failed_path_recovery_pass','stuck_recovery_pass',
          'stable_collision_pass','motion_telemetry_pass','directional_flip_pass']
print(json.dumps(data, indent=2))
# Some macOS editor launchers do not propagate RequestExitWithStatus's status.
# Always check the actual report as well as the process return code.
sys.exit(0 if run.returncode == 0 and all(data.get(k) is True for k in checks) else 1)
