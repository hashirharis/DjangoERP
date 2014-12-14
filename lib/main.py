__author__ = 'Yussuf'
import os
from lib.narta.codecs import GenericReader
from lib.narta.exchanger import nartaExchanger

order = 'MUR1-8592A1'
#order = 'CLC4-679A1'

os.chdir(os.path.dirname(__file__))
f = open('./examples/%s.po' % order, 'r')
print GenericReader(f.read()).mapped

os.chdir(os.path.dirname(__file__))
f = open('./examples/%s.inv' % order, 'r')
print GenericReader(f.read()).mapped
