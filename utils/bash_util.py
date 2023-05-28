import subprocess

@staticmethod
def execute_command(command: str):
    """
        Executes a command in the shell and returns the output.
        # Arguments
            command: The command to execute.
        # Returns
            The output of the command.
    """
    return subprocess.check_output(command, shell=True).decode("utf-8")
