"""
bgg.loginpage
~~~~~~~~~~~~

Selenium Page Object to bind the login page and perform authentication

"""
#import urllib2
try:
    from urllib.parse import quote
except:
    from urllib2 import quote

from selenium.common.exceptions import NoSuchElementException

from bggcli import BGG_BASE_URL
from bggcli.ui import BasePage
from bggcli.util.logger import Logger


class LoginPage(BasePage):
    def authenticate(self, login, password):
        """
        Performs authentication

        :param login: BGG login
        :param password: BGG password
        """
        Logger.info("Authenticating...", break_line=False)

        self.driver.get("%s/login" % BGG_BASE_URL)

        # When user is already authenticated, just skip this task
        # TODO Handle case where another user is logged in
        if self.is_authenticated(login):
            Logger.info(" (already logged) [done]", append=True)
            return True

        self.update_text(self.driver.find_element_by_id("login_username"), login)
        self.update_text(self.driver.find_element_by_id("login_password"), password)
        self.driver.find_element_by_xpath("//div[@class='menu_login']//input[@type='submit']")\
            .click()

        if self.is_authenticated(login):
            Logger.info(" [done]", append=True)
            return True

        Logger.info(" [error]", append=True)
        Logger.error("Authentication failed, check your credentials!")
        return False

    def is_authenticated(self, login):
        try:
            self.driver.find_element_by_xpath("//div[@class='menu_login']//a[@href='/user/%s']"
                                              % quote(login))
            return True
        except NoSuchElementException:
            # try: # BGG 2018 style when on a boardgame page.
            # #<button class="btn btn-sm" type="button" login-required="">Sign In</button>
                # self.driver.find_element_by_xpath("//button[@login-required]") 
                # return False
            # except NoSuchElementException:
                # return True
            try: # BGG 2018, when on a boardgame page.
                #<span class="hidden-md hidden-lg"> 									MSGreg 								</span>
                self.driver.find_element_by_xpath("//span[@class='hidden-md hidden-lg' and contains(text(),'{}')]".format(quote(login))) 
                return True
            except NoSuchElementException:
                return False

#            'span[starts-with(@ng-show,"colltoolbarctrl.collection.items.length") and contains(text(),"In Collection")]'
                
