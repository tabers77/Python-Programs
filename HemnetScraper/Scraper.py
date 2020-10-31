# Libraries 
import pandas as pd
from selenium import webdriver 
import time
from bs4 import BeautifulSoup
import requests
from itertools import chain 
import numpy as np 
import re  
from Hemnet import preprocessing,hemnet_generator, dep_filter, pct_change_metric

#############
# Standard Paramters 
#############

min_size = 40
max_size = 60
all_pages = True
pages_size = 5 if all_pages == False else 50 

def url_extractor(area ='sundbyberg',keys = None, min_year = 1980):
    print('INITIAL EXTRACTION...')
    chrome_browser = webdriver.Chrome('/Users/Tabe/Desktop/pythonprojects/automation/chromedriver')
    chrome_browser.get('https://www.hemnet.se/bostader?item_types%5B%5D=bostadsratt')
    chrome_browser.maximize_window() 
    try:
        cookie_button = chrome_browser.find_element_by_xpath('/html/body/div[9]/div/div/div[2]/div/button')
        cookie_button.click()
        time.sleep(2)
    except NoSuchElementException: 
        cookie_button = chrome_browser.find_element_by_xpath('/html/body/div[10]/div/div/div[2]/div/button')
        cookie_button.click()
    #/html/body/div[8]/div/div/form/div[1]/div[2]/label[3]/span[2]

    try:
    # Area 
        box = chrome_browser.find_element_by_xpath('//*[@id="area-search-input-box"]')
        box.clear()
        time.sleep(2)
        box.send_keys(area)
        time.sleep(2)
        dropdown = chrome_browser.find_element_by_xpath('//*[@id="search-location-dropdowns"]/div/div[2]/div[1]/ul/li[1]')
        dropdown.click() # dropdown 
        time.sleep(2)
    # Bo area
        min_area = chrome_browser.find_element_by_xpath('//*[@id="search_living_area_min"]/option[6]')
        max_area =  chrome_browser.find_element_by_xpath('//*[@id="search_living_area_max"]/option[11]') 

        time.sleep(2)
        min_area.click() # dropdown 
        time.sleep(2)
        max_area.click() # dropdown 
        time.sleep(2)
    
    # Search price max : 2650 000

        op3 =  chrome_browser.find_element_by_xpath('//*[@id="search_price_max"]/option[15]')
        op3.click() # dropdown 
        time.sleep(2)
    
        if keys != None:
            search_keywords =  chrome_browser.find_element_by_xpath('//*[@id="search_keywords"]')
            search_keywords.send_keys(keys)
            time.sleep(1)
        
        op4 =  chrome_browser.find_element_by_xpath('//*[@id="new_search"]/button')
        op4.click() # dropdown 
    
        construction_year =  chrome_browser.find_element_by_xpath('//*[@id="search_construction_year_min"]')
        construction_year.send_keys(min_year)
        time.sleep(1)

        op5 = chrome_browser.find_element_by_xpath('//*[@id="search_fee_max"]/option[10]')
        op5.click() # dropdown 
        time.sleep(2)
        cta = chrome_browser.find_element_by_xpath('//*[@id="new_search"]/div[3]/div/button')
        cta.click() # dropdown 
        time.sleep(3)
        current_url = chrome_browser.current_url
        print('DONE WITH INITIAL EXTRACTION')
        return current_url
    
    except ElementClickInterceptedException as err: 
        print(f'You got this error{err}')


######
# 2 Initial scrape
######
def scraper2(current_url, relevant_only = 'yes' , sold_age = '6m' , loan_limit = 2985000):

    print('STEP 1: SCRAPING...')
    res = requests.get(current_url)
    soup = BeautifulSoup(res.content,'html.parser')
    street  =  [i.text for i in soup.find_all('h2', class_ ="listing-card__street-address qa-listing-title" )]
    location  =  [i.text for i in soup.find_all('span', class_ ="listing-card__location-name" )]

    prices_ =  [ i.text for i in soup.find_all('div', class_ ="listing-card__attributes-row" ) ]
    prices  = [prices_[i] for i in range(0,len(prices_),2)]
    links =  []
    for link in soup.findAll('a', attrs={'href': re.compile("^https://www.hemnet")}):
        links.append(link.get('href') )
    d = {'street':street , 'location':location , 'prices':prices , 'links':links }
    df = pd.DataFrame(d)
    
    df['start_price'] = df.prices.apply(lambda x: x.split('\n\n')[1] )
    df['ap_size'] = df.prices.apply(lambda x: x.split('\n\n')[2] )
    df['number_of_rooms'] = df.prices.apply(lambda x: x.split('\n\n')[3] )
    df.drop('prices', axis = 1 ,inplace = True )
    
    print('STEP 2: GENERATING NEW FEATURES...')
    df['ap_size'] = df['ap_size'].apply(lambda x: float(x.split()[0] if ',' not in x else float(x.split()[0].replace(',', '.'))) )
    df['start_price'] = df.start_price.apply(lambda col: int(''.join([i for i in col if i.isnumeric()] )))
    df['number_of_rooms'] = df.number_of_rooms.apply(lambda col: int(''.join([i for i in col if i.isnumeric()] )))
    df['city-kommun'] = df.location.apply(lambda x: str(x.split()[-1:] )[1:-1].strip("''") )
    df['area'] = df.location.apply(lambda x: x.split(',')[0].strip('\n '))
    df['street'] = df['street'].apply(lambda x: x.strip('\n ') )
    df.drop('location', axis= 1 , inplace=True )
    
    print('STEP 3: OBTAINING HISTORICAL DATA TO CALCULATE PREDICTED PRICE...')
    area_codes = {'järfälla_code': 17951,
                  'sollentuna_code' :18027,
                  'solna_code':18028,
                  'sundbyberg_code': 18042,
                  'stockholms_län_code': 18031,
                  'vällingby_code' : 473464, 
                  'söder_code' :898472, 
                  'bromma': 898740
                 
                 }

    area = df['city-kommun'][0] # get the area
    pat = re.compile(r"\b(\w*{}\w*)\b".format(area.lower()))

    area_code = 0
    for i in area_codes.keys(): 
        if pat.search(i):
            area_code+= area_codes[i]
    
    history = hemnet_generator(sold_age = sold_age, area_code = area_code  ,num_pages = pages_size, relevant_size= True)
    
    print('STEP 4: GENERATING LAST FEATURES...')
    mean_price_change = history.price_change.mean()
    mean_price_per_m2 = history.pris_per_m2.mean()

    df['predicted_price'] = df.start_price +  (df.start_price  * (mean_price_change/100) )
    df['price_per_m2'] = df.start_price /  df.ap_size
    df['label'] = df.predicted_price.apply(lambda x: 'possible' if x <= loan_limit else 'less possible')
    df['expected_price'] = df.ap_size * mean_price_per_m2

    
    # re order cols  
    df = df[['city-kommun','area','street','label','ap_size','number_of_rooms','start_price','predicted_price','expected_price','price_per_m2','links']]
    
    if relevant_only == 'yes' : 
        print('DONE')
        df_new = df[df['label']=='possible'].sort_values('predicted_price') 
        return df_new
    elif relevant_only == 'no' : 
        print('DONE')
        return df.sort_values('predicted_price') 
    else:
        raise KeyError 
            
