import paramiko

def run_ssh_command(ip, username, password, command):
    """
    Log in via SSH on a remote server and run a command.
    """
    try:
        # Create SSH client
        client = paramiko.SSHClient()

        # Automatically add host keys (if not already present)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the VM
        print(f"Connecting to {ip}...")
        client.connect(ip, username=username, password=password)

        # Prepare the command for running it in the background
        sudo_command = f"echo {password} | sudo -S sh -c 'nohup {command} > /dev/null 2>&1 &'"

        # Run the command in the background using exec_command
        print(f"Running command: {sudo_command}")
        stdin, stdout, stderr = client.exec_command(sudo_command)

        # Immediately return control to the script after sending the command
        print("Command has been initiated in the background.")

        # Read the output and error
        output = stdout.read().decode()
        error = stderr.read().decode()
        exit_status = stdout.channel.recv_exit_status()  # Get the exit status of the command

        # Close the SSH client session
        client.close()

        # Handle exit status
        if exit_status == 0:
            print("Command initiated successfully!")
        else:
            print(f"Error: {error}")
            print(f"Exit status: {exit_status}")

        return output, error, exit_status  # Return the output and error details

    except Exception as e:
        print(f"SSH connection failed: {e}")
        return "", str(e), None  # Return an empty string for output and error if something goes wrong
