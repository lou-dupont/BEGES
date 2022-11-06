import bs4
import os
import re
import requests

# HTML files will be downloaded in the following directory

html_path = './html/'

# This script tries to download all reports by scanning all possible integer identifiers (starting from 1).
# Unfortunately, we don't have a reliable method to determine the last index, so we decide that we stop trying new
# indexes after scanning more than GIVE_UP_THRESHOLD indexes without finding any valid URL.

GIVE_UP_THRESHOLD = 100

# Main download script

print('INFO: Checking output directory.')

if not os.path.exists(html_path):
    os.makedirs(html_path)

print('INFO: Iterating over expected pages.')

url_pattern = 'https://bilans-ges.ademe.fr/fr/bilanenligne/detail/index/idElement/%d/back/bilans'
index = 1
last_valid_index = index

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
