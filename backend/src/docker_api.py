import logging

from context import ctx

log = logging.getLogger("app")


def get_client(user_id):
    log.info(f"Getting new client for {user_id}")
    host_entry = list(sorted(ctx.docker_pool, key=lambda x: x[0]))[0]

    return host_entry[1]


def build_image(client, dockerfile_content, image_name, image_tag="latest"):
    log.info(f"Building image {image_name}:{image_tag}")

    image, build_logs = client.images.build(
        fileobj=dockerfile_content,
        custom_context=True,
        tag=f"{image_name}:{image_tag}",
    )

    log.info(build_logs)

    return image.id


def run_container(
    client, image_name, image_tag="latest", command=None, validator=None, **kwargs
):
    container = client.containers.run(
        f"{image_name}:{image_tag}", detach=True, command=command, tty=True
    )
    log.info(f"Started container: {container.id}")
    return container.id


def stop_container(client, container_id):
    container = client.containers.get(container_id)
    container.stop()
    log.info(f"Container stopped successfully: {container_id}")
