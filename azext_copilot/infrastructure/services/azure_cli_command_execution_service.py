import subprocess


class AzureCliCommandExecution:
    def execute(self, command):
        try:
            completed_process = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return completed_process.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
