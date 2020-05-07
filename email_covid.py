import sys 
from selenium import webdriver 
import time 

browser = webdriver.Chrome('./chromedriver')
browser.maximize_window() 
browser.get('https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread/') 
table = browser.find_element_by_xpath('//*[@id="table3"]')

country1 = 'Ecuador'
country2 = 'Brazil'

c1 = table.find_element_by_xpath(f"//td[contains(., '{country1}')]")
c2 = table.find_element_by_xpath(f"//td[contains(., '{country2}')]")

row_c1 = c1.find_element_by_xpath("./..") # grab all the columns 
row_c2= c2.find_element_by_xpath("./..") # grab all the columns 

data_c1 = row_c1.text.split(" ")
data_c2 = row_c2.text.split(" ")

# Country calculation:

lst2 = []

for i in data_c1:
    r = i.replace(',', '')
    lst2.append(r)

lst2[1] = int(lst2[1])
lst2[2] = int(lst2[2])
a = round(lst2[2] / lst2[1] *100,2)
lst2.append(a)

country_c1 = lst2[0]
cases_c1 = lst2[1]
deaths_c1 = lst2[2]
death_rate_c1 = lst2[5]

#country 2 

lst3 = []

for i in data_c2:
    r = i.replace(',', '')
    lst3.append(r)

lst3[1] = int(lst3[1])
lst3[2] = int(lst3[2])
a = round(lst3[2] / lst3[1] *100,2)
lst3.append(a)

country_c2 = lst3[0]
cases_c2 = lst3[1]
deaths_c2= lst3[2]
death_rate_c2= lst3[5]


# ##############################

# Email sending

import smtplib  
from email.message import EmailMessage
import datetime as dt
import time
from string import Template # I could substitute 
from pathlib import Path

# Email function 
def send_email():
	html = Template(Path('index.html').read_text())
	email = EmailMessage() 
	email['from'] = 'Tabe'
	#email['to'] = ['tabers77@gmail.com', 'amanda.molina-zoppas@electrolux.com']
	email['to'] = ['tabers77@gmail.com']
	email['subject'] = 'COVID 19 directo en tu correo'
	email.set_content(html.substitute({'name':'Persona', 'pais1':country_c1 , 'casos1':cases_c1 ,'muertos1':deaths_c1, 'rate1':death_rate_c1 , 'pais2':country_c2 , 'casos2':cases_c2 ,'muertos2':deaths_c2, 'rate2':death_rate_c2 }),'html')
	
	with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.login('carlosmolinete77@gmail.com' , 'library77!')
		smtp.send_message(email) 
		smtp.quit() # here I quit the server 
		print(f'Todo listo jefe!')
		browser.close()



# Email sending 

from datetime import datetime
from threading import Timer

x= datetime.today()
y=x.replace(day=x.day+1, hour=16, minute=51, second=0, microsecond=0)

delta_t= y-x
secs=delta_t.seconds+1

t = Timer(secs, send_email)
t.start() # hello world will run at that time 


#References: 

#https://towardsdatascience.com/how-to-track-coronavirus-with-python-a5320b778c8e
# https://stackoverflow.com/questions/15088037/python-script-to-do-something-at-the-same-time-every-day







