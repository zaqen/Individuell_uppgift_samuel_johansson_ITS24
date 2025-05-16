import subprocess
import os



def is_vm_running(vmx_path):
    """Check if the VM is already running using vmrun list."""
    try:
        result = subprocess.run([r"Z:\vmrun.exe", "list"], capture_output=True, text=True, check=True)
        running_vms = result.stdout.splitlines()[1:]
        running_vms = [vm.strip().lower() for vm in running_vms]
        return vmx_path.lower() in running_vms
    except subprocess.CalledProcessError as error:
        print("Error listing VMs:", error.stderr)
        return False
    
def start_vm(vmx_path):
    """Start the VM using vmrun start."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
        return
    

    try:
        print("Starting VM...")
        subprocess.run([r"Z:\vmrun.exe", "start", vmx_path, "gui"], capture_output=True, text=True, check=True)
        print("VM started successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to start VM:", error.stderr)
        
def stop_vm_soft(vmx_path):
    """Stop the VM using vmrun stop soft."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
        return
    try:
        print("Stopping VM...soft...")
        subprocess.run([r"Z:\vmrun.exe", "stop", vmx_path, "soft"], capture_output=True, text=True, check=True)
        print("VM stopped successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to stop VM:", error.stderr)
        
        
def stop_vm_hard(vmx_path):
    """Stop the VM using vmrun stop hard."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
        return
    try:
        print("Stopping VM...HARD!..")
        subprocess.run([r"Z:\vmrun.exe", "stop", vmx_path, "hard"], capture_output=True, text=True, check=True)
        print("VM stopped successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to stop VM:", error.stderr)
        
        