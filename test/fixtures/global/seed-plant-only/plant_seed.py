import os
import sys

image = os.environ.get("IMAGE_NAME", "(unset)")
instance = os.environ.get("SEED_INSTANCE_NAME", "(unset)")

print(f"plant_seed.py OK  image={image!r}  instance={instance!r}")

if not image or image == "(unset)":
    print("ERROR: IMAGE_NAME was not set", file=sys.stderr)
    sys.exit(1)
