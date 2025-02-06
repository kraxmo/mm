#combatdata.py

from datetime import datetime
import configparser as cp1
import lib.sqldb_access as db1

CONFIG_FILE = r'C:\users\jkraxberger\pyproj\github\mm\config.ini'

class CombatData():
    def __init__(self):
        # get database reference
        config = cp1.ConfigParser()
        config.read(CONFIG_FILE)
        config_key = 'Database'
        connect_string = config[config_key]['access_file']
        uses_orm       = config[config_key].getboolean('uses_orm')
        echo_sql       = config[config_key].getboolean('echo_sql')
        
        # connect to database
        self.db = db1.SQLDB_Access(connect_string, uses_orm, echo_sql)

    def close(self) -> None:
        """close database connection"""
        self.db.close()

    def delete_dead_foes(self) -> None:
        """delete dead foe combatants"""
        combatant = self.db.get_table_definition('Combatant')
        if self.db.uses_orm:
            if (self.db.session.query(combatant).filter(combatant.CombatType == 'FOE', combatant.hp <= 0).delete()):
                self.db.session.commit()
        else:
            stmt = db1.sa_delete(combatant).where(combatant.c.CombatType == 'FOE' and combatant.c.hp <= 0)
            with self.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()

    def load_sql(self, table_name:str) -> dict:
        """load sql data into a dictionary
        
        args:
            table_name: name of table to load data from
        
        return: dictionary of data
        """
        table = self.db.get_table_definition(table_name)
        data_dict = {}
        
        # Query the data and load into a dictionary
        if self.db.uses_orm:
            if table_name == 'Combatant':
                results = self.db.session.query(table).filter(table.isactive == True).all()      # select filtered rows from table
            else:
                results = self.db.session.query(table).all()                                       # select all rows from table

            # Iterate over results and populate the dictionary
            for row in results:
                row_dict = row.__dict__         # build dictionary keys using row columns
                if table_name == 'Combatant':
                    data_dict[row.Abbr + str(row.seq)] = row_dict
                elif table_name == 'SavingThrow':
                    data_dict[str(row.ClassType) + '-' + str(row.Level)] = row_dict
                elif table_name == 'Participant':
                    data_dict[row.Abbr] = row_dict
        else:
            results = None
            with self.db.engine.connect() as conn:
                if table_name == 'Combatant':
                    results = conn.execute(db1.sa_select(table).where(table.c.isactive == True))   # select filtered rows from table
                else:
                    results = conn.execute(db1.sa_select(table))                                   # select all rows from table
                    
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
        """insert action values into database log table
        
        args:
            encounter: encounter number
            round: round number
            Attacker_type: type of attacker
            Attacker_Abbr: attacker abbreviation
            Attacker_seq: attacker sequence
            Attacker_group: attacker group
            Attacker_initiative: attacker initiative
            Attacker_attack_number: attacker attack number
            Defender_type: type of defender
            Defender_Abbr: defender abbreviation
            Defender_seq: defender sequence
            Defender_group: defender group
            Defender_initiative: defender initiative
            Defender_hp_max: defender max hit points
            Defender_hp: defender hit points
            Defender_damage: defender damage
            xp_total: total experience points
            xp_earned: experience points earned
            notes: notes
        """
        
        table = self.db.get_table_definition('Log')
        if self.db.uses_orm:
            log = table(
                logDate                = datetime.now(),
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
            self.db.session.add(log)
            self.db.session.commit()
        else:
            stmt: str = db1.sa_insert(table).values(
                logDate                = datetime.now(),
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
        """insert initiative values into database log table
        
        args:
            encounter: encounter number
            round: round number
            type: type of combatant
            Abbr: combatant abbreviation
            seq: combatant sequence
            group: combatant group
            initiative: combatant initiative
            hp_original: combatant original hit points
            hp: combatant hit points
        """
        self.log_action(encounter, round, type, Abbr, seq, group, initiative, 0, 'N/A', 'N/A', 0, 'N/A', 0, hp_original, hp, 0, 0, 0, 'initiative')

    def update_combatant_hit_points(self, combattype: str, abbr: str, seq: int, hpmax: int, hp: int) -> None:
        """update combatant hit points
        
        args:
            combattype: combatant type
            abbr: combatant abbreviation
            seq: combatant sequence
            hpmax: combatant max hit points
            hp: combatant hit points
        """
        table = self.db.get_table_definition('Combatant')
        if self.db.uses_orm:
            self.db.session.query(table).filter(table.CombatType == combattype, table.Abbr == abbr, table.seq == seq).update({table.hpmax: hpmax, table.hp: hp})
            self.db.session.commit()
        else:
            stmt = db1.sa_update(table).where(db1.sa_and(table.c.CombatType == combattype, table.c.Abbr == abbr, table.c.seq == seq)).values(hp = hp, hpmax = hpmax)
            with self.db.engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
