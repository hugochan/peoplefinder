# -*- coding: utf-8 -*-

import jieba
import sys
sys.path.extend(['mail', 'social/linkedin', 'social/renren'])
from mailcleaner import MailCleaner
from visualgraph import VisualGraph
from renren import RenRen

class PeopleFinder(object):
    def __init__(self, mail_handler, social_handler):
        self.mail_handler = mail_handler
        self.social_handler = social_handler

    def create_email_network(self, show_and_save=False):
        self.email_mapping_table, self.email_contact_table = self.mail_handler.clean_emailaddrs(\
                                                            mc.DEFAULT_STOP_PATTERN)
        # mc.save_emailaddrs([self.email_mapping_table, self.email_contact_table], 'mail/umich')
        if show_and_save:
            vg = VisualGraph()
            vg.import_data(self.email_contact_table)
            vg.save_graph('tmp_mail.png')
        return self.email_mapping_table

    def create_social_network(self, mapping_table, show_and_save=False):
        top_num = 20
        first_circle_candidates = {}
        self.social_friend_table = {} # friend list
        for emailaddr, username in mapping_table.iteritems():
            candidates_table = self.social_handler.search_profiles(emailaddr, top_num)
            if not candidates_table:
                search_name = username and username or emailaddr.split('@')[0]
                candidates_table = self.social_handler.search_profiles(search_name, top_num)
            first_circle_candidates.update(candidates_table)

        self.social_mapping_table = first_circle_candidates.copy()
        for each_uid, each_uname in first_circle_candidates.keys():
            all_friends = self.social_handler.get_friends(each_uid)
            self.social_mapping_table.update(all_friends)
            self.social_friend_table.update({each_uid: set(all_friends.keys())})
            for each_friend in all_friends.keys():
                try:
                    self.social_friend_table[each_friend].update([each_uid])
                except:
                    self.social_friend_table.update({each_friend: set([each_uid])})
        return self.social_mapping_table, self.social_friend_table

    def calc_entry_sim_overlap(self, email_uid, social_uid):
        self.email_contact_table[email_uid]


        self.social_friend_table[social_uid]



    def get_optimal_socials(self, email_entry):
        result_list = {}
        email_pf = email_entry[1] and email_entry[1] or email_entry[0].split('@')[0]
        for each_uid, each_uname in self.social_mapping_table.iteritems():
            sim = self.calc_profile_sim(email_pf, each_uname)
            result_list.update({each_uid: sim})
            ## to do

    def calc_profile_sim(self, email_pf, social_pf):
        sim = self.calc_string_sim(email_pf, social_pf)
        return sim

    def calc_string_sim(self, a, b):
        try:
            a_seg_list = [x for x in jieba.cut(a, cut_all=False)]
            b_seg_list = [x for x in jieba.cut(b, cut_all=False)]
        except Exception, e:
            print e
            assert False
        sim = self.jaccard_sim(a_seg_list, b_seg_list)
        return sim

    def jaccard_sim(self, a, b): # remove repeated words
        a, b = set(a), set(b)
        union_count = float(len(a | b))
        sim = union_count and len(a&b)/union_count or 0
        return sim

if __name__ == '__main__':
    email = "1256679551@qq.com"
    passwd = '1993042887564299'
    test_mapping_table = {'1256679551@qq.com':'陈田'}
    # renren = RenRen(email, passwd)
    renren = None
    pf = PeopleFinder(None, renren)
    # import pdb;pdb.set_trace()
    # V, E = pf.create_social_network(test_mapping_table)
    # print V
    # print E

    # import jieba
    # seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
    # for each in seg_list:
    #     print each
    # # print "Full Mode: " + "/ ".join(seg_list)  # 全模式
