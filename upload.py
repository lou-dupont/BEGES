import datetime
import json
from params import *
import requests
import zipfile

url_api = 'https://www.data.gouv.fr/api/1/datasets/5db60fb28b4c412aa82e1447/resources/'
resource_XLSX = 'd124cf97-6935-4682-8c33-492447c40ee1'
resource_CSV_ZIP = 'c90e1000-d51a-4e7a-9276-f613ea8afea9'

today = datetime.date.today()
today = today.strftime('%Y-%m-%d')
path = './output/' + today + '/published/'


def upload_file(local_name, resource_id):
    print('Uploading file')
    headers = {
        'X-API-KEY': X_API_KEY
    }
    response = requests.post(url_api + resource_id + '/upload/', files={'file': open(local_name, 'rb')}, headers=headers)
    print('Uploaded file')
    print('Uploading metadata')
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': X_API_KEY
    }
    old_data = response.json()
    data = { 
        'published': old_data['last_modified']
    }
    response = requests.put(url_api + resource_id + '/', data=json.dumps(data), headers=headers)
    print('Uploaded metadata')

# Build ZIP archive of CSV files 

zip_file = zipfile.ZipFile(path + 'bilans-ges.zip', 'w', zipfile.ZIP_DEFLATED)
zip_file.write(path + 'assessments.csv', 'assessments.csv')
zip_file.write(path + 'emissions.csv', 'emissions.csv')
zip_file.write(path + 'legal_units.csv', 'legal_units.csv')
zip_file.write(path + 'scope_items.csv', 'scope_items.csv')
zip_file.write(path + 'texts.csv', 'texts.csv')
zip_file.close()

# Upload files to data.gouv.fr

upload_file(path + 'bilans-ges.xlsx', resource_XLSX)
upload_file(path + 'bilans-ges.zip', resource_CSV_ZIP)
