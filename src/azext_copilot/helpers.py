import subprocess


# This is a helper function that will execute a command and return the output
def execute(command, enable_logging):
    if enable_logging:
        print(f"[HELPERS|EXECUTE] Command: {command}")

    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate()

    has_err = bool(stderr.strip())

    if enable_logging:
        print(f"[HELPERS|EXECUTE] stdout: {stdout}")
        print(f"[HELPERS|EXECUTE] stderr: {stderr}")

    if stderr.startswith(
        "WARNING: Unable to prompt for confirmation as no tty available. Use --yes."
    ):
        if enable_logging:
            print("[HELPERS|EXECUTE] Command requires confirmation. Adding --yes.")
        has_err = False
        execute(f"{command} --yes", enable_logging)

    if stderr.startswith("WARNING: The command requires the extension"):
        has_err = False
        print(
            "This command requires an extension, which has been installed for you."
        )
        execute(command, enable_logging)

    return stdout, stderr, has_err
