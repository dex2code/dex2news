from loguru import logger


@logger.catch
def in_out_debug(func):
    @logger.catch
    def wrapper(*args, **kwargs):
        logger.debug(f"--> In function {func.__name__}() with {args=}, {kwargs=}")
        result = func(*args, **kwargs)
        logger.debug(f"<-- Out function {func.__name__}() with {result=}")
        return result
    return wrapper


if __name__ == "__main__":
    pass