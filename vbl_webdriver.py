# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:21:32 2020

@author: Lukas
"""

from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import pyderman as pydriver
from selenium import webdriver
import time

class Webdriver:
    
    """
    Generate a chrome webdriver that can navigate the VBL website
    
    >>> webdriver = Webdriver()
    
    """
    
    def __init__(self):
        # Automatically create a webdriver when class Webdriver is called
        self.generate_driver()
        
    def generate_driver(self):  
        """
        Installs Selenium chromedriver if not yet installed.
        Generates a running webdriver
        This function is called when the Webdriver class is initialized.
        
        :return: a running webdriver.chrome instance
        
        >>> Webdriver.generate_driver()
        """
        
        try: 
            # Check if chromedriver is installed (necessary for selenium). Else, install it.
            path = pydriver.install(browser=pydriver.chrome)
            print('Chromedriver is installed to path: %s' % path)

            # Create the chromedriver instance
            self.driver = webdriver.Chrome(path)

        except:
            print('chromedriver not installed correctly')
            
    def login(self, username, password):
        """
        Logs into Vlaamse basketballiga website using the running Selenium chromedriver.
        Need to redirect to the log in page first before this function is called.
        
        :param username: existing username (normally an e-mail) to log into the VBL website
        :param password: existing password to log into the VBL website
        :return: a running webdriver.chrome instance that is logged into the VBL website
        
        >>> Webdriver.login(username, password)
        """
        
        
        # Find the username box, password box, & submit button on the page
        element_username = self.driver.find_element_by_xpath("/html/body/div[2]/form/div[1]/input")
        element_password = self.driver.find_element_by_xpath("/html/body/div[2]/form/div[2]/input")
        element_button = self.driver.find_element_by_xpath("/html/body/div[2]/form/div[4]/button")
        
        # Clear box and fill in username & password
        element_username.clear()
        element_username.send_keys(username)
            
        element_password.clear()
        element_password.send_keys(password)
        
        # Submit
        element_button.send_keys(Keys.RETURN)
        
         # Make sure we are logged in before doing anything else
        time.sleep(5)
     
    def redirect_page(self, url):
        """
        Redirects to the given url on the Vlaamse basketballiga website using the running Selenium chromedriver.
        
        :param url: an url of the VBL website in the format of "https://vblweb.wisseq.eu/Home/MatchDetail?wedguid=" + wedguid + "&ID=Uitslag"
        :return: a running webdriver.chrome instance that is redirected to the given page
        
        >>> Webdriver.redirect_page("https://vblweb.wisseq.eu/Home/MatchDetail?wedguid=BVBL20219180NAHSE11AGD&ID=Uitslag#sectionF")
        """
        
        # Go to the selected page using our chromedriver. Wait for 1 sec to account for input lag.
        try:
            url = url
            self.driver.get(url)   
            time.sleep(1)
        except:
            print("Incorrect page")
            
    def button_verslag(self):
        
        """
        Presses the 'verslag' button to redirect to the correct view on the current webdriver page.
        """      
        try:
            # Press buton 'Verslag'
            element_button = self.driver.find_element_by_link_text("Verslag")
            element_button.click()
            time.sleep(1)
        except:
            print('Incorrect page')
        
    def export_verslag(self, thuis_uit):
        
        """
        Exports the tables of the points per player and the points per quarters on the current webdriver page as a list. 
        Either the 'home' or 'away' team table exported for the points per players, depending on the params.
        Both points per quarters tables are extracted.
        
        :param thuis_uit: Either 'thuis' or 'uit', depending on whether the team of interest was the home or away team.
        :return: a list with the table of points per players, a list with the points per quarters for the home team, a list with the points per quarters for the away team
        
        >>> Webdriver.export_verslag("thuis")
        """      
        
        # Download tables under 'Verslag' using the BeautifulSoup package
        page = BeautifulSoup(self.driver.page_source, 'html.parser')             
        data_thuis = []
        data_uit = []
        
        # Find the 'thuis' and 'uit' tables    

        table_thuis = page.find('div', {'id':'teamthuis'})
        rows_thuis = table_thuis.select('table tbody tr')
        for row in rows_thuis:
            tds = row.select('td')
            # Check if the table has four columns, else the table won't be correct
            if len(tds) == 4: 
                data_thuis.append([tds[0].text, tds[1].text, tds[2].text, tds[3].text])
       

        table_uit = page.find('div', {'id':'teamUit'})
        rows_uit = table_uit.select('table tbody tr')
        for row in rows_uit:
            tds = row.select('td')
            # Check if the table has four columns, else the table won't be correct
            if len(tds) == 4:
                data_uit.append([tds[0].text, tds[1].text, tds[2].text, tds[3].text]) 
        
        # Check where the line containing 'Totaal' is (= end of totals table). 
        # Use this to select the table after this line (points per players) and before this line (points per quarter)
        try:            
            index_totaal_thuis = ['Totaal' in list for list in data_thuis].index(True) 
            index_totaal_uit = ['Totaal' in list for list in data_uit].index(True)  
        # Create a wrong value if 'Totaal' isnt found in the tables to output an error
        except:
            index_totaal_thuis = -1
            index_totaal_uit = -1
            
        points_quarters_thuis = data_thuis[:index_totaal_thuis]
        points_quarters_uit = data_uit[:index_totaal_uit]
        
        if thuis_uit == "thuis":       
            points_players = data_thuis[index_totaal_thuis+1:]    
        elif thuis_uit == "uit":   
            points_players = data_uit[index_totaal_uit+1:]
                  
        return points_players, points_quarters_thuis, points_quarters_uit