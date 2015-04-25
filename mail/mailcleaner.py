# -*- coding: utf-8 -*-

import mailbox
import re
import os
import pickle

class MailCleaner(object):
    EMAIL_PATTERN1 = r'<(.*)>'
    EMAIL_PATTERN2 = r'^[\s]?([^\s]*)[\s]?'
    EMAIL_PATTERN3 = r'^[\s]?[^()]*[\s]'
    DATA_ROOT = './data/'

    def __init__(self, path, stoplist):
        self.mbox = [mailbox.mbox(each) for each in path]
        self.stoplist = stoplist

    def get_emailaddrs(self):
        collector = set()
        for each_mbox in self.mbox:
            for each_record in each_mbox:
                collector.update([each_record['From']])
                if each_record.has_key('To'):
                    collector.update(each_record['To'].split(','))
                if each_record.has_key('Cc'):
                    collector.update(each_record['Cc'].split(','))
        return collector

    def handle_reg(self, string):
        ret = re.findall(self.EMAIL_PATTERN1, string)
        if not ret:
            ret = re.findall(self.EMAIL_PATTERN2, string)
            username = None
        else:
            try:
                username = re.findall(self.EMAIL_PATTERN3, string)[0].strip().strip('"')
                if '?' in username or '=' in username:
                    username = None
            except:
                username = None
        assert isinstance(ret[0], str)
        emailaddr = '@' in ret[0] and ret[0] or ''
        return [emailaddr, username]

    def test_reg(self):
        collector = self.get_emailaddrs()
        for each in collector:
            print self.handle_reg(each)

    def clean_emailaddrs(self):
        mapping_table = {} # username-email mapping table
        contact_table = {} # contact list
        for each_mbox in self.mbox:
            for each_record in each_mbox:
                tmp_contact_set = set()
                tmp_raw_contact_set = set()
                tmp_raw_contact_set.update([each_record['From']])
                if each_record.has_key('To'):
                    tmp_raw_contact_set.update(each_record['To'].split(','))
                if each_record.has_key('Cc'):
                    tmp_raw_contact_set.update(each_record['Cc'].split(','))

                for each_raw_contact in tmp_raw_contact_set:
                    emailaddr, username = self.handle_reg(each_raw_contact)
                    if emailaddr:
                        tmp_contact_set.update([emailaddr])
                        mapping_table[emailaddr] = username # cover, to do
                for each_contact in tmp_contact_set:
                    try:
                        contact_table[each_contact].update(tmp_contact_set)
                    except:
                        contact_table.update({each_contact:tmp_contact_set})
        return [mapping_table, contact_table]

    def save_emailaddrs(self, emailaddrs, foldername):
        """
        save your data under the folder named data by default
        """
        mapping_table = pickle.dumps(emailaddrs[0])
        contact_table = pickle.dumps(emailaddrs[1])
        if not os.path.exists(os.path.join(self.DATA_ROOT, foldername)):
            os.makedirs(os.path.join(self.DATA_ROOT, foldername))
        try:
            with open(os.path.join(self.DATA_ROOT, foldername, 'mapping_table.dat'), 'w') as f1, \
                open(os.path.join(self.DATA_ROOT, foldername, 'contact_table.dat'), 'w') as f2:
                f1.write(mapping_table)
                f2.write(contact_table)
        except Exception, e:
            print e
            return False
        return True

    def load_emailaddrs(self, foldername):
        try:
            with open(os.path.join(self.DATA_ROOT, foldername, 'mapping_table.dat'), 'r') as f1, \
                open(os.path.join(self.DATA_ROOT, foldername, 'contact_table.dat'), 'r') as f2:
                mapping_table = pickle.loads(f1.read())
                contact_table = pickle.loads(f2.read())
        except Exception, e:
            print e
            return False
        return [mapping_table, contact_table]

if __name__ == '__main__':
    # mbox_path = ['gmail_takeout/Mail/all.mbox']
    mbox_path = ['umich_takeout/Mail/Important.mbox', 'umich_takeout/Mail/Inbox.mbox', \
                'umich_takeout/Mail/Sent.mbox', 'umich_takeout/Mail/Starred.mbox', \
                'umich_takeout/Mail/Unread.mbox']
    stoplist = ['',]
    mc = MailCleaner(mbox_path, stoplist)
    mc.get_emailaddrs()
    mc.test_reg()
    emailaddrs = mc.clean_emailaddrs()
    mc.save_emailaddrs(emailaddrs, 'umich')
    [mapping_table, contact_table] = mc.load_emailaddrs('umich')
