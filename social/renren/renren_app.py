# -*- coding: utf-8 -*-

from renren import RenRen
from selenium import webdriver # parse dynamic web pages
import time

email = "XXXXXXXXXXXXXXX"
passwd = 'XXXXXXXXXXXXXXX'
renren = RenRen(email, passwd)
# import pdb;pdb.set_trace()
# friends_list = renren.get_friends()

driver = webdriver.Firefox() # assume you have firefox on your local computer
# login first
driver.get('http://renren.com')
username = driver.find_element_by_id("email")
password = driver.find_element_by_id("password")
username.send_keys(email)
password.send_keys(passwd)
driver.find_element_by_id("login").click()
time.sleep(5)
# import pdb;pdb.set_trace()
print renren.search_profiles('name', 20, driver)
driver.close()
