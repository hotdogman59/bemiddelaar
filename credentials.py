from googlesearch import search
import gspread
from google.oauth2 import service_account
from bs4 import BeautifulSoup
import requests

# Laad de Google Sheets credentials en authenticatie
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(credentials)

# Open de Google Spreadsheet
spreadsheet = client.open('Bemiddelaar')  # Vervang dit door de daadwerkelijke naam van je spreadsheet
worksheet = spreadsheet.sheet1

# Definieer je zoektermen
zoektermen = ['Horeca Bemiddelaar', 'Horeca Bemiddeling', 'Horeca flexwerk', 'Horeca freelancen', 'Horeca freelancer']

def gegevens_ophalen_van_website(website):
    response = requests.get(website)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Bedrijfsnaam ophalen
    bedrijfsnaam_element = soup.find(class_='bedrijfsnaam')
    bedrijfsnaam = bedrijfsnaam_element.text if bedrijfsnaam_element else None

    # Telefoonnummer ophalen
    telefoon_element = soup.find(class_='telefoon')
    telefoon = telefoon_element.text if telefoon_element else None

    # E-mailadres ophalen
    email_element = soup.find(class_='email')
    email = email_element.text if email_element else None
    
    # Fallback: Als bedrijfsnaam, telefoon of e-mail niet gevonden wordt, zoek naar KVK-nummer
    if not bedrijfsnaam or not telefoon or not email:
        kvk_nummer_element = soup.find(class_='kvk-nummer')
        kvk_nummer = kvk_nummer_element.text if kvk_nummer_element else None
        
        if kvk_nummer:
            kvk_url = f'https://www.kvk.nl/zoeken/?source=all&q={kvk_nummer}'
            kvk_response = requests.get(kvk_url)
            kvk_soup = BeautifulSoup(kvk_response.content, 'html.parser')
            
            # Bedrijfsnaam ophalen indien ontbrekend
            if not bedrijfsnaam:
                bedrijfsnaam_element = kvk_soup.find(class_='company-name')
                bedrijfsnaam = bedrijfsnaam_element.text if bedrijfsnaam_element else None
            
            # Telefoonnummer ophalen indien ontbrekend
            if not telefoon:
                telefoon_element = kvk_soup.find(class_='tel-link')
                telefoon = telefoon_element.text if telefoon_element else None
            
            # E-mailadres ophalen indien ontbrekend
            if not email:
                email_element = kvk_soup.find(class_='email-link')
                email = email_element.text if email_element else None
    
    return bedrijfsnaam or 'Bedrijfsnaam niet gevonden', telefoon or 'Telefoonnummer niet gevonden', email or 'E-mailadres niet gevonden'

# Itereer door de zoektermen en voer Google-zoekopdrachten uit
for zoekterm in zoektermen:
    resultaten = search(zoekterm, num_results=1000)

    # Itereer over de zoekresultaten
    for resultaat in resultaten:
        bedrijfsnaam, telefoon, email = gegevens_ophalen_van_website(resultaat)

        # Schrijf de gegevens naar de Google Spreadsheet
        try:
            worksheet.append_row([bedrijfsnaam, telefoon, email])
            print("Gegevens succesvol naar de Google Spreadsheet geschreven.")
        except Exception as e:
            print("Er is een fout opgetreden bij het schrijven naar de Google Spreadsheet:", str(e))

print("Voltooide gegevensverwerking.")
