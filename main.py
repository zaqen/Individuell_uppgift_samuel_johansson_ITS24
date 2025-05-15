import os
import keyboard
import time
import subprocess
import vmActions

# Menyval
meny_item1 = ["Start", "Status", "Exit"]
vald = 0
# VM variabler
vmx_path = r"C:\Users\Samuel\Documents\Virtual Machines\Ubuntu 64-bit.vmx"
vmrun = r""

def rensa():
    os.system("cls" if os.name == "nt" else "clear")

def skriv_meny(vald, meny_item):
    rensa()
    print("\n" * 3) 
    for i, item in enumerate(meny_item):
        if i == vald:
            # Highlight selected item
            print(f"\033[48;5;15m\033[30m-> {item}\033[0m")  
        else:
            print(f"   {item}")


def välj_val(vald, meny_item):
    if meny_item[vald] == "Start":
            if os.path.exists(vmx_path):
                vmActions.start_vm(vmx_path)
    elif meny_item[vald] == "Status":
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                print("VM är igång.")
            else:
                print("VM är inte igång.")
        else:
            print("Error: VMX filen hittades ej:", vmx_path)
    elif meny_item[vald] == "Exit":
        rensa()
        print("Avslutar programmet...")
        time.sleep(1)
        exit()
    else:
        print("Error: VMX filen hittades ej:", vmx_path)

def vald_meny_print(vald, meny_item):
    print(f"Du valde: {meny_item[vald]}".center(os.get_terminal_size().columns))
    
def meny_kontroll(vald, meny_item): 
    skriv_meny(vald, meny_item)
    while True:
        if keyboard.is_pressed("up"):
            vald = (vald - 1) % len(meny_item)
            skriv_meny(vald, meny_item)
            time.sleep(0.1)

        elif keyboard.is_pressed("down"):
            vald = (vald + 1) % len(meny_item)
            skriv_meny(vald, meny_item)
            time.sleep(0.1) 

        elif keyboard.is_pressed("enter"):
            rensa()
            vald_meny_print(vald, meny_item)
            välj_val(vald, meny_item)
            break
        
meny_kontroll(vald, meny_item1)

