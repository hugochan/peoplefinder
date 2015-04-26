# -*- coding: utf-8 -*-

import sys
sys.path.extend(['mail', 'social/linkedin'])
from mailcleaner import MailCleaner
from visualgraph import VisualGraph

if __name__ == '__main__':
     # mbox_path = ['gmail_takeout/Mail/all.mbox']
    mbox_path = ('mail/umich_takeout/Mail/Important.mbox', 'mail/umich_takeout/Mail/Inbox.mbox', \
                'mail/umich_takeout/Mail/Sent.mbox', 'mail/umich_takeout/Mail/Starred.mbox', \
                'mail/umich_takeout/Mail/Unread.mbox')
    mc = MailCleaner(mbox_path)
    # emailaddrs = mc.clean_emailaddrs(mc.DEFAULT_STOP_PATTERN)
    # mc.save_emailaddrs(emailaddrs, 'mail/umich')
    [mapping_table, contact_table] = mc.load_emailaddrs('mail/umich')
    vg = VisualGraph()
    vg.import_data(contact_table)
    vg.save_graph('test.png')
    vg.show_histogram('histogram.png')
