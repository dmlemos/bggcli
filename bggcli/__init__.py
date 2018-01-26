# Updated BGG_SUPPORTED_FIELDS
# Added BGG_EXPORTED_FIELDS and BGG_GAMEDB_FIELDS

import os

if os.environ.get('CI') == 'true':
    # Issues with Sauce Labs and HTTPS
    BGG_BASE_URL = "http://www.boardgamegeek.com"
else:
    BGG_BASE_URL = "https://www.boardgamegeek.com"

UI_ERROR_MSG = "Unexpected error while controlling the UI!\nEither the web pages have " \
               "changed and bggcli must be updated, or the site is down for " \
               "maintenance."

BGG_SUPPORTED_FIELDS = ['objectname', 'objectid', 'rating', 'own',
                        'fortrade', 'want', 'wanttobuy', 'wanttoplay', 'prevowned',
                        'preordered', 'wishlist', 'wishlistpriority', 'wishlistcomment',
                        'comment', 'conditiontext', 'haspartslist', 'wantpartslist',
                        'publisherid', 'imageid', 'year', 'language', 'other', 'pricepaid',
                        'pp_currency', 'currvalue', 'cv_currency', 'acquisitiondate',
                        'acquiredfrom', 'quantity', 'privatecomment',
                        '_versionid']

BGG_SUPPORTED_FIELDS = ['own',
                        'want', 'wanttobuy', 'wanttoplay', 'prevowned',
                        'preordered',
                        'fortrade', 'conditiontext',   # these must be in this order
                        'wishlist', 'wishlistpriority', 'wishlistcomment', # these must be in this order
                        'comment', 'rating',
                        'pricepaid', 'currvalue', 
                        'acquisitiondate', 'acquiredfrom', 'quantity', 'privatecomment',
                        'haspartslist', 'wantpartslist','publisherid', 'imageid',
                        'year', 'language', 'other',
                        #'cv_currency', 'pp_currency',
                        'objectname', 
                        'objectid', '_versionid', 'invlocation'
                       ]
                       
# More fields in the add/edit collection dialog:
# Inventory Date
# Inventory Location
# Barcode
# Aquisition Date
# Inventory Date
# Inventory Location
# Custom Title
# Custom Image Id
# Publisher Id
# Year
# Other
# Barcode

# list of headings in direct downloaded collection.csv
BGG_EXPORTED_FIELDS = [
'objectname',
'objectid',
'rating',
'numplays',
'weight',
'own',
'fortrade',
'want',
'wanttobuy',
'wanttoplay',
'prevowned',
'preordered',
'wishlist',
'wishlistpriority',
'wishlistcomment',
'comment',
'conditiontext',
'haspartslist',
'wantpartslist',
'numowned',
'publisherid',
'imageid',
'year',
'language',
'other',
'pricepaid',
'pp_currency',
'currvalue',
'cv_currency',
'acquisitiondate',
'acquiredfrom',
'quantity',
'privatecomment',
'version_publishers',
'version_languages',
'version_yearpublished',
'version_nickname',
]

BGG_GAMEDB_FIELDS = [
'collid',
'baverage',
'average',
'avgweight',
'rank',
'objecttype',
'originalname',
'minplayers',
'maxplayers',
'playingtime',
'maxplaytime',
'minplaytime',
'yearpublished',
'bggrecplayers',
'bggbestplayers',
'bggrecagerange',
'bgglanguagedependence',
'itemtype',
]

#print(set(BGG_EXPORTED_FIELDS)-set(BGG_SUPPORTED_FIELDS))
