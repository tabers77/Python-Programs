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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

#############
# Standard Paramters 
#############

min_size = 40
max_size = 60
all_pages = True
pages_size = 5 if all_pages == False else 50 

def url_extractor(area ='sundbyberg',keys = None, min_year = 1980):
    """
    
    """
    print('INITIAL EXTRACTION...')
    chromeOptions = Options() 
    #chromeOptions.headless = True
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('window-size=1920x1080')
    chrome_browser = webdriver.Chrome('/Users/Tabe/Desktop/pythonprojects/automation/chromedriver' , options=chromeOptions)
    chrome_browser.get('https://www.hemnet.se/bostader?item_types%5B%5D=bostadsratt')
    
    try:
        cookie_button = chrome_browser.find_element_by_xpath('/html/body/div[9]/div/div/div[2]/div/button')
        cookie_button.click()
        time.sleep(2)
    except NoSuchElementException: 
        cookie_button = chrome_browser.find_element_by_xpath('/html/body/div[10]/div/div/div[2]/div/button')
        cookie_button.click()

    try:
    # Area 
        box = chrome_browser.find_element_by_xpath('//*[@id="area-search-input-box"]')
        box.clear()
        box.send_keys(area)
        time.sleep(2)
        dropdown = chrome_browser.find_element_by_xpath('//*[@id="search-location-dropdowns"]/div/div[2]/div[1]/ul/li[1]')
        dropdown.click() # dropdown 
        time.sleep(2)
    # Bo area
        min_area = chrome_browser.find_element_by_xpath('//*[@id="search_living_area_min"]/option[6]')
        #max_area =  chrome_browser.find_element_by_xpath('//*[@id="search_living_area_max"]/option[11]') 

        time.sleep(2)
        min_area.click() # dropdown 
        time.sleep(2)
        #max_area.click() # dropdown 
        #time.sleep(2)
    
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
        

def calculate_time(start = 'vasavägen 89'  , dest = 'mariatorget' ): 
    print(f'CALCULATING FOR {start}...')
    # Headless is not working here and it is slowing down the application
    #chromeOptions = Options()# test 
    #chromeOptions.headless = True# test 
    #chromeOptions.add_argument('--headless')# test 
    #chromeOptions.add_argument('window-size=1920x1080')# test 
    chrome_browser = webdriver.Chrome('/Users/Tabe/Desktop/pythonprojects/automation/chromedriver')
    chrome_browser.get('https://www.google.com/maps/dir/')

    time.sleep(5)
    # 1.1 cookie 
    chrome_browser.switch_to.frame(chrome_browser.find_element_by_xpath('//*[@id="consent-bump"]/div/div[1]/iframe') )
    element = chrome_browser.find_element_by_id('introAgreeButton')
    element.click()

    # 2 write start point and destination 
    start_point = chrome_browser.find_element_by_xpath('//*[@id="sb_ifc50"]/input')
    start_point.clear()
    start_point.send_keys(start)

    destination = chrome_browser.find_element_by_xpath('//*[@id="sb_ifc51"]/input')
    destination.clear()
    destination.send_keys(dest)
    
    # 3 click on transit 
    transit = chrome_browser.find_element_by_xpath('//*[@id="omnibox-directions"]/div/div[2]/div/div/div[1]/div[3]/button/img')
    transit.click() 
    time.sleep(5)
  
    output = chrome_browser.find_element_by_xpath( '//*[@id="section-directions-trip-0"]/div[1]/div[2]/div[1]/div' ).text
    return  output

######
# 2 Initial scrape
######

def scraper2(current_url, relevant_only = 'yes' , sold_age = '6m' , loan_limit = 2985000 , dest_street = 'mariatorget'  ):
    """
    Scrape results 
    """
    print('STEP 1: SCRAPING - BASELINE...')
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
    df['area_fixed'] = df['area'].apply(lambda x: x.split(' ')[0] ) # here I only take the first character
    df['street'] = df['street'].apply(lambda x: x.strip('\n ') )
    #df['street'] = df['street'].apply(lambda x: x.split(',')[0])
    df['street'] = df['street'].apply(lambda x: re.split('/|,|-' , x)[0] ) 
    df.drop('location', axis = 1 , inplace = True )

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

    area_inp = df['city-kommun'][0] # get the area
    pat = re.compile(r"\b(\w*{}\w*)\b".format(area_inp.lower()))

    area_code = 0
    for i in area_codes.keys(): 
        if pat.search(i):
            area_code+= area_codes[i]
    # Observe that if we choose a short span for sold_age we could still see outliers for the price change calculation
    history = hemnet_generator(sold_age = sold_age, area_code = area_code  ,num_pages = pages_size, relevant_size= True)
     
    # 1 Define dict 
    by_area = history.groupby('area_g1').price_change.mean().reset_index() 
    d = pd.Series (data = by_area.price_change.values , index = by_area.area_g1 ).to_dict()

    # 2 fill nan values
    mean_val = round(by_area.price_change.mean())
    pct_change_dict = {k: mean_val if np.isnan(v) else v for k,v in d.items()}

    # 3 match the area 
    df['pct_change'] = df['area_fixed'].map(pct_change_dict)
      
    print('STEP 4: GENERATING LAST FEATURES...')
    
    #mean_price_change = history.price_change.mean() # 
    mean_price_per_m2 = history.pris_per_m2.mean()
    
    df['predicted_price'] = df.start_price +  (df.start_price  * (df['pct_change']/100) )

       
    df['price_per_m2'] = df.start_price /  df.ap_size
    df['label'] = df.predicted_price.apply(lambda x: 'possible' if x <= loan_limit else 'less possible')
    df['expected_price'] = df.ap_size * mean_price_per_m2

    # re order cols  
    df = df[['city-kommun','area','area_fixed','pct_change','street', 'label','ap_size','number_of_rooms','start_price','predicted_price','expected_price','price_per_m2','links']]
    
    if relevant_only == 'yes' : 
       
        df_new = df[df['label']=='possible'].sort_values('predicted_price') 
        ##### TEST 
        print('STEP 2.1: CALCULATING DISTANCES')
        df_new['distance_to_work'] =  df_new['street'].apply(lambda street:  calculate_time (start = street , dest = dest_street) )
        ##### TEST    
        return df_new
    elif relevant_only == 'no' : 
        print('DONE')
        return df.sort_values('predicted_price') 
    else:
        raise KeyError 