from bs4 import BeautifulSoup
import pandas as pd
import requests
from itertools import chain 
import numpy as np 

def preprocessing (df): 
    #To int: 
    def to_int (item):
        a =[]
        for n in item:
            if n.isnumeric():
                a.append(n)
        return int(''.join(a)) 
    
    df['slutpris'] = df['slutpris'].apply(to_int) # convert to int 
    df['city-kommun'] = df['område'].apply(lambda i :  i.split()[-1] )# choose an specific character 
    df['type of boende'] = df['område'].apply(lambda i :  i.split()[0] )
    df['area'] = df['område'].apply(lambda row : row.split()[1].strip(','))
    df['size'] = df['size'].apply(lambda x: float(x.split()[0].replace(',', '.')) if len(x) >30 else np.nan)
    df['price_change'] = df['price_change'].apply(lambda x: x.split()[0] if type(x) != float and len(x)!=1 else np.nan)
    df['price_change'] = df['price_change'].apply(lambda x: int(x.strip('-')) if type(x) != float else np.nan)
    df['pris_per_m2'] = round(df['slutpris'] / df['size'],0)
    cols_to_drop = ['område']
    df.drop(cols_to_drop,axis=1,inplace=True)
    df = df[['gata','city-kommun','type of boende','area', 'slutpris', 'pris_per_m2', 'size', 'price_change']]
    return df 

def hemnet_generator(sold_age = '6m',area_code = None,num_pages = 3, keyword = None ,relevant_size = False, min_size=40, max_size=50, max_loan = 2600000): 
    """
    Hemnet scraper function 
    """
    adress_ = [] 
    adress2_ = []
    size = [] 
    tomt_size = [] 
    slutpris_ = [] 
    pris_per_m2_ = [] 
    price_change = [] 
    
    for n in range(1,num_pages + 1 ):
        # Parse all the pages that I need 
        
        järfälla_url = f"https://www.hemnet.se/salda/bostader?location_ids%5B%5D={area_code}&page={n}&sold_age={sold_age}"
        for page in järfälla_url:
            b = ''.join(järfälla_url)
        page = requests.get(b)
        soup = BeautifulSoup(page.text, "html.parser")
        
        # Main variables 
        location = soup.findAll('div', class_='sold-property-listing__location')
        price = soup.findAll('div', class_='sold-property-listing__price')
        main_size = soup.findAll('div', class_='sold-property-listing__size')
        fee1 = soup.find_all('div', class_= "sold-property-listing__fee")
        
        # Sub variables - Observe that the class_name could change 
        adr = [i.find('span', class_= 'item-result-meta-attribute-is-bold item-link qa-selling-price-title').text for i in location]
        adr2 =  [i.find('div').text for i in location]
        sp =[i.find('span', class_= 'sold-property-listing__subheading sold-property-listing--left').text for i in price]
        si = [i.find('div').text for i in main_size]
        p_m2 =[i.find('div', class_= 'sold-property-listing__price-per-m2 sold-property-listing--left') for i in price ] 
        
        # Preprocess price change 
        for i in soup.findAll('div', class_='sold-property-listing'): 
            pc = i.find('div', class_='sold-property-listing__price-change')
            if pc == None:
                price_change.append(np.nan)
            else:
                price_change.append(pc.text)
        # Preprocess size 
        for row in soup.findAll('div', class_='sold-property-listing__size'): 
            a = row.find('div', class_='sold-property-listing__subheading')
            size.append(a.text)
        
        ##### To lists:
        adress_.append(adr)
        adress2_.append(adr2)
        slutpris_.append(sp)
        pris_per_m2_.append(p_m2)
        
    ##### Flatten arrays 
    adress = list(chain.from_iterable(adress_))
    pris_per_m2 = list(chain.from_iterable(pris_per_m2_))
    slutpris = list(chain.from_iterable(slutpris_))
    adress2 = list(chain.from_iterable(adress2_))
        
    d = {
        'gata': adress, 
        'område':adress2, 
        'slutpris':slutpris,
        'pris_per_m2':pris_per_m2,
        'size':size,
        'price_change':price_change
        }
    ##### Data Cleansing
    df = pd.DataFrame(d)
    df = preprocessing (df)
    df['label'] = df['slutpris'].apply(lambda x: 'possible' if x <= max_loan else 'less possible')

    ##### Take only a part of the dataset 
    if relevant_size: 
        if area_code == 18027: # Sollentuna code  
            df = df[(df['size']>= min_size) & (df['size']<= 60)]
        else:
            df = df[(df['size']>= min_size) & (df['size']<= max_size)] 
    else: 
        df
        
    ##### Checking keywords 
    if keyword != None :
        kw_list = []
        for row in df.gata: 
            if keyword in row:
                kw_list.append(row)
        return df[df["gata"].isin(kw_list)] 
               
    else:
        return df   


def dep_filter(df, min_size=40, max_size= 75 , max_price=None,probas= False):
    """
    Standard function to return general stats about the apartament and return probability
    """
    num_deps_all = int(len(df[(df['size']>=min_size) & (df['size']<=max_size)]))
    df_all = df[(df['size']>=min_size) & (df['size']<=max_size)]
    if max_price != None:
        if probas == False:
            df = df[(df['size']>=min_size) & (df['size']<=max_size) & (df['slutpris']<=max_price)]
            num_deps = int(len(df))
            price_change = round(df_all['price_change'].mean(),2)
            price_per_m2 = round(df_all['pris_per_m2'].mean(),2) 
            p1 =  max_price * (price_change/100) 
            start_price = round(max_price - p1,0)
            mean_final_price = round(df_all['slutpris'].mean(),2)
            prob = round(num_deps / num_deps_all * 100,2)
            return f'There were {num_deps} number of deps sold. The average price change is{price_change},the price per square meter is {price_per_m2}, the avg final price is {mean_final_price} and the start price in Hemnet could be {start_price}. The probobability is {prob} since the total number of deps is {num_deps_all}'
        elif probas:
            df = df[(df['size']>=min_size) & (df['size']<=max_size) & (df['slutpris']<=max_price)]
            num_deps = int(len(df))
            prob = round(num_deps / num_deps_all * 100,2)
            return prob 
    else:
        return num_deps_all

# Compare the percentage of change in zones 
def pct_change_metric (area_code , num_pages= 50, metric = 'pris_per_m2'):
    """
    Quick comparision of change previous or new data
    """
    comp = {}   
    sold_ages = ['12m','6m','3m']
    for sold_age in sold_ages: 
        print(f'Calculating param {sold_age}...')
        df = hemnet_generator(area_code = area_code, num_pages = 50,sold_age=sold_age)
        mean_metric = df[metric].mean() 
        comp[sold_age] =  mean_metric 
        
    ans = round((comp['3m'] - comp['12m']) / comp['12m'] *100, 0 )
    bol = 'increased' if  ans > 0 else 'decreased'
    
    print( f'The {metric} has {bol} by {ans}%')
    print(comp)

