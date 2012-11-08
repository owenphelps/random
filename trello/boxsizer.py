#!/usr/bin/env python
import sys
from cmdln import Cmdln, alias, option
from trello import TrelloApi

class BoxSizer(Cmdln):
    name = 'boxsizer'

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

if __name__ == "__main__":
    boxsizer = BoxSizer()
    sys.exit(boxsizer.main())

