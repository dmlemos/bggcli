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
import traceback

LOOPLIMIT = 30
def execute(args, options):
    print('Executing!')
    login = args['--login']

    file_path = check_file(args)

    csv_reader = CsvReader(file_path)
    csv_reader.open()
    rows = []
    try:
        csv_reader.iterate(lambda row: rows.append(row))
    except:
        pass
    
    print len(rows)
    # interestingrows=rows[130:]
    # print len(interestingrows)
    #sys.exit()
    
    Logger.info("Importing games for '%s' account..." % login)

    with WebDriver('collection-import', args, options) as web_driver:
        if not LoginPage(web_driver.driver).authenticate(login, args['--password']):
            sys.exit(1)

        Logger.info("Importing %s games to collection..." % csv_reader.rowCount)
        game_page = GamePage(web_driver.driver)
        #csv_reader.iterate(lambda row: game_page.update(row))
        #badrows = []
        #rows = rows[:5]
        rows.reverse()
        firstrow = rows[0]
        loop = 1
        Logger.info('Loop {}'.format(loop))
        if loop > LOOPLIMIT:
            Logger.info("Loop limit of {} reached.".format(loop))
            return
        while len(rows):
            row = rows.pop()
            Logger.info('Name: {}'.format(row['objectname']))
            
            if firstrow is None or firstrow == row:
                loop += 1
                Logger.info('Loop {}'.format(loop))
                if rows:
                    firstrow = rows[0]
                    Logger.info('First assigned {}'.format(firstrow['objectname']))
                else:
                    firstrow = None
                    Logger.info('First assigned None')
            try:
                val = game_page.update(row)
                Logger.info('update returned {}'.format(val))
                
                if val:
                    Logger.info('Updated!')
                else:
                    Logger.info('returned False??, back in queue.')
                    rows.insert(0,row)

            except Exception as e:
                traceback.print_exc(limit=2, file=sys.stdout)

                Logger.info('Exception occurred, back in queue.')
                rows.insert(0,row)

                #badrows.append(row)
        # for row in rows:
            # try:
                # game_page.update(row)
            # except:
                # badrows.append(row)
            # print
        Logger.info("Import has finished.")
