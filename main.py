import os
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import sys
import csv
import re
from pyvirtualdisplay import Display

app = Flask(__name__)


class RepresentativeData():

    def __init__(self, string_list, email, website):
        self.email = email
        self.website = website
        self.title = None
        self.name = None
        self.district = None
        self.party = None
        self.capitol_phone = None
        self.district_phone = None

        title = string_list[0]
        if title in ('State Delegate', 'State Senator'):
            self._process_state_rep(string_list)
        elif title == 'U.S. Congress':
            self._process_us_congress(string_list)
        elif title == 'U.S. Senator':
            self._process_us_senate(string_list)

    def to_dict(self):
        return {
            'email': self.email,
            'website': self.website,
            'title': self.title,
            'name': self.name,
            'district': self.district,
            'party': self.party,
            'capitol_phone': self.capitol_phone,
            'district_phone': self.district_phone
        }

    def _process_state_rep(self, string_list):
        """
        process state rep data from a list like this:
        [u'State Delegate',
         u'Patrick A. Hope',
         u'District:47', 
         u'Party:D', 
         u'Capitol Phone:(804) 698-1047', 
         u'District Phone:(703) 486-1010', 
         u'email | more info', 
         u'Click to view boundaries']
        """
        self.title = string_list[0]
        self.name = string_list[1]
        self.district = string_list[2].split(":")[-1].strip()
        self.party = string_list[3].split(":")[-1].strip()
        self.capitol_phone = string_list[4].split(":")[-1].strip()
        self.district_phone = string_list[5].split(":")[-1].strip()

    def _process_us_congress(self, string_list):
        """
        [u'U.S. Congress',
         u'Don Beyer', 
         u'District: 8', 
         u'Party:D', 
         u'more info', 
         u'Click to view boundaries']
        """
        self.title = string_list[0]
        self.name = string_list[1]
        self.district = string_list[2].split(":")[-1].strip()
        self.party = string_list[3].split(":")[-1].strip()

    def _process_us_senate(self, string_list):
        """
        [u'U.S. Senator', 
         u'Mark R. Warner',
         u'Party:D', 
         u'more info', 
         u'Click to view boundaries']
        """
        self.title = string_list[0]
        self.name = string_list[1]
        self.party = string_list[2].split(":")[-1].strip()


def enter_address(address, browser):
    """
    Enter the specified address into the search box
    """
    address_box = browser.find_element_by_id("txtAddress")
    address_box.clear()
    address_box.send_keys(address, Keys.ENTER)
    suggestion = browser.find_element_by_xpath('//*[@id="tblAddressResults"]/ul/li[1]')
    if suggestion.text == 'No results found':
        raise ValueError()
    suggestion.click()

def get_visible_reps(browser):
    rep_info = []
    reps = browser.find_elements_by_xpath('//*[contains(@class, "showNode")]')
    for rep in reps:
        string_list = rep.text.split("\n")
        website = None
        email = None
        link_list = rep.find_elements_by_tag_name('a')
        for link in link_list:
            if 'more info' in link.text:
                website = link.get_attribute('href')
            if 'email' in link.text:
                raw_email = link.get_attribute('href')
                email = re.match(r'mailto:(.*)\?', raw_email).groups()[0]
        rep_data = RepresentativeData(string_list, email, website)
        rep_info.append(rep_data)
    return rep_info

def process_reps(address, browser):
    enter_address(address, browser)
    sleep(5)
    return get_visible_reps(browser)

@app.route('/repfind')
def repfinder():
    address = request.args.get('address')
    error = None
    rep_list = None
    if address:
        display = Display(visible=0, size=(800,600))
        display.start()
        browser = webdriver.Firefox()
        browser.get('http://whosmy.virginiageneralassembly.gov')
        try:
            rep_list = [x.to_dict() for x in process_reps(address, browser)]
        except ValueError:
            rep_list=None
            error=True
        browser.quit()
        display.stop()
    return render_template('search.html', error=error, results=rep_list)


if __name__ == '__main__':
    app.run(debug=True)
