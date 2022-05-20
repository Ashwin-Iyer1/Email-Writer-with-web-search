import os
import re
from requests_html import HTMLSession

#from scraper import results
import requests
import urllib.request
from urllib.parse import urlparse
import webbrowser
import scraper

i = 0
v = 0
a = 0
searchterm = input('What would you like to email: ')
numPages = int(input("How many pages to parse: "))
website = (scraper.get_results(searchterm, numPages)).split()
emails = []
r = 0
print(website)
while r < len(website):
	temp = "https://" + urlparse(website[r]).netloc
	response = requests.get(temp)
	if(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))) != set():
		emails.extend(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I)))
	elif (requests.get(temp + "/about/")).status_code == requests.codes.ok:
		response = requests.get(temp + "/about/")
		if(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))) != set():
			emails.extend(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I)))
	elif (requests.get(temp + "/contact/")).status_code == requests.codes.ok:
		response = requests.get(temp + "/contact/")
		if(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))) != set():
			emails.extend(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I)))
	elif (requests.get(temp + "/contact-us/")).status_code == requests.codes.ok:
		response = requests.get(temp + "/contact-us/")
		if(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))) != set():
			emails.extend(set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I)))
	else:
		print("no emails found at " + temp)
	r = r + 1
if(len(emails) != 0):
	while i < len(emails):
		print(str(i) + " " + str(emails[i]))
		i = i + 1

	remove = input('Would you like to remove any emails?\ny/n\n')
	if(remove == "y"):
		while True:
			removenum = int(input("which email? \n input the number of the one you want to delete: "))
			emails.pop(removenum)
			while v < len(emails):
				print(str(v) + " " + str(emails[v]))
				v = v + 1
			remove = input('Would you like to remove any more emails?\ny/n\n')
			if(remove == "y"):
				v = 0
				continue
			else:
				while a < len(emails):
					print(str(a) + " " + str(emails[a]))
					a = a + 1
				break
	if(len(emails) == 0):
		print("no emails to send.")
else:
	print("no emails")
	exit()
# while i < len(results):
# 	#print(urlparse(results[i]).netloc)
# 	website.append(("https://" + urlparse(results[i]).netloc))
# 	i = i + 1
# r = 0
# while r < len(website):
# 	emails.append(website[r] + "/about/")
# 	time_request = requests.get(website[r])
# 	if time_request.status_code == requests.codes.ok:
# 		print("able to connect to " + emails[r])
# 		#webbrowser.open(website[r])

# 	else:
# 		print("failed to connect to " + website[r])
# 	r = r + 1


# while r < len(website):
# 	EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
# 	session = HTMLSession()
# 	v = session.get(website[r])
# 	v.html.render()
# 	for re_match in re.finditer(EMAIL_REGEX, r.html.raw_html.decode()):
# 		print(re_match.group())
# 	r = r + 1