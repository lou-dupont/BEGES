import os
import requests

# This script tries to download all reports by scanning all possible integer identifiers in a given range.
# Unfortunately, we currently have no automated solution to guess the appropriate range.

url_pattern = 'http://www.bilans-ges.ademe.fr/fr/bilanenligne/detail/index/idElement/%d/back/bilans'
html_path = '../html/'
last_index = 4100

print('INFO: Checking output directory.')

if not os.path.exists(html_path):
    os.makedirs(html_path)

print('INFO: Iterating over expected pages.')

for index in range(1, last_index):
    url = url_pattern % index
    response = requests.get(url, allow_redirects=False)
    print('DEBUG: For file %d, received status code %d.' % (index, response.status_code))
    if response.status_code == 200:
        filename = html_path + '%d.html' % index
        with open(filename, 'wb') as file:
            file.write(response.content)

print('INFO: Finished.')
