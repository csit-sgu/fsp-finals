from tenacity import (
    after_log,
    before_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)
import logging


logger = logging.getLogger("app")


base_retry = retry(
    wait=wait_exponential(min=2, max=30, multiplier=1.5),
    after=after_log(logger, logging.DEBUG),
    before=before_log(logger, log_level=logging.DEBUG),
    before_sleep=before_sleep_log(logger, logging.DEBUG),
    reraise=True,
    stop=stop_after_attempt(5),
)


@base_retry
async def send_request(client, input, model="gpt-4"):
    return (
        (
            await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": input,
                    }
                ],
                model=model,
            )
        )
        .choices[0]
        .message.content
    )
