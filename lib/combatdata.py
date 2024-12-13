#combatdata.py

import configparser as cp1
import lib.sqldb_access as db1

CONFIG_FILE = r'C:\users\jkraxberger\pyproj\github\mm\config.ini'

class CombatData():
    def __init__(self):
        # get database reference
        config = cp1.ConfigParser()
        config.read(CONFIG_FILE)
        connect_string = config['Database']['access_file']
        
        # connect to database
        self.db = db1.SQLDB_Access(connect_string)

    def close(self) -> None:
        """close database connection"""
        self.db.close()

    def delete_dead_foes(self) -> None:
        """delete dead foe combatants"""
        table = self.db.get_table_definition('Combatant')
        stmt = db1.sa_delete(table).where(table.c.CombatType == 'FOE' and table.c.hp <= 0)
        with self.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def load_sql(self, table_name:str) -> dict:
        """load sql data into a dictionary"""

        table = self.db.get_table_definition(table_name)
        data_dict = {}
        
        # Query the data and load into a dictionary
        with self.db.engine.connect() as conn:
            if table_name == 'Combatant':
                results = conn.execute(db1.sa_select(table).where(table.c.isactive == True))   # select all rows from table
            else:
                results = conn.execute(db1.sa_select(table))   # select all rows from table
            
            # Iterate over results and populate the dictionary
            for row in results:
                row_dict = dict(row._mapping)   # build dictionary keys using row columns
                if table_name == 'Combatant':
                    data_dict[row.Abbr + str(row.seq)] = row_dict
                elif table_name == 'SavingThrow':
                    data_dict[str(row.ClassType) + '-' + str(row.Level)] = row_dict
                elif table_name == 'Participant':
                    data_dict[row.Abbr] = row_dict
    
        return data_dict        
    
    def load_combatants(self) -> None:
        """load encounter combatants"""
        self.combatants: dict = self.load_sql('Combatant')

    def load_participants(self) -> None:
        """load participants from database into dictionary"""
        self.participants: dict = self.load_sql('Participant')

    def load_saving_throws(self) -> None:
        """load saving throws from database into dictionary"""
        self.savingthrows: dict = self.load_sql('SavingThrow')

    def log_action(self, encounter: int, round: int, Attacker_type: str, Attacker_Abbr: str, Attacker_seq: int, Attacker_group:str, Attacker_initiative: int, Attacker_attack_number: int, Defender_type: str, Defender_Abbr: str, Defender_seq: int, Defender_group: str, Defender_initiative: int, Defender_hp_max: int, Defender_hp: int, Defender_damage: int, xp_total: int, xp_earned: int, notes: str) -> None:
        """insert action values into database log table"""
        table = self.db.get_table_definition('Log')
        stmt: str = db1.sa_insert(table).values(
            encounter              = encounter, 
            round                  = round, 
            Attacker_type          = Attacker_type, 
            Attacker_Abbr          = Attacker_Abbr,
            Attacker_seq           = Attacker_seq,
            Attacker_group         = Attacker_group,
            Attacker_initiative    = Attacker_initiative,
            Attacker_attack_number = Attacker_attack_number,
            Defender_type          = Defender_type,
            Defender_Abbr          = Defender_Abbr,
            Defender_seq           = Defender_seq,
            Defender_group         = Defender_group,
            Defender_initiative    = Defender_initiative,
            Defender_hp_max        = Defender_hp_max,
            Defender_hp            = Defender_hp,
            Defender_damage        = Defender_damage,
            xp_total               = xp_total,
            xp_earned              = xp_earned,
            notes                  = notes
        )

        with self.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        
    def log_initiative(self, encounter: int, round: int, type: str, Abbr: str, seq: int, group:str, initiative: int, hp_original: int, hp: int) -> None:
        """insert initiative values into database log table"""
        self.log_action(encounter, round, type, Abbr, seq, group, initiative, 0, 'N/A', 'N/A', 0, 'N/A', 0, hp_original, hp, 0, 0, 0, 'initiative')

    def update_combatant_hit_points(self, Abbr: str, seq: int, hpmax: int, hp: int) -> None:
        """update combatant hit points"""
        table = self.db.get_table_definition('Combatant')
        stmt = db1.sa_update(table).where(table.c.Abbr == Abbr and table.c.seq == seq).values(hp = hp, hpmax = hpmax)
        with self.db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
