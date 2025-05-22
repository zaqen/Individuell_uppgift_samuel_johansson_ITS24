import os
#import keyboard
import msvcrt
import sys
import time
import subprocess
import vmActions
import ctypes
#import paramiko

# Menyer arrays, för val
meny_item1 = ["Start", "Status", "Stäng av VM", "Kör igång lastbalanserare", "Avsluta"]
meny_item2 = ["Backa", "Avsluta"]
vald = 0
# VM variabler
vmx_path = r"C:\Users\Samuel\Documents\Virtual Machines\Ubuntu 64-bit\Ubuntu 64-bit.vmx"
vmrun = r"Z:\vmrun.exe"
header1 = ""


# Kollar om programmet körs med administratörsrättigheter
# Om inte, avsluta programmet
if ctypes.windll.shell32.IsUserAnAdmin():
    pass    
else:
    print("Denna fil kräver administratörsrättigheter för att köras")
    print("Avslutar programmet...")
    time.sleep(1)
    sys.exit()


# Rensar terminalen
def rensa():
    os.system("cls" if os.name == "nt" else "clear")

# Skriver ut en meny med val
def skriv_meny(vald, meny_item):
    global header1
    rensa()
    if meny_item == meny_item2:
        print()
        print(header1)
        print()
    print("\n" * 3) 
    for i, item in enumerate(meny_item):
        if i == vald:
            # Highlighta itemet med en annan bakgrunds- och textfärg
            print(f"\033[48;5;15m\033[30m-> {item}\033[0m")  
        else:
            print(f"   {item}")

# Väljer ett val i menyn och kör det
def välj_val(vald, meny_item):
    nyVald = 0
    global header1
    if meny_item[vald] == "Start":
            if os.path.exists(vmx_path):
                vmActions.start_vm(vmx_path)
                meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == "Status":
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                header1 = "VM är igång."
                print(header1)
            else:
                header1 = "VM är inte igång."
                print(header1)
        else:
            print("Error: VMX filen hittades ej:", vmx_path)  
        meny_kontroll(nyVald, meny_item2)
    elif meny_item[vald] == "Avsluta":
        rensa()
        print("Avslutar programmet...")
        time.sleep(1)
        exit()
    elif meny_item[vald] == "Stäng av VM":
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                vmActions.stop_vm_hard(vmx_path)
                print("VM stängdes av.")
                pass
            else:
                print("VM är inte igång.")
                pass
            meny_kontroll(vald, meny_item2) 
    elif meny_item[vald] == "Backa":
        rensa()
        meny_kontroll(vald, meny_item1)
    elif meny_item[vald] == "Kör igång lastbalanserare":
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                print("VM är igång.")
                print("Kör igång lastbalanserare...")
                vmActions.run_loadBalancer(vmx_path)
                meny_kontroll(vald, meny_item2)
            else:
                print("VM är inte igång.")
                meny_kontroll(vald, meny_item2)
    else:
        print("Error: VMX filen hittades ej:", vmx_path)
        meny_kontroll(vald, meny_item2)

# Skriver ut vald meny i text
def vald_meny_print(vald, meny_item):
    print(f"Du valde: {meny_item[vald]}".center(os.get_terminal_size().columns))
    
# Rörelsekontroll inom menyn med piltangenter, enter och esc
def meny_kontroll(vald, meny_item):
    skriv_meny(vald, meny_item)
    while True:
        key = msvcrt.getch()

        if key == b'\xe0':  # specialtangenter (piltangenter)
            key2 = msvcrt.getch()
            if key2 == b'H':  # pil upp
                vald = (vald - 1) % len(meny_item)
                skriv_meny(vald, meny_item)
            elif key2 == b'P':  # pil ner
                vald = (vald + 1) % len(meny_item)
                skriv_meny(vald, meny_item)

        elif key == b'\r':  # Enter
            rensa()
            välj_val(vald, meny_item)
            break

        elif key == b'\x1b':  # ESC
            rensa()
            print("Avslutar programmet...")
            time.sleep(1)
            sys.exit()

# Huvudprogrammet som kör första gången programmet startas     
meny_kontroll(vald, meny_item1)

