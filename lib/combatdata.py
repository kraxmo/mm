#combatdata.py

import pyodbc as py1
import lib.sqldb_access as db1

class CombatData():
    def __init__(self):
        """connect to database"""
        self.db = db1.SQLDB_Access(r'C:\users\jkraxberger\pyproj\pvt\mm\meleemanager.accdb')
    
    def close(self) -> None:
        """close database connection"""
        self.db.close()

    def delete_dead_foes(self) -> None:
        """delete dead foe combatants"""
        sql = "delete from [Combatant] where [CombatType] = 'FOE' and [hp] <= 0"
        self.db.cursor.execute(sql)
        self.db.cursor.commit()
        
    def load_sql(self, sql:str, tabletype:str) -> dict:
        """load sql data into a dictionary"""
        self.db.cursor.execute(sql)
        data_dict = {}
        columns = [description[0] for description in self.db.cursor.description]
        for row in self.db.cursor.fetchall():
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]

            if tabletype == 'combatants':
                data_dict[row.Abbr + str(row.seq)] = row_dict
            elif tabletype == 'saving throws':
                data_dict[str(row.ClassType) + '-' + str(row.Level)] = row_dict
            elif tabletype == 'participants':
                data_dict[row[0]] = row_dict
            else:
                raise Exception
    
        return data_dict        
    
    def load_combatants(self) -> None:
        """load encounter combatants"""
        sql: str = "select [Abbr], [combattype], [seq], [group], [hpmax], [hp], [attackmodifier], [defensemodifier] from [Combatant] where [isactive] = True"
        self.combatants: dict = self.load_sql(sql, 'combatants')

    def load_participants(self) -> None:
        """load participants from database into dictionary"""
        sql: str = "select * from Participant"
        self.participants: dict = self.load_sql(sql, 'participants')

    def load_saving_throws(self) -> None:
        """load saving throws from database into dictionary"""
        sql: str = "select * from SavingThrow"
        self.savingthrows: dict = self.load_sql(sql, 'saving throws')

    def log_action(self, encounter: int, round: int, Attacker_type: str, Attacker_Abbr: str, Attacker_seq: int, Attacker_group:str, Attacker_initiative: int, Attacker_attack_number: int, Defender_type: str, Defender_Abbr: str, Defender_seq: int, Defender_group: str, Defender_initiative: int, Defender_hp_max: int, Defender_hp: int, Defender_damage: int, xp_total: int, xp_earned: int, notes: str) -> None:
        """log actions to database log table"""
        sql: str = "insert into [Log] ([encounter], [round], [Attacker_type], [Attacker_Abbr], [Attacker_seq], [Attacker_group], [Attacker_initiative], [Attacker_attack_number], [Defender_type], [Defender_Abbr], [Defender_seq], [Defender_group], [Defender_initiative], [Defender_hp_max], [Defender_hp], [Defender_damage], [xp_total], [xp_earned], [notes] ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )"
        self.db.cursor.execute(sql, [encounter, round, Attacker_type, Attacker_Abbr, Attacker_seq, Attacker_group, Attacker_initiative, Attacker_attack_number, Defender_type, Defender_Abbr, Defender_seq, Defender_group, Defender_initiative, Defender_hp_max, Defender_hp, Defender_damage, xp_total, xp_earned, notes])
        self.db.cursor.commit()
        
    def log_initiative(self, encounter: int, round: int, type: str, Abbr: str, seq: int, group:str, initiative: int, hp_original: int, hp: int) -> None:
        """log initiative to database log table"""
        self.log_action(encounter, round, type, Abbr, seq, group, initiative, 0, 'N/A', 'N/A', 0, 'N/A', 0, hp_original, hp, 0, 0, 0, 'initiative')
        
    def update_combatant_hit_points(self, Abbr: str, seq: int, hpmax: int, hp: int) -> None:
        """update combatant hit points"""
        sql: str = "update [Combatant] set [hp] = "+str(hp)+", [hpmax] = "+str(hpmax)+" where [Abbr] = '"+Abbr+"' and seq = "+str(seq)
        self.db.cursor.execute(sql)
        self.db.cursor.commit()
