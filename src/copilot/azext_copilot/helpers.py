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

    if stderr.startswith(
        "WARNING: Unable to prompt for confirmation as no tty available. Use --yes."
    ):
        if enable_logging:
            print("[HELPERS|EXECUTE] Command requires confirmation. Adding --yes.")
        execute(f"{command} --yes", enable_logging)

    if stderr.startswith(
        "WARNING: The command requires the extension load. It will be installed first."
    ):
        print("This command requires an extension. Installing...")

    if enable_logging:
        print(f"[HELPERS|EXECUTE] stdout: {stdout}")
        print(f"[HELPERS|EXECUTE] stderr: {stderr}")

    return stdout
