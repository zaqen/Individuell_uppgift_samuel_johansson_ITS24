import subprocess
import os
import sshLogin
from dotenv import load_dotenv
import sys
import msvcrt

load_dotenv(".env.local")

vmrun = os.getenv("VMRUN_PATH")
#vmx_path = r"C:\Users\Samuel\Documents\Virtual Machines\Ubuntu 64-bit\Ubuntu 64-bit.vmx"
node_path = "/usr/bin/node"
balancer_path = "/home/grupp3/server_group3v0.1/loadBalancer.js"

def is_vm_running(vmx_path):
    """Check if the VM is already running using vmrun list."""
    try:
        result = subprocess.run([vmrun, "list"], capture_output=True, text=True, check=True)
        running_vms = result.stdout.splitlines()[1:]
        running_vms = [os.path.normcase(os.path.normpath(vm.strip())) for vm in running_vms]
        vmx_path_clean = os.path.normcase(os.path.normpath(vmx_path.strip()))
        return vmx_path_clean in running_vms
    except subprocess.CalledProcessError as error:
        print("Error listing VMs:", error.stderr)
        return False
    
def start_vm(vmx_path):
    """Start the VM using vmrun start."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
    try:
        print("Starting VM...")
        subprocess.run([vmrun, "start", vmx_path, "nogui"], capture_output=True, text=True, check=True, timeout=5)
        print("VM started successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to start VM:", error.stderr)
        
def stop_vm_soft(vmx_path):
    """Stop the VM using vmrun stop soft."""
    if is_vm_running(vmx_path):
        print("VM is running.")
    try:
        print("Stopping VM...softly...")
        subprocess.run([vmrun, "stop", vmx_path, "soft"], capture_output=True, text=True, check=True)
        print("VM stopped successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to stop VM:", error.stderr)
        
        
def stop_vm_hard(vmx_path):
    """Stop the VM using vmrun stop hard."""
    if is_vm_running(vmx_path):
        print("VM is running.")
    try:
        print("Stopping VM...HARD!..")
        subprocess.run([vmrun, "stop", vmx_path, "hard"], capture_output=True, text=True, check=True)
        print("VM stopped successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to stop VM:", error.stderr)
        

def suspend_vm(vmx_path):
    """Suspend the VM using vmrun suspend."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
        return
    try:
        print("Suspending VM...")
        subprocess.run([vmrun, "suspend", vmx_path], capture_output=True, text=True, check=True)
        print("VM suspended successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to suspend VM:", error.stderr)
        
def reset_vm(vmx_path): 
    """Reset the VM using vmrun reset."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
        return
    try:
        print("Resetting VM...")
        subprocess.run([vmrun, "reset", vmx_path], capture_output=True, text=True, check=True)
        print("VM reset successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to reset VM:", error.stderr)
        
def list_vms():
    """List all VMs using vmrun list."""
    try:
        result = subprocess.run([vmrun, "list"], capture_output=True, text=True, check=True)
        running_vms = result.stdout.splitlines()[1:]
        return running_vms
    except subprocess.CalledProcessError as error:
        print("Error listing VMs:", error.stderr)
        return []
    
def get_vm_info(vmx_path):
    """Get VM information using vmrun getGuestInfo."""
    try:
        result = subprocess.run([vmrun, "getGuestInfo", vmx_path], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as error:
        print("Error getting VM info:", error.stderr)
    
def get_vm_ip(vmx_path):  
    """Get VM IP address using vmrun getGuestIPAddress."""
    try:
        result = subprocess.run([vmrun, "getGuestIPAddress", vmx_path, "nogui"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        print("Error getting VM IP address:", error.stderr)
        return None
    
def run_loadBalancer(vmx_path):
    command = "sudo node /home/grupp3/server_group3v0.1/loadBalancer.js"
    username = "grupp3"
    password = "hejsan123"
    ip = get_vm_ip(vmx_path)
    
    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    # Kolla om kommandot kördes framgångsrikt
    if exit_status == 0:
        return f"Lastbalanserare har startats korrekt och körs på IP: {ip}"
    else:
        return f"Det gick inte att starta lastbalanseraren. Fel: {error}"

def run_server1(vmx_path, balancer_ip, database_ip):
    command = f"node /home/grupp3/server_group3v0.1/server1.js {balancer_ip} {database_ip}" #testar för att se om det går att köra utan sudo
    username = "grupp3"
    password = "hejsan123"
    ip = get_vm_ip(vmx_path)
    
    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    # Kolla om kommandot kördes framgångsrikt
    if exit_status == 0:
        return f"Webbservern har startats korrekt och körs på IP: {ip}"
    else:
        return f"Det gick inte att starta webbservern. Fel: {error}"
    
def run_database(vmx_path):
    command = "sudo node /home/grupp3/server_group3v0.1/Database.js"
    username = "grupp3"
    password = "hejsan123"
    ip = get_vm_ip(vmx_path)

    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    # Kolla om kommandot kördes framgångsrikt
    if exit_status == 0:
        return f"Databas-servern har startats korrekt och körs på IP: {ip}"
    else:
        return f"Det gick inte att starta databas-servern. Fel: {error}"
    
def get_password_with_stars(prompt=""):
    print(prompt, end='', flush=True)
    password = ""
    while True:
        char = msvcrt.getch()
        if char in {b'\r', b'\n'}:  # Enter
            print()  # Go to next line
            break
        elif char == b'\x08':  # Backspace
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        elif char == b'\x1b':  # ESC
            print("\nAvbrutet.")
            sys.exit()
        else:
            password += char.decode('utf-8')
            print('*', end='', flush=True)
    return password