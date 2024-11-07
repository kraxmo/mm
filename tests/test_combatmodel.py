#test_combatmodel.py

from lib.combatmodel import(
    Combatant,
    Encounter,
)

from lib.combatdata import(
    CombatData,
)

from unittest import(
    TestCase,
)
class TestCombatModel(TestCase):
    @classmethod
    def setUpClass(self):
        self.data = CombatData()
        self.data_cursor = self.data.db.cursor
        
        # disable all active Combantants (take all existing good combatants offline)
        sql = "update [Combatant] set [isactive] = False"
        self.data_cursor.execute(sql)
        self.data_cursor.commit()
        
        # delete all test Combatants
        sql = "delete from [Combatant] where [seq] >= 99"
        self.data_cursor.execute(sql)
        self.data_cursor.commit()

        # define test combatants
        combatants = [
            {'CombatType': 'FOE',    'Abbr': 'AAA_DM',  'seq':  '99', 'group': 'D9', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FOE',    'Abbr': 'ANTG',    'seq':  '99', 'group': 'O1', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FOE',    'Abbr': 'ANTG',    'seq': '100', 'group': 'O1', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FOE',    'Abbr': 'ANTG',    'seq': '101', 'group': 'O1', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FOE',    'Abbr': 'APEC',    'seq':  '99', 'group': 'O1', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FOE',    'Abbr': 'DRREDAD', 'seq':  '99', 'group': 'O1', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FRIEND', 'Abbr': 'ALIEL',   'seq':  '99', 'group': 'A0', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FRIEND', 'Abbr': 'DORAN',   'seq':  '99', 'group': 'A0', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FRIEND', 'Abbr': 'ERIC',    'seq':  '99', 'group': 'A0', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
            {'CombatType': 'FRIEND', 'Abbr': 'THAB',    'seq':  '99', 'group': 'A0', 'hpmax': '0', 'hp': '0', 'attackmodifier': '0', 'defensemodifier': '0'},
        ]

        # add test combatants to database
        for combatant in combatants:
            combattype = combatant['CombatType']
            abbr = combatant['Abbr']
            seq = combatant['seq']
            group = combatant['group']
            hpmax = combatant['hpmax']
            hp = combatant['hp']
            attackmodifier = combatant['attackmodifier']
            defensemodifier = combatant['defensemodifier']
            sql = f"insert into [Combatant] ([CombatType], [Abbr], [seq], [group], [hpmax], [hp], [attackmodifier], [defensemodifier]) "
            sql += f"values ('{combattype}', '{abbr}', {int(seq)}, '{group}', {int(hpmax)}, {int(hp)}, {int(attackmodifier)}, {int(defensemodifier)})"
            self.data_cursor.execute(sql)
            self.data_cursor.commit()

    @classmethod
    def tearDownClass(self):
        self.data = CombatData()
        self.data_cursor = self.data.db.cursor
        
        # delete all test Combatants
        sql = "delete from [Combatant] where [seq] >= 99"
        self.data_cursor.execute(sql)
        self.data_cursor.commit()

        # enable all active Combantants (place all existing good combatants online)
        sql = "update [Combatant] set [isactive] = True"
        self.data_cursor.execute(sql)
        self.data_cursor.commit()
        
    def setUp(self):
        self.encounter = Encounter()
        self.encounter.load_participants()
        self.encounter.load_combatants()

    def test_encounter(self):
        self.assertIsInstance(self.encounter, Encounter)

    def test_combatant(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            with self.subTest(combatant=combatant, abbr=abbr, seq=seq):
                self.assertIsInstance(combatant, Combatant)

    def test_combatant_combattype(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            combattype = combatant.combattype
            with self.subTest(abbr=abbr, seq=seq, combattype=combattype):
                if abbr in ['ALIEL', 'ERIC', 'DORAN', 'THAB']:
                    self.assertEqual(combattype, self.encounter.COMBATTYPE_FRIEND)
                else:
                    self.assertEqual(combattype, self.encounter.COMBATTYPE_FOE)

    def test_combatant_get_level(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            level = combatant.level
            charactertype = combatant.charactertype
            with self.subTest(abbr=abbr, seq=seq, level=level, charactertype=charactertype):
                for parsed_level in level.split(','):
                    if charactertype == 'M':
                        self.assertEqual(int(parsed_level), 0)
                    else:
                        self.assertNotEqual(int(parsed_level), 0)

    def test_combatant_is_active(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            with self.subTest(abbr=abbr, seq=seq):
                self.assertFalse(combatant.is_active())

    def test_combatant_is_inactive(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            with self.subTest(abbr=abbr, seq=seq):
                self.assertTrue(combatant.is_inactive())
                
    def test_combatant_is_alive(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            with self.subTest(abbr=abbr, seq=seq):
                self.assertTrue(combatant.is_alive())
                
    def test_combatant_is_dead(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            with self.subTest(abbr=abbr, seq=seq):
                self.assertFalse(combatant.is_dead())
                
    def test_combatant_is_dungeon_master(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            classtype = combatant.classtype
            with self.subTest(abbr=abbr, seq=seq, classtype=classtype):
                if abbr == 'AAA_DM':
                    self.assertTrue(combatant.is_dungeon_master())
                else:
                    self.assertFalse(combatant.is_dungeon_master())

    def test_combatant_is_monster(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            classtype = combatant.classtype
            with self.subTest(abbr=abbr, seq=seq, classtype=classtype):
                if abbr in ['AAA_DM', 'ANTG', 'APEC', 'DRREDAD']:
                    self.assertTrue(combatant.is_monster())
                else:
                    self.assertFalse(combatant.is_monster())

    def test_combatant_is_non_player_character(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            classtype = combatant.classtype
            with self.subTest(abbr=abbr, seq=seq, classtype=classtype):
                if abbr in ['ERIC', 'THAB']:
                    self.assertTrue(combatant.is_non_player_character())
                else:
                    self.assertFalse(combatant.is_non_player_character())

    def test_combatant_is_player_character(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            classtype = combatant.classtype
            with self.subTest(abbr=abbr, seq=seq, classtype=classtype):
                if abbr in ['ALIEL', 'DORAN']:
                    self.assertTrue(combatant.is_player_character())
                else:
                    self.assertFalse(combatant.is_player_character())

    def test_combatant_is_unconscious(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            with self.subTest(abbr=abbr, seq=seq):
                self.assertFalse(combatant.is_unconscious())
                
    def test_combatant_is_spellcaster(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            classtype = combatant.classtype
            with self.subTest(abbr=abbr, seq=seq, classtype=classtype):
                if abbr in ['AAA_DM', 'DORAN', 'THAB']:
                    self.assertTrue(combatant.is_spellcaster())
                else:
                    self.assertFalse(combatant.is_spellcaster())

    def test_count_combatants_friends(self):
        friends = self.encounter.count_combatants('FRIEND')
        self.assertEqual(friends, 4)

    def test_count_combatants_foes(self):
        foes = self.encounter.count_combatants('FOE')
        self.assertEqual(foes, 5)

    def test_count_available_combatants(self):
        self.encounter.friend_count = 0
        self.encounter.foe_count = 0
        self.encounter.count_available_combatants()
        self.assertEqual(self.encounter.friend_count, 4)
        self.assertEqual(self.encounter.foe_count, 5)

    def test_find_combatant_known(self):
        for combatant in self.encounter.combatants:
            abbr = combatant.abbr
            seq  = combatant.seq
            abbrseq = abbr+str(seq)
            with self.subTest(abbrseq=abbrseq):
                self.assertIsNotNone(self.encounter.find_combatant(abbrseq))

    def test_find_combatant_unknown(self):
        for combatant in self.encounter.combatants:
            abbr = 'BIF'
            seq  = '99'
            abbrseq = abbr+str(seq)
            with self.subTest(abbrseq=abbrseq):
                self.assertIsNone(self.encounter.find_combatant(abbrseq))
