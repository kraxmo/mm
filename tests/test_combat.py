#test_combat.py

import lib.combat as c
import lib.combatant as ct
import unittest

class TestCombat(unittest.TestCase):
    def test_encounter(self):
        encounter = c.Encounter()
        self.assertIsInstance(encounter, c.Encounter)
        
    def test_round(self):
        fighter1           = ct.Combatant("Eric" , ct.CombatantType.PC , "fighter"           , '11' , 3.2,  6, -1, 0, 0, 'pf', 50, False)
        fighter2           = ct.Combatant("Aliel", ct.CombatantType.PC , "fighter"           , '13' , 2  , 10, -1, 0, 0, 'pf', 60, True)
        magicuser1         = ct.Combatant("Doran", ct.CombatantType.PC , "magicuser"         , '15' , 1  , 16, -1, 0, 0, 'pf', 62, True)
        magicuserassassin1 = ct.Combatant("Thab" , ct.CombatantType.NPC, "magicuser,assassin", '3,2', 1  , 16,  5, 0, 0, 'pf', 20, True)
        attackers = [fighter1, magicuser1]
        defenders = [fighter2, magicuserassassin1]
        round = c.Round(attackers, defenders)
        self.assertIsInstance(round, c.Round)
        
    def test_die(self):
        self.assertGreaterEqual(4, c.die(4))
        self.assertGreaterEqual(6, c.die(4, 2))
    
    def test_dice(self):
        self.assertGreaterEqual(8, c.dice(2,4))
        self.assertGreaterEqual(10, c.dice(2,4,2))