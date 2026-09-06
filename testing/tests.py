
def green(text):
    return f"\033[32m{text}\033[0m"

def red(text):
    return f"\033[31m{text}\033[0m"

def full_test():
    tests = 0
    success = 0
    failure = 0

    try:
        tests += 1
        import classes
        import constants
        import testing
        print(green("Version 0.0.1 project foundation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.1 failed"))

    try:
        tests += 1
        from constants.rag import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K
        assert isinstance(CHUNK_SIZE, int)
        assert isinstance(CHUNK_OVERLAP, int)
        assert isinstance(TOP_K, int)
        assert CHUNK_SIZE > 0
        assert CHUNK_OVERLAP >= 0
        assert CHUNK_OVERLAP < CHUNK_SIZE
        assert TOP_K > 0
        print(green("Version 0.0.2 RAG constants are online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.2 failed"))

    try:
        tests += 1
        from classes.logger import Logger
        logger = Logger()
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        logger.info("Information message test.")
        logger.warning("Warning message test.")
        logger.error("Error message test.")
        print(green("Version 0.0.3 logger is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.3 failed"))

    if failure > 0:
        print(red(f"There was {failure} failures, please fix."))
    else:
        print(green(f"All versions online! {success}/{tests}"))