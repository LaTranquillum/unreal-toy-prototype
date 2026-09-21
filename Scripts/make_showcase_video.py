"""Render a silent, portrait 15-second showcase of the rigged 3D Trunks.
Run: python3 Scripts/make_showcase_video.py
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
video = output / 'trunks_3d_showcase_15s.mp4'
# The 3D sequence uses idle, run, dodge and sword, with a closer camera.
with tempfile.TemporaryDirectory(prefix='showcase_frames_', dir=output) as frames:
    with (output / 'showcase-console.log').open('w') as log:
        subprocess.run([
            str(engine / 'Engine/Binaries/Mac/UnrealEditor-Cmd'),
            str(project / 'ToyPrototype.uproject'), '/Game/Toy/Maps/ToyLab',
            '-game', '-ToyShowcase', f'-ShowcaseOutput={frames}',
            '-windowed', '-ForceRes', '-ResX=720', '-ResY=1280',
            '-ExecCmds=r.SetRes 720x1280w', '-nosound', '-unattended',
            f'-abslog={output / "showcase.log"}',
        ], stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900)
    missing = [i for i in range(450) if not (Path(frames) / f'frame_{i:04d}.png').is_file()]
    if missing:
        raise SystemExit(f'Missing rendered frames: {missing[:10]}')
    for index in (0,90,125,173,300):
        shutil.copy2(Path(frames)/f'frame_{index:04d}.png',output/f'showcase_{index:04d}.png')
    subprocess.run([
        ffmpeg, '-y', '-loglevel', 'error', '-framerate', '30',
        '-i', str(Path(frames) / 'frame_%04d.png'), '-frames:v', '450',
        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', str(video),
    ], check=True, timeout=120)
print(video)
