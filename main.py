import os
import msvcrt
import sys
import time
import subprocess
import vmActions
import ctypes
from dotenv import load_dotenv
import hashlib
#----------------------------------------------------------------------------------------------
# Meny-arrays, Används för att bygga upp de olika typerna av menyer
# Används för att trigga if-satser i 'välj val()'-funktionen
meny_item1 = ["Välj VM att hantera", "Välj skript att köra", "Välj service att stänga av", "Förinställda Program", "Starta VM", "Stäng av VM", "Status", "Avsluta"]
meny_item2 = ["Backa"]
meny_item3 = ["Lastbalanserare", "Webbserver 1", "Webbserver 2", "MySQL Databas", "Backa"]
meny_item4 = ["Kör Lastbalanserare", "Kör Webbserver", "Kör Databas", "Uppdatera repository", "Backa"]
meny_item5 = ["Starta alla VMs", "Kör igång lastbalanserad hemsida", "Stäng av alla VMs", "Backa"]
meny_item6 = ["Stäng av Lastbalanserar-skript", "Stäng av Webbserver-skript", "Stäng av Databas-skript", "Backa"]
vald = 0
# Skapar VM-variabler, nollställd från början 
vmx_path = "" 
activeVM = "ingen VM" #stalls in till vilken VM som hanteras, ändrad så fort ett val görs

#Dynamiska textvariabler som används vid menynavigering
header1 = "" # Handling utförd av val
header2 = "" # Vilket val du gjorde
#----------------------------------------------------------------------------------------------
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

# Lösenordshantering
#Hashat lösenord
stored_passkey = "a9a6c6e73b20ba3b3e5b4af90a44603c566bb03af6f54832adebded12d4c0177d8183b82631a89192de4a9a88bb5b3fc"  
max_tries = 3
# Tre försök att skriva rätt lösenord
for attempt in range(max_tries):
    passkey = vmActions.get_password_with_stars("Ange lösenord för att fortsätta: ")
    input_result = hashlib.sha384(passkey.encode()).hexdigest()

    if input_result == stored_passkey:
        print("Lösenord korrekt. Fortsätter...")
        break
    else:
        print("Fel lösenord.")
        if attempt < max_tries - 1:
            print(f"Försök kvar: {max_tries - attempt - 1}")
        else:
            print("För många felaktiga försök. Avslutar programmet...")
            time.sleep(2)
            sys.exit()
#----------------------------------------------------------------------------------------------
#Laddar in miljövariabler från .env.local filen
load_dotenv(".env.local")
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
        
    print("\n" * 2) 
    for i, item in enumerate(meny_item):
        if i == vald:
            # Highlighta itemet med en annan bakgrunds- och textfärg
            print(f"\033[48;5;15m\033[30m-> {item}\033[0m")  
        else:
            print(f"   {item}")

# Väljer ett val i menyn och kör det
def välj_val(vald, meny_item):
    nyVald = 0
    # Variabler som uppdateras globalt för att följa med menyer och andra funktioner på ett enkelt sätt.
    global header1
    global header2
    global activeVM
    global vmx_path

#---------------------------------------------------------------------------------------------  
# Fem enklare val i menyn, starta, status, avsluta, stäng av VM och backa
#Inkluderar även multi-kommandon som stänger av eller startar alla 
    match meny_item[vald]:
        case "Starta VM":
            if os.path.exists(vmx_path) and not vmActions.is_vm_running(vmx_path):
                vmActions.start_vm(vmx_path)
                header1 = f"{activeVM} startad."
                header2 = meny_item[vald]
                meny_kontroll(vald, meny_item2)
            elif os.path.exists(vmx_path) and vmActions.is_vm_running(vmx_path):
                header1 = f"{activeVM} är redan igång."
                header2 = meny_item[vald]
                meny_kontroll(vald, meny_item2)
            else:
                print("Error: VMX filen hittades ej:", vmx_path)
                meny_kontroll(vald, meny_item2)
         
        case "Starta alla VMs": #Startar alla VMs i VM_PATH_LIST
            rensa()
            print("Startar alla VMs...")
            for vm_name, vm_path in zip(meny_item3[:4], VM_PATH_LIST):
                if vm_path and os.path.exists(vm_path) and not vmActions.is_vm_running(vm_path):
                    vmActions.start_vm(vm_path)
                    print(f"{vm_name} startad.")
                elif vm_path and os.path.exists(vm_path) and vmActions.is_vm_running(vm_path):
                    print(f"{vm_name} är redan igång.")
                else:
                    print(f"Error: VMX-filen hittades ej för {vm_name}.")
            header1 = "Alla VMs startade."
            meny_kontroll(vald, meny_item2)
        
        case "Status":
            header2 = meny_item[vald]
            if os.path.exists(vmx_path):
                if vmActions.is_vm_running(vmx_path):
                    ip = vmActions.get_vm_ip(vmx_path)
                    header1 = f"{activeVM} är igång med IP: {ip}"
                else:
                    header1 = f"{activeVM} är inte igång."
            else:
                print("Error: VMX filen hittades ej:", vmx_path)  
            meny_kontroll(nyVald, meny_item2)

        case "Avsluta":
            rensa()
            print("Avslutar programmet...")
            time.sleep(1)
            exit()

        case "Stäng av VM":
            header2 = meny_item[vald]
            if os.path.exists(vmx_path):
                if vmActions.is_vm_running(vmx_path):
                    vmActions.stop_vm_hard(vmx_path)
                    print(f"{activeVM} stängdes av.")
                    header1 = f"{activeVM} stängdes av."
                    pass
                else:
                    print(f"{activeVM} är inte igång.")
                    pass
            meny_kontroll(vald, meny_item1)

        case "Stäng av alla VMs":
            rensa()
            print("Stänger av alla VMs...")
            for vm_name, vm_path in zip(meny_item3[:4], VM_PATH_LIST):
                if vm_path and os.path.exists(vm_path):
                    if vmActions.is_vm_running(vm_path):
                        vmActions.stop_vm_hard(vm_path)
                        print(f"{vm_name} stängdes av.")
                    else:
                        print(f"{vm_name} är inte igång.")
                else:
                    print(f"Error: VMX-filen hittades ej för {vm_name}.")
            header1 = "Alla VMs stängdes av."
            meny_kontroll(vald, meny_item2)

        case "Backa":
            rensa()
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item1)
            
#--------------------------------------------------------------------------------------------
# Start av nya menyer, även Backa är en meny men den är inte direkt en undermeny
        case "Välj VM att hantera":
            rensa()
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item3)

        case "Välj skript att köra":
            rensa()
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item4)
        
        case "Välj service att stänga av":
            rensa()
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item6)
            
        case "Förinställda Program":
            rensa()
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item5)
        
        case "Välj service att stänga av":
            rensa()
            header2 = meny_item[vald]
            meny_kontroll(vald, meny_item6)
            
#--------------------------------------------------------------------------------------------     
# Kör-kommandon för de tre olika Javascripten och att köra git pull
        case "Kör Lastbalanserare":  # Kör igång filen loadBalancer.js i VMen
            header2 = meny_item[vald]
            kör_program_lastbalanserare(vmx_path)
            meny_kontroll(vald, meny_item2)

        case "Kör Webbserver":  # Kör igång filen server1.js i VMen
            # Behöver mer info, det krävs IP från både lastbalanseraren och databasen för att kunna köra igång servern korrekt
            header2 = meny_item[vald]
            kör_program_webbserver(vmx_path)
            meny_kontroll(vald, meny_item2)

        case "Kör Databas":  # Kör igång filen Database.js i VMen
            header2 = meny_item[vald]
            kör_program_databas(vmx_path)
            meny_kontroll(vald, meny_item2)
            
        case "Uppdatera repository":  # Uppdaterar repositoryn i VMen
            header2 = meny_item[vald]
            uppdatera_repository(vmx_path)
            meny_kontroll(vald, meny_item2)
        
        case "Kör igång lastbalanserad hemsida":  # Startar alla VMs och kör igång hemsidan med services i rätt ordning.
            Kör_hemsida()
            meny_kontroll(vald, meny_item2)
#---------------------------------------------------------------------------------------------
# Stänger av de olika servicesen i VMen, dvs stoppar de tre Javascripten
        case "Stäng av Lastbalanserar-skript":  # Stänger av lastbalanseraren
            header2 = meny_item[vald]
            if os.path.exists(vmx_path):
                if vmActions.is_vm_running(vmx_path) and vmActions.get_vm_ip(vmx_path) is not None:
                    header1 = vmActions.shut_down_loadBalancer(vmx_path)
                elif vmActions.get_vm_ip(vmx_path) is None:
                    header1 = f"{activeVM} har ingen IP-adress, kan inte stänga av via SSH."
                else:
                    header1 = f"{activeVM} är inte igång."
            else:
                print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)

        case "Stäng av Webbserver-skript":  # Stänger av webbservern
            header2 = meny_item[vald]
            if os.path.exists(vmx_path):
                if vmActions.is_vm_running(vmx_path) and vmActions.get_vm_ip(vmx_path) is not None:
                    header1 = vmActions.shut_down_server1(vmx_path)
                elif vmActions.get_vm_ip(vmx_path) is None:
                    header1 = f"{activeVM} har ingen IP-adress, kan inte stänga av via SSH."
                else:
                    header1 = f"{activeVM} är inte igång."
            else:
                print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)

        case "Stäng av Databas-skript":  # Stänger av databasen
            header2 = meny_item[vald]
            if os.path.exists(vmx_path):
                if vmActions.is_vm_running(vmx_path) and vmActions.get_vm_ip(vmx_path) is not None:
                    header1 = vmActions.shut_down_database(vmx_path)
                elif vmActions.get_vm_ip(vmx_path) is None:
                    header1 = f"{activeVM} har ingen IP-adress, kan inte stänga av via SSH."
                else:
                    header1 = f"{activeVM} är inte igång."
            else:
                print("Error: VMX filen hittades ej:", vmx_path)
            meny_kontroll(vald, meny_item2)



#---------------------------------------------------------------------------------------------
# Välj vilken VM du vill hantera och göra val för, dvs ändra vmx_path
#Undermeny av "Välj VM att hantera"
        case vm_namn if vm_namn in meny_item3[:4]:  # Matchar en av de fyra VM-namnen
            index = meny_item3.index(vm_namn)
            header2 = meny_item[vald]
            if os.path.exists(VM_PATH_LIST[index]):
                activeVM = meny_item3[index]
                header1 = f"Du hanterar nu {meny_item3[index]}"
                vmx_path = VM_PATH_LIST[index]
                meny_kontroll(vald, meny_item1)  # Gå tillbaka till huvudmenyn
            else:
                print("Error: VMX filen hittades ej:", vmx_path)
                meny_kontroll(vald, meny_item2)

#---------------------------------------------------------------------------------------------
# Om det av någon anledning inte matchar något av de ovanstående alternativen
        case _:
            print("Ogiltigt val.")
            vald = 0  # Nollställ vald index
            meny_kontroll(vald, meny_item1)
#----------------------------------------------------------------------------------------------
# Om jag bryter ett case så vill jag att den ska gå tillbaka till huvudmenyn
    meny_kontroll(vald, meny_item1)


# Skriver ut vald som du valde senast i text
def vald_meny_print():
    global header2
    print(f"Du valde: {header2}".center(os.get_terminal_size().columns))
# Rörelsekontroll inom menyn med piltangenter, enter och esc
def meny_kontroll(vald, meny_item):
    vald = vald % len(meny_item)  # Säkerställ att vald är inom gränserna
    vald = 0
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

# Funktioner för att köra olika program på VMen
def kör_program_lastbalanserare(vmx_path):
    global header1
    if os.path.exists(vmx_path):
        if vmActions.is_vm_running(vmx_path):
            print("VM är igång.")
            print("Kör igång lastbalanserare...")
            header1 = vmActions.run_loadBalancer(vmx_path)
        else:
            header1 = "VM är inte igång."
                       
def kör_program_webbserver(vmx_path):
    global header1
    if os.path.exists(vmx_path):
        if vmActions.is_vm_running(vmx_path):
            print("VM är igång.")
            print("Kör igång webbserver...")
            header1 = vmActions.run_server1(
                vmx_path,
                vmActions.get_vm_ip(VM_PATH_LIST[0]),
                vmActions.get_vm_ip(VM_PATH_LIST[3])
            )
        else:
            header1 = "VM är inte igång."

def kör_program_databas(vmx_path):
    global header1
    if os.path.exists(vmx_path):
        if vmActions.is_vm_running(vmx_path):
            print("VM är igång.")
            print("Kör igång databas...")
            header1 = vmActions.run_database(vmx_path)
        else:
            header1 = "VM är inte igång."

def uppdatera_repository(vmx_path):
    global header1
    global activeVM
    if os.path.exists(vmx_path):
        if vmActions.is_vm_running(vmx_path):
            print(f"{activeVM} är igång.")
            print("Uppdaterar repository...")
            header1 = vmActions.git_pull_repo(vmx_path)
        else:
            header1 = f"{activeVM} är inte igång och kan därför inte uppdatera repository."   
            
def Kör_hemsida():
    global header1
    rensa()
    print("Startar alla VMs och kör igång alla skript på respektive maskin...")
    for vm_name, vm_path in zip(meny_item3[:4], VM_PATH_LIST):
        if vm_path and os.path.exists(vm_path) and not vmActions.is_vm_running(vm_path):
            vmActions.start_vm(vm_path)
            print(f"{vm_name} startad.")
        elif vm_path and os.path.exists(vm_path) and vmActions.is_vm_running(vm_path):
            print(f"{vm_name} är redan igång.")
        else:
            print(f"Error: VMX-filen hittades ej för {vm_name}.")
            meny_kontroll(vald, meny_item2)
    print("Väntar på att alla VMs ska starta... ca 60 sekunder")
    time.sleep(15)  # Väntar 60 sekunder för att säkerställa att alla VMs är startade
    print("45 sekunder...")
    time.sleep(15)
    print("30 sekunder...")
    time.sleep(15)
    print("15 sekunder...")
    time.sleep(15)
    kör_program_lastbalanserare(VM_PATH_LIST[0])
    kör_program_databas(VM_PATH_LIST[3])
    kör_program_webbserver(VM_PATH_LIST[1])
    kör_program_webbserver(VM_PATH_LIST[2])
    header1 = "Alla VMs startade och hemsidan är igång."   



# Huvudprogrammet som kör första gången programmet startas     
meny_kontroll(vald, meny_item1)

