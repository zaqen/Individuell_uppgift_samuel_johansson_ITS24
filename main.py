import os
import msvcrt
import sys
import time
import subprocess
import vmActions
import ctypes
from dotenv import load_dotenv

# Menyer arrays, för val
meny_item1 = ["Välj VM att hantera", "Välj Javascript att köra", "Starta VM", "Stäng av VM", "Status", "Avsluta"]
meny_item2 = ["Backa", "Avsluta"]
meny_item3 = ["Lastbalanserare", "Webbserver 1", "Webbserver 2", "MySQL Databas", "Backa", "Avsluta"]
meny_item4 = ["Kör Lastbalanserare", "Kör Webbserver", "Kör Databas", "Backa", "Avsluta"]
vald = 0
# VM variabler
vmx_path = "" #r"C:\Users\Samuel\Documents\Virtual Machines\Ubuntu 64-bit\Ubuntu 64-bit.vmx"
#vmrun = r"Z:\vmrun.exe"
activeVM = "ingen VM"



header1 = "" # Handling utförd av val
header2 = "" # Vilket val du gjorde
header3 = f"Du hanterar {activeVM} för tillfället."

# Kollar om programmet körs med administratörsrättigheter
# Om inte, avsluta programmet
def is_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        pass    
    else:
        print("Denna fil kräver administratörsrättigheter för att köras")
        print("Avslutar programmet...")
        time.sleep(1)
        sys.exit()
is_admin()

load_dotenv(".env.dev")
VM_PATH_LIST = ["", "", "", ""]  # Lista för VM paths
# Hämtar VM paths från miljövariabler
VM_PATH_LIST[0] = os.getenv("VM_LOAD_BALANCER_PATH")
VM_PATH_LIST[1] = os.getenv("VM_WEB_SERVER_1_PATH")
VM_PATH_LIST[2] = os.getenv("VM_WEB_SERVER_2_PATH")
VM_PATH_LIST[3] = os.getenv("VM_DATABASE_PATH")
vmrun = os.getenv("VMRUN_PATH")
# Rensar terminalen
def rensa():
    os.system("cls" if os.name == "nt" else "clear")

# Skriver ut en meny med val
def skriv_meny(vald, meny_item):
    global header1
    global header2
    rensa()
    
    vald_meny_print()
    print(header1)
        
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
    global header2
    global activeVM
    global vmx_path
    
    
    #Fem enklare val i menyn, starta, status, avsluta, stäng av VM och backa
    if meny_item[vald] == "Starta VM":
        if os.path.exists(vmx_path):
            vmActions.start_vm(vmx_path)
            header1 = "VM startad."
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item2)
        else:
            print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == "Status":
        header2 = meny_item[vald]
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                ip = vmActions.get_vm_ip(vmx_path)
                header1 = f"{activeVM} är igång med IP: {ip}"
            else:
                header1 = "VM är inte igång."
        else:
            print("Error: VMX filen hittades ej:", vmx_path)  
        meny_kontroll(nyVald, meny_item2)
    elif meny_item[vald] == "Avsluta":
        rensa()
        print("Avslutar programmet...")
        time.sleep(1)
        exit()
    elif meny_item[vald] == "Stäng av VM":
        header2 = meny_item[vald]
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                vmActions.stop_vm_hard(vmx_path)
                print("VM stängdes av.")
                header1 = "VM stängdes av."
                pass
            else:
                print("VM är inte igång.")
                pass
            meny_kontroll(vald, meny_item2) 
    elif meny_item[vald] == "Backa":
        rensa()
        header2 = meny_item[vald]
        vald = 0  # Nollställ vald index
        meny_kontroll(vald, meny_item1)
        
    # Start av nya menyer
    elif meny_item[vald] == "Välj VM att hantera":
        rensa()
        header2 = meny_item[vald]
        vald = 0  # Nollställ vald index
        meny_kontroll(vald, meny_item3)
    elif meny_item[vald] == "Välj Javascript att köra":
        rensa()
        header2 = meny_item[vald]
        vald = 0  # Nollställ vald index
        meny_kontroll(vald, meny_item4)
        
        
    # Kör-kommandon för de tre olika Javascripten
    elif meny_item[vald] == "Kör Lastbalanserare": #Kör igång filen loadBalancer.js i VMen
        header2 = meny_item[vald]
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                print("VM är igång.")
                print("Kör igång lastbalanserare...")
                header1 = vmActions.run_loadBalancer(vmx_path)
                meny_kontroll(vald, meny_item2)
            else:
                print("VM är inte igång.")
                meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == "Kör Webbserver":  #Kör igång filen server1.js i VMen
        #Behöver mer info, det krävs IP från både lastbalanseraren och databasen för att kunna köra igång servern korrekt
        header2 = meny_item[vald]
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                print("VM är igång.")
                print("Kör igång webbserver...")
                header1 = vmActions.run_server1(vmx_path, vmActions.get_vm_ip(VM_PATH_LIST[0]), vmActions.get_vm_ip(VM_PATH_LIST[3]))
                meny_kontroll(vald, meny_item2)
            else:
                print("VM är inte igång.")
                meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == "Kör Databas": #Kör igång filen Database.js i VMen
        header2 = meny_item[vald]
        if os.path.exists(vmx_path):
            if vmActions.is_vm_running(vmx_path):
                print("VM är igång.")
                print("Kör igång databas...")
                header1 = vmActions.run_database(vmx_path)
                meny_kontroll(vald, meny_item2)
            else:
                print("VM är inte igång.")
                meny_kontroll(vald, meny_item2)
                
    # Välj vilken VM du vill hantera och göra val för, dvs ändra vmx_path
    elif meny_item[vald] == meny_item3[0]:  # Lastbalanserare
        header2 = meny_item[vald]
        if os.path.exists(VM_PATH_LIST[0]):
            activeVM = meny_item3[0]
            header1 = f"Du hanterar nu {meny_item3[0]}"
            vmx_path = VM_PATH_LIST[0]
            meny_kontroll(vald, meny_item2)
        else:
            print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == meny_item3[1]:  # Webbserver 1
        header2 = meny_item[vald]
        if os.path.exists(VM_PATH_LIST[1]):
            activeVM = meny_item3[1]
            header1 = f"Du hanterar nu {meny_item3[1]}"
            vmx_path = VM_PATH_LIST[1]
            meny_kontroll(vald, meny_item2)
        else:
            print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == meny_item3[2]:  # Webbserver 2
        header2 = meny_item[vald]
        if os.path.exists(VM_PATH_LIST[2]):
            activeVM = meny_item3[2]
            header1 = f"Du hanterar nu {meny_item3[2]}"
            vmx_path = VM_PATH_LIST[2]
            meny_kontroll(vald, meny_item2)
        else:
            print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)
    elif meny_item[vald] == meny_item3[3]:  # MySQL Databas
        header2 = meny_item[vald]
        if os.path.exists(VM_PATH_LIST[3]):
            activeVM = meny_item3[3]
            header1 = f"Du hanterar nu {meny_item3[3]}"
            vmx_path = VM_PATH_LIST[3]
            meny_kontroll(vald, meny_item2)
        else:
            print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)

# Skriver ut vald meny i text
def vald_meny_print():
    global header2
    print(f"Du valde: {header2}".center(os.get_terminal_size().columns))
    
# Rörelsekontroll inom menyn med piltangenter, enter och esc
def meny_kontroll(vald, meny_item):
    vald = vald % len(meny_item)  # Säkerställ att vald är inom gränserna
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

