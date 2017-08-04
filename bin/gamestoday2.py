#!/usr/bin/python
from sportstg import allgames
import sys,os

datadir = os.path.join(sys.path[0],'..','data')


displaylist = [allgames(x) for x in allcomps]
