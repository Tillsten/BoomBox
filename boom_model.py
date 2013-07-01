# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 14:07:36 2013

@author: Tillsten
"""
#import traits
from __future__ import print_function
import decimal


class Item(object):
    def __init__(self, name, price, image_path=None):
        """
        A drink or something to eat
        """
        self.name = name
        self.price = decimal.Decimal(price)
        self.image_path = image_path

class Register(object):
    def __init__(self, cash):
        self.cash = decimal.Decimal(cash)

Kasse = Register('0.00')

class Tab(object):
    """
    Represents a client, has a tab.
    """
    def __init__(self, name):
        self.name = name
        self.tab = []        
    
    def add_to_tab(self, prod):
        self.tab.append(prod)            
        
    def remove_from_tab(self, prod):
        self.tab.remove(prod)
        
    def calc_total(self):
        return self.calc_subtotal(self.tab)
        
    def calc_subtotal(self, selected_prods):
        total = decimal.Decimal('0.00')
        for i in selected_prods:
            total += i.price
        return total
        
    def pprint(self):
        for i in self.tab:
            print("{0:20} {1}".format(i.name, i.price))
        print('---------------------------')
        print("{0:20} {1}".format("TOTAL", self.calc_total()))
            



if __name__ == '__main__':
        
    ClubMate = Item('Club Mate', '1.50')
    ClubMate.image_path = 'club_mate_flaschen.png'
    Kickern = Item('Kickern', '3.00')
            
           
    Till = Tab('Till')
    Till.add_to_tab(ClubMate)
    Till.add_to_tab(ClubMate)
    Till.add_to_tab(ClubMate)
    Till.add_to_tab(Kickern)
    Till.pprint()
    #print Till.alc_total()