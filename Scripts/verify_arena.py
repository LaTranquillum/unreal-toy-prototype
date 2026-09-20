"""One bounded runtime verification of the local kitchen combat slice."""
import json
import os
from pathlib import Path
import subprocess

project = Path(__file__).resolve().parents[1]
engine = Path(os.environ.get('UNREAL_ENGINE_ROOT', '/Users/Shared/Epic Games/UE_5.8'))
output = project / 'Saved/Verification'
output.mkdir(parents=True, exist_ok=True)
report = output / 'arena.json'
report.unlink(missing_ok=True)
with (output / 'arena-verifier-stdout.log').open('w') as log:
    subprocess.run([
        str(engine / 'Engine/Binaries/Mac/UnrealEditor-Cmd'),
        str(project / 'ToyPrototype.uproject'), '/Game/Toy/Maps/ToyLab',
        '-game', '-ArenaVerify', '-windowed', '-ForceRes', '-ResX=1280', '-ResY=800',
        '-ExecCmds=r.SetRes 1280x800w', '-unattended',
        f'-abslog={output / "arena-verifier.log"}',
    ], stdout=log, stderr=subprocess.STDOUT, timeout=180, check=True)
result = json.loads(report.read_text())
print(json.dumps(result, indent=2))
raise SystemExit(0 if result.get('passed') else 1)
