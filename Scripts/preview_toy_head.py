"""Capture four facial states in the configured Unreal ToyLab (one bounded run)."""
import os
from pathlib import Path
import subprocess

project=Path(__file__).resolve().parents[1]
engine=Path(os.environ.get('UNREAL_ENGINE_ROOT','/Users/Shared/Epic Games/UE_5.8'))
output=project/'Saved/Verification/Head';output.mkdir(parents=True,exist_ok=True)
frames=(20,90,172,200)
for ext in ('png','txt'):(output/f'head_blink_closed.{ext}').unlink(missing_ok=True)
for frame in frames:
    for ext in ('png','txt'):(output/f'head_{frame:03d}.{ext}').unlink(missing_ok=True)
with (output/'console.log').open('w') as log:
    subprocess.run([str(engine/'Engine/Binaries/Mac/UnrealEditor-Cmd'),
        str(project/'ToyPrototype.uproject'),'/Game/Toy/Maps/ToyLab',
        '-game','-ToyShowcase','-ToyHeadPreview',f'-ShowcaseOutput={output}',
        '-windowed','-ForceRes','-ResX=720','-ResY=1280','-ExecCmds=r.SetRes 720x1280w',
        '-nosound','-unattended',f'-abslog={output}/runtime.log'],
        stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
for frame in frames:
    report=(output/f'head_{frame:03d}.txt').read_text()
    assert 'passed=1' in report,report
    assert (output/f'head_{frame:03d}.png').read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    print(report.strip())
print('Head preview states passed. Inspect PNGs for visual quality:',output)

blink=(output/'head_blink_closed.txt').read_text();assert 'passed=1' in blink,blink
assert (output/'head_blink_closed.png').is_file()
print(blink.strip())
