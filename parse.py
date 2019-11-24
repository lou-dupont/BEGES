import bs4
import os
import pandas as pd
import re

# HTML files will be parsed from the following directory

html_path = '../html/'

# Output consolidated files will be generated in the following directory

output_path = '../output/'

# Main parsing logic

url_pattern = 'http://www.bilans-ges.ademe.fr/fr/bilanenligne/detail/index/idElement/%d/back/bilans'
raw_codes_pattern = re.compile('([0-9]{9}) - (.+) \\(([0-9]{3,5}[A-Z])\\)( - ([^\\(\\)]+) \\(([^\\(\\)]+)\\))?')

keys = {
    'Code(s) NAF :': 'legal_units',
    'Descriptif Sommaire de l\'activité :': 'organization_description',
    'Effectifs': 'staff',
    'Mode de consolidation': 'consolidation_method',
    'Nombre d\'agents': 'staff',
    'Nombre de salariés': 'staff',
    'Population :': 'population',
    'Type :': 'organization_type',
    'Type de collectivité :': 'collectivity_type'
}
text_ids = {
    'bloc-pa-scope1': 'Plan d\'action Scope 1',
    'bloc-pa-scope2': 'Plan d\'action Scope 2',
    'bloc-pa-scope3': 'Plan d\'action Scope 3',
    'presentation-entreprise': 'Présentation de l\'organisation',
    'politique-developpement-durable': 'Politique de développement durable',
    'bloc-m-scope1': 'Méthodologie Scope 1',
    'bloc-m-scope2': 'Méthodologie Scope 2',
    'bloc-m-scope3': 'Méthodologie Scope 3',
    'bloc-m-incertitude': 'Méthodologie Incertitudes',
    'bloc-m-exclusion': 'Méthodologie Exclusions',
    'bloc-m-source': 'Méthodologie Sources',
    'bloc-m-recalcul': 'Méthodologie Recalcul',
    'bloc-m-siret': 'Méthodologie SIRET',
}
reductions = {
    'reductions_scope_1_2': re.compile('.*attendu pour les scopes 1 et 2 est de ([0-9]+\\.[0-9]+) tCO2e.*'),
    'reductions_scope_1': re.compile('.*attendu pour le scope 1 est de ([0-9]+\\.[0-9]+) tCO2e.*'),
    'reductions_scope_2': re.compile('.*attendu pour le scope 2 est de ([0-9]+\\.[0-9]+) tCO2e.*'),
    'reductions_scope_3': re.compile('.*attendu pour le scope 3 est de ([0-9]+\\.[0-9]+) tCO2e.*'),
}

print('INFO: Started.')

assessments = []
emissions = []
legal_units = []
texts = []


def get_value(cell):
    value = cell.text.strip()
    if value == 'nc':
        value = ''
    if value != '':
        value = float(value.replace(',', '.'))
    return value


def clean_string(value):
    result = value.strip()
    return result


def find_text(html_content, div_id):
    div = html_content.find('div', {'id': div_id})
    if div is None:
        return ''
    else:
        if div_id == 'politique-developpement-durable' or div_id == 'presentation-entreprise':
            div = div.find('div').find('div')
        for p in div.findAll('p'):
            if p.text.strip() == '':
                p.extract()
        result = '\n'.join([str(child) for child in div.contents]).strip()
        result = re.sub(r'\n+', "\n", result)
        return result


def load_emissions_table(table, assessment_index, assessment_type):
    result = []
    totals = {1: 0, 2: 0, 3: 0}
    for row in table.findAll('tr'):
        cells = row.findAll(['td', 'th'])
        if len(cells) == 7 and re.match('[0-9]+', cells[0].text.strip()):
            scope_item_id = int(cells[0].text.strip())
            emission = {
                'assessment_id': assessment_index,
                'type': assessment_type,
                'scope_item_id': scope_item_id,
                'co2': get_value(cells[1]),
                'ch4': get_value(cells[2]),
                'n2o': get_value(cells[3]),
                'other': get_value(cells[4]),
                'total': get_value(cells[5]),
                'co2_biogenic': get_value(cells[6]),
            }
            if emission['total'] != '':
                total = emission['total']
                if scope_item_id <= 5:
                    totals[1] += total
                elif scope_item_id <= 7:
                    totals[2] += total
                else:
                    totals[3] += total
            if emission['total'] != '' or emission['co2_biogenic'] != '':
                result.append(emission)
    return result, totals


def extract_codes(codes_text):
    codes_text = re.sub('\s+', '', codes_text)
    codes_text = re.sub('-+', '', codes_text)
    siret_codes = re.findall(r"[0-9]{14}", codes_text)
    for siret_code in siret_codes:
        codes_text = codes_text.replace(siret_code, '')
    siren_codes = re.findall(r"[0-9]{9}", codes_text)
    siren_codes = siren_codes + [siret_code[:9] for siret_code in siret_codes]
    return siren_codes, siret_codes


print('INFO: Checking output directory.')
if not os.path.exists(output_path):
    os.makedirs(output_path)


print('INFO: Loading published indexes.')
published_indexes = []
with open(html_path + 'indexes.txt', 'r') as file:
    for line in file:
        published_indexes.append(int(re.sub('[^0-9]', '', line)))

print('INFO: Processing files.')
filename_pattern = re.compile(r'([0-9]+).html')
filenames = [x for x in os.listdir(html_path) if filename_pattern.match(x) is not None]
indexes = sorted([int(filename_pattern.match(x).groups()[0]) for x in filenames])
for index in indexes:
    filename = html_path + '%d.html' % index
    with open(filename, encoding='utf-8') as file:
        print('DEBUG: Processing file %s.' % filename)
        content = bs4.BeautifulSoup(file, 'lxml')
        assessment = {
            'id': index,
            'source_url': url_pattern % index,
            'organization_name': clean_string(content.find('div', {'id': 'nomEntreprise'}).text),
            'reporting_year': int(content.find('div', {'class': 'anneefiche'}).text.strip()),
            'is_draft': not index in published_indexes,
        }
        reference = content.find('label', {'for': 'BGS_IS_ANNEE_REFERENCE_CALCULE'})
        if reference is not None:
            assessment['reference_year'] = int(reference.next_sibling.strip().replace('01/01/', ''))
        # Texts
        has_action_plan = False
        for text_div_id in sorted(text_ids):
            text = find_text(content, text_div_id)
            if text != '':
                texts.append({'assessment_id': index, 'key': text_ids[text_div_id], 'value': text})
                if 'bloc-pa-scope' in text_div_id:
                    has_action_plan = True
                if text_div_id == 'bloc-m-siret':
                    siren_codes, siret_codes = extract_codes(text)
                    for siren_code in siren_codes:
                        legal_units.append({
                            'assessment_id': index,
                            'legal_unit_id_type': 'SIREN',
                            'legal_unit_id': siren_code,
                        })
                    for siret_code in siret_codes:
                        legal_units.append({
                            'assessment_id': index,
                            'legal_unit_id_type': 'SIRET',
                            'legal_unit_id': siret_code,
                        })
        assessment['action_plan'] = 'Oui' if has_action_plan else 'Non'
        # Reductions
        reductions_p = content.find_all('p', {'class': 'pBold'})
        reductions_text = ''.join([p.text for p in reductions_p])
        reductions_text = reductions_text.replace("\n", '')
        for reduction_key, reduction_pattern in reductions.items():
            reduction_match = reduction_pattern.match(reductions_text)
            if reduction_match is not None:
                assessment[reduction_key] = float(reduction_match.groups()[0])
        # Others
        identity_card = content.find('div', {'id': 'fiche-identite'})
        identity_table = identity_card.find('td', text=re.compile('Type :')).findParent('table')
        for identity_row in identity_table.findAll('tr'):
            identity_key = identity_row.findAll('td')[0].text.strip()
            identity_value = identity_row.findAll('td')[1].text
            assessment[keys[identity_key]] = clean_string(identity_value)
        if 'legal_units' in assessment:
            for line in assessment['legal_units'].splitlines():
                if len(line.strip()) > 0:
                    match = raw_codes_pattern.match(line.strip())
                    if match is not None:
                        legal_unit = {
                            'assessment_id': index,
                            'legal_unit_id_type': 'SIREN',
                            'legal_unit_id': match.groups()[0],
                        }
                        legal_units.append(legal_unit)
                    else:
                        print('ERROR: Invalid legal unit string format "%s".' % line)
            del assessment['legal_units']
        if 'staff' in assessment and assessment['staff'] != '':
            assessment['staff'] = int(assessment['staff'])
        if 'population' in assessment and assessment['population'] != '':
            assessment['population'] = int(assessment['population'])
        current_table = content.find('table', {'id': 'tableauAnneeDeclaration'})
        if current_table is not None:
            current_emissions, current_totals = load_emissions_table(current_table, index, 'Déclaration')
            emissions += current_emissions
            assessment['total_scope_1'] = current_totals[1]
            assessment['total_scope_2'] = current_totals[2]
            assessment['total_scope_3'] = current_totals[3]
        reference_table = content.find('table', {'id': 'tableauAnneeReference'})
        if reference_table is not None:
            reference_emissions, reference_totals = load_emissions_table(reference_table, index, 'Référence')
            emissions += reference_emissions
        assessments.append(assessment)

print('INFO: Converting and saving to CSV/XLSX tables.')

emissions = pd.DataFrame(emissions)
emissions = emissions[['assessment_id', 'type', 'scope_item_id', 'co2', 'ch4', 'n2o', 'other', 'total', 'co2_biogenic']]
emissions.to_csv(output_path + 'emissions.csv', index=False, encoding='UTF-8')

assessments = pd.DataFrame(assessments)
assessments = assessments[['id', 'organization_name', 'organization_description', 'organization_type', 
                           'collectivity_type', 'staff', 'population', 'consolidation_method', 'reporting_year', 
                           'total_scope_1', 'total_scope_2', 'total_scope_3',
                           'reference_year', 'action_plan',
                           'reductions_scope_1_2', 'reductions_scope_1', 'reductions_scope_2', 'reductions_scope_3',
                           'is_draft', 'source_url']]
assessments.to_csv(output_path + 'assessments.csv', index=False, encoding='UTF-8')

legal_units = pd.DataFrame(legal_units)
legal_units = legal_units[['assessment_id', 'legal_unit_id_type', 'legal_unit_id']]
legal_units = legal_units.drop_duplicates()
legal_units.to_csv(output_path + 'legal_units.csv', index=False, encoding='UTF-8')

texts = pd.DataFrame(texts)
texts.to_csv(output_path + 'texts.csv', index=False, encoding='UTF-8')

scope_items = pd.read_csv('scope_items.csv', index_col=False, encoding='UTF-8')
scope_items.to_csv(output_path + 'scope_items.csv', index=False, encoding='UTF-8')

with pd.ExcelWriter(output_path + 'BEGES.xlsx') as writer:
    scope_items.to_excel(writer, sheet_name='scope_items', index=False)
    assessments.to_excel(writer, sheet_name='assessments', index=False)
    legal_units.to_excel(writer, sheet_name='legal_units', index=False)
    emissions.to_excel(writer, sheet_name='emissions', index=False)
    texts.to_excel(writer, sheet_name='texts', index=False)

print('INFO: Finished.')
