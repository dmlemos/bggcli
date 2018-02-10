#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# Updated for BGG 2018
"""
bgg.gamepage
~~~~~~~~~~~~

Selenium Page Object to bind the game details page

"""
import time
import inspect
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bggcli import BGG_BASE_URL, BGG_SUPPORTED_FIELDS
from bggcli.ui import BasePage
from bggcli.util.logger import Logger
import traceback
def in_private_info_popup(func):
    """
    Ensure the Private Info popup is displayed when updating its attributes
    """
    # Not verified for BGG 2018
    
    def _wrapper(self, *args, **kwargs):
        try:
            self.itemEl \
                .find_element_by_xpath(".//td[@class='collection_ownershipmod editfield']") \
                .click()
        except NoSuchElementException:
            pass
        else:
            self.privateInfoPopupEl = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='select-free'][contains(@id, 'editownership')]")))

        return func(self, *args, **kwargs)

    return _wrapper


def in_version_popup(func):
    """
    Ensure the Version popup is displayed when updating its attributes
    """
    # Not verified for BGG 2018
    def _wrapper(self, *args, **kwargs):
        try:
            self.itemEl \
                .find_element_by_xpath(".//td[@class='collection_versionmod editfield']") \
                .click()
        except NoSuchElementException:
            pass
        else:
            self.versionPopupEl = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='select-free'][contains(@id, 'editversion')]")))
            self.versionPopupEl \
                .find_element_by_xpath("//a[contains(@onclick, 'oldversion_version')]").click()
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@id, 'oldversion_version')]")))

        return func(self, *args, **kwargs)

    return _wrapper


class GamePage(BasePage):
    # CSV_SUPPORTED_COLUMNS = [
    #     'objectid', 'rating', 'weight', 'own', 'fortrade', 'want', 'wanttobuy', 'wanttoplay',
    #     'prevowned', 'preordered', 'wishlist', 'wishlistpriority', 'wishlistcomment', 'comment',
    #     'conditiontext', 'haspartslist', 'wantpartslist', 'publisherid', 'imageid',
    #     'year', 'language', 'other', 'pricepaid', 'pp_currency', 'currvalue', 'cv_currency',
    #     'acquisitiondate', 'acquiredfrom', 'quantity', 'privatecomment', '_versionid'
    # ]
    #objectname	objectid	rating	own	fortrade	want	wanttobuy	wanttoplay	prevowned	preordered	wishlist	wishlistpriority	wishlistcomment	comment	conditiontext	haspartslist	wantpartslist	publisherid	imageid	year	language	other	pricepaid	pp_currency	currvalue	cv_currency	acquisitiondate	acquiredfrom	quantity	privatecomment	_versionid


    def __init__(self, driver):
        BasePage.__init__(self, driver)

        self.itemEl = None
        self.privateInfoPopupEl = None
        self.versionPopupEl = None

    # Verified BGG 2018
    def goto(self, game_attrs):
        """
        Set Web Driver on the game details page

        :param game_attrs: Game attributes as a dictionary
        """
        self.driver.get("%s/boardgame/%s" % (BGG_BASE_URL, game_attrs['objectid']))

    # Verified BGG 2018
    def update(self, game_attrs):
        #Logger.info("update()", append=True, break_line=True)
        
        # First, see if objectid exists.
        id = game_attrs.get('objectid',None)
        
        # if objectid doesn't exist, find it via the name:
        # this doesn't work at the moment. All the work is done in updateid()
        if id is None:
            pass        
        return self.updateid(game_attrs)

    def notincollection(self):
        """Either returns button or False, suitable for if statement"""
        try:
            Logger.info("edit button? ", append=True, break_line=False)
            button1 = self.driver.find_element_by_xpath(
            "(//button[contains(@ng-click, 'colltoolbarctrl.editItem')])[last()]")
            return button1
        except NoSuchElementException:
            return False
            
    def openeditform(self):
        button = self.notincollection()
        if button:
            button.click()
        else:
            Logger.info(" not found. ", append=True, break_line=False)
            Logger.info("(i.e. game in col'n)...", append=True, break_line=False)
            # div = self.driver.find_element_by_xpath(
            # "(//div[@class, 'toolbar-actions'])[last()]")

            Logger.info("'In Col'n' button? ", append=True, break_line=False)
            button = self.driver.find_element_by_xpath(
                '('
                '//'
                'button[@id="button-collection" and descendant::'
                    'span[starts-with(@ng-show,"colltoolbarctrl.collection.items.length") and '
                        'contains(text(),"In Collection")]'
                    ']'
                ')[last()]'
            )
            Logger.info("Click. ", append=True, break_line=False)
            button.click()
            
            clickable = self.driver.find_element_by_xpath(
            '//span[@class="collection-dropdown-item-edit" and //button[contains(text(),"Edit")]]')
            Logger.info("Click col'n dropdown. ", append=True, break_line=False)
            clickable.click()
        
        Logger.info("form...", append=True, break_line=False)
        
        self.itemEl = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='modal-content']")))

    # Verified BGG 2018
    def updateid(self, game_attrs):
        """
        Update game details

        :param game_attrs: Game attributes as a dictionary
        """
        # General use of Selenium is 
        #   A) goto page,
        #   B) find element using xpath expression, then 
        #   C) take action related to the element.
        #
        # Flow of this function is:
        #    1) Go to game page
        #    2) Try to click "Add to Collection" button.
        #    3) If it didn't exist,
        #       a) click the "In Collection" button.
        #       b) click the "Edit" button
        #    4) Open the additional two form dialogs
        #       (Show Advanced, Show Custom)
        #    5) fill out items on form, dependencies show which values must
        #       exist before the indicated item.
        #       For example, 'wishlistpriority':{'wishlist':1},
        #       means that to set wishlistpriority, then
        #       wishlist must equal 1.
        #    6) Finally, find the form element and submit it.
        
        
        #Logger.info("updateid()", append=True, break_line=True)
        #Logger.info("{} {}, ".format(game_attrs.get('objectid',''),game_attrs.get('objectname','')), append=True, break_line=True)
        
        self.goto(game_attrs)
        
        Logger.info("page, ", append=False, break_line=False)
 
        self.openeditform()
        
        # Open advanced data entry panel.
        #<a class="toggler-caret" ng-href="" ng-click="editctrl.showvars.showAdvanced = !editctrl.showvars.showAdvanced" ng-class="{ 'is-active': editctrl.showvars.showAdvanced }"> 			<span class="glyphicon glyphicon-menu-right"></span> 			<strong>Advanced</strong> (private info, parts exchange) 		</a>
        Logger.info("Advanced button...", append=True, break_line=False)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, 
            "//a[starts-with(@class,'toggler-caret') and starts-with(@ng-click,'editctrl.showvars.showAdvanced')]"
            )))
        try:
            Logger.info("finding advanced dropdown...", append=True, break_line=False)
            b = self.itemEl.find_element_by_xpath(".//a[@class='toggler-caret' and starts-with(@ng-click,'editctrl.showvars.showAdvanced')]")
            Logger.info("Click. ", append=True, break_line=False)
            b.click()
        except:
            Logger.info("Failed.", append=True, break_line=False)
            pass
        # Open Customize Game Info data entry panel.
        #<a class="toggler-caret" ng-href="" ng-click="editctrl.showvars.showCustom = !editctrl.showvars.showCustom" ng-class="{ 'is-active': editctrl.showvars.showCustom }"> 				<span class="glyphicon glyphicon-menu-right"></span> 				<strong>Customize Game Info</strong> (title, image) 			</a>
        Logger.info("Custom button...", append=True, break_line=False)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, 
            "//a[starts-with(@class,'toggler-caret') and starts-with(@ng-click,'editctrl.showvars.showCustom')]"
            )))
        try:
            self.itemEl.find_element_by_xpath(".//a[@class='toggler-caret' and starts-with(@ng-click,'editctrl.showvars.showCustom')]").click()
        except:
            Logger.info("Failed. ", append=True, break_line=False)

        # custom = self.wait.until(EC.element_to_be_clickable(
            # (By.XPATH, ".//a[starts-with(@ng-click,'editctrl.showvars.showCustom')]")))
        # custom.click()
        
        #<input ng-model="editctrl.editdata.item.textfield.customname.value" class="form-control ng-pristine ng-valid ng-empty ng-touched" type="text" placeholder="Gloomhaven Nickname" style="">
        Logger.info("Name field...", append=True, break_line=False)
        nickname = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, './/input[@ng-model="editctrl.editdata.item.textfield.customname.value"]')))
        
        # self.itemEl = self.wait.until(EC.element_to_be_clickable(
            # (By.XPATH, "//form[@name='collectioneditorform']")))
        # Fill all provided values using dynamic invocations 'fill_[fieldname]'
        dependencies = {
            'wishlistpriority':{'wishlist':1},
            'wishlistcomment':{'wishlist':1},
            'conditiontext':{'fortrade':1}
        }

# 'fortrade', 'conditiontext',   # these must be in this order
# 'wishlist', 'wishlistpriority', 'wishlistcomment', # these must be in this order

        
        Logger.info("Updating fields: ", append=True, break_line=False)
        try:
            for key in BGG_SUPPORTED_FIELDS:
                dontdo = 0
                if key in game_attrs:
                    value = game_attrs[key]
                    if value is not None:
                        #print '{}'.format(key),
                        #time.sleep(2)
                        dep = dependencies.get(key,None)
                        if dep:
                            #print 'depends on: ',
                            for k,v in dep.items(): # for python 2: iteritems()
                                #print '{}={}?'.format(k,v),
                                if str(game_attrs[k]) != str(v):
                                    dontdo = 1
                        if dontdo:
                            continue
                        getattr(self, "fill_%s" % key)(value)
        except:
            Logger.info("\nEXCEPTION.", append=True, break_line=True)
            traceback.print_exc()
            return False
        # <button class="visible-xs-inline btn btn-primary" ng-disabled="editctrl.saving" type="submit"> 				<span>Save</span> 			</button>
        #savebutton = self.itemEl.find_element_by_xpath(".//button[@ng-disabled='editctrl.saving']")
        Logger.info("Form? ", append=True, break_line=False)
        form = self.itemEl.find_element_by_xpath(".//form[@name='collectioneditorform']")
        # action=selenium.interactions.Actions(driver);
        # import selenium.webdriver.common.actions.pointer_actions 
        # selenium.webdriver.common.actions.pointer_actions().click(savebutton)
        #Logger.info("submitting, ", append=True, break_line=False)
        form.submit() ;
        Logger.info("submitted. ", append=True, break_line=False)
        time.sleep(0.1)
        # action.moveToElement(savebutton).click().perform();
        return True
        # Save "Private Info" popup if opened
        try:
            self.privateInfoPopupEl.find_element_by_xpath(".//input[@type='submit']").click()
        except WebDriverException:
            pass
        else:
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, ".//td[@class='collection_ownershipmod editfield']")))

        # Save "Version" popup if opened
        try:
            self.versionPopupEl.find_element_by_xpath(".//input[@type='submit']").click()
        except WebDriverException:
            pass
        else:
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, ".//td[@class='collection_versionmod editfield']")))
                
        return True

    # Not verified BGG 2018
    def delete(self, game_attrs):
        """
        Delete a game in the collection

        :param game_attrs: Game attributes as a dictionary. Only the id will be used
        """

        self.goto(game_attrs)
        #<button type="button" uib-tooltip="More options" tooltip-popup-delay="500" tooltip-append-to-body="true" tooltip-placement="left" class="btn btn-empty text-muted dropdown-toggle" uib-dropdown-toggle="" aria-haspopup="true" aria-expanded="false"> 				<span class="glyphicon glyphicon-option-vertical"></span> 			</button>
        try:
            if self.notincollection():
                Logger.info(" (not in collection)", append=True, break_line=False)
                return # Not in collection
            self.openeditform()
            
            more = self.driver.find_element_by_xpath("//button[@uib-tooltip='More options']'")
            more.click()
            
            #<button type="button" class="btn btn-empty" ng-click="editctrl.deleteItem(editctrl.editdata.item)"> 					Delete from Collection 				</button>
            del_button = self.driver.find_element_by_xpath('//button[ng-click="editctrl.deleteItem(editctrl.editdata.item)"]')
            del_button.click()
        except NoSuchElementException:
            Logger.info(" Failed: can't find delete button!", append=True, break_line=False)
            return

        # Confirm alert message
        #<button class="btn btn-danger" ng-click="ok()">Yes, Delete</button>
        # wait_and_accept_alert is a browser thing, not an "on page popup".
        #self.wait_and_accept_alert()

    ###############################################################################################
    # All following functions are invoked dynamically, for each attribute that can be updated     #
    # Functions are named 'fill_{attribute-name}'                                                 #
    ###############################################################################################


    # Verified BGG 2018
    def fill_objectid(self, value):
        """Ignore objectid field in the CSV."""
        pass

    # Verified BGG 2018
    def fill_objectname(self, value):
        """Ignore objectname field in the CSV."""
        pass

    # Verified BGG 2018
    def hover (self,element):
        """Hover over an element."""
        #wd = webdriver_connection.connection
        #element = wd.find_element_by_link_text(self.locator)
        hov = ActionChains(self.driver).move_to_element(element)
        hov.perform()
        
    # Verified BGG 2018
    def fill_rating(self, value):
        # hover over a star, then the input box will appear. Then fill the box
        #<i ng-repeat-end="" ng-mouseenter="enter($index + 1)" ng-click="rate($index + 1)" class="glyphicon fi-star" ng-class="$index < value &amp;&amp; (r.stateOn || 'glyphicon-star') || (r.stateOff || 'glyphicon-star-empty')" ng-attr-title="{{r.title}}" title="10 Stars" style=""></i>
        star = self.itemEl.find_element_by_xpath('(//i[@class="glyphicon fi-star"])[1]')
        #print(star.location_once_scrolled_into_view)
        star.location_once_scrolled_into_view
        self.hover(star)
        #<input type="text" class="form-control input-sm rating-stars-textbox ng-empty has-rating-border- ng-touched" ng-model="editctrl.editdata.item.rating" ng-show="editctrl.editdata.item.rating || overstar != null" value="" style="">
        
        #<input type="text" class="form-control input-sm rating-stars-textbox has-rating-border- ng-touched" ng-model="editctrl.editdata.item.rating" ng-show="editctrl.editdata.item.rating || overstar != null" value="" style="">
        self.update_text(self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//input[@ng-model="editctrl.editdata.item.rating"]'))), value)
        
        # td = self.driver.find_element_by_xpath("//td[contains(@id, 'CEcell_rating')]")
        # td.click()

        # self.update_text(self.wait.until(
            # EC.element_to_be_clickable((By.XPATH, "//input[@style='editrating']"))), value)
        # td.find_element_by_xpath(".//input[@type='submit']").click()

    def fill_weight(self, value):
        self.update_select(self.itemEl.find_element_by_xpath(".//select[@name='weight']"), value)

    def fill_own(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_fortrade(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_want(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_wanttobuy(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_wanttoplay(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_prevowned(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_preordered(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_wishlist(self, value):
        varname = inspect.currentframe().f_code.co_name[5:]
        self.update_checkbox(self.itemEl, ".//input[@ng-model='item.status.{}']".format(varname),
                             value)

    def fill_wishlistpriority(self, value):
        #Wishlist checkbox must be checked for this to be visible
        #<select class="form-control ng-pristine ng-valid ng-not-empty ng-touched" ng-init="item.wishlistpriority = (item.wishlistpriority ? item.wishlistpriority : 3)" ng-model="item.wishlistpriority" ng-options="w.priority as (w.name) for w in config.wishlistoptions" style=""><option label="Must have" value="number:1">Must have</option><option label="Love to have" value="number:2">Love to have</option><option label="Like to have" value="number:3" selected="selected">Like to have</option><option label="Thinking about it" value="number:4">Thinking about it</option><option label="Don't buy this" value="number:5">Don't buy this</option></select>
        element = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//select[@ng-model="item.wishlistpriority"]')))
        self.update_select(element, int(value)-1, by_index=True)
        # Wishlist 1=musthave;2=lovetohave;3=liketohave;4=thinking about it; 5=Don't buy this

    def fill_invlocation(self, value):
        #<input id="invlocation" type="text" class="form-control ng-pristine ng-valid ng-empty ng-touched" ng-model="editctrl.editdata.item.invlocation" style="">
        #self.update_textarea(self.itemEl, 'invlocation', value)
        element = self.wait.until(EC.element_to_be_clickable(
                (By.ID, 'invlocation')))
        self.update_text(element,value)
    def fill_wishlistcomment(self, value):
        #Wishlist checkbox must be checked for this to be visible
        element = self.wait.until(EC.element_to_be_clickable(
                (By.ID, 'wishlistcomment')))
        self.update_textarea(self.itemEl, 'wishlistcomment', value)

    def fill_comment(self, value):
    #<textarea id="comment" class="form-control ng-pristine ng-valid ng-empty ng-touched" style="height: 100px; overflow: hidden; word-wrap: break-word; resize: horizontal;" msd-elastic="" ng-model="editctrl.editdata.item.textfield.comment.value"> 				</textarea>
        self.update_textarea(self.itemEl, 'comment', value)

    def fill_conditiontext(self, value):
        # "For Trade" must be selected to see this textarea
        #<textarea msd-elastic="" id="conditiontext" class="form-control ng-pristine ng-valid ng-empty ng-touched" style="height: 50px; overflow: hidden; word-wrap: break-word; resize: horizontal;" ng-model="editctrl.editdata.item.textfield.conditiontext.value"> 				</textarea>
        element = self.wait.until(EC.element_to_be_clickable(
                (By.ID, 'conditiontext')))
        self.update_textarea(self.itemEl, 'conditiontext', value)

    def fill_haspartslist(self, value):
        self.update_textarea(self.itemEl, 'haspartslist', value)

    def fill_wantpartslist(self, value):
        self.update_textarea(self.itemEl, 'wantpartslist', value)

    #@in_version_popup
    def fill__versionid(self, value):
        if value:
            radio_version = self.itemEl.find_element_by_xpath(
                "(.//ul)[1]//input[@value='%s']" % value)
            radio_version.click()

    #@in_version_popup
    def fill_publisherid(self, value):
        self.update_text(self.itemEl.find_element_by_id('publisherid'), value)

    #@in_version_popup
    def fill_imageid(self, value):
        #<input type="text" id="customimage" class="form-control ng-pristine ng-valid ng-empty ng-touched" ng-model="editctrl.editdata.item.imageid" style="">
        self.update_text(self.itemEl.find_element_by_id('customimage'), value)
    #@in_version_popup
    def fill_year(self, value):
        self.update_text(self.itemEl.find_element_by_id('year'), value)

    #@in_version_popup
    def fill_language(self, value):
        #<select class="form-control ng-pristine ng-valid ng-empty ng-touched" ng-model="editctrl.editdata.item.languageid" ng-options="lang.languageid as lang.name for lang in editctrl.editdata.config.languages" style=""><option value="" selected="selected"></option><option label="Afrikaans" value="string:2677">Afrikaans</option><option label="Arabic" value="string:2178">Arabic</option><option label="Azerbaijani" value="string:2785">Azerbaijani</option><option label="Basque" value="string:2711">Basque</option><option label="Bengali" value="string:2787">Bengali</option><option label="Bulgarian" value="string:2675">Bulgarian</option><option label="Catalan" value="string:2179">Catalan</option><option label="Chinese" value="string:2181">Chinese</option><option label="Croatian" value="string:2656">Croatian</option><option label="Czech" value="string:2180">Czech</option><option label="Danish" value="string:2182">Danish</option><option label="Dutch" value="string:2183">Dutch</option><option label="English" value="string:2184">English</option><option label="Esperanto" value="string:2712">Esperanto</option><option label="Estonian" value="string:2185">Estonian</option><option label="Filipino" value="string:2759">Filipino</option><option label="Finnish" value="string:2186">Finnish</option><option label="French" value="string:2187">French</option><option label="Galician" value="string:2740">Galician</option><option label="German" value="string:2188">German</option><option label="Greek" value="string:2189">Greek</option><option label="Hebrew" value="string:2190">Hebrew</option><option label="Hindi" value="string:2666">Hindi</option><option label="Hungarian" value="string:2191">Hungarian</option><option label="Icelandic" value="string:2347">Icelandic</option><option label="Indonesian" value="string:2192">Indonesian</option><option label="Iranian" value="string:2696">Iranian</option><option label="Italian" value="string:2193">Italian</option><option label="Japanese" value="string:2194">Japanese</option><option label="Korean" value="string:2195">Korean</option><option label="Latin" value="string:2752">Latin</option><option label="Latvian" value="string:2196">Latvian</option><option label="Lithuanian" value="string:2197">Lithuanian</option><option label="Luxembourgish" value="string:2750">Luxembourgish</option><option label="Malay" value="string:2714">Malay</option><option label="(neutral)" value="string:2205">(neutral)</option><option label="Norwegian" value="string:2198">Norwegian</option><option label="Persian" value="string:2756">Persian</option><option label="Polish" value="string:2199">Polish</option><option label="Portuguese" value="string:2200">Portuguese</option><option label="Romanian" value="string:2201">Romanian</option><option label="Russian" value="string:2202">Russian</option><option label="Serbian" value="string:2681">Serbian</option><option label="Slovak" value="string:2206">Slovak</option><option label="Slovenian" value="string:2207">Slovenian</option><option label="Spanish" value="string:2203">Spanish</option><option label="Swedish" value="string:2204">Swedish</option><option label="Thai" value="string:2709">Thai</option><option label="Turkish" value="string:2349">Turkish</option><option label="Ukrainian" value="string:2665">Ukrainian</option><option label="Vietnamese" value="string:2738">Vietnamese</option><option label="Welsh" value="string:2653">Welsh</option></select>
        
        self.update_select(self.itemEl.find_element_by_xpath('//select[@ng-model="editctrl.editdata.item.languageid"]'), value,
                           by_text=True)

    #@in_version_popup
    def fill_other(self, value):
        self.update_text(self.itemEl.find_element_by_id('other'), value)

    #@in_private_info_popup
    def fill_pricepaid(self, value):
        #<input id="pricepaid" type="number" ng-model="editctrl.editdata.item.pricepaid" class="form-control ng-pristine ng-valid ng-empty ng-touched" style="">
        self.update_text(self.itemEl.find_element_by_id('pricepaid'), value)

    #@in_private_info_popup
    def fill_pp_currency(self, value):
        # self.update_select(self.itemEl.find_element_by_id('pp_currency'), value)
        if value == '':
            return
        #button = self.itemEl.find_element_by_xpath('//button[@id="pp_currency"]')
        self.itemEl.find_element_by_xpath(
            '//a[starts-with(@ng-click="editctrl.editdata.item.pp_currency") and contains(text(), "{}")]'.format(value)).click()


    #@in_private_info_popup
    def fill_currvalue(self, value):
        self.update_text(self.itemEl.find_element_by_id('currvalue'), value)

    #@in_private_info_popup
    def fill_cv_currency(self, value):
        #<a ng-href="" ng-click="editctrl.editdata.item.cv_currency=currency.value"> 												USD 											</a>
        #<a ng-href="" ng-click="editctrl.editdata.item.cv_currency=currency.value"> 												USD 											</a>
        if value == '':
            return
        div = self.itemEl.find_element_by_xpath(
        '//div[@class="form-group"]/label[@for="cv_currency"]')
        button = self.itemEl.find_element_by_xpath('//button[@id="cv_currency"]').click()
        a = self.itemEl.find_element_by_xpath(
            '//a[starts-with(@ng-click,"editctrl.editdata.item.cv_currency") and contains(text(), "{}")]'.format(value))
        print (a)
        a.click()

    #@in_private_info_popup
    def fill_acquisitiondate(self, value):
        self.update_text(
            self.itemEl.find_element_by_xpath(
                "//input[contains(@id, 'acquisitiondate')]"), value)

    #@in_private_info_popup
    def fill_acquiredfrom(self, value):
        self.update_text(self.itemEl.find_element_by_id('acquiredfrom'), value)

    #@in_private_info_popup
    def fill_quantity(self, value):
        self.update_text(self.itemEl.find_element_by_id('quantity'), value)

    #@in_private_info_popup
    def fill_privatecomment(self, value):
        self.update_text(self.itemEl.find_element_by_id('privatecomment'), value)
