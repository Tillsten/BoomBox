# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 16:01:31 2013

@author: Tillsten
"""



from __future__ import print_function
import codecs
from boom_model import *
f = codecs.open('inventar.txt', encoding='utf-8')
inv = f.readlines()
list_it = []
for line in inv:
    name, price, image_path = line.rstrip().split('|')

    list_it.append(Item(name, price, image_path))


class Controller(object):
    def __init__(self):
        self.tabs = {}
        self.inv = []
        self.cash_register = Register(0.0)
        self.add_default_inv()
        self.current_tab = None


    def add_default_inv(self):
        self.inv.extend(list_it)

    def create_tab(self, name):
        names =  self.tabs.keys()
        if name in names:
            raise NameError('name already has a tab')
        tab = Tab(name)
        self.tabs[name] = tab

    def create_tabs_from_file(self, fname):
        with open(fname,'r') as f:
            for i in f:
                i = i.strip()
                self.create_tab(unicode(i))

    def add_to_tab(self, tab_name, item):
        tab = self.tabs[tab_name]
        tab.add_to_tab(item)

    def pay_tab(self, tab_name):
        tab = self.tabs[tab_name]
        payed = tab.calc_total()
        with open('full_log.txt', 'a') as f:
            f.write('\n')
            f.write(tab.make_recipe())

        with open('total_payments.txt', 'a') as f:
            f.writelines(tab_name +' '+ unicode(payed)+'\n')
        self.cash_register.cash += payed

        self.tabs.pop(tab_name)
        if tab_name == 'Bar':
            self.create_tab('Bar')
            self.current_tab = self.tabs['Bar']


if __name__ == '__main__':
    c = Controller()
    c.create_tab('Till')
    c.add_to_tab('Till', c.inv[0])
    c.tabs['Till'].pprint()
    c.pay_tab('Till')




