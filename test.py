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

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

searchterm = input('What would you like to email: ')
numPages = int(input("How many pages to parse: "))
def get_results(search_term):
	url = "https://www.startpage.com//"
	browser = webdriver.Chrome(executable_path=r'chromedriver_win32\chromedriver.exe')
	browser.get(url)
	browser.maximize_window()
	search_box = browser.find_element(By.ID, "q")
	search_box.send_keys(search_term)
	search_box.submit()
	x = 0
	links = []
	results = []
	i = 0
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
		print(results)
get_results(searchterm)
	#Remove duplicate websites

	# for b in len(results): 
	# 	for g in len(results):
	# 		if(results[b] == results[g]):
	# 			results.pop(b)

