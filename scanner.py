import tkinter as tk
from tkinter import messagebox
import socket
import threading
import re
import time

#======================================================
# /\_\   /\_\     /\  /\  /\  /\_____\ / ____/\
# \/_/  ( ( (     \ \ \/ / / ( (_____/ ) ) __\/
#  /\_\  \ \_\     \ \__/ /   \ \__\    \ \ \
# / / /  / / /__    \__/ /    / /__/_   _\ \ \
#( (_(  ( (_____(   / / /    ( (_____\ )____) )
# \/_/   \/_____/   \/_/      \/_____/ \____\/
#======================================================

# Expression régulière pour reconnaître les adresses IPv4.
pattern_ip = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
# Expression régulière pour extraire la plage de ports à scanner.
pattern_plage_ports = re.compile("([0-9]+)-([0-9]+)")
# Liste pour stocker les ports ouverts.
ports_ouverts = []

# Configuration du délai d'attente pour les connexions socket.
delai_timeout = 1  # 1 seconde pour chaque tentative de connexion


# Fonction pour scanner un seul port TCP en utilisant un socket
def scanner_port_tcp(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(delai_timeout)
            resultat = s.connect_ex((ip, port))
            if resultat == 0:
                ports_ouverts.append(port)
    except socket.error:
        pass


# Fonction pour gérer le processus de scan des ports
def scanner_ports(ip, port_debut, port_fin):
    for port in range(port_debut, port_fin + 1):
        threading.Thread(target=scanner_port_tcp, args=(ip, port)).start()


# Fonction pour valider l'adresse IP entrée
def valider_ip(ip):
    return bool(pattern_ip.search(ip))


# Fonction pour valider la plage de ports
def valider_plage_ports(plage_ports):
    plage_validée = pattern_plage_ports.search(plage_ports.replace(" ", ""))
    if plage_validée:
        return int(plage_validée.group(1)), int(plage_validée.group(2))
    return None, None


# Fonction pour démarrer le scan
def demarrer_scan():
    ip = entry_ip.get()
    plage_ports = entry_ports.get()

    if not valider_ip(ip):
        text_resultats.insert(tk.END, "Erreur: Adresse IP invalide\n")
        return

    port_min, port_max = valider_plage_ports(plage_ports)
    if port_min is None or port_max is None:
        text_resultats.insert(tk.END, "Erreur: Plage de ports invalide\n")
        return

    global ports_ouverts
    ports_ouverts = []
    text_resultats.delete(1.0, tk.END)

    debut_scan = time.time()
    scanner_ports(ip, port_min, port_max)

    time.sleep(1)  # Temps d'attente pour que les threads démarrent

    while threading.active_count() > 1:
        time.sleep(0.1)  # Attendre que tous les threads soient terminés

    fin_scan = time.time()
    if ports_ouverts:
        for port in ports_ouverts:
            text_resultats.insert(tk.END, f"Port {port} ouvert\n")
    else:
        text_resultats.insert(tk.END, f"Aucun port ouvert trouvé.\n")

    text_resultats.insert(tk.END, f"Scan terminé en {fin_scan - debut_scan:.2f} secondes.\n")


# Créer la fenêtre principale
root = tk.Tk()
root.title("Scanner de Ports")
root.geometry("500x500")
root.config(bg="#2b2b2b")  # Fond sombre

# Styles
label_style = {"fg": "#ffffff", "bg": "#2b2b2b", "font": ("Helvetica", 12)}
entry_style = {"bg": "#1a1a1a", "fg": "#ffffff", "font": ("Helvetica", 12)}
button_style = {"bg": "#444444", "fg": "#ffffff", "font": ("Helvetica", 12), "relief": "flat"}
text_resultats_style = {"bg": "#1a1a1a", "fg": "#00ff00", "font": ("Courier New", 12)}

# Création des éléments de l'interface
label_ip = tk.Label(root, text="Adresse IP :", **label_style)
label_ip.pack(pady=10)

entry_ip = tk.Entry(root, width=30, **entry_style)
entry_ip.pack(pady=10)

label_ports = tk.Label(root, text="Plage de Ports (ex: 20-80) :", **label_style)
label_ports.pack(pady=10)

entry_ports = tk.Entry(root, width=30, **entry_style)
entry_ports.pack(pady=10)

button_scan = tk.Button(root, text="Démarrer le Scan", command=demarrer_scan, **button_style)
button_scan.pack(pady=20)

text_resultats = tk.Text(root, height=10, width=40, **text_resultats_style)
text_resultats.pack(pady=10)

# Lancer l'interface graphique
root.mainloop()

