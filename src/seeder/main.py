import os
import subprocess
import sys
from pathlib import Path


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def setup_seed_config(config_path: Path) -> None:
    repo_url = get_env("SEED_CONFIG_REPO")
    if not repo_url:
        return

    if config_path.exists() and any(config_path.iterdir()):
        print(f"[seed-config] {config_path} already populated, skipping clone")
        return

    print(f"[seed-config] Cloning {repo_url} into {config_path}")
    config_path.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["git", "clone", repo_url, str(config_path)])
    if result.returncode != 0:
        print(f"[seed-config] ERROR: git clone failed (exit {result.returncode})")
        sys.exit(1)


def find_image_dirs(seed_dir: Path, instance_name: str) -> list[tuple[str, Path]]:
    scopes = ["global"]
    if instance_name:
        scopes.append(instance_name)

    found = []
    for scope in scopes:
        scope_path = seed_dir / scope
        if not scope_path.is_dir():
            continue
        for entry in sorted(scope_path.iterdir()):
            if entry.is_dir():
                found.append((entry.name, entry))

    return found


def build_image(image_name: str, image_dir: Path) -> bool:
    print(f"[build] {image_name}:latest  ({image_dir})")
    result = subprocess.run(
        ["docker", "build", "-t", f"{image_name}:latest", "."],
        cwd=image_dir,
    )
    if result.returncode != 0:
        print(f"[build] ERROR: docker build failed for {image_name} (exit {result.returncode})")
        return False
    return True


def run_plant_seed(image_name: str, image_dir: Path, instance_name: str) -> bool:
    script = image_dir / "plant_seed.py"
    print(f"[plant] {image_name}  ({script})")
    env = os.environ.copy()
    env["SEED_INSTANCE_NAME"] = instance_name
    env["IMAGE_NAME"] = image_name
    result = subprocess.run([sys.executable, str(script)], cwd=image_dir, env=env)
    if result.returncode != 0:
        print(f"[plant] ERROR: plant_seed.py failed for {image_name} (exit {result.returncode})")
        return False
    return True


def main() -> None:
    instance_name = get_env("SEEDER_INSTANCE_NAME")
    seed_config_path = Path(get_env("SEED_CONFIG_PATH", "/seed_config"))

    setup_seed_config(seed_config_path)

    raw_dirs = get_env("SEEDER_DIRECTORIES")
    if not raw_dirs:
        print("ERROR: SEEDER_DIRECTORIES is not set")
        sys.exit(1)

    seed_dirs = [Path(d.strip()) for d in raw_dirs.split(",") if d.strip()]

    errors: list[str] = []

    for seed_dir in seed_dirs:
        if not seed_dir.is_dir():
            print(f"[skip] {seed_dir} does not exist or is not a directory")
            continue

        for image_name, image_dir in find_image_dirs(seed_dir, instance_name):
            dockerfile = image_dir / "Dockerfile"
            plant_seed = image_dir / "plant_seed.py"

            if not dockerfile.exists() and not plant_seed.exists():
                continue

            if dockerfile.exists():
                if not build_image(image_name, image_dir):
                    errors.append(f"build failed: {image_name}")

            if plant_seed.exists():
                if not run_plant_seed(image_name, image_dir, instance_name):
                    errors.append(f"plant_seed failed: {image_name}")

    if errors:
        print("\nCompleted with errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("\nAll seeds planted successfully.")


if __name__ == "__main__":
    main()
