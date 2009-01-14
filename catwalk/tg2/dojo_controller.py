"""
Dojo Catwalk Module

A Dojo implementation for Catwalk

Classes:
Name                               Description
DojoCatwalk

Copywrite (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from catwalk.tg2.controller import Catwalk,  CatwalkModelController
from sprox.dojo.fillerbase import DojoTableFiller
from sprox.dojo.tablebase import DojoTableBase

class DojoCatwalkModelController(CatwalkModelController):
    table_base_type       = DojoTableBase
    table_filler_type     = DojoTableFiller
    get_action            = '.json'

    
class DojoCatwalk(Catwalk):
    catwalkModelControllerType = DojoCatwalkModelController
    