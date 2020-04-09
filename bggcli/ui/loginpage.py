"""
bgg.loginpage
~~~~~~~~~~~~

Selenium Page Object to bind the login page and perform authentication

"""
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

        self.update_text(self.driver.find_element_by_id("username"), login)
        self.update_text(self.driver.find_element_by_id("password"), password)
        self.driver.find_element_by_xpath("//*[@class='forum_table']//input[@type='Submit']") \
            .click()

        if self.is_authenticated(login):
            Logger.info(" [done]", append=True)
            return True

        Logger.info(" [error]", append=True)
        Logger.error("Authentication failed, check your credentials!")
        return False

    def is_authenticated(self, login):
        try:
            self.driver.find_element_by_xpath("//*[contains(@class, 'dropdown-menu')]//a[lowercase(@href)='/user/%s']"
                % quote(login.lower()))

            return True
        except NoSuchElementException:
            try:
                # Admin access is only shown for logged in users
                self.driver.find_element_by_xpath("//*[contains(@show-access, 'admin_login')]")

                return True
            except NoSuchElementException:
                return False

#            'span[starts-with(@ng-show,"colltoolbarctrl.collection.items.length") and contains(text(),"In Collection")]'

