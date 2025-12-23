import base64
import hashlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def build_pyc_wheel():
    # Source directory (current directory assumption)
    project_root = Path.cwd()
    src_dir = project_root / "src"

    # Ensure we are in the right place
    if not (src_dir / "md_spreadsheet_parser").exists():
        print(
            "Error: Could not find src/md_spreadsheet_parser. Please run from project root."
        )
        sys.exit(1)

    print(f"Building pyc wheel from {src_dir}")

    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory() as temp_dir:
        build_root = Path(temp_dir)
        lib_build_dir = build_root / "src"

        # Copy source to temp
        shutil.copytree(src_dir, lib_build_dir)

        # Compile to .pyc
        # -b: Write byte-code files to their legacy locations and names (overwrite .py or side-by-side)
        # Actually, compileall with -b writes .pyc files to the same directory as .py files,
        # NOT in __pycache__, and without the version tag. This is what we want for direct loading if we remove .py.
        print("Compiling to bytecode...")
        subprocess.check_call(
            [sys.executable, "-m", "compileall", "-b", "-f", str(lib_build_dir)]
        )

        # Remove all .py files, keep only .pyc
        print("Removing .py files...")
        for py_file in lib_build_dir.rglob("*.py"):
            py_file.unlink()

        # Verify we have .pyc files
        pyc_count = len(list(lib_build_dir.rglob("*.pyc")))
        print(f"Found {pyc_count} .pyc files.")
        if pyc_count == 0:
            print("Error: No .pyc files generated.")
            sys.exit(1)

        # Create the wheel manually or use a builder?
        # Using a builder (like build or hatch) might regenerate from source or get confused by missing .py files.
        # So we will create a wheel-compatible ZIP manually mimicking the structure 'hatch build' would produce,
        # OR we can try to hack it.
        #
        # Simplest consistent way: Create a ZIP file with .whl extension.
        # Structure:
        #   md_spreadsheet_parser/
        #     __init__.pyc
        #     ...
        #   md_spreadsheet_parser-0.5.0.dist-info/
        #     METADATA
        #     WHEEL
        #     RECORD

        # To get the valid dist-info, we can build a standard wheel first, allow it to finish,
        # then unzip it, replace contents with .pyc, and zip it back.

        print("Building standard wheel to get metadata...")
        subprocess.check_call(
            [
                "uv",
                "run",
                "python",
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(build_root / "dist"),
            ]
        )

        # Find the generated wheel
        wheels = list((build_root / "dist").glob("*.whl"))
        if not wheels:
            print("Error: Standard build failed to produce a wheel.")
            sys.exit(1)

        std_wheel = wheels[0]
        wheel_name = std_wheel.name
        print(f"Base wheel: {wheel_name}")

        # Extract the standard wheel
        unpack_dir = build_root / "unpacked"
        with zipfile.ZipFile(std_wheel, "r") as zf:
            zf.extractall(unpack_dir)

        # Replace source with compiled bytecode in the unpacked dir
        # 1. Remove .py files from unpacked package dir
        pkg_dir = unpack_dir / "md_spreadsheet_parser"
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)

        # 2. Copy our compiled .pyc tree to where the package was
        # lib_build_dir contains 'md_spreadsheet_parser' directly? Check structure.
        # src/md_spreadsheet_parser -> lib_build_dir/md_spreadsheet_parser
        shutil.copytree(lib_build_dir / "md_spreadsheet_parser", pkg_dir)

        # 3. Update RECORD file?
        # Wheels require a RECORD file with hashes. If we modify files, hashes change.
        # We should stick to verified wheel standards.
        # To update RECORD properly, we would need to calculate hashes for new .pyc files
        # and update the RECORD lines.
        #
        # OR, we can use the 'wheel' library to repack?
        # Let's try to update RECORD manually for now:
        # Iterate all files in unpack_dir, calculate hash/size, write RECORD.

        dist_info_dir = list(unpack_dir.glob("*.dist-info"))[0]
        # record_file variable removed as it was unused

        print(f"Re-packing into {wheel_name}...")

        output_dir = project_root / "dist" / "pyodide"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_wheel_path = output_dir / wheel_name

        with zipfile.ZipFile(
            output_wheel_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            # We need to write files and build the RECORD entries on the fly?
            # Or assume the RECORD is the last file to be added.

            # Actually, let's write all files EXCEPT RECORD, calculate their hashes,
            # then write RECORD at the end.

            valid_files = []
            for filepath in unpack_dir.rglob("*"):
                if filepath.is_dir():
                    continue
                if filepath.name == "RECORD":
                    continue

                arcname = filepath.relative_to(unpack_dir)

                # Check contents
                data = filepath.read_bytes()
                sha256 = hashlib.sha256(data).digest()
                hash_str = "sha256=" + base64.urlsafe_b64encode(sha256).decode(
                    "utf-8"
                ).rstrip("=")
                size = len(data)

                zf.write(filepath, arcname)
                valid_files.append((str(arcname), hash_str, size))

            # Now create RECORD content
            # The RECORD file itself is listed in RECORD with empty checksum/size
            record_lines = []
            for fname, fhash, fsize in valid_files:
                record_lines.append(f"{fname},{fhash},{fsize}")

            record_lines.append(f"{dist_info_dir.name}/RECORD,,")
            record_content = "\n".join(record_lines) + "\n"

            # Write RECORD
            zf.writestr(f"{dist_info_dir.name}/RECORD", record_content)

    print(f"Successfully created optimized wheel at {output_wheel_path}")


if __name__ == "__main__":
    build_pyc_wheel()
