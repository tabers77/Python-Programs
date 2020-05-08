import requests
from bs4 import BeautifulSoup
import pprint
from itertools import chain 
import sys
import re 

num_pages = int(input('Num of pages'))
pattern = re.compile(r"((D|d)ecline|(C|c)orona|(g|G)oat|(v|V)irus)")

links_l = []
subtext_l = []

for i in range(1,num_pages+1): #here I am looping through the number
    a = 'https://news.ycombinator.com/news?p=' + str(i)
    for page in a:
        b = ''.join(a)
    res = requests.get(b)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.select('.storylink')
    subtext = soup.select('.subtext')

    links_l.append(links)
    subtext_l.append(subtext)

#I flatten 3d list
f_links = list(chain.from_iterable(links_l)) 
f_sub_text = list(chain.from_iterable(subtext_l)) 

def sort_vy_votes(h_list):
	return sorted(h_list,key=lambda k:k['votes'],reverse=True)
def create_custom_hn (links,subtext):
	hn =[]
	for idx, item  in enumerate (links): # here I create an index and item 
		title = links[idx].getText() # is the same as writing title = items.getText(), here I get the text 
		href = links[idx].get('href',None) # here I get the url 
		vote = subtext[idx].select('.score') # the vote comes froms scores  
		if pattern.search(title):
			if len(vote): 
				points = int(vote[0].getText().replace(' points',''))
				if points > 50:
					hn.append({'title':title,'link':href,'votes':points})#this will create a dictionary with link and title
						

	return sort_vy_votes(hn)

pprint.pprint(create_custom_hn(f_links,f_sub_text)) 
