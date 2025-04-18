'''
# Tableau de Bord Dynamique

## Description du projet

Ce script Python crée une interface graphique Full‑screen (pensée pour une TV ou un écran de monitoring) affichant en temps réel :

- **Heure & Date** : Mise à jour chaque seconde et changement automatique du thème (`clair/sombre`) selon l’heure.  
- **Météo** : Température et conditions actuelles via l’API WeatherAPI.  
- **Actualités** : Titres des 3 dernières dépêches du flux RSS (Le Monde par défaut).  
- **Emploi du temps** : Premier et dernier cours de la journée récupérés via Selenium et Pronote.  
- **Verset du Coran** : Proposition aléatoire parmi une liste de versets.  
- **Compte à rebours Brevet** : Jours, heures, minutes, secondes jusqu’à la date du Brevet.  
- **Compte à rebours Vacances** : Affiche le prochain début de vacances ou indique si c’est déjà les vacances.  
- **Horaires de prière** : Heures de Fajr, Dhuhr, Asr, Maghrib et Isha via l’API Aladhan, avec indication de la prochaine prière.

---

## Prérequis

- **Python 3.7+**  
- **Google Chrome** installé + **ChromeDriver** compatible (ajouté au PATH)  
- Bibliothèques Python :

  ```bash
  pip install customtkinter requests feedparser selenium locale
  ```

  > _Si `locale` n’est pas installé, utilisez votre gestionnaire de paquets système pour activer le support `fr_FR.UTF-8`._

---

## Configuration

Ouvrez `main.py` et modifiez :

```python
CITY       = "Paris"                                # Ville pour la météo
API_KEY    = "VOTRE_CLE_API_WEATHERAPI"             # Clé API WeatherAPI
RSS_URL    = "https://www.lemonde.fr/rss/une.xml"   # URL du flux RSS
USERNAME   = "votre.login.pronote"                  # Identifiants Pronote
PASSWORD   = "votre_mot_de_passe"                   # (écran d’authentification)
```

- **ChromeDriver** : Vérifiez que la variable d’environnement PATH pointe vers l’exécutable `chromedriver`.

---

## Structure

```
main.py           # Script principal
```

---

## Utilisation

1. Assurez-vous que ChromeDriver est accessible.  
2. Lancez le script :

   ```bash
   python main.py
   ```

3. Pour quitter le mode plein écran, appuyez sur `Esc`. Pour y revenir, pressez `F`.

---

## Explication rapide du code

- **`update_time()`** : Met à jour l’heure, la date et le thème toutes les secondes.  
- **`update_data()`** : Rafraîchit météo, actualités et verset chaque minute.  
- **`threaded_schedule_update()`** : Lance la récupération Pronote en arrière‑plan.  
- **`update_brevet_countdown()`** et **`update_vacances_countdown()`** : Affichent des compte‑à‑rebours.  
- **`update_prayer_block()`** : Récupère et affiche les horaires de prière, avec indication de la prochaine.

---

## Personnalisation

- **Thème** : `ctk.set_appearance_mode("system")` → `"light"` ou `"dark"`.  
- **Flux RSS** : Changez `RSS_URL`.  
- **Versets** : Ajoutez ou modifiez la liste `QURAN_VERSES`.  
- **Dates des vacances** : Ajustez le tableau `dates` dans `get_next_vacances()`.

---

## Dépannage

- **Selenium/ChromeDriver** :  
  - Assurez‑vous que la version de ChromeDriver correspond à votre Chrome.  
  - Ajoutez `--verbose` aux `options` pour du logging.
- **API météo ou Aladhan** :  
  - Vérifiez la validité de vos clés et l’accès réseau.
- **Erreur de locale** :  
  - Activez `fr_FR.UTF-8` dans votre OS ou commentez `locale.setlocale(...)`.

---

## Sécurité

- Ne versionnez jamais vos **identifiants Pronote** ni vos **clés API** dans un dépôt public.  
- Utilisez un fichier `.env` ou un gestionnaire de secrets si nécessaire.

---

## Licence

Please just don't steal my code..
