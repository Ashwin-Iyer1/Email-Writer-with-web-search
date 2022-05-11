import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
import requests, sys, bs4, webbrowser
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

searchterm = input('What would you like to email: ')
numPages = input("How many pages to parse: ")
def get_results(search_term):
	url = "https://www.startpage.com//"
	browser = webdriver.Chrome(executable_path=r'\chromedriver_win32\chromedriver.exe')
	browser.get(url)
	search_box = browser.find_element(By.ID, "q")
	search_box.send_keys(search_term)
	search_box.submit()

	for i in numPages:
		#page = i + 1
		try:
			links = browser.find_elements(By.XPATH, "//A[@class='w-gl__result-url result-link']")
		except:
			links = browser.find_elements(By.XPATH, "//A[@class='w-gl__result-url result-link']//a")
		# Get more sites by accessing more web pages
		# if page < numPages:
		# 	pageNum = "//BUTTON[@class='pagination__num'][text()='" + page + "']/self::BUTTON"
		# 	button = browser.find_elements(By.XPATH, pageNum)
		# 	button.click()
		
	results = []
	for link in links:
		href = link.get_attribute("href")
		href = urlparse(href).netloc
		if(href[-3:] == "org"):
			print(href)
			results.append(href)
	browser.close
	#Remove duplicate websites

	# for b in len(results): 
	# 	for g in len(results):
	# 		if(results[b] == results[g]):
	# 			results.pop(b)
	return (results)
get_results(searchterm)
