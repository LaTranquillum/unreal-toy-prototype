"""Exercise keyboard bindings through Unreal PlayerController input processing."""
from pathlib import Path
import subprocess,json,time,sys
p=Path(__file__).resolve().parents[1]
started=time.time()
r=subprocess.run(['/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd',str(p/'ToyPrototype.uproject'),'/Game/Toy/Maps/ToyLab','-game','-ToyControlVerify','-unattended','-nosound','-nullrhi','-UseFixedTimeStep','-FPS=60',f'-abslog={p}/Saved/Verification/controls.log'],timeout=180)
f=p/'Saved/Verification/controls.json'
assert f.exists() and f.stat().st_mtime>=started,'Missing fresh control report'
data=json.loads(f.read_text());print(json.dumps(data,indent=2))
sys.exit(0 if r.returncode==0 and data.get('controls_pass') else 1)
