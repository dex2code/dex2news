import asyncio
from tools import in_out_debug


shutdown_event = asyncio.Event()
sleep_event = asyncio.Event()

@in_out_debug
def sigint_handler() -> None:
    shutdown_event.set()
    sleep_event.set()

@in_out_debug
def sigterm_handler() -> None:
    shutdown_event.set()
    sleep_event.set()


if __name__ == "__main__":
    pass
