
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

    if failure > 0:
        print(red(f"There was {failure} failures, please fix."))
    else:
        print(green(f"All versions online! {success}/{tests}"))