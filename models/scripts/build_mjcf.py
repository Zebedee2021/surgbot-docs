"""build_mjcf.py - Convert CR5 URDF to MuJoCo MJCF with actuators and damping.

Usage:  py -3.11 models/scripts/build_mjcf.py
"""
import pathlib
import sys
import xml.etree.ElementTree as ET

try:
    import mujoco
except ImportError:
    sys.exit("mujoco not installed. Run: pip install mujoco")

BASE = pathlib.Path(__file__).resolve().parent.parent
CR5_DIR = BASE / "cr5"
URDF_PATH = CR5_DIR / "cr5_robot.urdf"
MJCF_PATH = CR5_DIR / "cr5_robot.xml"

# Actuator gains per joint (Nm-scale position servo)
JOINT_KP = {
    "joint1": 200,
    "joint2": 200,
    "joint3": 150,
    "joint4": 80,
    "joint5": 80,
    "joint6": 50,
}

JOINT_DAMPING = {
    "joint1": 10,
    "joint2": 10,
    "joint3": 8,
    "joint4": 5,
    "joint5": 5,
    "joint6": 3,
}


def patch_urdf_effort(urdf_path: pathlib.Path):
    """Set effort/velocity to non-zero and add MuJoCo meshdir hint."""
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    for limit in tree.iter("limit"):
        if limit.get("effort") == "0":
            limit.set("effort", "150")
        if limit.get("velocity") == "0":
            limit.set("velocity", "3.14")

    # Add <mujoco><compiler meshdir="meshes"/></mujoco> inside <robot>
    # This tells MuJoCo's URDF parser where to find mesh files
    mj_ext = root.find("mujoco")
    if mj_ext is None:
        mj_ext = ET.SubElement(root, "mujoco")
    compiler_ext = mj_ext.find("compiler")
    if compiler_ext is None:
        compiler_ext = ET.SubElement(mj_ext, "compiler")
    compiler_ext.set("meshdir", "meshes")

    patched = urdf_path.with_suffix(".patched.urdf")
    tree.write(str(patched), xml_declaration=True, encoding="utf-8")
    return patched


def convert_urdf_to_mjcf(urdf_path: pathlib.Path, mjcf_path: pathlib.Path):
    """Load URDF via MuJoCo compiler, save as MJCF, then post-process."""
    import os

    # MuJoCo resolves mesh paths relative to the model file directory,
    # so we chdir to the URDF parent to let it find meshes/
    orig_cwd = os.getcwd()
    os.chdir(urdf_path.parent)

    # Step 1: Load URDF (use just the filename since we're in its directory)
    print(f"Loading URDF: {urdf_path}")
    model = mujoco.MjModel.from_xml_path(urdf_path.name)
    print(f"  Bodies: {model.nbody}, Joints: {model.njnt}, Geoms: {model.ngeom}")

    # Step 2: Save initial MJCF
    tmp_name = mjcf_path.stem + ".raw.xml"
    mujoco.mj_saveLastXML(tmp_name, model)
    tmp_mjcf = urdf_path.parent / tmp_name
    print(f"  Raw MJCF saved: {tmp_mjcf}")

    os.chdir(orig_cwd)

    # Step 3: Post-process XML
    tree = ET.parse(tmp_mjcf)
    root = tree.getroot()

    # Ensure compiler settings
    compiler = root.find("compiler")
    if compiler is None:
        compiler = ET.SubElement(root, "compiler")
    compiler.set("angle", "radian")
    compiler.set("meshdir", "meshes")

    # Add option if missing
    option = root.find("option")
    if option is None:
        option = ET.SubElement(root, "option")
    option.set("timestep", "0.002")
    option.set("gravity", "0 0 -9.81")

    # Add default block with joint damping
    default = root.find("default")
    if default is None:
        default = ET.SubElement(root, "default")
    joint_default = default.find("joint")
    if joint_default is None:
        joint_default = ET.SubElement(default, "joint")
    joint_default.set("damping", "5")

    geom_default = default.find("geom")
    if geom_default is None:
        geom_default = ET.SubElement(default, "geom")
    geom_default.set("condim", "4")
    geom_default.set("friction", "1 0.5 0.005")

    # Set per-joint damping
    for joint in root.iter("joint"):
        jname = joint.get("name", "")
        if jname in JOINT_DAMPING:
            joint.set("damping", str(JOINT_DAMPING[jname]))

    # Add end-effector site on Link6
    for body in root.iter("body"):
        if body.get("name") in ("Link6", "link6"):
            site = ET.SubElement(body, "site")
            site.set("name", "ee_site")
            site.set("pos", "0 0 0")
            site.set("size", "0.01")
            site.set("rgba", "1 0 0 0.5")
            break

    # Add actuator block
    actuator = root.find("actuator")
    if actuator is None:
        actuator = ET.SubElement(root, "actuator")
    # Clear existing actuators
    for child in list(actuator):
        actuator.remove(child)

    for jname, kp in JOINT_KP.items():
        pos = ET.SubElement(actuator, "position")
        pos.set("name", f"{jname}_ctrl")
        pos.set("joint", jname)
        pos.set("kp", str(kp))
        # Get joint range for ctrlrange
        for joint in root.iter("joint"):
            if joint.get("name") == jname:
                jrange = joint.get("range", "")
                if jrange:
                    pos.set("ctrlrange", jrange)
                break

    # Write final MJCF
    ET.indent(tree, space="  ")
    tree.write(str(mjcf_path), xml_declaration=True, encoding="utf-8")
    print(f"  Final MJCF saved: {mjcf_path}")

    # Clean up temp files
    tmp_mjcf.unlink(missing_ok=True)

    return mjcf_path


def verify_mjcf(mjcf_path: pathlib.Path):
    """Quick verification that the MJCF loads correctly."""
    print(f"\nVerifying: {mjcf_path}")
    model = mujoco.MjModel.from_xml_path(str(mjcf_path))
    data = mujoco.MjData(model)

    print(f"  Bodies:    {model.nbody}")
    print(f"  Joints:    {model.njnt}")
    print(f"  Geoms:     {model.ngeom}")
    print(f"  Actuators: {model.nu}")

    # Print joint info
    print("\n  Joint details:")
    for i in range(model.njnt):
        name = model.joint(i).name
        jrange = model.jnt_range[i]
        print(f"    {name}: range [{jrange[0]:.2f}, {jrange[1]:.2f}] rad")

    # Compute total mass
    total_mass = sum(model.body_mass)
    print(f"\n  Total mass: {total_mass:.2f} kg")

    # Run FK at zero position
    mujoco.mj_forward(model, data)
    ee_id = model.site("ee_site").id
    ee_pos = data.site_xpos[ee_id]
    print(f"  EE position at zero: [{ee_pos[0]:.4f}, {ee_pos[1]:.4f}, {ee_pos[2]:.4f}] m")

    # Run 100 steps
    for _ in range(100):
        mujoco.mj_step(model, data)
    print(f"  100-step simulation: OK (time={data.time:.3f}s)")

    print("\n  VERIFICATION PASSED")


def main():
    if not URDF_PATH.exists():
        sys.exit(f"URDF not found: {URDF_PATH}")

    # Patch effort/velocity
    patched_urdf = patch_urdf_effort(URDF_PATH)
    print(f"Patched URDF: {patched_urdf}")

    # Convert
    convert_urdf_to_mjcf(patched_urdf, MJCF_PATH)

    # Clean up patched file
    patched_urdf.unlink(missing_ok=True)

    # Verify
    verify_mjcf(MJCF_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())
