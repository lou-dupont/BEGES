import bs4
import os
import re
import requests

# HTML files will be downloaded in the following directory

html_path = '../html/'

# This script tries to download all reports by scanning all possible integer identifiers (starting from 1).
# Unfortunately, we don't have a reliable method to determine the last index, so we decide that we stop trying new
# indexes after scanning more than GIVE_UP_THRESHOLD indexes without finding any valid URL.

GIVE_UP_THRESHOLD = 100

# Main download script

print('INFO: Checking output directory.')

if not os.path.exists(html_path):
    os.makedirs(html_path)

print('INFO: Downloading search result lists.')


def build_payload(type_id, page):
    return {'TYS_ID': type_id, 'BGS_NOM_ENTREPRISE': '', 'SEA_ID': '', 'RDR_CODE': '', 'BGS_ANNEE_REPORTING': '',
            'MIN_SLR': '', 'MAX_SLR': '', 'IS_SCOPE3': 0, 'BT_ID': '', 'page': page}

url = 'http://www.bilans-ges.ademe.fr/fr/bilanenligne/bilans/xhr-page'
published_indexes = []

# To download the set of published indexes
for type_id in [1, 2, 3, 4]:
    response = requests.post(url, data=build_payload(type_id, 1))
    content = bs4.BeautifulSoup(response.content, 'lxml')
    count_text = content.find('h4', {'class': 'bilans'}).text
    count = int(re.sub('[^0-9]', '', count_text))
    print('DEBUG: For type %d, received %d results.' % (type_id, count))
    for page in range(count // 10 + 1):
        print('DEBUG: Querying page %d.' % (page + 1))
        response = requests.post(url, data=build_payload(type_id, page + 1))
        content = bs4.BeautifulSoup(response.content, 'lxml')
        links = content.find_all('a', {'class': 'button voir'})
        for link in links:
            report_id = re.sub('[^0-9]', '', link.get('href'))
            published_indexes.append(int(report_id))

published_indexes = sorted(list(set(published_indexes)))
with open(html_path + 'indexes.txt', 'w') as file:
    for index in published_indexes:
        file.write(str(index) + '\n')

# To load the set of published indexes from a file
# with open(html_path + 'indexes.txt', 'r') as file:
    # for line in file:
        # published_indexes.append(int(line.replace('\n', '')))

print('INFO: Iterating over expected pages.')

url_pattern = 'http://www.bilans-ges.ademe.fr/fr/bilanenligne/detail/index/idElement/%d/back/bilans'
last_valid_index = 0
index = 1

while index - last_valid_index <= GIVE_UP_THRESHOLD:
    url = url_pattern % index
    response = requests.get(url, allow_redirects=False)
    print('DEBUG: For file %d, received status code %d.' % (index, response.status_code))
    filename = html_path + '%d.html' % index
    if response.status_code == 200:
        last_valid_index = index
        with open(filename, 'wb') as file:
            file.write(response.content)
    else:
        # We typically receive a 302 code when the index is not associated with an existing page, and the website tries
        # to redirect us towards the home page.
        if os.path.exists(filename):
            # The file was probably downloaded previously, but the page was removed from the website. We decide to trash
            # it also on our side since we want to be synchronized with the distant website.
            print('WARNING: Page %d is not present anymore on the website. Deleting it locally.' % index)
            os.remove(filename)
    index += 1

print('INFO: Finished iterating.')
