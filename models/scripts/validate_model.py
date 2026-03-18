"""validate_model.py - Validate the complete MuJoCo scene model.

Usage:  py -3.11 models/scripts/validate_model.py
"""
import math
import pathlib
import sys

try:
    import mujoco
    import numpy as np
except ImportError:
    sys.exit("mujoco/numpy not installed. Run: pip install mujoco numpy")

BASE = pathlib.Path(__file__).resolve().parent.parent
SCENE_PATH = BASE / "scene" / "surgbot_scene.xml"
CR5_PATH = BASE / "cr5" / "cr5_robot.xml"

# Known joint angles (degrees → radians)
RESET_DEG = [0, 32.6, -129.1, 6.7, 90, -90]
TARGET_DEG = [0, -50.2, -67.3, 112.5, 90, -90]
RESET_RAD = [math.radians(d) for d in RESET_DEG]
TARGET_RAD = [math.radians(d) for d in TARGET_DEG]


def validate_cr5_standalone():
    """Validate the standalone CR5 model."""
    print("=" * 60)
    print("Validating CR5 standalone model")
    print("=" * 60)

    import os
    orig = os.getcwd()
    os.chdir(CR5_PATH.parent)
    model = mujoco.MjModel.from_xml_path(CR5_PATH.name)
    os.chdir(orig)

    data = mujoco.MjData(model)

    print(f"  Bodies:    {model.nbody}")
    print(f"  Joints:    {model.njnt}")
    print(f"  Geoms:     {model.ngeom}")
    print(f"  Actuators: {model.nu}")

    total_mass = sum(model.body_mass)
    print(f"  Total mass: {total_mass:.2f} kg")

    # FK at zero
    mujoco.mj_forward(model, data)
    ee_id = model.site("ee_site").id
    ee_pos = data.site_xpos[ee_id]
    print(f"  EE @zero: [{ee_pos[0]:.4f}, {ee_pos[1]:.4f}, {ee_pos[2]:.4f}] m")

    # FK at RESET
    for i in range(6):
        data.qpos[i] = RESET_RAD[i]
    mujoco.mj_forward(model, data)
    ee_pos = data.site_xpos[ee_id]
    print(f"  EE @reset: [{ee_pos[0]:.4f}, {ee_pos[1]:.4f}, {ee_pos[2]:.4f}] m")

    # FK at TARGET
    for i in range(6):
        data.qpos[i] = TARGET_RAD[i]
    mujoco.mj_forward(model, data)
    ee_pos = data.site_xpos[ee_id]
    print(f"  EE @target: [{ee_pos[0]:.4f}, {ee_pos[1]:.4f}, {ee_pos[2]:.4f}] m")

    print("  CR5 standalone: PASS\n")


def validate_scene():
    """Validate the complete scene model."""
    print("=" * 60)
    print("Validating complete scene")
    print("=" * 60)

    import os
    orig = os.getcwd()
    os.chdir(SCENE_PATH.parent)
    model = mujoco.MjModel.from_xml_path(SCENE_PATH.name)
    os.chdir(orig)

    data = mujoco.MjData(model)

    print(f"  Bodies:    {model.nbody}")
    print(f"  Joints:    {model.njnt} (6 arm + 2 gripper + 4x7 instrument free)")
    print(f"  Geoms:     {model.ngeom}")
    print(f"  Actuators: {model.nu} (6 arm + 2 gripper)")
    print(f"  Sensors:   {model.nsensor}")
    print(f"  Sites:     {model.nsite}")

    total_mass = sum(model.body_mass)
    print(f"  Total mass: {total_mass:.2f} kg")

    # Check joint names
    print("\n  Joint names:")
    for i in range(min(model.njnt, 10)):
        name = model.joint(i).name
        jtype = model.jnt_type[i]
        type_str = {0: "free", 1: "ball", 2: "slide", 3: "hinge"}[jtype]
        print(f"    [{i}] {name} ({type_str})")
    if model.njnt > 10:
        print(f"    ... and {model.njnt - 10} more")

    # Check actuator names
    print("\n  Actuator names:")
    for i in range(model.nu):
        name = model.actuator(i).name
        print(f"    [{i}] {name}")

    # Run 100 steps without crashing
    for _ in range(100):
        mujoco.mj_step(model, data)
    print(f"\n  100-step simulation: OK (time={data.time:.3f}s)")

    # Load keyframe "reset" and check
    print("\n  Testing keyframes:")
    for key_id in range(model.nkey):
        key_name = model.key(key_id).name
        data.qpos[:] = model.key_qpos[key_id]
        data.ctrl[:] = model.key_ctrl[key_id]
        mujoco.mj_forward(model, data)
        ee_id = model.site("ee_site").id
        ee_pos = data.site_xpos[ee_id]
        print(f"    '{key_name}': EE=[{ee_pos[0]:.3f}, {ee_pos[1]:.3f}, {ee_pos[2]:.3f}]")

    # Test gripper open/close
    print("\n  Gripper test:")
    data.ctrl[6] = 0.0   # close
    data.ctrl[7] = 0.0
    for _ in range(200):
        mujoco.mj_step(model, data)
    left_adr = model.joint("gripper_left").qposadr[0]
    left_q = data.qpos[left_adr]
    print(f"    Closed: left_joint={left_q} m")

    data.ctrl[6] = 0.025  # open
    data.ctrl[7] = 0.025
    for _ in range(200):
        mujoco.mj_step(model, data)
    left_q = data.qpos[left_adr]
    print(f"    Open:   left_joint={left_q} m")

    print("\n  Complete scene: PASS")


def main():
    errors = 0

    if CR5_PATH.exists():
        try:
            validate_cr5_standalone()
        except Exception as e:
            print(f"  CR5 standalone: FAIL - {e}")
            errors += 1
    else:
        print(f"  SKIP: {CR5_PATH} not found")

    if SCENE_PATH.exists():
        try:
            validate_scene()
        except Exception as e:
            print(f"  Complete scene: FAIL - {e}")
            errors += 1
    else:
        print(f"  SKIP: {SCENE_PATH} not found")

    print("\n" + "=" * 60)
    if errors == 0:
        print("ALL VALIDATIONS PASSED")
    else:
        print(f"FAILED: {errors} error(s)")
    print("=" * 60)
    return errors


if __name__ == "__main__":
    sys.exit(main())
