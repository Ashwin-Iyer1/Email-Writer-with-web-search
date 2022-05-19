import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import requests, sys, bs4, webbrowser
from urllib.parse import urlparse
import time
from selenium.webdriver.support import expected_conditions as EC
import platform

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_results(search_term, numPages):
	url = "https://www.startpage.com//"
	if platform.system() == 'Windows':
		browser = webdriver.Chrome(executable_path=r'chromedrivers\chromedriver.exe')
	if platform.system() == 'Darwin':
		browser = webdriver.Chrome(executable_path = '/Users/ashwin/Downloads/Email-Writer-with-web-search-main/chromedrivers/chromedriver-mac')
		#browser = webdriver.Chrome(executable_path = 'chromedrivers\chromedriver-mac)
	browser.get(url)
	browser.maximize_window()
	search_box = browser.find_element(By.ID, "q")
	search_box.send_keys(search_term)
	search_box.submit()
	x = 0
	links = []
	results = []
	i = 0
	v = 0
	while x < numPages:
		try:
			links.extend(browser.find_elements(By.XPATH, "//A[@class='w-gl__result-url result-link']"))
		except:
			links.extend(browser.find_elements(By.XPATH, "//A[@class='w-gl__result-url result-link']"))
		while i < len(links):
			href = links[i].get_attribute('href')
			time.sleep(.1)
			results.append(href)
			i = i+1
		if (x + 1) != numPages:
			button = browser.find_element(By.XPATH, "//button[normalize-space()='Next']")
			button.submit()
		x = x+1
	browser.close
	if len(results) == 0:
		print("\nno organizations")
	else:
		while v < len(results):

			try:
				r = requests.head(results[v])
    	# prints the int of the status code. Find more at httpstatusrappers.com :)
			except requests.ConnectionError:
				print("failed to connect to " + results[v])
			str1 = " "
			str1 = (str1.join(results))
			v = v + 1
	return(str1)
	#Remove duplicate website

	# for b in len(results): 
	# 	for g in len(results):
	# 		if(results[b] == results[g]):
	# 			results.pop(b)

