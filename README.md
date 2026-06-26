# homelab-container-seed

Builds and registers local Docker images on a homelab host via a single `docker compose up`.

The seeder container scans a set of directories for image definitions and runs
`docker build` (and/or a custom `plant_seed.py` script) for each one it finds.

## Quick start

Copy the compose file below into your project, adjust the environment variables,
and run:

```bash
docker compose up
```

```yaml
services:
  seeder:
    image: ghcr.io/andrebq/homelab-container-seed:latest
    volumes:
      # Gives the seeder access to the host Docker daemon
      - /var/run/docker.sock:/var/run/docker.sock
      # Persists the seed config between runs
      - seed_config:/seed_config
    environment:
      # Comma-separated absolute paths that contain image definitions.
      # The seed_config volume is mounted at /seed_config and is a good default.
      - SEEDER_DIRECTORIES=/seed_config
      # Optional: also searches <dir>/<SEEDER_INSTANCE_NAME>/ in addition to <dir>/global/
      - SEEDER_INSTANCE_NAME=my-homelab-node
      # If the seed_config volume is empty on first run, this repo is cloned into it
      - SEED_CONFIG_REPO=https://github.com/you/your-homelab-seeds.git
    restart: "no"
    # Uncomment to keep the container alive for inspection instead of running the seeder.
    # Useful when you want to exec in and debug. Remove for normal use.
    # command: ["tail", "-f", "/dev/null"]

volumes:
  seed_config:
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `SEEDER_DIRECTORIES` | yes | Comma-separated absolute paths to scan for image definitions. Defaults to `/seed_config`. |
| `SEEDER_INSTANCE_NAME` | no | When set, also scans `<dir>/<SEEDER_INSTANCE_NAME>/` in addition to `<dir>/global/`. |
| `SEED_CONFIG_REPO` | no | Git repository URL. Cloned into the `seed_config` volume on first run if the volume is empty. |

## Directory layout

The seeder looks for image definitions under two scopes within each directory:

```
/seed_config/
  global/                        # built on every host
    my-base-image/
      Dockerfile
    my-other-image/
      Dockerfile
      plant_seed.py
  my-homelab-node/               # only built when SEEDER_INSTANCE_NAME=my-homelab-node
    node-specific-image/
      Dockerfile
```

For each image directory the seeder finds:

1. If a `Dockerfile` is present, runs:
   ```
   docker build -t <image-name>:latest .
   ```
2. If a `plant_seed.py` is present, runs it with two environment variables injected:
   - `IMAGE_NAME` — the name of the image directory
   - `SEED_INSTANCE_NAME` — the value of `SEEDER_INSTANCE_NAME` (empty string if unset)

Both can coexist in the same directory; the build always runs before the script.

## Using a remote seed config

If your image definitions live in a Git repository, point `SEED_CONFIG_REPO` at it.
On first run, the seeder clones the repo into the `seed_config` volume. Subsequent
runs reuse the existing volume contents.

```env
SEED_CONFIG_REPO=https://github.com/you/your-homelab-seeds.git
```

## Debugging

The seeder exits as soon as it finishes (or fails). To keep the container alive so
you can `exec` into it and inspect the environment, override the command in your
`docker-compose.yml`:

```yaml
command: ["tail", "-f", "/dev/null"]
```

Then exec in and run the seeder manually:

```bash
docker compose exec seeder sh
seeder
```

Remove the `command` override once you are done.

## Building locally

```bash
make build        # build the seeder image
make test-local   # run seeder against test fixtures using uv
make test-docker  # build + run end-to-end inside the container
make clean        # remove seeder image and test images
```
