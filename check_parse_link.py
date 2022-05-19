import requests, sys, bs4, webbrowser
from urllib.parse import urlparse
import time
import urllib.request
import requests
import test
searchterm = input('What would you like to email: ')
numPages = int(input("How many pages to parse: "))
links = (test.get_results(searchterm, numPages))
li =  links.split()
i = 0
while i < len(li):
	test = li[i] + "about"
	try:
		requests.head(test)
	except requests.ConnectionError:
		print("failed to connect to " + results[i])