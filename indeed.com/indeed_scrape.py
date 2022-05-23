import csv
import time
import requests
import openpyxl
import pandas as pd
from bs4 import BeautifulSoup
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

filepath = input("Enter Excel file name: ")
wb = openpyxl.Workbook()
wb.save(filepath+'.xlsx')

def session_request(url, stream=False):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url, headers=headers)
    return response


stop = None
next = input("Enter Indeed Job Results URL: ")
columns = ['Job Link', 'Job Title','Company Name','Company Profile Indeed URL','Location','Date Posted',
            'Founded','Company Size','Revenue','Industry','Company Website Link']
data = [columns]
while 1:
    n= -1
    while n == -1:
        main_response = session_request(next)
        soup_main = BeautifulSoup(main_response.text,"lxml")
        job_links = soup_main.find_all('a', {'class':'jcs-JobTitle'})
        if len(job_links) > 0:
            print('Indeed blocked You, Retrying...')
            n=1

    for job_link in  job_links:
        print('Running>>>')
        job_link = 'https://www.indeed.com'+job_link['href']
        response = session_request(job_link)
        soup = BeautifulSoup(response.text,"html.parser")
        job_title = soup.find('h1').text.strip() if soup.find('h1') else None
        main_company_div = soup.find('div', {'class':'jobsearch-InlineCompanyRating icl-u-xs-mt--xs jobsearch-DesktopStickyContainer-companyrating'})
        sub_company_div = main_company_div.find_all('div', {'class':'icl-u-lg-mr--sm icl-u-xs-mr--xs'})[1] if main_company_div else None
        company =  sub_company_div.find('a') if sub_company_div else None
        company_name = company.text.strip() if company else None
        company_indeed_url = company['href'] if company and company.has_attr('href') else None
        location_div = soup.find('div', {'class':'icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle'})
        location = location_div.find_all('div') if location_div else None
        location = location[-2].text.strip() if location else None
        posted_list = soup.find('span', {'class':'jobsearch-HiringInsights-entry--text'}).text.strip().split(' ') if soup.find('span',{'class':'jobsearch-HiringInsights-entry--text'}) else None
        post_day = None
        for post in posted_list:
            if posted_list[0].lower() in 'just':
                post_day = ' '.join(posted_list)
            else:
                post_day = ' '.join(posted_list[1:])

        if company_indeed_url== None : continue
        company_response = session_request(company_indeed_url)
        soup_company = BeautifulSoup(company_response.text,"html.parser")
        founded_li = soup_company.find('li', {'data-testid':'companyInfo-founded'})
        founded_div = founded_li.find('div', {'class':'css-1w0iwyp e1wnkr790'}) if founded_li else None
        founded = founded_div.text.strip() if founded_div else None
        size_li = soup_company.find('li', {'data-testid':'companyInfo-employee'})
        size_div = size_li.find('div', {'class':'css-1w0iwyp e1wnkr790'}, recursive=False) if size_li else None
        span = size_div.text.strip() if size_div else []
        if 'more' in span or 'less' in span:
            size = span.split(' ')[-1]
        else:
            size = span
        revenue_li = soup_company.find('li', {'data-testid':'companyInfo-revenue'})
        revenue_div = revenue_li.find('div', {'class':'css-1w0iwyp e1wnkr790'}) if revenue_li else None
        revenue = revenue_div.text.strip() if revenue_div else None

        industry_li = soup_company.find('li', {'data-testid':'companyInfo-industry'})
        industry_div = industry_li.find('div', {'class':'css-1w0iwyp e1wnkr790'}) if industry_li else None
        industry = industry_div.text.strip() if industry_div else None

        company_url_li = soup_company.find('li', {'data-testid':'companyInfo-companyWebsite'})
        company_url_div = company_url_li.find('div', {'class':'css-1k3kdg3 e37uo190'}) if company_url_li else None
        company_url_a = company_url_div.find('a') if company_url_div else None
        company_url = company_url_a['href'] if company_url_a else None
        data_item = [job_link, job_title, company_name, company_indeed_url, location, post_day, founded, size, revenue, industry, company_url]
        data.append(data_item)
        
        with open(f'{filepath}.csv', mode='a+', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(data) 
        data= []
        time.sleep(10)
    with pd.ExcelFile(f"{filepath}.xlsx", engine='openpyxl') as writer:  
        df = pd.read_csv(f'{filepath}.csv')
        df.drop_duplicates(inplace=True)
        df.to_excel(writer, sheet_name='Sheet1', index = False)

    next_ul = soup_main.find('ul', {'class':'pagination-list'})
    next_li = next_ul.find_all('li') if next_ul else None
    next_li_final = next_li[-1] if next_li else None
    next_a = next_li_final.find('a') if next_li_final else None
    next = 'https://www.indeed.com' + next_a['href'] if next_a else None
    print(stop)
    if stop == next:
        break
    print(next)
    stop = next
    print(f"########## Change page to {next}  ###############")
        