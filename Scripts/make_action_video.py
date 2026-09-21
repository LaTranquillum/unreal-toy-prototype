"""Render a silent, portrait 15-second montage of the existing Trunks actions.
Run: python3 Scripts/make_action_video.py
Requires the built project, configured ToyLab assets, and ffmpeg on PATH.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

project = Path(__file__).resolve().parents[1]
engine = Path(os.environ.get('UNREAL_ENGINE_ROOT', '/Users/Shared/Epic Games/UE_5.8'))
ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    raise SystemExit('ffmpeg is required on PATH.')
output = project / 'Saved/Videos'
output.mkdir(parents=True, exist_ok=True)
video = output / 'trunks_actions_15s.mp4'
# The C++ montage uses 30 fps: wander, look, sway, jump, bend, crawl, sword, idle.
with tempfile.TemporaryDirectory(prefix='action_frames_', dir=output) as frames:
    with (output / 'montage-console.log').open('w') as log:
        subprocess.run([
            str(engine / 'Engine/Binaries/Mac/UnrealEditor-Cmd'),
            str(project / 'ToyPrototype.uproject'), '/Game/Toy/Maps/ToyLab',
            '-game', '-ToyMontage', f'-MontageOutput={frames}',
            '-windowed', '-ForceRes', '-ResX=720', '-ResY=1280',
            '-ExecCmds=r.SetRes 720x1280w', '-nosound', '-unattended',
            f'-abslog={output / "montage.log"}',
        ], stdout=log, stderr=subprocess.STDOUT, check=True, timeout=600)
    missing = [i for i in range(450) if not (Path(frames) / f'frame_{i:04d}.png').is_file()]
    if missing:
        raise SystemExit(f'Missing rendered frames: {missing[:10]}')
    subprocess.run([
        ffmpeg, '-y', '-loglevel', 'error', '-framerate', '30',
        '-i', str(Path(frames) / 'frame_%04d.png'), '-frames:v', '450',
        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', str(video),
    ], check=True, timeout=120)
print(video)
