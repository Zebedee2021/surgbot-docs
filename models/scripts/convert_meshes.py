"""convert_meshes.py - DAE (COLLADA) → STL batch converter for CR5 meshes.

Usage:  py -3.11 models/scripts/convert_meshes.py
"""
import pathlib
import sys

try:
    import trimesh
except ImportError:
    sys.exit("trimesh not installed. Run: pip install trimesh")

MESH_DIR = pathlib.Path(__file__).resolve().parent.parent / "cr5" / "meshes"

DAE_FILES = [
    "base_link.dae",
    "Link1.dae",
    "Link2.dae",
    "Link3.dae",
    "Link4.dae",
    "Link5.dae",
    "Link6.dae",
]


def convert_dae_to_stl(dae_path: pathlib.Path) -> pathlib.Path:
    """Load a DAE file and export as binary STL."""
    stl_path = dae_path.with_suffix(".stl")
    scene = trimesh.load(str(dae_path), force="scene")

    if isinstance(scene, trimesh.Scene):
        mesh = scene.to_geometry()
    else:
        mesh = scene

    mesh.export(str(stl_path), file_type="stl")
    return stl_path


def main():
    ok, fail = 0, 0
    for name in DAE_FILES:
        dae_path = MESH_DIR / name
        if not dae_path.exists():
            print(f"  SKIP  {name} (not found)")
            fail += 1
            continue
        try:
            stl_path = convert_dae_to_stl(dae_path)
            size_kb = stl_path.stat().st_size / 1024
            print(f"  OK    {name} -> {stl_path.name}  ({size_kb:.0f} KB)")
            ok += 1
        except Exception as e:
            print(f"  FAIL  {name}: {e}")
            fail += 1

    print(f"\nResult: {ok} converted, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
