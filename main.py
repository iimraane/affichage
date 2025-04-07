import customtkinter as ctk
import time
import requests
import feedparser
import random
import threading
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import locale

# ---------------- CONFIGURATION ----------------
ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("system")  # Adaptation dynamique au moment de la journée
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

CITY = "Paris"
API_KEY = "8bd587c92f684d8f90d92008250604"
RSS_URL = "https://www.lemonde.fr/rss/une.xml"
USERNAME = "imrane.aboussaid"
PASSWORD = "Imrane789789*"

# Versets du Coran
QURAN_VERSES = [
    "Et rappelle-toi: ton Seigneur est proche. (Sourate 50:16)",
    "Allah est avec les patients. (Sourate 2:153)",
    # ... (troncature pour lisibilité)
    "C'est Lui le Pardonneur, le Très Aimant. (Al-Buruj 85:14)"
]

# ------------------ FONCTIONS ------------------

def get_weather():
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&lang=fr"
        data = requests.get(url).json()
        temp = round(data["current"]["temp_c"])
        condition = data["current"]["condition"]["text"]
        return f"{CITY} : {temp}°C, {condition}"
    except:
        return "Météo indisponible"

def get_news():
    try:
        feed = feedparser.parse(RSS_URL)
        return [entry.title for entry in feed.entries[:3]]
    except:
        return ["Pas d'actualités"]

def get_schedule_data(username, password):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://keycloak.moncollege-valdoise.fr/realms/CD95/protocol/cas/login?service=https:%2F%2F0950937C.index-education.net%2Fpronote%2Feleve.html")
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "kc-login").click()
        time.sleep(5)

        cours_list = driver.find_elements(By.CSS_SELECTOR, 'ul.liste-cours > li.flex-contain')
        premiere_matiere = heure_debut = derniere_heure = None

        for bloc in cours_list:
            try:
                matiere = bloc.find_element(By.CSS_SELECTOR, ".libelle-cours").text
                heures = bloc.find_elements(By.CSS_SELECTOR, ".container-heures > div")
                debut = heures[0].text if heures else None
                if not debut:
                    continue
                if not premiere_matiere and "Pas de cours" not in matiere and "E-sport" not in matiere:
                    premiere_matiere, heure_debut = matiere, debut
                if "E-sport" not in matiere:
                    derniere_heure = debut
            except:
                continue

        return (heure_debut, premiere_matiere, derniere_heure) if all([heure_debut, premiere_matiere, derniere_heure]) else None
    finally:
        driver.quit()

def update_time():
    now = datetime.now()
    heure_label.configure(text=now.strftime("%H:%M:%S"))
    date_label.configure(text=now.strftime("%A %d %B %Y").capitalize())
    ctk.set_appearance_mode("dark" if now.hour >= 20 or now.hour < 9 else "light")
    root.after(1000, update_time)

def update_data():
    meteo_label.configure(text=get_weather())
    news_label.configure(text="\n".join(get_news()))
    verse_label.configure(text=random.choice(QURAN_VERSES))
    root.after(60000, update_data)

def update_schedule():
    schedule = get_schedule_data(USERNAME, PASSWORD)
    if schedule:
        h_deb, mat, h_fin = schedule
        schedule_label.configure(text=f"Début cours: {h_deb}\nPremière matière: {mat}\nFin cours: {h_fin}")
    else:
        schedule_label.configure(text="Horaire indisponible")

def threaded_schedule_update():
    threading.Thread(target=update_schedule, daemon=True).start()

def update_brevet_countdown():
    now = datetime.now()
    diff = datetime(2025, 6, 26) - now
    d, rem = divmod(diff.seconds, 3600)
    h, rem = divmod(rem, 60)
    m, s = rem, diff.seconds % 60
    brevet_label.configure(text=f"{diff.days}j {d}h {m}m {s}s")
    root.after(1000, update_brevet_countdown)

def get_next_vacances():
    now = datetime.now()
    dates = [
        ("Vacances de printemps", datetime(2025, 4, 12), datetime(2025, 4, 28)),
        ("Vacances d'été", datetime(2025, 7, 5), None)
    ]
    for nom, debut, fin in dates:
        if debut > now:
            return nom, debut
        elif debut <= now <= fin:
            return nom, "vacances"
    return None, None

def update_vacances_countdown():
    nom, date = get_next_vacances()
    if date == "vacances":
        vacances_label.configure(text=f"🌴 C’est les vacances ! ({nom})")
    elif date:
        diff = date - datetime.now()
        d, rem = divmod(diff.seconds, 3600)
        h, rem = divmod(rem, 60)
        m, s = rem, diff.seconds % 60
        vacances_label.configure(text=f"{diff.days}j {d}h {m}m {s}s")
    else:
        vacances_label.configure(text="🎉 Vacances inconnues")
    root.after(1000, update_vacances_countdown)

def get_prayer_times_aladhan():
    url = "http://api.aladhan.com/v1/timingsByCity"
    params = {"city": "Paris", "country": "France", "method": 2, "school": 0, "language": "fr"}
    try:
        response = requests.get(url, params=params)
        timings = response.json()["data"]["timings"]
        return {k: timings[k] for k in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]}
    except:
        return None

def get_next_prayer(prayer_times):
    now_min = datetime.now().hour * 60 + datetime.now().minute
    for name, time_str in prayer_times.items():
        h, m = map(int, time_str.split(":"))
        if h * 60 + m > now_min:
            return name, time_str
    return None, None

def update_prayer_block():
    horaires = get_prayer_times_aladhan()
    if not horaires:
        for lbl in prayer_labels.values():
            lbl.configure(text="Erreur")
        prochaine_label.configure(text="🏛️ Erreur récupération")
        return

    for nom, heure in horaires.items():
        if nom in prayer_labels:
            prayer_labels[nom].configure(text=f"{nom} : {heure}")

    nom, heure = get_next_prayer(horaires)
    prochaine_label.configure(text=f"🏛️ Prochaine : {nom} ({heure})" if nom else "🏛️ Toutes les prières sont passées")
    root.after(60000, update_prayer_block)

# ---------------- Interface Graphique ----------------

root = ctk.CTk()
root.geometry("1280x720")
root.title("Tableau de bord moderne")

padx_global = 20
pady_global = 10

# Bloc Heure & Date
time_frame = ctk.CTkFrame(root, corner_radius=15, border_width=2, border_color="#d0d0d0")
time_frame.pack(pady=(20,10), padx=padx_global, fill="x")

heure_label = ctk.CTkLabel(time_frame, font=("Helvetica Neue", 72))
heure_label.pack(pady=(10,0))

date_label = ctk.CTkLabel(time_frame, font=("Helvetica Neue", 28))
date_label.pack(pady=(0,10))

# Sous-cadres pour les compteurs
left_counter_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
left_counter_frame.place(relx=0.01, rely=0.5, anchor="w")

right_counter_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
right_counter_frame.place(relx=0.99, rely=0.5, anchor="e")

# Titre + compteur pour le brevet
brevet_title = ctk.CTkLabel(left_counter_frame, text="🧠 Brevet dans:", font=("Helvetica Neue", 18, "bold"))
brevet_title.pack()
brevet_label = ctk.CTkLabel(left_counter_frame, font=("Helvetica Neue", 18))
brevet_label.pack()

# Titre + compteur pour les vacances
vacances_title = ctk.CTkLabel(right_counter_frame, text="⏳ Vacances dans:", font=("Helvetica Neue", 18, "bold"))
vacances_title.pack()
vacances_label = ctk.CTkLabel(right_counter_frame, font=("Helvetica Neue", 18))
vacances_label.pack()


# Météo et Emploi du temps
info_frame = ctk.CTkFrame(root, corner_radius=15, border_width=2, border_color="#d0d0d0")
info_frame.pack(pady=(10,10), padx=padx_global, fill="x")

weather_frame = ctk.CTkFrame(info_frame, corner_radius=15)
weather_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)
ctk.CTkLabel(weather_frame, text="🌦️ Météo", font=("Helvetica Neue", 26, "bold")).pack(pady=(0,5))
meteo_label = ctk.CTkLabel(weather_frame, font=("Helvetica Neue", 20))
meteo_label.pack(pady=(0,10))

schedule_frame = ctk.CTkFrame(info_frame, corner_radius=15)
schedule_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
ctk.CTkLabel(schedule_frame, text="⏰ Emploi du temps", font=("Helvetica Neue", 26, "bold")).pack(pady=(0,5))
schedule_label = ctk.CTkLabel(schedule_frame, font=("Helvetica Neue", 20))
schedule_label.pack(pady=(0,10))
ctk.CTkButton(schedule_frame, text="Mettre à jour", command=threaded_schedule_update).pack(pady=(0,10))

# Verset du Coran
verse_frame = ctk.CTkFrame(root, corner_radius=15, border_width=2, border_color="#d0d0d0")
verse_frame.pack(pady=(10,10), padx=padx_global, fill="x")
ctk.CTkLabel(verse_frame, text="📖 Verset du Coran", font=("Helvetica Neue", 26, "bold")).pack(pady=(10,5))
verse_label = ctk.CTkLabel(verse_frame, font=("Helvetica Neue", 20), wraplength=1000, justify="center")
verse_label.pack(pady=(0,10))

# Actualités
news_frame = ctk.CTkFrame(root, corner_radius=15, border_width=2, border_color="#d0d0d0")
news_frame.pack(pady=(10,20), padx=padx_global, fill="x")
ctk.CTkLabel(news_frame, text="📰 Actualités", font=("Helvetica Neue", 26, "bold")).pack(pady=(10,5))
news_label = ctk.CTkLabel(news_frame, font=("Helvetica Neue", 18), wraplength=1100, justify="center")
news_label.pack(pady=(0,10))

# Heures de prière
prayer_frame = ctk.CTkFrame(root, corner_radius=15, border_width=2, border_color="#d0d0d0")
prayer_frame.pack(pady=(0, 20), padx=padx_global, fill="x")
prochaine_label = ctk.CTkLabel(prayer_frame, font=("Helvetica Neue", 22, "bold"))
prochaine_label.pack(pady=(5, 5))
prayer_row = ctk.CTkFrame(prayer_frame, fg_color="transparent")
prayer_row.pack(pady=(0, 10))

prayer_labels = {}
for nom in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
    lbl = ctk.CTkLabel(prayer_row, text=f"{nom} : --:--", font=("Helvetica Neue", 18), padx=20)
    lbl.pack(side="left", padx=20)
    prayer_labels[nom] = lbl

# ---------------- LANCEMENT ----------------
update_time()
update_data()
threaded_schedule_update()
update_brevet_countdown()
update_vacances_countdown()
update_prayer_block()

root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
root.bind("<f>", lambda event: root.attributes("-fullscreen", True))
root.mainloop()