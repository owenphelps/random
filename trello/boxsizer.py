#!/usr/bin/env python
import sys
from cmdln import Cmdln, alias, option

from trello import TrelloApi
import gspread

class BoxSizer(Cmdln):
    name = 'boxsizer'

    def google_creds(self, opts):
        account, pwd = open(opts.credentials_file, 'r').read().strip().splitlines()
        return account, pwd

    def access_token(self, opts):
        return opts.token if opts.token else open(opts.token_file, 'r').read().strip()

    def app_key(self, opts):
        return opts.app_key if opts.app_key else open(opts.app_key_file, 'r').read().strip()

    def connect(self, app_key, token=None):
        trello = TrelloApi(app_key)
        if token:
            trello.set_token(token)
        return trello

    @option("-k", "--app-key", help='Trello supplied key to identify this application')
    @option("--app-key-file", default='APP_KEY',  help='Trello supplied key to identify this application (default "APP_KEY")')
    @option("-x", "--expires", default="30days", help='One of "30days" (default) or "never"')
    @option("-w", "--write-access", action="store_true", help="Always get read access, add this for write access")
    def do_token_request(self, subcmd, opts):
        """${cmd_name}: Generate a request for a trello access token
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        
        trello = self.connect(self.app_key(opts))
        print trello.get_token_url(self.name, opts.expires, write_access=opts.write_access)
        
    @option("-k", "--app-key", help='Trello supplied key to identify this application')
    @option("--app-key-file", default='APP_KEY',  help='Trello supplied key to identify this application (default "APP_KEY")')
    @option("-t", "--token", help='Access token for trello user')
    @option("-f", "--token-file", default='ACCESS_TOKEN', help='File in which the access token is stored (default "ACCESS_TOKEN")')
    def do_cards(self, subcmd, opts, board_id):
        """${cmd_name}: List the cards for supplied BOARD_ID
        
        ${cmd_usage}
        ${cmd_option_list}
        """

        trello = self.connect(self.app_key(opts), self.access_token(opts))

        raw_lists = trello.boards.get_list(board_id, fields='name') # gets all lists for board, id + name
        raw_cards = trello.boards.get_card(board_id, fields='name,idList') # gets all cards for board, id + name + idList

        lists_map = {x['id']:x['name'] for x in raw_lists} # so we can lookup the list for each card below
        cards     = [(lists_map[x['idList']], x['name']) for x in raw_cards]
        output    = ['%s,%s' % (card[0], card[1]) for card in cards]
        print '\n'.join(output)

    @option("-k", "--app-key", help='Trello supplied key to identify this application')
    @option("--app-key-file", default='APP_KEY',  help='Trello supplied key to identify this application (default "APP_KEY")')
    @option("-t", "--token", help='Access token for trello user')
    @option("-f", "--token-file", default='ACCESS_TOKEN', help='File in which the access token is stored (default "ACCESS_TOKEN")')
    def do_lists(self, subcmd, opts, BOARD_ID):
        """${cmd_name}: List the lists for supplied BOARD_ID
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        trello = self.connect(self.app_key(opts), self.access_token(opts))
        raw_lists = trello.boards.get_list(BOARD_ID, fields='name')
        output = ['%s,%s' % (x['id'], x['name']) for x in raw_lists]
        print '\n'.join(output)

    @option("-k", "--app-key", help='Trello supplied key to identify this application')
    @option("--app-key-file", default='APP_KEY', help='Trello supplied key to identify this application (default "APP_KEY")')
    @option("-t", "--token", help='Access token for trello user')
    @option("-f", "--token-file", default='ACCESS_TOKEN', help='File in which the access token is stored (default "ACCESS_TOKEN")')
    def do_load_list(self, subcmd, opts, LIST_ID, FILENAME):
        """${cmd_name}: Create new cards in LIST_ID for each line in FILENAME
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        trello = self.connect(self.app_key(opts), self.access_token(opts))
        lines = open(FILENAME, 'r').read().strip().splitlines()
        for line in lines:
            print line
            trello.lists.new_card(LIST_ID, name=line)

    @option("-c", "--credentials-file", default='GOOGLE_CREDENTIALS', help='File containing username and password, on separate lines (default "GOOGLE_CREDENTIALS")')
    def do_load_sheet(self, subcmd, opts, SPREADSHEET, WORKSHEET, FILENAME):
        """${cmd_name}: Load lines from FILENAME into WORKSHEET (name) in SPREADSHEET (name)
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        gc = gspread.login(*self.google_creds(opts))
        wks = gc.open(SPREADSHEET).worksheet(WORKSHEET)

        lines = open(FILENAME, 'r').read().strip().splitlines()
        reqs = [line.split(',', 1) for line in lines]

        cells = wks.range('A2:B%d' % len(reqs))
        for cell in cells:
            cell.value = reqs[cell.row-2][cell.col-1]
        wks.update_cells(cells)

if __name__ == "__main__":
    boxsizer = BoxSizer()
    sys.exit(boxsizer.main())

