# -*- coding: utf-8 -*-

import networkx as nx
import pylab

class VisualGraph(object):
    def __init__(self, name='Graph'):
        self.name = name

    def import_data(self, relation_dict, clear_degree=None):
        self.G = nx.Graph(name=self.name)  # Create a Graph object
        for usr, contacts in relation_dict.iteritems():
            for each_contact in contacts:
                if not usr == each_contact:
                    self.G.add_edge(usr, each_contact)
        if clear_degree and isinstance(clear_degree, int):
            self.clear_nodes(clear_degree)
        return self.G

    def clear_nodes(self, min_degree=2):
        while self._clear_nodes(min_degree):
            pass

    def _clear_nodes(self, min_degree):
        need_clear = False
        for each_node in self.G.nodes():
            if self.G.degree(each_node) < min_degree:
                self.G.remove_node(each_node)
                need_clear = True
        return need_clear

    def make_graph_fig(self):
        fig = pylab.figure()
        pylab.title(self.G.name)
        try:
            pos = nx.spring_layout(self.G)
            nx.draw(self.G, pos)
        except Exception, e:
            print e
            return False
        return fig

    def save_graph(self, filename):
        fig = self.make_graph_fig()
        try:
            fig.savefig(filename)
        except Exception, e:
            print e
            return False
        return True

    def show_graph(self):
        fig = self.make_graph_fig()
        try:
            fig.show()
        except Exception, e:
            print e
            return False
        return True

    def make_histogram(self):
        fig = pylab.figure()
        # ax = fig.add_subplot(1,1,1)
        pylab.title(self.G.name)
        hist = nx.degree_histogram(self.G)
        pylab.bar(range(len(hist)), hist, align = 'center')
        pylab.xlim((0, len(hist)))
        # ax.set_xscale('log')
        # ax.set_yscale('log')
        pylab.xlabel("Degree of node")
        pylab.ylabel("Number of nodes")
        return fig

    def save_histogram(self, filename):
        fig = self.make_histogram()
        try:
            fig.savefig(filename)
        except Exception, e:
            print e
            return False
        return True

    def show_histogram(self):
        fig = self.make_histogram()
        try:
            fig.show()
        except Exception, e:
            print e
            return False
        return True
