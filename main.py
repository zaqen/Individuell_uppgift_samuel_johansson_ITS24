import os
import keyboard
import time
import subprocess
import vmActions

# Menyval
meny_item = ["Start", "Show Server IP", "Reset Counter", "Exit"]
vald = 0
# VM variabler
vmx_path = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
vmrun = r""

def rensa():
    os.system("cls" if os.name == "nt" else "clear")

def skriv_meny(selected_index):
    rensa()
    print("\n" * 3) 
    for i, item in enumerate(meny_item):
        if i == selected_index:
            #Färgar om text och bakgrund för att visa nurarande val i menyn
            print(f"\033[48;5;15m\033[30m-> {item}\033[0m")  
            print(f"   {item}")

def välj_val(vald, meny_item):
    if vald == "Start":
            if os.path.exists(vmx_path):
                vmActions.start_vm(vmx_path)
    else:
        print("Error: VMX filen hittades ej:", vmx_path)

def vald_meny_print(vald, meny_item):
    print(f"Du valde: {meny_item[vald]}".center(os.get_terminal_size().columns))

skriv_meny(vald)
while True:
    if keyboard.is_pressed("up"):
        vald = (vald - 1) % len(meny_item)
        skriv_meny(vald)
        time.sleep(0.1)

    elif keyboard.is_pressed("down"):
        vald = (vald + 1) % len(meny_item)
        skriv_meny(vald)
        time.sleep(0.1) 

    elif keyboard.is_pressed("enter"):
        rensa()
        vald_meny_print(vald, meny_item)
        välj_val(vald, meny_item)
        break