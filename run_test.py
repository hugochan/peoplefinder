# -*- coding: utf-8 -*-

import sys
sys.path.extend(['mail', 'social/linkedin', 'social/renren'])
from mailcleaner import MailCleaner
from visualgraph import VisualGraph
from renren import RenRen
from peoplefinder import *
import numpy as np
import matplotlib.pyplot as plt

class PeopleFinderTest(object):

    def __init__(self, pf):
        self.pf = pf

    def test(self, method):
        accuracy_dict = {}
        ranking_score_dict = {}
        if method == 'profile':
            results = self.pf.load_results(method)
            for top_num in range(1, 11):
                accuracy_count = 0.0
                ranking_score = 0.0
                for email_uid, social_uid in self.real_mapping.iteritems():
                    candidate_social_uid = zip(*results[email_uid])[0][:top_num]
                    if social_uid in candidate_social_uid:
                        accuracy_count += 1
                        rank = candidate_social_uid.index(social_uid)
                        ranking_score += rank/float(top_num)
                    else:
                        ranking_score += 1.0
                accuracy_dict[top_num] = accuracy_count/len(self.real_mapping)
                ranking_score_dict[top_num] = ranking_score/len(self.real_mapping)
            print accuracy_dict
            print ranking_score_dict
        elif method == 'graph':
            # results = self.pf.load_results(method)
            email_index2uid = self.pf.email_mapping_table.keys()
            social_index2uid = self.pf.social_mapping_table.keys()
            email_uid2index = dict(zip(email_index2uid, range(len(self.pf.email_mapping_table))))
            social_uid2index = dict(zip(social_index2uid, range(len(self.pf.social_mapping_table))))
            for itn in range(1, 8):
                graph_sim_matrix = np.load('data/results/graph_sim_mat_it%s.npy'%itn)
                for top_num in range(1, 11):
                    accuracy_count = 0.0
                    ranking_score = 0.0
                    for email_uid, social_uid in self.real_mapping.iteritems():
                        candidates = zip(social_index2uid, graph_sim_matrix[email_uid2index[email_uid]])
                        candidates = sorted(candidates, key=lambda d:d[1], reverse=True)

                        candidate_social_uid = zip(*candidates)[0][:top_num]
                        if social_uid in candidate_social_uid:
                            accuracy_count += 1
                            rank = candidate_social_uid.index(social_uid)
                            ranking_score += rank/float(top_num)
                        else:
                            ranking_score += 1.0
                    accuracy_dict[top_num] = accuracy_count/len(self.real_mapping)
                    ranking_score_dict[top_num] = ranking_score/len(self.real_mapping)
                print 'iteration %s'%itn
                print accuracy_dict
                print ranking_score_dict
        elif method == 'overlap':
            results = self.pf.load_results(method)
            for top_num in range(1, 11):
                accuracy_count = 0.0
                ranking_score = 0.0
                for email_uid, social_uid in self.real_mapping.iteritems():
                    candidate_social_uid = zip(*results[email_uid])[0][:top_num]
                    if social_uid in candidate_social_uid:
                        accuracy_count += 1
                        rank = candidate_social_uid.index(social_uid)
                        ranking_score += rank/float(top_num)
                    else:
                        ranking_score += 1.0
                accuracy_dict[top_num] = accuracy_count/len(self.real_mapping)
                ranking_score_dict[top_num] = ranking_score/len(self.real_mapping)
            print accuracy_dict
            print ranking_score_dict
        elif method == 'PPGM':
            email_index2uid = self.pf.email_mapping_table.keys()
            social_index2uid = self.pf.social_mapping_table.keys()
            email_uid2index = dict(zip(email_index2uid, range(len(self.pf.email_mapping_table))))
            social_uid2index = dict(zip(social_index2uid, range(len(self.pf.social_mapping_table))))
            profile_sim_matrix = np.load('profile_sim_matrix_part.npy')
            graph_sim_matrix = np.load('data/results/graph_sim_mat_it1.npy')
            accuracy_results = {}
            ranking_score_results = {}

            for top_num in [2, 4, 6, 8, 9]:
                accuracy_dict = {}
                ranking_score_dict = {}
                for ratio in [0.2]:
                    accuracy_count = 0.0
                    ranking_score = 0.0
                    index = 0
                    for email_uid, social_uid in self.real_mapping.iteritems():
                        total_sim_matrix = ratio*profile_sim_matrix[index] + (1-ratio)*graph_sim_matrix[email_uid2index[email_uid]]
                        candidates = zip(social_index2uid, total_sim_matrix)
                        candidates = sorted(candidates, key=lambda d:d[1], reverse=True)
                        candidate_social_uid = zip(*candidates)[0][:top_num]

                        if social_uid in candidate_social_uid:
                            accuracy_count += 1
                            rank = candidate_social_uid.index(social_uid)
                            ranking_score += rank/float(top_num)
                        else:
                            ranking_score += 1.0
                        index += 1
                    accuracy_dict[ratio] = accuracy_count/len(self.real_mapping)
                    ranking_score_dict[ratio] = ranking_score/len(self.real_mapping)
                    print 'ratio:%s done!'%ratio
                accuracy_results[top_num] = accuracy_dict
                ranking_score_results[top_num] = ranking_score_dict
                print 'top_num:%s done!'%top_num

            print accuracy_results
            print ranking_score_results

    def load_real_mapping(self, path):
        self.real_mapping = {}
        try:
            with open(path, 'r') as f:
                for line in f:
                    content = line.split(',')
                    if len(content) == 3:
                        self.real_mapping[content[0]] = content[2].replace('\n', '')
                f.close()

        except Exception, e:
            print e
            return False
        # print len(self.real_mapping)
        # for k, v in self.real_mapping.items():
        #     print k, v

    def visual_results(self):
        # # GM algorithm
        # iteration_time = [(1, 9613.35643), (2, 12113.567425), (3, 14974.5322859), (4, 19351.0366409), (5, 23430.754087), (6, 27597.5242889), (7, 31598.7238252)]

        # # plt.axes([0.12, 0.1, 0.8, 0.8])
        # # plt.text(2.5, 5.0, 'caixin')
        # plt.title(u"GM algorithm: iteration-time graph")

        # # ylim = [auc_min - (auc_max - auc_min)*0.1, auc_max + (auc_max - auc_min)*0.1]
        # plt.hold(True)
        # plt.plot(zip(*iteration_time)[0], zip(*iteration_time)[1], "d--", color="g", linewidth=1.5)
        # plt.xlabel("iteration")
        # plt.ylabel("run time (s)")
        # # plt.ylim(ylim)
        # # plt.legend(loc='upper left', fontsize=12)
        # plt.savefig("GM_it_time.eps", figsize=(20,20), dpi=1200)
        # plt.show()



        # # GM algorithm

        # iteration_changes = [(1, 0.99998057833513221), (2, 1.9420548532056962e-05), (3, 1.1163185994961189e-09), \
        #     (4, 1.7140689518981823e-14), (5, 4.8749159221841542e-18), (6, 9.5714254167198772e-23), (7, 2.58219402037e-26)]

        # # plt.axes([0.12, 0.1, 0.8, 0.8])
        # # plt.text(2.5, 5.0, 'caixin')
        # plt.title(u"GM algorithm: iteration-changes graph")

        # # ylim = [auc_min - (auc_max - auc_min)*0.1, auc_max + (auc_max - auc_min)*0.1]
        # plt.hold(True)
        # iteration, changes = zip(*iteration_changes)[0], zip(*iteration_changes)[1]
        # plt.plot(iteration, changes, "d--", color="g", linewidth=1.5)
        # plt.xlabel("iteration")
        # plt.ylabel("log(changes)")
        # plt.semilogy(iteration, changes, lw=2)
        # # plt.ylim(ylim)
        # # plt.legend(loc='upper left', fontsize=12)
        # plt.savefig("GM_it_changes.eps", figsize=(20,20), dpi=1200)
        # plt.show()



        # plt.title(u"GM algorithm: iteration-accuracy graph")
        # plt.hold(True)

        # # k = 1
        # iteration_accuracy = [0.3169642857142857, 0.16964285714285715, 0.17410714285714285, 0.17410714285714285, 0.17410714285714285, 0.16964285714285715, 0.16964285714285715]
        # plt.plot(range(1, 8), iteration_accuracy, "d--", color="g", linewidth=1.5, label="k=1")
        # plt.legend(loc='upper left', fontsize=12)

        # # k = 3
        # iteration_accuracy = [0.36160714285714285, 0.18303571428571427, 0.18303571428571427, 0.17857142857142858, 0.17857142857142858, 0.17857142857142858, 0.17857142857142858]
        # plt.plot(range(1, 8), iteration_accuracy, "s--", color="r", linewidth=1.5, label="k=3")
        # plt.legend(loc='upper left', fontsize=12)


        # # k = 5
        # iteration_accuracy = [0.38839285714285715, 0.1875, 0.1875, 0.17857142857142858, 0.18303571428571427, 0.17857142857142858, 0.17857142857142858]
        # plt.plot(range(1, 8), iteration_accuracy, "v--", color="b", linewidth=1.5, label="k=5")
        # plt.legend(loc='upper left', fontsize=12)


        # # # k = 7
        # # iteration_accuracy = [0.4017857142857143, 0.19196428571428573, 0.1875, 0.1875, 0.18303571428571427, 0.1875, 0.17857142857142858]
        # # plt.plot(range(1, 8), iteration_accuracy, "p--", color="m", linewidth=1.5, label="k=7")
        # # plt.legend(loc='upper left', fontsize=12)


        # # k = 10
        # iteration_accuracy = [0.41517857142857145, 0.19642857142857142, 0.19642857142857142, 0.19196428571428573, 0.19196428571428573, 0.19196428571428573, 0.19196428571428573]
        # plt.plot(range(1, 8), iteration_accuracy, "k--", color="y", linewidth=1.5, label="k=10")
        # plt.legend(loc='upper left', fontsize=12)

        # plt.xlabel("iteration")
        # plt.ylabel("accuracy")
        # plt.savefig("GM_it_accuracy.eps", figsize=(20,20), dpi=1200)
        # plt.show()


        # plt.title(u"GM algorithm: iteration-ranking score graph")
        # plt.hold(True)

        # # k = 1
        # iteration_ranking = [0.6830357142857143, 0.8303571428571429, 0.8258928571428571, 0.8258928571428571, 0.8258928571428571, 0.8303571428571429, 0.8303571428571429]
        # plt.plot(range(1, 8), iteration_ranking, "d--", color="g", linewidth=1.5, label="k=1")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 3
        # iteration_ranking = [0.6547619047619048, 0.8229166666666666, 0.8199404761904762, 0.8229166666666666, 0.8229166666666666, 0.824404761904762, 0.824404761904762]
        # plt.plot(range(1, 8), iteration_ranking, "s--", color="r", linewidth=1.5, label="k=3")
        # plt.legend(loc='lower right', fontsize=12)


        # # k = 5
        # iteration_ranking = [0.6410714285714285, 0.8187500000000002, 0.8169642857142857, 0.8223214285714285, 0.8214285714285714, 0.8232142857142858, 0.8232142857142858]
        # plt.plot(range(1, 8), iteration_ranking, "v--", color="b", linewidth=1.5, label="k=5")
        # plt.legend(loc='lower right', fontsize=12)


        # # k = 10
        # iteration_ranking = [0.6183035714285715, 0.8120535714285714, 0.8125, 0.8165178571428571, 0.8169642857142857, 0.8169642857142857, 0.8178571428571428]
        # plt.plot(range(1, 8), iteration_ranking, "k--", color="y", linewidth=1.5, label="k=10")
        # plt.legend(loc='lower right', fontsize=12)

        # plt.xlabel("iteration")
        # plt.ylabel("ranking score")
        # plt.savefig("GM_it_ranking.eps", figsize=(20,20), dpi=1200)
        # plt.show()


        # # PPGM
        # k_ratio_accuracy = {1: {0.0: 0.3169642857142857, 1.0: 0.18303571428571427, 0.4: 0.3392857142857143, 0.8: 0.3392857142857143, 0.6: 0.3392857142857143, 0.2: 0.3392857142857143}, 3: {0.0: 0.36160714285714285, 1.0: 0.28125, 0.4: 0.375, 0.8: 0.375, 0.6: 0.375, 0.2: 0.375}, 5: {0.0: 0.38839285714285715, 1.0: 0.3482142857142857, 0.4: 0.39285714285714285, 0.8: 0.39285714285714285, 0.6: 0.39285714285714285, 0.2: 0.39285714285714285}, 7: {0.0: 0.4017857142857143, 1.0: 0.36607142857142855, 0.4: 0.4017857142857143, 0.8: 0.4017857142857143, 0.6: 0.4017857142857143, 0.2: 0.4017857142857143},10: {0.0: 0.41517857142857145, 1.0: 0.4330357142857143, 0.4: 0.4419642857142857, 0.8: 0.4419642857142857, 0.6: 0.4419642857142857, 0.2: 0.4419642857142857}}
        # plt.hold(True)

        # # k = 1
        # tmp = sorted(k_ratio_accuracy[1].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "d--", color="g", linewidth=1.5, label="k=1")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 3
        # tmp = sorted(k_ratio_accuracy[3].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "s--", color="b", linewidth=1.5, label="k=3")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 5
        # tmp = sorted(k_ratio_accuracy[5].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "v--", color="r", linewidth=1.5, label="k=5")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 10
        # tmp = sorted(k_ratio_accuracy[10].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "p--", color="y", linewidth=1.5, label="k=10")
        # plt.legend(loc='lower right', fontsize=12)

        # plt.xlabel("$\phi$")
        # plt.ylabel("accuracy")
        # plt.savefig("PPGM_k_ratio_accuracy.eps", figsize=(20,20), dpi=1200)
        # plt.show()


        # # PPGM
        # k_ratio_ranking = {1: {0.0: 0.6830357142857143, 1.0: 0.8169642857142857, 0.4: 0.6607142857142857, 0.8: 0.6607142857142857, 0.6: 0.6607142857142857, 0.2: 0.6607142857142857}, 3: {0.0: 0.6547619047619048, 1.0: 0.7663690476190474, 0.4: 0.6398809523809523, 0.8: 0.6398809523809523, 0.6: 0.6398809523809523, 0.2: 0.6398809523809523}, 5: {0.0: 0.6410714285714285, 1.0: 0.724107142857143, 0.4: 0.6276785714285715, 0.8: 0.6276785714285715, 0.6: 0.6276785714285715, 0.2: 0.6276785714285715}, 7: {0.0: 0.6301020408163265, 1.0: 0.6996173469387753, 0.4: 0.6192602040816327, 0.8: 0.6192602040816327, 0.6: 0.6192602040816327, 0.2: 0.6192602040816327}, 10: {0.0: 0.6183035714285715, 1.0: 0.665625, 0.4: 0.6044642857142856, 0.8: 0.6044642857142856, 0.6: 0.6044642857142856, 0.2: 0.6044642857142856}}
        # plt.hold(True)

        # # k = 1
        # tmp = sorted(k_ratio_ranking[1].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "d--", color="g", linewidth=1.5, label="k=1")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 3
        # tmp = sorted(k_ratio_ranking[3].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "s--", color="b", linewidth=1.5, label="k=3")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 5
        # tmp = sorted(k_ratio_ranking[5].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "v--", color="r", linewidth=1.5, label="k=5")
        # plt.legend(loc='lower right', fontsize=12)

        # # k = 10
        # tmp = sorted(k_ratio_ranking[10].iteritems(), key=lambda d:d[0])
        # plt.plot(zip(*tmp)[0], zip(*tmp)[1], "p--", color="y", linewidth=1.5, label="k=10")
        # plt.legend(loc='lower right', fontsize=12)

        # plt.xlabel("$\phi$")
        # plt.ylabel("ranking score")
        # plt.savefig("PPGM_k_ratio_ranking.eps", figsize=(20,20), dpi=1200)
        # plt.show()


        # # accuracy
        # plt.hold(True)

        # pm_k_accuracy = {1: 0.18303571428571427, 2: 0.22767857142857142, 3: 0.29017857142857145, 4: 0.32589285714285715, 5: 0.34375, 6: 0.35714285714285715, 7: 0.36160714285714285, 8: 0.38839285714285715, 9: 0.41517857142857145, 10: 0.4330357142857143}
        # k, accuracy = pm_k_accuracy.keys(), pm_k_accuracy.values()
        # plt.plot(k, accuracy, "d--", color="g", linewidth=1.5, label="PM algorithm")
        # plt.xlabel("k")
        # plt.ylabel("accuracy")
        # plt.legend(loc='lower right', fontsize=12)


        # gm_k_accuracy = {1: 0.3169642857142857, 2: 0.35714285714285715, 3: 0.36160714285714285, 4: 0.3705357142857143, 5: 0.38839285714285715, 6: 0.39285714285714285, 7: 0.4017857142857143, 8: 0.4017857142857143, 9: 0.4107142857142857, 10: 0.41517857142857145}
        # k, accuracy = gm_k_accuracy.keys(), gm_k_accuracy.values()
        # plt.plot(k, accuracy, "s--", color="r", linewidth=1.5, label="GM algorithm")
        # plt.xlabel("k")
        # plt.ylabel("accuracy")
        # plt.legend(loc='lower right', fontsize=12)

        # mpgm_k_accuracy = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.004464285714285714, 8: 0.004464285714285714, 9: 0.004464285714285714, 10: 0.004464285714285714}
        # k, accuracy = mpgm_k_accuracy.keys(), mpgm_k_accuracy.values()
        # plt.plot(k, accuracy, "v--", color="b", linewidth=1.5, label="MPGM algorithm")
        # plt.xlabel("k")
        # plt.ylabel("accuracy")
        # plt.legend(loc='lower right', fontsize=12)



        # ppgm_k_accuracy = {8: 0.41517857142857145, 9: 0.4330357142857143, 2: 0.36607142857142855, 4: 0.38839285714285715, 6: 0.4017857142857143, 1: 0.3392857142857143, 3: 0.375, 5:0.39285714285714285, 7: 0.4017857142857143, 10:0.4419642857142857}
        # k, accuracy = ppgm_k_accuracy.keys(), ppgm_k_accuracy.values()
        # plt.plot(k, accuracy, "p--", color="y", linewidth=1.5, label="PPGM algorithm")
        # plt.xlabel("k")
        # plt.ylabel("accuracy")
        # plt.legend(loc='center right', fontsize=12)
        # plt.savefig("k_accuracy.eps", figsize=(20,20), dpi=1200)
        # plt.show()



        # ranking score
        plt.hold(True)

        pm_k_ranking = {1: 0.8169642857142857, 2: 0.7946428571428571, 3: 0.7663690476190476, 4: 0.7433035714285714, 5: 0.7258928571428572, 6: 0.7120535714285713, 7: 0.7015306122448981, 8: 0.6902901785714286, 9: 0.6785714285714288, 10: 0.6674107142857144}
        k, ranking_score = pm_k_ranking.keys(), pm_k_ranking.values()
        plt.plot(k, ranking_score, "d--", color="g", linewidth=1.5, label="PM algorithm")
        plt.xlabel("k")
        plt.ylabel("ranking score")
        plt.legend(loc='center right', fontsize=12)

        gm_k_ranking = {1: 0.6830357142857143, 2: 0.6629464285714286, 3: 0.6547619047619048, 4: 0.6484375, 5: 0.6410714285714285, 6: 0.6354166666666667, 7: 0.6301020408163265, 8: 0.6261160714285714, 9: 0.6220238095238096, 10: 0.6183035714285715}
        k, ranking_score = gm_k_ranking.keys(), gm_k_ranking.values()
        plt.plot(k, ranking_score, "s--", color="r", linewidth=1.5, label="GM algorithm")
        plt.xlabel("k")

        mpgm_k_ranking = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 0.9993622448979592, 8: 0.9988839285714286, 9: 0.9985119047619048, 10: 0.9982142857142857}
        k, ranking_score = mpgm_k_ranking.keys(), mpgm_k_ranking.values()
        plt.plot(k, ranking_score, "v--", color="b", linewidth=1.5, label="MPGM algorithm")
        plt.xlabel("k")
        plt.ylabel("ranking score")
        plt.legend(loc='center right', fontsize=12)


        ppgm_k_ranking = {8: 0.6149553571428571, 9: 0.6096230158730159, 2: 0.6473214285714286, 4: 0.6328125, 6: 0.6227678571428573, 1:0.6607142857142857, 3:0.6398809523809523, 5:0.6276785714285715, 7:0.6192602040816327, 10:0.6044642857142856}
        k, accuracy = ppgm_k_ranking.keys(), ppgm_k_ranking.values()
        plt.plot(k, accuracy, "p--", color="y", linewidth=1.5, label="PPGM algorithm")
        plt.xlabel("k")
        plt.ylabel("ranking score")
        plt.legend(loc='center right', fontsize=12)

        plt.ylabel("ranking score")
        plt.legend(loc='center right', fontsize=12)

        plt.savefig("k_ranking.eps", figsize=(20,20), dpi=1200)
        plt.show()

