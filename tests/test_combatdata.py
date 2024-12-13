#test_combatmodel.py

from lib.combatdata import(
    CombatData,
)

from sqlalchemy import (
    delete        as sa_delete,
    insert        as sa_insert,
    update        as sa_update,
)

from unittest import(
    TestCase,
)

class TestCombatData(TestCase):
    @classmethod
    def setUpClass(self):
        self.data = CombatData()
        table = self.data.db.get_table_definition('Combatant')
        
        # disable all active Combatants (take all existing good combatants offline)
        stmt = sa_update(table).values(isactive = False)
        with self.data.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        
        # delete all test Combatants
        stmt = sa_delete(table).where(table.c.seq >= 99)
        with self.data.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

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
        with self.data.db.engine.connect() as conn:
            for combatant in combatants:
                combattype = combatant['CombatType']
                abbr = combatant['Abbr']
                seq = combatant['seq']
                group = combatant['group']
                hpmax = combatant['hpmax']
                hp = combatant['hp']
                attackmodifier = combatant['attackmodifier']
                defensemodifier = combatant['defensemodifier']
                stmt: str = sa_insert(table).values(
                    CombatType      = combattype,
                    Abbr            = abbr,
                    seq             = seq,
                    group           = group,
                    hpmax           = hpmax,
                    hp              = hp,
                    attackmodifier  = attackmodifier,
                    defensemodifier = defensemodifier,
                )

                conn.execute(stmt)
                conn.commit()

    @classmethod
    def tearDownClass(self):
        self.data = CombatData()
        combatant_table = self.data.db.get_table_definition('Combatant')
        log_table = self.data.db.get_table_definition('Log')
        
        # delete all test Combatants
        stmt = sa_delete(combatant_table).where(combatant_table.c.seq >= 99)
        with self.data.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

        # delete all test Logs
        stmt = sa_delete(log_table).where(log_table.c.encounter == 9999999)
        with self.data.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        
        # enable all active Combantants (place all existing good combatants online)
        stmt = sa_update(combatant_table).values(isactive = True)
        with self.data.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        
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
        self.data.log_initiative(bignumber, bignumber, 'TEST', 'ALIEL', 99, 'TEST', bignumber, bignumber, bignumber)
    
    def test_update_combatant_hit_points(self):
        self.data.update_combatant_hit_points('ALIEL', 99, 99, 99)
        
    def test_delete_dead_foes(self):
        self.data.update_combatant_hit_points('ANTG', 1, 99, 0)
        self.data.delete_dead_foes()
