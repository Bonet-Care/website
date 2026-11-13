# Arm-raise mannequin sprite (website hero)

`mannequin.py` is a copy of Sync/web/design/mannequin/mannequin.py (Blender rig and model, unchanged).
`armraise_export.py` renders one seamless loop (32 frames, 12 fps, transparent, fixed ortho camera 15 deg off-axis,
frame 360x540, working arm blue) and writes joints.json (joints projected through the render camera).
`build_sheet.py` packs the sprite sheets and armraise.json.

Re-render:

    OUT=/tmp/armraise_frames
    /Applications/Blender.app/Contents/MacOS/Blender -b -P armraise_export.py -- $OUT
    /usr/bin/python3 build_sheet.py $OUT     # needs Pillow; writes ../../../img/figure/armraise{,-sm}.webp + armraise.json

Notes: l_* joints are the figure's arm on the image left, r_* on the image right (the working arm, "r").
Mirror for a selfie view with x -> 360 - x. Frame timing: bottom hold frames 29..3, peak frames 15..18.

Side-on scene sheet (Move demo: the figure faces the propped phone): `AZ=68 /Applications/Blender.app/Contents/MacOS/Blender -b -P armraise_export.py -- /tmp/armraise_side` then `NAME=armraise-side /usr/bin/python3 build_sheet.py /tmp/armraise_side`. The page mirrors it with CSS so the figure faces the phone on the right; the phone then shows the front camera preview (mirrored like a selfie, arm on the image right). `FRAMES=16` renders a single test frame.
