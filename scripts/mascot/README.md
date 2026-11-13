# Mascot animation sheets

`toffee_v5.py` is a copy of the Sync mascot model (extended with animated poses: wave, cheer, point, wiggle, tilt, sleep, idle).
`animate.py` renders each frame in headless Blender (EEVEE, transparent) and packs one-row WebP sheets.

    python3 animate.py            # all clips (about 1.5 min per clip)
    python3 animate.py wave tilt  # selected clips

Needs Blender at /Applications/Blender.app and Pillow. Frames go to /private/tmp/mascot-frames (override with MASCOT_FRAMES).
Output: ../../img/mascot/anim/<clip>.webp + .json and <clip>-sm.webp (240 px). Edit frame counts / fps in CLIPS, poses in `build()` of toffee_v5.py.
`make_v5_reference.py` is the original still/idle build script, kept for reference only.
