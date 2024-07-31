#test_combatant.py

from lib.combatant import(
    Character,
    ClassType,
    Combatant,
    CombatantType,
    CombatType,
    Monster,
)
import unittest

class TestCombatant(unittest.TestCase):
    def test_main(self):
        fighter1 = Combatant("ERIC", None, "Eric", CombatType.FRIEND, CombatantType.NPC, "fighter", '11', 3.2, 6, -1, 0, 0, 'pf', 50, False)
        self.assertIsInstance(fighter1, Combatant)
        self.assertEqual('ERIC1', fighter1.abbrseq)
        self.assertIn("fighter", fighter1.classtype)
        self.assertEqual("Eric", fighter1.name)
        self.assertIn('11', fighter1.level)
        self.assertEqual(50, fighter1.hitpoints)
        self.assertEqual(-1, fighter1.armorclass)

        magicuser1 = Combatant("DORAN", 1, "Doran", CombatantType.PC, "magicuser", '15', 1, 16, -1, 0, 0, 'pf', 62, True)
        self.assertIsInstance(magicuser1, Combatant)
        self.assertEqual('DORAN1', magicuser1.abbrseq)
        self.assertIn("magicuser", magicuser1.classtype)
        self.assertEqual("Doran", magicuser1.name)
        self.assertIn('15', magicuser1.level)
        self.assertEqual(62, magicuser1.hitpoints)
        self.assertEqual(-1, magicuser1.armorclass)
        
        magicuserassassin1 = Character("Thab", CombatantType.PC, "magicuser,assassin", '3,2', 1, 16, 5, 0, 0, 'pf', 20, True)
        self.assertIsInstance(magicuserassassin1, Character)
        self.assertEqual('THAB1', magicuserassassin1.abbrseq)
        self.assertIn("assassin", magicuserassassin1.classtype)
        self.assertEqual("Thab", magicuserassassin1.name)
        self.assertIn('2', magicuserassassin1.level)
        self.assertEqual(20, magicuserassassin1.hitpoints)
        self.assertEqual(5, magicuserassassin1.armorclass)
    
        monster1 = Monster("ANTG", 2, "Ant, Giant", CombatType.FOE, CombatantType.M, ClassType.monster, 1, 16, 3, 2, 8, "df", 16, False),
        self.assertIsInstance(monster1, Monster)
        self.assertIn("assassin", monster1.classtype)
        self.assertEqual("Thab", monster1.name)
        self.assertIn('2', monster1.level)
        self.assertEqual(16, monster1.hitpoints)
        self.assertEqual(3, monster1.armorclass)
    
