FIXTURES := test/fixtures
IMAGE    := homelab-seeder:latest
INSTANCE := test-instance

# Images that the test fixtures will build; cleaned up by `make clean`
TEST_IMAGES := seed-global-hello:latest seed-instance-hello:latest

.PHONY: all build test test-local test-docker clean

all: test

build:
	docker build -t $(IMAGE) .

# Run seeder locally against the fixtures (no container needed for seeder itself,
# but Docker must be reachable to build the fixture images)
test-local:
	SEEDER_DIRECTORIES=$(CURDIR)/$(FIXTURES) \
	SEEDER_INSTANCE_NAME=$(INSTANCE) \
	uv run python -m seeder.main

# Run seeder inside the built container against the fixtures (full end-to-end)
test-docker: build
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/$(FIXTURES):/fixtures:ro \
		-e SEEDER_DIRECTORIES=/fixtures \
		-e SEEDER_INSTANCE_NAME=$(INSTANCE) \
		$(IMAGE)

test: test-local test-docker

clean:
	docker rmi $(IMAGE) $(TEST_IMAGES)
