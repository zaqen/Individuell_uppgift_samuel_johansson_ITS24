import subprocess
import os

def is_vm_running(vmx_path):
    """Check if the VM is already running using vmrun list."""
    try:
        result = subprocess.run(["vmrun", "list"], capture_output=True, text=True, check=True)
        running_vms = result.stdout.splitlines()[1:]  # First line is the count
        running_vms = [vm.strip().lower() for vm in running_vms]
        return vmx_path.lower() in running_vms
    except subprocess.CalledProcessError as e:
        print("Error listing VMs:", e.stderr)
        return False

def start_vm(vmx_path):
    """Start the VM using vmrun start."""
    if is_vm_running(vmx_path):
        print("VM is already running.")
        return

    try:
        print("Starting VM...")
        result = subprocess.run(["vmrun", "start", vmx_path, "gui"], capture_output=True, text=True, check=True)
        print("VM started successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to start VM:", e.stderr)