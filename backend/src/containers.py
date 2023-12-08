import docker
from main import app
import logging

log = logging.getLogger("app")
client = docker.from_env()

DEFAULT_CONTAINER_IMAGE = "ubuntu:24.04"


def build_image(dockerfile_content, image_name, image_tag="latest"):
    log.info(f"Building image {image_name}:{image_tag}")

    image, build_logs = client.images.build(
        fileobj=dockerfile_content,
        custom_context=True,
        tag=f"{image_name}:{image_tag}",
    )

    log.info(build_logs)

    return image.id


def run_container(image_name, image_tag="latest", command=None):
    container = client.containers.run(
        f"{image_name}:{image_tag}", detach=True, command=command
    )
    log.info(f"Started container: {container.id}")
    return container.id


def stop_container(container_id):
    container = client.containers.get(container_id)
    container.stop()
    log.info(f"Container stopped successfully: {container_id}")
