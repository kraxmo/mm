#test_combatmodel.py

from lib.combatdata import(
    CombatData,
)
from sqlalchemy import (
    delete        as sa_delete,
    insert        as sa_insert,
    update        as sa_update,
)
import sys
import unittest

class TestCombatData(unittest.TestCase):
    VERBOSE = False
    def identify(func):
        def wrapper(*args, **kwargs):
            if TestCombatData.VERBOSE: print(f"\nTEST: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper

    @classmethod
    def setUpClass(self):
        self.data = CombatData()
        if self.data.is_orm or self.data.is_core:
            table = self.data.db.get_table_definition('Combatant')
        
        # disable all active Combatants (take all existing good combatants offline)
        if self.data.is_odbc:
            sql: str = f"update [Combatant] set [isactive] = False"
            self.data.db.cursor.execute(sql)
            self.data.db.cursor.commit()
        elif self.data.is_orm:
            self.data.db.session.query(table).update({table.isactive: False})
            self.data.db.session.commit()
        elif self.data.is_core:
            stmt = sa_update(table).values(isactive = False)
            with self.data.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        else:
            raise Exception('Unknown database reference')
        
        # delete all test Combatants
        if self.data.is_odbc:
            self.data.db.cursor.execute("delete from [Combatant] where [CombatType] = 'FOE' and [hp] <= 0")
            self.data.db.cursor.commit()
        elif self.data.is_orm:
            self.data.db.session.query(table).filter(table.seq >= 99).delete()
            self.data.db.session.commit()
        elif self.data.is_core:
            stmt = sa_delete(table).where(table.c.seq >= 99)
            with self.data.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        else:
            raise Exception('Unknown database reference')

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
        if self.data.is_odbc:
            sql: str = "insert into [Combatant] ([CombatType], [Abbr], [seq], [group], [hpmax], [hp], [attackmodifier], [defensemodifier]) values (?, ?, ?, ?, ?, ?, ?, ?)"
            for combatant in combatants:
                self.data.db.cursor.execute(
                    sql, 
                    combatant['CombatType'], 
                    combatant['Abbr'], 
                    combatant['seq'],
                    combatant['group'],
                    combatant['hpmax'], 
                    combatant['hp'], 
                    combatant['attackmodifier'], 
                    combatant['defensemodifier'],
                )
                self.data.db.cursor.commit()
        elif self.data.is_orm:
            for combatant in combatants:
                log = table(
                    CombatType      = combatant['CombatType'],
                    Abbr            = combatant['Abbr'],
                    seq             = combatant['seq'],
                    group           = combatant['group'],
                    hpmax           = combatant['hpmax'],
                    hp              = combatant['hp'],
                    attackmodifier  = combatant['attackmodifier'],
                    defensemodifier = combatant['defensemodifier'],
                )

                self.data.db.session.add(log)
                # self.data.db.session.execute(table.insert().values(combatants))
            self.data.db.session.commit()
        elif self.data.is_core:
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
        else:
            raise Exception('Unknown database reference')

    @classmethod
    def tearDownClass(self):
        self.data = CombatData()
        if self.data.is_orm or self.data.is_core:
            combatant_table = self.data.db.get_table_definition('Combatant')
            log_table = self.data.db.get_table_definition('Log')
        
        # delete all test Combatants
        if self.data.is_odbc:
            self.data.db.cursor.execute("delete from [Combatant] where [seq] >= 99")
            self.data.db.cursor.commit()
        elif self.data.is_orm:
            self.data.db.session.query(combatant_table).filter(combatant_table.seq >= 99).delete()
            self.data.db.session.commit()
        elif self.data.is_core:
            stmt = sa_delete(combatant_table).where(combatant_table.c.seq >= 99)
            with self.data.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        else:
            raise Exception('Unknown database reference')

        # delete all test Logs
        if self.data.is_odbc:
            self.data.db.cursor.execute("delete from [Log] where encounter = 9999999")
            self.data.db.cursor.commit()
        elif self.data.is_orm:
            self.data.db.session.query(log_table).filter(log_table.encounter == 9999999).delete()
            self.data.db.session.commit()
        elif self.data.is_core:
            stmt = sa_delete(log_table).where(log_table.c.encounter == 9999999)
            with self.data.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        else:
            raise Exception('Unknown database reference')
        
        # enable all active Combantants (place all existing good combatants online)
        if self.data.is_odbc:
            sql: str = f"update [Combatant] set [isactive] = True"
            self.data.db.cursor.execute(sql)
            self.data.db.cursor.commit()
        elif self.data.is_orm:
            self.data.db.session.query(combatant_table).update({combatant_table.isactive: True})
            self.data.db.session.commit()
        elif self.data.is_core:
            stmt = sa_update(combatant_table).values(isactive = True)
            with self.data.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        else:
            raise Exception('Unknown database reference')
        
    @identify
    def test_combatdata(self):
        self.assertIsInstance(self.data, CombatData)

    @identify
    def test_load_combatants(self):
        self.data.load_combatants()
        self.assertEqual(type(self.data.combatants), type(dict()))
        
    @identify
    def test_load_participants(self):
        self.data.load_participants()
        self.assertEqual(type(self.data.participants), type(dict()))
        
    @identify
    def test_load_saving_throws(self):
        self.data.load_saving_throws()
        self.assertEqual(type(self.data.savingthrows), type(dict()))

    @identify
    def test_log_action(self):
        bignumber = 9999999
        self.data.log_action(bignumber, bignumber, 'TEST', 'ALIEL', 99, 'TEST', bignumber, bignumber, 'TEST', 'TEST', bignumber, 'TEST', bignumber, bignumber, bignumber, bignumber, bignumber, bignumber, 'TEST LOG ACTION')

    @identify
    def test_log_initiative(self):
        bignumber = 9999999
        self.data.log_initiative(bignumber, bignumber, 'TEST', 'ALIEL', 99, 'TEST', bignumber, bignumber, bignumber)
    
    @identify
    def test_update_combatant_hit_points(self):
        self.data.update_combatant_hit_points('FRIEND', 'ALIEL', 99, 99, 99)
        
    @identify
    def test_delete_dead_foes(self):
        self.data.update_combatant_hit_points('FOE', 'ANTG', 1, 99, 0)
        self.data.delete_dead_foes()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-v':   
        TestCombatData.VERBOSE = True
    else:
        TestCombatData.VERBOSE = False
        
    unittest.main()