"""
Import a game collection from a CSV file.

Note this action can be used to initialize a new collection, but also to update an existing
collection. Only the fields defined in the file will be updated.

Usage: bggcli [-v] -l <login> -p <password>
              [-c <name>=<value>]...
              collection-import <file>

Options:
    -v                              Activate verbose logging
    -l, --login <login>             Your login on BGG
    -p, --password <password>       Your password on BGG
    -c <name=value>                 To specify advanced options, see below

Advanced options:
    browser-keep=<true|false>       If you want to keep your web browser opened at the end of the
                                    operation
    browser-profile-dir=<dir>       Path or your browser profile if you want to use an existing

Arguments:
    <file> The CSV file with games to import
"""
# Updated for BGG 2018
import sys
from bggcli.commands import check_file
from bggcli.ui.gamepage import GamePage
from bggcli.ui.loginpage import LoginPage
from bggcli.util.csvreader import CsvReader
from bggcli.util.logger import Logger
from bggcli.util.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

import traceback

LOOPLIMIT = 5
def execute(args, options):
    print('Executing!')
    login = args['--login']

    file_path = check_file(args)

    csv_reader = CsvReader(file_path)
    csv_reader.open()
    rows = []
#    try:
    Logger.info("Parsing input file '{}'...".format(file_path))
    csv_reader.iterate(lambda row: rows.append(row))
    #Logger.info("Found %s games to put in collection..." % csv_reader.rowCount)
    rows.reverse()
    firstrow = rows[0]
    loop = 0
    
    Logger.info("Importing {} games to collection of '{}' ...".format(csv_reader.rowCount,login))
    while rows:
        try:
            with WebDriver('collection-import', args, options) as web_driver:
                if not LoginPage(web_driver.driver).authenticate(login, args['--password']):
                    sys.exit(1)
                #input("Kill Firefox, then Press Enter to continue...")
                game_page = GamePage(web_driver.driver)
                while rows:
                    row = rows.pop()
                    if firstrow is None or firstrow == row:
                        loop += 1
                        if loop >= LOOPLIMIT:
                            Logger.info("Loop limit of {} reached.".format(loop))
                            return
                        Logger.info('Loop {} (maximum {})'.format(loop,LOOPLIMIT))
                        if rows:
                            firstrow = rows[0]
                            Logger.info('First assigned {}'.format(firstrow['objectname']))
                        else:
                            firstrow = None
                            Logger.info('First assigned None')
                            
                    Logger.info('(BGGID {}) Name: {} ({} game left)'.format(row['objectid'],row['objectname'],len(rows)+1))
                    
                    try:
                        val = game_page.update(row)
                        Logger.info('update returned {}'.format(val))
                        
                        if val:
                            #Logger.info('Updated (BGGID {0}) "{1}"'.format(row['objectid'],row['objectname']))
                            Logger.info('(BGGID {}) Name: {} UPDATED!'.format(row['objectid'],row['objectname'],len(rows)))
                            #  ({} game left)
                        else:
                            rows.insert(0,row)
                            Logger.info('returned False??, back in queue.'.format(len(rows))) #  ({} game left)

                    except WebDriverException:
                        rows.insert(0,row)
                        Logger.info('Exception occurred, back in queue.'.format(len(rows))) # ({} left)
                        Logger.info('WebDriverException occurred, restarting browser.')
                        raise
                        
                    except Exception as e:
                        traceback.print_exc(limit=2, file=sys.stdout)

                        rows.insert(0,row)
                        Logger.info('Exception occurred, back in queue.'.format(len(rows))) #  ({} left)

                        #badrows.append(row)
                # for row in rows:
                    # try:
                        # game_page.update(row)
                    # except:
                        # badrows.append(row)
                    # print
        except WebDriverException:
            pass
    Logger.info("Import has finished.")
