"""Build the MuJoCo Phase A demo Colab notebook.

Layout: Dual-tray design based on 雄安现场测试 Figure 1
  - Instrument tray (器械托盘, -Y side)
  - Bed-end tray (床尾托盘, +Y side)
  - Camera 1 watches instrument tray, Camera 2 watches bed-end tray
  - Robot arm picks from instrument tray, delivers to bed-end tray

Usage: py -3.11 notebooks/build_mujoco_notebook.py
"""
import json
import pathlib

NB_PATH = pathlib.Path(__file__).resolve().parent / "mujoco_demo.ipynb"


def md(source: str):
    return {"cell_type": "markdown", "metadata": {}, "outputs": [],
            "source": [line + "\n" for line in source.strip().split("\n")]}


def code(source: str):
    return {"cell_type": "code", "metadata": {}, "outputs": [],
            "execution_count": None,
            "source": [line + "\n" for line in source.strip().split("\n")]}


cells = []

# ── Cell 0: Title ──
cells.append(md("""# MuJoCo Simulation Demo - Dobot CR5 Surgical Robot

**Phase A: Dual-Tray Clinical Workflow (器械托盘 → 床尾托盘)**

Based on the 雄安现场测试 Figure 1 layout, this notebook demonstrates:
- **Robot arm** (Dobot CR5) picks instruments from the **instrument tray** (-Y side)
- Rotates via J1 (0 → π) to face the **bed-end tray** (+Y side)
- Delivers instruments to the bed-end tray for the surgeon

| Component | Description |
|-----------|-------------|
| CR5 MJCF model | 6-DOF collaborative arm (from official URDF + STL meshes) |
| DH-3 parallel gripper | 2-finger, slide joints, red fingers on blue housing |
| 4 surgical instruments | Scalpel (yellow), tweezers (gold), scissors (green), needle holder (blue) |
| Instrument tray (器械托盘) | Blue tray on -Y side, holds instruments for pickup |
| Bed-end tray (床尾托盘) | Pink tray on +Y side, receives delivered instruments |
| Dual cameras | Camera 1 watches instrument tray, Camera 2 watches bed-end tray |
| Hospital bed | +Y far side, representing surgical field |

> Run all cells in order. First cell installs dependencies (~30s)."""))

# ── Cell 1: Install ──
cells.append(code("""# Cell 1: Install dependencies
!pip install -q mujoco mediapy numpy matplotlib

import sys
print(f"Python {sys.version}")
import mujoco; print(f"MuJoCo {mujoco.__version__}")
import mediapy as media; print("mediapy OK")
import numpy as np; print(f"NumPy {np.__version__}")"""))

# ── Cell 2: Clone repo & load model ──
cells.append(code("""# Cell 2: Clone repository and load model
import os, shutil

REPO = "https://github.com/Zebedee2021/surgbot-docs.git"
LOCAL = "/content/surgbot-docs"

if os.path.exists(LOCAL):
    shutil.rmtree(LOCAL)

!git clone --depth 1 -q {REPO} {LOCAL}

SCENE_PATH = os.path.join(LOCAL, "models", "scene", "surgbot_scene.xml")
CR5_PATH = os.path.join(LOCAL, "models", "cr5", "cr5_robot.xml")

# Load scene
os.chdir(os.path.dirname(SCENE_PATH))
model = mujoco.MjModel.from_xml_path(os.path.basename(SCENE_PATH))
data = mujoco.MjData(model)

print(f"Scene loaded!")
print(f"  Bodies:    {model.nbody}")
print(f"  Joints:    {model.njnt}")
print(f"  Actuators: {model.nu}")
print(f"  Sensors:   {model.nsensor}")
print(f"  Keyframes: {model.nkey}")
print(f"  Total mass: {sum(model.body_mass):.1f} kg")"""))

# ── Cell 3: Render helper ──
cells.append(code("""# Cell 3: Rendering helpers
import math

renderer = mujoco.Renderer(model, height=720, width=960)

def render_frame(data, camera_name=None, elevation=-25, azimuth=135, distance=2.0, lookat=None):
    \"\"\"Render a single frame with specified camera parameters.\"\"\"
    if lookat is None:
        lookat = [0.0, 0.0, 0.8]
    scene_cam = mujoco.MjvCamera()
    scene_cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    scene_cam.lookat[:] = lookat
    scene_cam.distance = distance
    scene_cam.elevation = elevation
    scene_cam.azimuth = azimuth
    renderer.update_scene(data, scene_cam)
    return renderer.render()

# Degree to radian shortcut
def deg2rad(degrees):
    return [math.radians(d) for d in degrees]

# Known poses (J1=0 faces -Y inst tray, J1=pi faces +Y bed tray)
RESET_RAD  = deg2rad([0,   32.6, -129.1, 6.7,  90, -90])   # facing inst tray
TARGET_RAD = deg2rad([180, -50.2, -67.3, 112.5, 90, -90])   # facing bed tray

print("Renderer ready: 960x720")
print(f"  RESET  (inst tray):  J1={RESET_RAD[0]:.3f} rad")
print(f"  TARGET (bed tray):   J1={TARGET_RAD[0]:.3f} rad")"""))

# ── Cell 4: Keyframe gallery ──
cells.append(code("""# Cell 4: Keyframe gallery - dual tray workflow poses
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
keyframe_names = ['home', 'reset', 'target']
titles = [
    'Home (Zero Position)',
    'Reset: Facing Instrument Tray (-Y)',
    'Target: Facing Bed-end Tray (+Y)',
]

for idx, (kname, title) in enumerate(zip(keyframe_names, titles)):
    key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, kname)
    data.qpos[:] = model.key_qpos[key_id]
    data.ctrl[:] = model.key_ctrl[key_id]
    mujoco.mj_forward(model, data)

    frame = render_frame(data, distance=2.4, elevation=-20, azimuth=135)
    axes[idx].imshow(frame)
    axes[idx].set_title(title, fontsize=13, fontweight='bold')
    axes[idx].axis('off')

    # Print EE position
    ee_id = model.site("ee_site").id
    ee = data.site_xpos[ee_id]
    axes[idx].text(0.5, 0.02, f"EE: [{ee[0]:.3f}, {ee[1]:.3f}, {ee[2]:.3f}]",
                   transform=axes[idx].transAxes, ha='center', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.suptitle('CR5 Dual-Tray Workflow Keyframes', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()"""))

# ── Cell 5: Multi-angle view ──
cells.append(code("""# Cell 5: Multi-angle view of the dual-tray scene (reset pose)
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Set to reset pose (facing instrument tray)
key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, 'reset')
data.qpos[:] = model.key_qpos[key_id]
data.ctrl[:] = model.key_ctrl[key_id]
mujoco.mj_forward(model, data)

views = [
    ("Front View",   -15, 180, 2.2),
    ("Right Side",   -15, 90,  2.2),
    ("Top Down",     -89, 90,  2.8),
    ("Perspective",  -25, 135, 2.4),
]

for idx, (title, elev, azim, dist) in enumerate(views):
    r, c = divmod(idx, 2)
    frame = render_frame(data, elevation=elev, azimuth=azim, distance=dist)
    axes[r][c].imshow(frame)
    axes[r][c].set_title(title, fontsize=13, fontweight='bold')
    axes[r][c].axis('off')

plt.suptitle('Dual-Tray Scene: CR5 + Gripper + 2 Trays + 2 Cameras (Reset Pose)',
             fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()"""))

# ── Cell 6: Instrument close-up ──
cells.append(code("""# Cell 6: Close-up of instrument tray (器械托盘, -Y side)
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Set to home (instruments visible on tray)
key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, 'home')
data.qpos[:] = model.key_qpos[key_id]
mujoco.mj_forward(model, data)

frame = render_frame(data, distance=0.65, elevation=-30, azimuth=160,
                     lookat=[0.0, -0.3, 0.76])
ax.imshow(frame)
ax.set_title('Instrument Tray Close-up (器械托盘, 4 Surgical Instruments)',
             fontsize=14, fontweight='bold')
ax.axis('off')

# Label instruments
instruments = {
    'Scalpel (黄)': 'scalpel_handle',
    'Tweezers (金)': 'tweezers',
    'Scissors (绿)': 'scissors',
    'Needle Holder (蓝)': 'needle_holder',
}
info_text = "\\n".join([f"  {name}" for name in instruments.keys()])
ax.text(0.02, 0.98, f"Instruments on tray:\\n{info_text}",
        transform=ax.transAxes, va='top', fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

plt.tight_layout()
plt.show()"""))

# ── Cell 7: Animate arm rotation from inst tray to bed tray ──
cells.append(code("""# Cell 7: Arm rotation animation - Instrument Tray (-Y) → Bed-end Tray (+Y)
# J1 rotates from 0 to π while other joints interpolate reset→target
frames = []
n_steps = 180
fps = 30

# Start from reset pose (facing instrument tray)
mujoco.mj_resetData(model, data)
key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, 'reset')
data.qpos[:] = model.key_qpos[key_id]
data.ctrl[:] = model.key_ctrl[key_id]
for i in range(6):
    data.ctrl[i] = RESET_RAD[i]
data.ctrl[6] = 0.02  # gripper open
data.ctrl[7] = 0.02
# Settle
for _ in range(500):
    mujoco.mj_step(model, data)

# Interpolate from reset to target (inst tray → bed tray)
for step in range(n_steps):
    t = step / (n_steps - 1)
    # Smooth ease-in-out
    t_smooth = 0.5 * (1 - math.cos(math.pi * t))
    for i in range(6):
        data.ctrl[i] = RESET_RAD[i] * (1 - t_smooth) + TARGET_RAD[i] * t_smooth
    data.ctrl[6] = 0.02
    data.ctrl[7] = 0.02
    for _ in range(15):
        mujoco.mj_step(model, data)
    # Render every 3rd step
    if step % 3 == 0:
        # Slowly rotate camera to follow arm
        az = 135 + t_smooth * 30
        frames.append(render_frame(data, distance=2.4, elevation=-22, azimuth=az))

print(f"Captured {len(frames)} frames")
print(f"Arm J1: 0 rad (inst tray, -Y) → π rad (bed tray, +Y)")
media.show_video(frames, fps=fps,
                 title="Arm Rotation: Instrument Tray → Bed-end Tray")"""))

# ── Cell 8: Pick-and-place from instrument tray to bed-end tray ──
cells.append(code("""# Cell 8: Pick-and-place - Scalpel from Instrument Tray → Bed-end Tray
# Full workflow: pre-grasp → close → hold → rotate arm → deliver → release → settle
frames_pick = []

# === Phase 0: Reset at instrument tray, stabilize ===
mujoco.mj_resetData(model, data)
key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, 'reset')
data.qpos[:] = model.key_qpos[key_id]
data.ctrl[:] = model.key_ctrl[key_id]
for i in range(6):
    data.ctrl[i] = RESET_RAD[i]
data.ctrl[6] = 0.03  # gripper open
data.ctrl[7] = 0.03
for _ in range(1000):
    mujoco.mj_step(model, data)

tcp_id = model.site("gripper_tcp").id

# Place scalpel between gripper pads (simulate arm already reached instrument)
scalpel_jnt = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'scalpel_free')
scalpel_qadr = model.jnt_qposadr[scalpel_jnt]
scalpel_dofadr = model.jnt_dofadr[scalpel_jnt]
tcp_pos = data.site_xpos[tcp_id].copy()
data.qpos[scalpel_qadr:scalpel_qadr+3] = tcp_pos
data.qpos[scalpel_qadr+3:scalpel_qadr+7] = [0.707, 0, 0, 0.707]
data.qvel[scalpel_dofadr:scalpel_dofadr+6] = 0
mujoco.mj_forward(model, data)

print("Phase 0: Arm at instrument tray (-Y), scalpel positioned for grasp")

# === Phase 1: Pre-grasp (show scalpel between open fingers) ===
print("Phase 1: Pre-grasp - scalpel between open fingers")
for _ in range(10):
    for __ in range(20):
        mujoco.mj_step(model, data)
    frames_pick.append(render_frame(data, distance=0.5, elevation=-20,
                                    azimuth=150, lookat=list(tcp_pos)))

# === Phase 2: Close gripper to grasp scalpel ===
print("Phase 2: Closing gripper on scalpel")
for step in range(40):
    data.ctrl[6] = 0.0  # close
    data.ctrl[7] = 0.0
    for _ in range(30):
        mujoco.mj_step(model, data)
    if step % 2 == 0:
        cur_tcp = data.site_xpos[tcp_id].copy()
        frames_pick.append(render_frame(data, distance=0.5, elevation=-20,
                                        azimuth=150, lookat=list(cur_tcp)))

# Hold grip - close-up confirmation
for _ in range(8):
    for __ in range(30):
        mujoco.mj_step(model, data)
    cur_tcp = data.site_xpos[tcp_id].copy()
    frames_pick.append(render_frame(data, distance=0.35, elevation=-15,
                                    azimuth=145, lookat=list(cur_tcp)))

# === Phase 3: Rotate arm from inst tray (-Y) to bed tray (+Y) ===
# Interpolate all 6 joints from RESET_RAD to TARGET_RAD while holding grip
print("Phase 3: Rotating arm from instrument tray to bed-end tray (J1: 0→π)")
n_rotate = 120
scene_center = [0.0, 0.0, 0.85]
for step in range(n_rotate):
    t = step / (n_rotate - 1)
    t_smooth = 0.5 * (1 - math.cos(math.pi * t))
    for i in range(6):
        data.ctrl[i] = RESET_RAD[i] * (1 - t_smooth) + TARGET_RAD[i] * t_smooth
    data.ctrl[6] = 0.0  # keep gripping
    data.ctrl[7] = 0.0
    for _ in range(20):
        mujoco.mj_step(model, data)
    if step % 3 == 0:
        az = 135 + t_smooth * 30
        d = 0.6 + t_smooth * 1.2
        frames_pick.append(render_frame(data, distance=d, elevation=-22,
                                        azimuth=az, lookat=scene_center))

# Stabilize at target pose
for _ in range(10):
    for __ in range(20):
        mujoco.mj_step(model, data)

# === Phase 4: Show arm at bed-end tray, zoom in ===
print("Phase 4: Arrived at bed-end tray (+Y)")
cur_tcp = data.site_xpos[tcp_id].copy()
for _ in range(8):
    for __ in range(20):
        mujoco.mj_step(model, data)
    frames_pick.append(render_frame(data, distance=0.5, elevation=-18,
                                    azimuth=170, lookat=list(cur_tcp)))

# === Phase 5: Open gripper - release scalpel onto bed-end tray ===
print("Phase 5: Releasing scalpel onto bed-end tray")
for step in range(40):
    data.ctrl[6] = 0.03  # open
    data.ctrl[7] = 0.03
    for _ in range(30):
        mujoco.mj_step(model, data)
    if step % 2 == 0:
        frames_pick.append(render_frame(data, distance=0.8, elevation=-22,
                                        azimuth=165, lookat=[0.0, 0.3, 0.8]))

# === Phase 6: Let scalpel settle on bed-end tray (physics!) ===
print("Phase 6: Scalpel settling on bed-end tray surface")
for step in range(30):
    for _ in range(50):
        mujoco.mj_step(model, data)
    if step % 2 == 0:
        frames_pick.append(render_frame(data, distance=1.0, elevation=-25,
                                        azimuth=160, lookat=[0.0, 0.3, 0.8]))

# Final check
scalpel_pos = data.qpos[scalpel_qadr:scalpel_qadr+3].copy()
bed_tray_y = 0.3
print(f"\\nScalpel final pos: [{scalpel_pos[0]:.3f}, {scalpel_pos[1]:.3f}, {scalpel_pos[2]:.3f}]")
print(f"Bed-end tray center: y={bed_tray_y}")
print(f"Distance to bed tray (y): {abs(scalpel_pos[1] - bed_tray_y):.3f} m")
print(f"Captured {len(frames_pick)} frames")
print("Workflow: instrument tray → grasp → rotate (J1: 0→π) → bed-end tray → release")
media.show_video(frames_pick, fps=15,
                 title="Pick-and-Place: Instrument Tray → Bed-end Tray")"""))

# ── Cell 9: Model summary ──
cells.append(code("""# Cell 9: Complete model summary
print("=" * 60)
print("SURGBOT MuJoCo MODEL SUMMARY - Dual-Tray Layout")
print("=" * 60)

print(f"\\nRobot: Dobot CR5AF (6-DOF collaborative arm)")
print(f"Gripper: DH-3 (2-finger parallel, slide joints)")
print(f"Layout: Based on 雄安现场测试 Figure 1")
print(f"  Instrument Tray (器械托盘): -Y side, blue, holds 4 instruments")
print(f"  Bed-end Tray (床尾托盘): +Y side, pink, delivery target")
print(f"  Camera 1: watches instrument tray")
print(f"  Camera 2: watches bed-end tray")
print(f"  Hospital Bed: +Y far side")

print(f"\\n--- Model Statistics ---")
print(f"Bodies:     {model.nbody}")
print(f"Joints:     {model.njnt} (6 arm + 2 gripper + 4 free)")
print(f"Geoms:      {model.ngeom}")
print(f"Actuators:  {model.nu} (6 arm + 2 gripper)")
print(f"Sensors:    {model.nsensor} (force, torque, 2x touch)")
print(f"Keyframes:  {model.nkey} (home, reset, target)")
print(f"Total mass: {sum(model.body_mass):.1f} kg")

print(f"\\n--- Joint Ranges ---")
for i in range(model.njnt):
    jname = model.joint(i).name
    jtype = {0: "free", 1: "ball", 2: "slide", 3: "hinge"}[model.jnt_type[i]]
    if jtype == "hinge":
        lo, hi = model.jnt_range[i]
        print(f"  {jname:20s} [{math.degrees(lo):7.1f}, {math.degrees(hi):7.1f}] deg")
    elif jtype == "slide":
        lo, hi = model.jnt_range[i]
        print(f"  {jname:20s} [{lo*1000:7.1f}, {hi*1000:7.1f}] mm")
    else:
        print(f"  {jname:20s} ({jtype})")

print(f"\\n--- Dual-Tray Workflow EE Positions ---")
for kname in ['home', 'reset', 'target']:
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, kname)
    data.qpos[:] = model.key_qpos[kid]
    mujoco.mj_forward(model, data)
    ee = data.site_xpos[model.site("ee_site").id]
    j1_deg = math.degrees(data.qpos[0])
    facing = "center" if abs(j1_deg) < 5 else ("-Y inst tray" if j1_deg < 90 else "+Y bed tray")
    print(f"  {kname:8s}: EE=[{ee[0]:.3f}, {ee[1]:.3f}, {ee[2]:.3f}] J1={j1_deg:.0f}° → {facing}")

print(f"\\n--- Phase A Status ---")
print(f"  CR5 URDF -> MJCF conversion:       DONE")
print(f"  DH-3 gripper model:                 DONE")
print(f"  Instrument models (4):              DONE")
print(f"  Dual-tray scene assembly:           DONE")
print(f"  Dual-camera placement:              DONE")
print(f"  Colab demo (dual-tray workflow):    DONE")
print(f"\\nReady for Phase B (control logic) and Phase C (Colab integration)")
print("=" * 60)"""))

# ── Build notebook ──
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {"name": "python", "version": "3.10.0"},
        "colab": {
            "provenance": [],
            "name": "SurgBot MuJoCo Demo - Dual-Tray Workflow"
        }
    },
    "cells": cells
}

NB_PATH.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Notebook written: {NB_PATH}")
print(f"  Cells: {len(cells)} ({sum(1 for c in cells if c['cell_type']=='code')} code, "
      f"{sum(1 for c in cells if c['cell_type']=='markdown')} markdown)")
