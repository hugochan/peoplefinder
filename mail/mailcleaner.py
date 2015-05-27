# -*- coding: utf-8 -*-

import email
import mailbox
import chardet
import re
import os

class MailCleaner(object):
    EMAIL_PATTERN1 = r'<(.*)>'
    EMAIL_PATTERN2 = r'^[\s]*([^\s]*)[\s]*'
    EMAIL_PATTERN3 = r'^[\s]*[^()]*[\s]*'
    DEFAULT_STOP_PATTERN = (r'(?:-|grad|app|notif(?:y|ication)|noreply|service|sail|business|airchina|help|gift|support|info|party|city|employ|pay|regist|admi(?:s|n)|(?:no|every)body)|(?:github|youtube|google|baidu|amazon|eefocus|zhaoshangju|elecfans|360buy|altera|7days(?:inn|room|)|verifylist|iar|wps|pingan|zhenpin|dangdang|xfcom)',)
    DATA_ROOT = './data/'

    def __init__(self, path):
        self.mbox = [mailbox.mbox(each) for each in path]
        self.mails_count = 0

    def get_emailaddrs(self):
        """
        Return all the email addresses involved in from, to or cc field
        might be dirty data
        """
        collector = set()
        for each_mbox in self.mbox:
            for each_record in each_mbox:
                if each_record.has_key('From'):
                    collector.update(each_record['From'].split(','))
                if each_record.has_key('To'):
                    collector.update(each_record['To'].split(','))
                if each_record.has_key('Cc'):
                    collector.update(each_record['Cc'].split(','))
        return collector

    def is_auto_sent_group(self, mail_list, stoplist):
        """
        Tell if it is an auto-sent group mail
        which may depend on your requirement
        """
        for each_receiver in mail_list:
            emailaddr, username = self.parseaddr(each_receiver)
            if emailaddr and not self.is_stopword(emailaddr, stoplist):
                return False
        return True

    def is_stopword(self, string, stoplist):
        """
        Tell if it is a stop word
        """
        for each_stop_pattern in stoplist:
            if re.findall(each_stop_pattern, string, re.I):
                return True
        return False

    def parseaddr(self, string):
        """
        Parse email addresses to get username and addresses
        """
        username, emailaddr = email.utils.parseaddr(string)
        if '1098796184' in emailaddr:
            import pdb;pdb.set_trace()
        try:
            if chardet.detect(username)['encoding'] == 'ascii':
                # parse username decoded like '=?gbk?Q?=CF=E0=C6=AC?='
                dh = email.Header.decode_header(email.Header.Header(username))
                username = dh[0][0]
                if dh[0][1] and dh[0][1] != 'utf-8':
                    username = username.decode(dh[0][1]).encode('utf-8')
        except Exception, e:
            print e
            return [emailaddr, None]
        return [emailaddr, username]

    def handle_reg(self, string):
        """
        Parse email addresses, replaced by the parseaddr method
        """
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
            print self.parseaddr(each)

    def clean_emailaddrs(self, stoplist):
        mapping_table = {} # username-email mapping table
        contact_table = {} # contact list
        for each_mbox in self.mbox:
            for each_record in each_mbox:
                self.mails_count += 1
                tmp_contact_set = set()
                tmp_raw_contact_set = set()

                if each_record.has_key('From'):
                    tmp_mail_from = each_record['From'].split(',')
                    # filter auto-sent group emails
                    if self.is_auto_sent_group(tmp_mail_from, stoplist):
                        continue
                    tmp_raw_contact_set.update(tmp_mail_from)
                if each_record.has_key('To'):
                    tmp_mail_to = each_record['To'].split(',')
                    # filter auto-sent group emails
                    if self.is_auto_sent_group(tmp_mail_to, stoplist):
                        continue
                    tmp_raw_contact_set.update(tmp_mail_to)
                if each_record.has_key('Cc'):
                    tmp_raw_contact_set.update(each_record['Cc'].split(','))

                for each_raw_contact in tmp_raw_contact_set:
                    emailaddr, username = self.parseaddr(each_raw_contact)
                    if emailaddr and not self.is_stopword(emailaddr, stoplist):
                        tmp_contact_set.update([emailaddr])
                        mapping_table[emailaddr] = username

                for each_contact in tmp_contact_set:
                    try:
                        contact_table[each_contact].update(tmp_contact_set)
                    except:
                        contact_table.update({each_contact:tmp_contact_set})
        return [mapping_table, contact_table]
