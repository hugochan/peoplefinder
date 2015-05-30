# -*- coding: utf-8 -*-

import os
import time
import pp # parallel python
import sys
sys.path.extend(['mail', 'social/linkedin', 'social/renren'])
from mailcleaner import MailCleaner
from visualgraph import VisualGraph
from renren import RenRen
import jieba
import pickle
import selenium # parse dynamic web pages


PROJECT_ROOT = os.path.split(os.path.realpath(__file__))[0]

class PeopleFinder(object):
    def __init__(self, mail_handler, social_handler):
        self.mail_handler = mail_handler
        self.social_handler = social_handler
        self.profile_results = {}

    def create_email_network(self, local=False, show_and_save=False):
        if not local:
            self.email_mapping_table, self.email_contact_table = self.mail_handler.clean_emailaddrs(\
                                                                mc.DEFAULT_STOP_PATTERN)
            # save data
            self.save_data([self.email_mapping_table, self.email_contact_table], 'email')
        else:
            self.email_mapping_table, self.email_contact_table = self.load_data('email')
        if show_and_save:
            vg = VisualGraph()
            vg.import_data(self.email_contact_table)
            vg.save_graph('tmp_mail.png')
        return self.email_mapping_table, self.email_contact_table

    def create_social_network(self, mapping_table):
        top_num = 10
        first_circle_candidates = {}
        social_friend_table = {} # friend list

        driver = selenium.webdriver.Firefox() # assume you have firefox on your local computer
        # login first
        driver.get('http://renren.com')
        username = driver.find_element_by_id("email")
        password = driver.find_element_by_id("password")
        username.send_keys(self.social_handler.email)
        password.send_keys(self.social_handler.password)
        driver.find_element_by_id("login").click()
        time.sleep(3) # import time delay

        for emailaddr, username in mapping_table:
            candidates_table = self.social_handler.search_profiles(emailaddr, top_num, driver)
            # candidates_table = {}
            if not candidates_table:
                search_name = username and username or emailaddr.split('@')[0]
                candidates_table = self.social_handler.search_profiles(search_name, top_num, driver)
            first_circle_candidates.update(candidates_table)
        driver.close()

        social_mapping_table = first_circle_candidates.copy()
        for each_uid in first_circle_candidates.keys():
            all_friends = self.social_handler.get_friends(each_uid)
            social_mapping_table.update(all_friends)
            social_friend_table.update({each_uid: set(all_friends.keys())})
            for each_friend in all_friends.keys():
                try:
                    social_friend_table[each_friend].update([each_uid])
                except:
                    social_friend_table.update({each_friend: set([each_uid])})
        return social_mapping_table, social_friend_table

    def create_social_network_pp(self, mapping_table, local=False, show_and_save=False):
        if not local:
            self.social_mapping_table = {}
            self.social_friend_table = {}
            mapping_table = mapping_table.items()

            # using parallel computing
            batch_num = 8
            task_num = len(mapping_table)
            batch_size = task_num/batch_num
            job_server = pp.Server()# require parallel python

            for index in range(0, batch_num):
                job = job_server.submit(func=self.create_social_network, \
                    args=(mapping_table[index*batch_size:(index+1)*batch_size],), \
                    depfuncs=(), modules=('selenium', 'time'), callback=self.merge_social_network)
            job_server.wait()
            print "%s tasks done !"%(batch_num*batch_size)

            if task_num - batch_num*batch_size != 0:
                job = job_server.submit(func=self.create_social_network, \
                    args=(mapping_table[batch_num*batch_size:task_num],), \
                    depfuncs=(), modules=('selenium', 'time'), callback=self.merge_social_network)
                job_server.wait()
                print "%s tasks done !"%task_num

            # save data
            self.save_data([self.social_mapping_table, self.social_friend_table], 'social')
        else:
            self.social_mapping_table, self.social_friend_table = self.load_data('social')

        if show_and_save:
            pass
        return self.social_mapping_table, self.social_friend_table

    def merge_social_network(self, result):
        self.social_mapping_table.update(result[0])
        for k, v in result[1].iteritems():
            try:
                self.social_friend_table[k].update(v)
            except:
                self.social_friend_table.update({k:v})

    def save_data(self, data, data_type):
        """
        Save your data in local environment
        """
        path_root = os.path.join(PROJECT_ROOT, 'data', data_type)
        if not os.path.exists(path_root):
            os.makedirs(path_root)
        try:
            with open(os.path.join(path_root, 'mapping_table.dat'), 'w') as f1, \
                open(os.path.join(path_root, 'contact_table.dat'), 'w') as f2:
                mapping_table = pickle.dumps(data[0])
                contact_table = pickle.dumps(data[1])
                f1.write(mapping_table)
                f2.write(contact_table)
        except Exception, e:
            print e
            return False
        return True

    def load_data(self, data_type):
        path_root = os.path.join(PROJECT_ROOT, 'data', data_type)
        try:
            with open(os.path.join(path_root, 'mapping_table.dat'), 'r') as f1, \
                open(os.path.join(path_root, 'contact_table.dat'), 'r') as f2:
                mapping_table = pickle.loads(f1.read())
                contact_table = pickle.loads(f2.read())
        except Exception, e:
            print e
            return False
        return [mapping_table, contact_table]

    def save_results(self, data, data_type):
        """
        Save your results in local environment
        """
        path_root = os.path.join(PROJECT_ROOT, 'data/results')
        if not os.path.exists(path_root):
            os.makedirs(path_root)
        try:
            with open(os.path.join(path_root, '%s.dat'%data_type), 'w') as f:
                results = pickle.dumps(data)
                f.write(results)
        except Exception, e:
            print e
            return False
        return True

    def load_results(self, data_type):
        path_root = os.path.join(PROJECT_ROOT, 'data/results')
        try:
            with open(os.path.join(path_root, '%s.dat'%data_type), 'r') as f:
                results = pickle.loads(f.read())
        except Exception, e:
            print e
            return False
        return results

    def merge_results(self, result):
        self.recommend_list.update(result)

    def run_pp(self, method, top_num=10):
        self.recommend_list = {}
        email_mapping_table = self.email_mapping_table.items()
        # using parallel computing
        batch_num = 8
        task_num = len(email_mapping_table)
        batch_size = task_num/batch_num
        job_server = pp.Server()# require parallel python

        for index in range(0, batch_num):
            job = job_server.submit(func=self.run, \
                args=(method, email_mapping_table[index*batch_size:(index+1)*batch_size], top_num),\
                depfuncs=(), modules=('jieba',), callback=self.merge_results)
        job_server.wait()
        print "%s tasks done !"%(batch_num*batch_size)

        if task_num - batch_num*batch_size != 0:
            job = job_server.submit(func=self.run, \
                args=(method, email_mapping_table[batch_num*batch_size:task_num], top_num),\
                depfuncs=(), modules=('jieba',), callback=self.merge_results)
            job_server.wait()
            print "%s tasks done !"%task_num

        self.save_results(self.recommend_list, method)

    def run(self, method, email_mapping_table, top_num=10):
        recommend_list = {}
        for each_email_uid, each_email_name in email_mapping_table:
            candidates = self.do_recommend(each_email_uid, method, top_num)
            recommend_list[each_email_uid] = candidates
            print '%s done!'%each_email_uid
        # self.save_results(recommend_list, method)
        return recommend_list

    def do_recommend(self, email_uid, method, top_num):
        candidates = {}
        if method == 'profile':
            email_pf = self.email_mapping_table[email_uid] and self.email_mapping_table[email_uid] or email_uid.split('@')[0]
            for each_social_uid, each_social_pf in self.social_mapping_table.iteritems():
                sim = self.calc_profile_sim(email_pf, each_social_pf)
                candidates.update({each_social_uid: sim})
        elif method == 'graph':
            pass
        elif method == 'overlap':
            for each_social_uid in self.social_mapping_table.keys():
                sim = self.calc_entry_sim_overlap(email_uid, each_social_uid)
                candidates.update({each_social_uid: sim})
        else:
            pass
        candidates = sorted(candidates.iteritems(), key=lambda d:d[1], reverse=True)
        return candidates[:top_num]

    def calc_entry_sim_overlap(self, email_uid, social_uid):
        RATIO = 0.5
        # neighborhood_optimal_match = {}
        overlap_score = 0.0
        total_score = 0.0
        for each_neighbor in self.email_contact_table[email_uid]:
            optimal_match = self.get_optimal_socials([each_neighbor, \
                                self.email_mapping_table[each_neighbor]])
            # neighborhood_optimal_match[optimal_match[0]] = optimal_match[1]
            total_score += optimal_match[1]
            if optimal_match[0] in self.social_friend_table[social_uid]:
                overlap_score += optimal_match[1]

        # method 1
        sim_overlap_a = total_score and overlap_score/total_score or 0.0
        # method 2
        count = len(self.social_friend_table[social_uid])
        sim_overlap_b = count and overlap_score/count or 0.0
        sim_overlap = sim_overlap_a*RATIO + sim_overlap_b*(1-RATIO)
        return sim_overlap

    def get_optimal_socials(self, email_entry, local=True):
        if local:
            return self.profile_results[email_entry[0]][0]
        result_list = {}
        email_pf = email_entry[1] and email_entry[1] or email_entry[0].split('@')[0]
        for each_uid, each_uname in self.social_mapping_table.iteritems():
            sim = self.calc_profile_sim(email_pf, each_uname)
            result_list.update({each_uid: sim})
        optimal_match = sorted(result_list.iteritems(), key=lambda d:d[1], reverse=True)[:1]
        return optimal_match

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

