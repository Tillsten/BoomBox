# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 16:01:31 2013

@author: Tillsten
"""



from __future__ import print_function
from boom_model import *

inv = """Wasser 0,5l| 1.00|pics\\wasser.png
Apfelschorle 0,5l| 1.00|pics\\apfelschrole.png
Kaffee| 1.00|pics\\kaffee.png
Tee| 1.00|pics\\tee.png
Cola 0,5l| 1.50|pics\\cola.png
Energy 0,3l| 1.30|pics\\energy.png
Club Mate 0,5l| 1.50|pics\\club_mate.png
Sternburg Export 0,5l| 1.20|pics\\sternburg.png
Radler | 1.20|pics\\radler.png
Becks 0,33l| 1.50|pics\\becks.png
"""
list_it = []
for line in inv.splitlines():
    print(line.split('|'))
    list_it.append(Item(*line.split('|')))
    print(list_it[-1].image_path)

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
            f.writelines(tab_name +' '+ str(payed)+'\n')
        self.cash_register.cash += payed
        self.tabs.pop(tab_name)


if __name__ == '__main__':
    c = Controller()
    c.create_tab('Till')
    c.add_to_tab('Till', c.inv[0])
    c.tabs['Till'].pprint()
    c.pay_tab('Till')




