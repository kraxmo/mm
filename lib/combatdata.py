#combatdata.py

from datetime import datetime
import configparser as cp1
import lib.sqldb_access_odbc as db_odbc
import lib.sqldb_access_sqlalchemy_core as db_sa_core
import lib.sqldb_access_sqlalchemy_orm as db_sa_orm
from sqlalchemy import (
    delete           as sa_delete,
    insert           as sa_insert,
    select           as sa_select,
    update           as sa_update,
    Table            as sa_Table,
)

CONFIG_FILE = r'C:\users\jkraxberger\pyproj\github\mm\config.ini'
DATABASE_CONNECTOR = ['pyodbc', 'sqlalchemy_core', 'sqlalchemy_orm']

class CombatData():
    def __init__(self):
        # get database reference
        config = cp1.ConfigParser()
        config.read(CONFIG_FILE)
        config_key = 'Database'
        connect_string     = config[config_key]['access_file']
        database_connector = config[config_key]['database_connector']
        echo_sql           = config[config_key].getboolean('echo_sql')

        self.is_odbc = False
        self.is_core = False
        self.is_orm  = False        
        if database_connector in DATABASE_CONNECTOR:
            if database_connector == 'pyodbc':
                self.db      = db_odbc.SQLDB_Access_ODBC(connect_string)
                self.is_odbc = True
            elif database_connector == 'sqlalchemy_core':
                self.db      = db_sa_core.SQLDB_Access_SQLAlchemy(connect_string, echo_sql)
                self.is_core = True
            elif database_connector == 'sqlalchemy_orm':
                self.db      = db_sa_orm.SQLDB_Access_SQLAlchemy_ORM(connect_string, echo_sql)
                self.is_orm  = True
        else:
            raise Exception(f"Invalid database connector: not in {''.join(DATABASE_CONNECTOR)}")
    
    def close(self) -> None:
        """close database connection"""
        self.db.close()

    def delete_dead_foes(self) -> None:
        """delete dead foe combatants"""
        if self.is_odbc:
            self.db.cursor.execute("delete from [Combatant] where [CombatType] = 'FOE' and [hp] <= 0")
            self.db.cursor.commit()
        else:
            combatant = self.db.get_table_definition('Combatant')
            if self.is_orm:
                if (self.db.session.query(combatant).filter(combatant.CombatType == 'FOE', combatant.hp <= 0).delete()):
                    self.db.session.commit()
            elif self.is_core:
                stmt = sa_delete(combatant).where(combatant.c.CombatType == 'FOE' and combatant.c.hp <= 0)
                with self.db.engine.connect() as conn:
                    conn.execute(stmt)
                    conn.commit()
            else:
                raise Exception(f"Invalid database connector: not in {''.join(DATABASE_CONNECTOR)}")

    def load_sql(self, table_name:str) -> dict:
        """load sql data into a dictionary
        
        args:
            table_name: name of table to load data from
        
        return: dictionary of data
        """
        data_dict = {}
        if self.is_odbc:    # Query the data by connector and load into a dictionary
            self.db.cursor.execute(f"select * from {table_name}")
            columns = [description[0] for description in self.db.cursor.description]
            for row in self.db.cursor.fetchall():
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]

                if table_name == 'Combatant':
                    data_dict[row.Abbr + str(row.seq)] = row_dict
                elif table_name == 'SavingThrow':
                    data_dict[str(row.ClassType) + '-' + str(row.Level)] = row_dict
                elif table_name == 'Participant':
                    data_dict[row[0]] = row_dict
        else:
            table = self.db.get_table_definition(table_name)
            if self.is_orm:
                if table_name == 'Combatant':
                    results = self.db.session.query(table).filter(table.isactive == True).all()      # select filtered rows from table
                else:
                    results = self.db.session.query(table).all()                                     # select all rows from table

                for row in results:                 # Iterate over results and populate the dictionary
                    row_dict = row.__dict__         # build dictionary keys using row columns
                    if table_name == 'Combatant':
                        data_dict[row.Abbr + str(row.seq)] = row_dict
                    elif table_name == 'SavingThrow':
                        data_dict[str(row.ClassType) + '-' + str(row.Level)] = row_dict
                    elif table_name == 'Participant':
                        data_dict[row.Abbr] = row_dict
            elif self.is_core:
                results = None
                with self.db.engine.connect() as conn:
                    if table_name == 'Combatant':
                        results = conn.execute(sa_select(table).where(table.c.isactive == True))   # select filtered rows from table
                    else:
                        results = conn.execute(sa_select(table))                                   # select filtered rows from table
                        
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
        
        if self.is_odbc:
            sql: str = "insert into [Log] ([encounter], [round], [Attacker_type], [Attacker_Abbr], [Attacker_seq], [Attacker_group], [Attacker_initiative], [Attacker_attack_number], [Defender_type], [Defender_Abbr], [Defender_seq], [Defender_group], [Defender_initiative], [Defender_hp_max], [Defender_hp], [Defender_damage], [xp_total], [xp_earned], [notes] ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )"
            self.db.cursor.execute(sql, [encounter, round, Attacker_type, Attacker_Abbr, Attacker_seq, Attacker_group, Attacker_initiative, Attacker_attack_number, Defender_type, Defender_Abbr, Defender_seq, Defender_group, Defender_initiative, Defender_hp_max, Defender_hp, Defender_damage, xp_total, xp_earned, notes])
            self.db.cursor.commit()
        else:
            table = self.db.get_table_definition('Log')
            if self.is_orm:
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
            elif self.is_core:
                stmt: str = sa_insert(table).values(
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
        if self.is_odbc:
            sql: str = f"update [Combatant] set [hp] = {hp}, [hpmax] = {hpmax} where [CombatType] = '{combattype}' and [Abbr] = '{abbr}' and seq = {seq}"
            self.db.cursor.execute(sql)
            self.db.cursor.commit()
        else:
            table = self.db.get_table_definition('Combatant')
            if self.is_orm:
                self.db.session.query(table).filter(table.CombatType == combattype, table.Abbr == abbr, table.seq == seq).update({table.hpmax: hpmax, table.hp: hp})
                self.db.session.commit()
            elif self.is_core:
                stmt = sa_update(table).where(table.c.CombatType == combattype, table.c.Abbr == abbr, table.c.seq == seq).values(hp = hp, hpmax = hpmax)
                with self.db.engine.connect() as conn:
                    conn.execute(stmt)
                    conn.commit()
