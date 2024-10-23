#test_combatmodel.py

from lib.combatdata import(
    CombatData,
)

from unittest import(
    TestCase,
)

class TestCombatData(TestCase):
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

        # delete all test Logs
        sql = "delete from [Log] where [encounter] = 9999999"
        self.data_cursor.execute(sql)
        self.data_cursor.commit()

        # enable all active Combantants (place all existing good combatants online)
        sql = "update [Combatant] set [isactive] = True"
        self.data_cursor.execute(sql)
        self.data_cursor.commit()
        
    # def setUp(self):
    #     self.combatdata = CombatData()
    #     self.combatdata_cursor = self.combatdata.db.cursor

    def test_combatdata(self):
        self.assertIsInstance(self.data, CombatData)

    def test_load_combatants(self):
        self.data.load_combatants()
        self.assertEqual(type(self.data.combatants), type(dict()))
        
    def test_load_participants(self):
        self.data.load_participants()
        self.assertEqual(type(self.data.participants), type(dict()))
        
    def test_load_saving_throws(self):
        self.data.load_saving_throws()
        self.assertEqual(type(self.data.savingthrows), type(dict()))

    def test_log_action(self):
        bignumber = 9999999
        self.data.log_action(bignumber, bignumber, 'TEST', 'ALIEL', 99, 'TEST', bignumber, bignumber, 'TEST', 'TEST', bignumber, 'TEST', bignumber, bignumber, bignumber, bignumber, bignumber, bignumber, 'TEST LOG ACTION')

    def test_log_initiative(self):
        bignumber = 9999999
        self.data.log_initiative(bignumber, bignumber, 'TEST', 'ALIEL', 99, 'TEST', bignumber)
    
    def test_update_combatant_hit_points(self):
        self.data.update_combatant_hit_points('ALIEL', 99, 99, 99)
