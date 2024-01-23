import requests
from bs4 import BeautifulSoup
import csv
import os

# Base URL without page parameter
base_url = 'https://www.avito.ma/fr/maroc/immobilier'

headers = {
    'User-Agent': 'Your User-Agent String Here',
}

# Define the order of labels you want to use as column names, including "Ville" and "Prix"
desired_labels = [
    'Ville', 'Secteur', 'Prix', 'Type', 'Âge du bien', 'Nombre de pièces', 'Salle de bain', 'Surface habitable', 'Salons', 'Étage',
    'Frais de syndic / mois'   # Add your desired labels here
]

# Define the CSV file path on your desktop
desktop_path = os.path.expanduser("~/Desktop")
csv_filename = os.path.join(desktop_path, 'RealEstate_data.csv')

# List to store the item URLs
urls = []

# Loop through pages, starting with page 1 (the first page has no page parameter)
for page_number in range(1, 30):  # Change the range as needed to scrape the desired number of pages
    if page_number == 1:
        page_url = base_url
    else:
        page_url = f'{base_url}?o={page_number}'  # Append page number to the base URL

    response = requests.get(page_url, headers=headers)

    if response.status_code == 200:
        main_soup = BeautifulSoup(response.content, 'html.parser')

        # Find the div element with class 'sc-1nre5ec-1 crKvIr'
        div_element = main_soup.find('div', class_='sc-1nre5ec-1 crKvIr listing')

        # Check if the div element is found
        if div_element:
            # Use BeautifulSoup to find and extract the item URLs within the div
            for link in div_element.find_all('a', href=True):
                item_url = link['href']
                urls.append(item_url)
        else:
            print(f"Div element not found on page {page_number} with class 'sc-1nre5ec-1 crKvIr'")
    else:
        print(f"Failed to retrieve data from page {page_number}. Status Code:", response.status_code)

# Create an empty list to store the data dictionaries
all_data = []

for url in urls:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Dictionary to hold the extracted details for this URL
        extracted_details = {}

        # Find all <li> tags
        list_items = soup.find_all('li', class_='sc-qmn92k-1 jJjeGO')

        for item in list_items:
            spans = item.find_all('span')
            if len(spans) == 2:
                label = spans[0].get_text(strip=True)
                value = spans[1].get_text(strip=True)
                extracted_details[label] = value

        # Extract "Ville" from the URL or use "N/A" if not found
        ville_element = soup.find('div', class_='sc-1g3sn3w-7 bNWHpB')
        ville = ville_element.find('span', class_='sc-1x0vz2r-0 iotEHk').text if ville_element else 'N/A'

        # Extract "Prix" from the div with class 'sc-1g3sn3w-10 leGvyq' or use "N/A" if not found
        prix_element = soup.find('div', class_='sc-1g3sn3w-10 leGvyq')
        prix = prix_element.text.strip() if prix_element else 'N/A'

        # Add "Ville" and "Prix" to the extracted details
        extracted_details['Ville'] = ville
        extracted_details['Prix'] = prix

        # Create a dictionary with the desired order of labels, filling in missing values with "N/A"
        data_dict = {label: extracted_details.get(label, 'N/A') for label in desired_labels}

        # Append the data dictionary to the list
        all_data.append(data_dict)
    else:
        print(f"Failed to retrieve data from URL: {url}. Status Code:", response.status_code)

# Write all the extracted data to the CSV file with fixed columns and values
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=desired_labels)

    # Write the header row with fixed column names
    writer.writeheader()

    # Write the data rows with corresponding values for each URL
    for data_dict in all_data:
        writer.writerow(data_dict)

print(f"Data from {len(urls)} URLs has been saved to {csv_filename}")
