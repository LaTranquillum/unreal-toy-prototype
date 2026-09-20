"""Capture the rendered placeholder after shader compilation completes."""
from pathlib import Path
import subprocess
import time
project=Path(__file__).resolve().parents[1]
started=time.time()
subprocess.run([
    '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd',
    str(project/'ToyPrototype.uproject'),'/Game/Toy/Maps/ToyLab',
    '-game','-ToyCapture','-ForceRes','-ExecCmds=r.SetRes 720x1280w','-windowed','-ResX=720','-ResY=1280','-nosound','-unattended',
    f'-abslog={project}/Saved/Verification/visual.log',
],check=True,timeout=420)
for name in ('01-look.png','02-gesture.png','03-walk.png','04-jump.png','05-bend.png','06-crawl.png','07-sword.png'):
    image=project/'Saved/Verification'/name
    assert image.exists() and image.stat().st_mtime>=started, f'Missing fresh capture: {name}'
    assert image.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {name}'
    print(image)
