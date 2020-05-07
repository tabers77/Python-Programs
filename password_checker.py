import requests 
import hashlib # we will apply hashing using this module
import sys
import re

email_checker = re.compile(r"(^[a-zA-Z0-9_.!+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)") 

#1 
def request_api_data(query_char): # here I will pass only the first 3 characters 

	url = 'https://api.pwnedpasswords.com/range/' + query_char # wwe will obtain the query character from the second function
	res = requests.get(url)
	if res.status_code != 200:
		raise RuntimeError (f'Error fetching {res.status_code} , check the API and try again')
	return res

#3
def get_password_leaks(hashes,hash_to_check):
	# hashes will return an object. This will contain the hash and the coount
	# I have to use splitlines 
	hashes = (line.split(':') for line in hashes.text.splitlines()) 
	for h,count in hashes:
		if h == hash_to_check:
			return count
	return 0 
#2
def pwned_api_check (password):
		#print(hashlib.sha1(password.encode('utf-8')).hexdigest().upper()) # this will return the hashe version I find here: https://passwordsgenerator.net/sha1-hash-generator/
		sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
		first_5_ch, tail = sha1password[:5], sha1password[5:] #Here our password into 2 
		response = request_api_data(first_5_ch)
		#print(first_5_ch,tail)
		#print(response) #we print the response to see the output
		return get_password_leaks(response,tail) # here I am returning the password 
		#return read_response(response)
		#return sha1password
#pwned_api_check('hello')
#request_api_data('40BD0') # remember to convert to string  
#4
def main (args):
	for password in args:
		count = pwned_api_check(password)
		if count: 
			print(f'{password} was found {count} you should change your password')
		else:
			print(f'{password} is a good password')
		return 'Thank you for using my service!'


###### Methods ######

# Method 1
# if __name__ == '__main__': 
# 	sys.exit(main (sys.argv[1:]))

#Method 2
if __name__ == '__main__': 

	while True:
		a = []
		mail = input('Enter a valid email adress >')
		if email_checker.fullmatch(mail):
			user_inp = input('Which password you want to test? >')
			a.append(user_inp)
			main(a)
			q = input('Do you want to try another password? y/n >')
			if q == 'y':
			    True # Here I keep looping trhough the program 
			elif q == 'n':
				print('Thank you for using my service, Good bye!!!')
				sys.exit()
			else:
				print ('mmm.. It looks like something went wrong')
		else: 
			print ('It looks like you are not entering a valid email, Please try again')

# Method 3

# if __name__ == '__main__': 
# 	with open('ps.txt',mode='r') as ps:
# 		ps = ps.read()
# 	a = []
# 	a.append(ps)
# 	#main (sys.argv[1:])
# 	#sys.exit(main (sys.argv[1:]))
# 	main(a)
