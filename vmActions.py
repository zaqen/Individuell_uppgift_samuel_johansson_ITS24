import subprocess
import os
import sshLogin
from dotenv import load_dotenv
import sys
import msvcrt

# Ladda miljövariabler från lokala .env-filen
load_dotenv(".env.local")

vmrun = os.getenv("VMRUN_PATH")
username = "grupp3"
password = "hejsan123"
# Detta är sökvägen till node.js som används för att köra JavaScript-filerna i min Ubuntumiljö
node_path = "/usr/bin/node"
#balancer_path = "/home/grupp3/server_group3v0.1/loadBalancer.js"

#---------------------------------------------------------------------------------------------
# Funktioner för att hantera VM med vmrun, dvs vmtools
def is_vm_running(vmx_path): #kollar om VMen är igång
    """Kolla om VM redan körs via vmrun list"""
    try:
        result = subprocess.run([vmrun, "list"], capture_output=True, text=True, check=True)
        running_vms = result.stdout.splitlines()[1:]
        running_vms = [os.path.normcase(os.path.normpath(vm.strip())) for vm in running_vms]
        vmx_path_clean = os.path.normcase(os.path.normpath(vmx_path.strip()))
        return vmx_path_clean in running_vms
    except subprocess.CalledProcessError as error:
        print("Error listing VMs:", error.stderr)
        return False
    
def start_vm(vmx_path): #Startar VM med vmrun utan GUI
    """Starta VM med vmrun utan GUI."""
    if is_vm_running(vmx_path):
        print("VM är redan på.")
    try:
        print("Starting VM...")
        subprocess.run([vmrun, "start", vmx_path, "nogui"], capture_output=True, text=True, check=True, timeout=5)
        print("VM started successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to start VM:", error.stderr)
        
def stop_vm_soft(vmx_path): #Används inte för tillfället, uppenbar framtida användning
    """Stop the VM using vmrun stop soft."""
    if is_vm_running(vmx_path):
        print("VM är på.")
    try:
        print("Stänger av VM...mjukt...")
        subprocess.run([vmrun, "stop", vmx_path, "soft"], capture_output=True, text=True, check=True)
        print("VM stopped successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to stop VM:", error.stderr)
           
def stop_vm_hard(vmx_path): #stänger av VM med vmrun stop hard
    """Stäng av VM hårt"""
    if is_vm_running(vmx_path):
        print("VM är på")
    try:
        print("Stänger av VM...HÅRT!..")
        subprocess.run([vmrun, "stop", vmx_path, "hard"], capture_output=True, text=True, check=True)
        print("VM stopped successfully.")
    except subprocess.CalledProcessError as error:
        print("Failed to stop VM:", error.stderr)

def get_vm_ip(vmx_path):  #Skaffar IP-adressen för VM med vmrun getGuestIPAddress
    """Get VM IP address using vmrun getGuestIPAddress."""
    try:
        result = subprocess.run([vmrun, "getGuestIPAddress", vmx_path, "nogui"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        print("Error getting VM IP address:", error.stderr)
        return None 
#---------------------------------------------------------------------------------------------      
#Oanvända grundfunktioner i vmrun, framtidsutveckling för Status från huvudmenyn        
def list_vms(): #Används inte för tillfället
    """List all VMs using vmrun list."""
    try:
        result = subprocess.run([vmrun, "list"], capture_output=True, text=True, check=True)
        running_vms = result.stdout.splitlines()[1:]
        return running_vms
    except subprocess.CalledProcessError as error:
        print("Error listing VMs:", error.stderr)
        return []
    
def get_vm_info(vmx_path): #Används inte för tillfället 
    """Get VM information using vmrun getGuestInfo."""
    try:
        result = subprocess.run([vmrun, "getGuestInfo", vmx_path], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as error:
        print("Error getting VM info:", error.stderr)  
#---------------------------------------------------------------------------------------------
# Funktioner för att KÖRA server-skript via SSH
def run_loadBalancer(vmx_path): #Startar loadBalancer.js med vmrun
    command = "sudo node /home/grupp3/server_group3v0.1/loadBalancer.js"
    ip = get_vm_ip(vmx_path)
    
    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    # Kolla om kommandot kördes framgångsrikt
    if exit_status == 0:
        return f"Lastbalanserare har startats korrekt och körs på IP: {ip}"
    else:
        return f"Det gick inte att starta lastbalanseraren. Fel: {error}"

def run_server1(vmx_path, balancer_ip, database_ip): #Startar server1.js med vmrun
    command = f"node /home/grupp3/server_group3v0.1/server1.js {balancer_ip} {database_ip}" #testar för att se om det går att köra utan sudo
    ip = get_vm_ip(vmx_path)
    
    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    # Kolla om kommandot kördes framgångsrikt
    if exit_status == 0:
        return f"Webbservern har startats korrekt och körs på IP: {ip}"
    else:
        return f"Det gick inte att starta webbservern. Fel: {error}"
    
def run_database(vmx_path): #Startar Database.js med vmrun
    command = "sudo node /home/grupp3/server_group3v0.1/Database.js"
    ip = get_vm_ip(vmx_path)
    if ip is None:
        return "Kunde inte hämta IP-adressen för VM. Kontrollera att VM är igång eller vänta ca 15 sekunder."
    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    # Kolla om kommandot kördes framgångsrikt
    if exit_status == 0:
        return f"Databas-servern har startats korrekt och körs på IP: {ip}"
    else:
        return f"Det gick inte att starta databas-servern. Fel: {error}"

def git_pull_repo(vmx_path): #Kör git pull i server_group3v0.1 mappen via SSH
    repo_path = "/home/grupp3/server_group3v0.1"
    command = f"cd {repo_path} && git pull"
    ip = get_vm_ip(vmx_path)

    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    if exit_status == 0:
        return f"Git-pull lyckades:\n{output}"
    else:
        return f"Git-pull misslyckades. Fel:\n{error}"
#---------------------------------------------------------------------------------------------
# Funktioner för att stänga AV server-skript via SSH
def shut_down_database(vmx_path):  # Stoppar Database.js via SSH
    command = f"echo {password} | sudo -S pkill -f /home/grupp3/server_group3v0.1/Database.js"
    ip = get_vm_ip(vmx_path)

    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    if exit_status == 0:
        return f"Databas-servern har stängts av på IP: {ip}"
    else:
        return f"Det gick inte att stänga av databas-servern. Fel: {error}"

def shut_down_loadBalancer(vmx_path):  # Stoppar loadBalancer.js via SSH
    command = f"echo {password} | sudo -S pkill -f /home/grupp3/server_group3v0.1/loadBalancer.js"
    ip = get_vm_ip(vmx_path)

    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    if exit_status == 0:
        return f"Lasbalanserar-processen har stängts av på IP: {ip}"
    else:
        return f"Det gick inte att stänga av lastbalans-servicen. Fel: {error}"

def shut_down_server1(vmx_path):  # Stoppar server1.js via SSH
    command = f"echo {password} | sudo -S pkill -f /home/grupp3/server_group3v0.1/server1.js"
    ip = get_vm_ip(vmx_path)

    output, error, exit_status = sshLogin.run_ssh_command(ip, username, password, command)

    if exit_status == 0:
        return f"Webbserver skriptet har stängts av på IP: {ip}"
    else:
        return f"Det gick inte att stänga av webbsserver-servicen. Fel: {error}"
#---------------------------------------------------------------------------------------------
#Lösenordshanteringen vid inloggning. 
def get_password_with_stars(prompt=""): #Funktion för att få lösenord skyddat med stjärnor i terminalen vid inloggning
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