"""Four-second Unreal guard/strike capture; requires configured local ToyLab."""
import os,shutil,subprocess
from pathlib import Path
p=Path(__file__).resolve().parents[1]
e=Path(os.environ.get('UNREAL_ENGINE_ROOT','/Users/Shared/Epic Games/UE_5.8'))
out=p/'Saved/Verification/UpperBody';out.mkdir(parents=True,exist_ok=True)
for f in out.glob('upper_*'):f.unlink()
with (out/'console.log').open('w') as log:
 subprocess.run([str(e/'Engine/Binaries/Mac/UnrealEditor-Cmd'),str(p/'ToyPrototype.uproject'),'/Game/Toy/Maps/ToyLab','-game','-ToyShowcase','-ToyUpperBodyPreview',f'-ShowcaseOutput={out}','-windowed','-ForceRes','-ResX=720','-ResY=1280','-ExecCmds=r.SetRes 720x1280w','-nosound','-unattended',f'-abslog={out}/runtime.log'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
for i in range(120):assert (out/f'upper_{i:04d}.png').is_file(),i
for i in (20,37,65):
 report=(out/f'upper_{i:04d}.txt').read_text();assert 'passed=1' in report,report;print(report.strip())
ffmpeg=shutil.which('ffmpeg');assert ffmpeg,'ffmpeg required'
video=p/'Saved/Videos/upper_body_fighter_4s.mp4';video.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate','30','-i',str(out/'upper_%04d.png'),'-frames:v','120','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True,timeout=90)
print(video)
