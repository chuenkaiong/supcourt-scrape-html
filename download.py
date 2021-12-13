from bs4 import BeautifulSoup
import json
import re
import requests
import os
import settings

meta_path = settings.meta_path
html_path = settings.html_path
pdf_path = settings.pdf_path


def get_urls():
    main_url = 'https://www.elitigation.sg/gdviewer'
    r = requests.get(main_url)
    if r.status_code != 200:
        print('Failed to load main url:', main_url)
        return
    soup = BeautifulSoup(r.text, 'lxml')
    div = soup.find('div', class_='gd-csummary')
    total = div.get_text().split(':')[-1].strip()
    assert total.isdigit()
    page_count = int(total) // 10 + 1

    # if os.path.exists(meta_path + 'info.json'):
    #     with open(meta_path + 'info.json', encoding='utf-8') as f:
    #         cases = json.load(f)
    # else:
    #     cases = []
    cases = []

    for i in range(1, 2):
    # for i in range(1, page_count + 1):
        url = main_url + '/Home/Index?YearOfDecision=All&SortBy=DateOfDecision&CurrentPage=' + str(i)
        r = requests.get(url)
        if r.status_code != 200:
            print('Failed to get page:', url)
            continue
        soup = BeautifulSoup(r.text, 'lxml')
        for div in soup.select('div.card.col-12'):
            div_tag = div.find('div', class_='gd-catchword-container')
            # tags = ['/'.join(x.strip('[] ') for x in re.split('\s+[—-]+\s+', a.get_text().strip('[] \r\n'))) for a in div_tag.find_all('a', class_='gd-cw')]
            # if len(tags) == 1 and re.search(r'\]\s+\[', tags[0]):
            #     tags = re.split(r'\]\s+\[', tags[0])
            # # "Criminal Law/Offences/Murder]\r\n[Criminal Law/General exceptions/Unsoundness of mind]\r\n[Criminal Procedure and Sentencing/Accused of unsound mind"
            tags = [a.get_text().strip('[] \r\n') for a in div_tag.find_all('a', class_='gd-cw')]
            div_gd = div.find('div', class_='gd-card-body')
            div_name = div_gd.find('a', class_='h5') # gd-card-title
            if div_name:
                name = div_name.get_text().strip()
                href = div_name.get('href')
            for span in div_gd.find_all('span', class_='gd-addinfo-text'):
                text = span.get_text().strip(' |')
                if re.match(r'\[\d{4}\]\s+[A-Z\(\)3]{4,}\s+\d+', text):
                    citation = text
                elif 'Decision Date' in text:
                    date = text.split(': ')[-1]
                else:
                    casenumber = text
            case_info = {
                'href': href,
                'casenumber': casenumber,
                'citation': citation,
                'date': date,
                'name': name,
                'tags': tags,
            }
            # if case_info in cases:
            #     if len(cases) != int(total):
            #         print(f'**WARNING: Number of cases mismatch. Downloaded {len(cases)} but should have {total} cases.')
            #     with open(meta_path + 'info.json', 'w', encoding='utf-8') as f:   
            #         json.dump(cases, f)
            #     return               
            cases.append(case_info)
        if len(cases) % 100 == 0:
            print(f'Processed {len(cases)} cases.')
    with open(meta_path + 'info.json', 'w', encoding='utf-8') as f:   
        json.dump(cases, f)


def download_judgms():
    with open(meta_path + 'info.json', encoding='utf-8') as f:
        cases = json.load(f)
    for case in cases:
        gd_url = case['href']
        fname = gd_url.rsplit('/', maxsplit=1)[-1] + '.html'
        fname = html_path + fname
        if os.path.exists(fname):
            continue
        url = 'https://www.elitigation.sg' + gd_url.replace('SUPCT/', '')
        r = requests.get(url)
        if r.status_code != 200:
            print('Failed:', url)
            continue
        if 'Page Not Found' in r.text:
            print('Page not found:', url)
            continue
        with open(fname, 'w', encoding='utf=8') as f:
            f.write(r.text)
        # pdf_fname = gd_url.rsplit('/', maxsplit=1)[-1] + '.pdf'
        # pdf_fname = pdf_path + pdf_fname
        # if os.path.exists(pdf_fname):
        #     continue       
        # pdf_url = url + '/pdf'
        # r = requests.get(pdf_url)
        # if r.status_code != 200:
        #     print('No PDF:', pdf_url)
        #     continue
        # with open(pdf_fname, 'wb') as f:
        #     f.write(r.content)


get_urls()
download_judgms()