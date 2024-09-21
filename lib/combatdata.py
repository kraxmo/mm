#combatdata.py

import pyodbc as py1
import lib.sqldb_access as db1

class CombatData():
    def __init__(self):
        """connect to database"""
        self.db = db1.SQLDB_Access(r'C:\users\jkraxberger\pyproj\pvt\mm\meleemanager.accdb')
        self.load_participants()
    
    def load_participants(self) -> None:
        """load participants from database into dictionary"""
    
        sql = "select * from Participant"
        self.db.cursor.execute(sql)

        self.participants = {}
        data_dict = {}
        columns = [description[0] for description in self.db.cursor.description]
        
        for row in self.db.cursor.fetchall():
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
                
            data_dict[row[0]] = row_dict
            
        self.participants = data_dict

    def load_combatants(self) -> None:
        """load encounter combatants"""
    
        sql = "select [Abbr], [combattype], [seq], [group], [hpmax], [hp], [attackmodifier], [defensemodifier] from [Combatant] where [isactive] = True"
        self.db.cursor.execute(sql)
            
        self.combatants = {}
        data_dict = {}
        columns = [description[0] for description in self.db.cursor.description]
        
        for row in self.db.cursor.fetchall():
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
                
            data_dict[row.Abbr + str(row.seq)] = row_dict
            
        self.combatants = data_dict

    def update_combatant_hit_points(self, Abbr, seq, hpmax, hp) -> None:
        """update combatant hit points"""
        sql = "update [Combatant] set [hp] = "+str(hp)+", [hpmax] = "+str(hpmax)+" where [Abbr] = '"+Abbr+"' and seq = "+str(seq)
        self.db.cursor.execute(sql)
        self.db.cursor.commit()

    def delete_dead_foes(self) -> None:
        sql = "delete from [Combatant] where [CombatType] = 'FOE' and [hp] <= 0"
        self.db.cursor.execute(sql)
        self.db.cursor.commit()
        
    def log_initiative(self, encounter: int, round: int, type: str, Abbr: str, seq: int, group:str, initiative: int) -> None:
        self.log_action(encounter, round, type, Abbr, seq, group, initiative, 0, 'N/A', 'N/A', 0, 'N/A', 0, 0, 0, 0, 0, 0, 'initiative')
        
    def log_action(self, encounter: int, round: int, Attacker_type: str, Attacker_Abbr: str, Attacker_seq: int, Attacker_group:str, Attacker_initiative: int, Attacker_attack_number: int, Defender_type: str, Defender_Abbr: str, Defender_seq: int, Defender_group: str, Defender_initiative: int, Defender_hp_original: int, Defender_hp: int, Defender_damage: int, xp_total: int, xp_earned: int, notes: str) -> None:
        """log actions to database log table"""
        sql = "insert into [Log] ([encounter], [round], [Attacker_type], [Attacker_Abbr], [Attacker_seq], [Attacker_group], [Attacker_initiative], [Attacker_attack_number], [Defender_type], [Defender_Abbr], [Defender_seq], [Defender_group], [Defender_initiative], [Defender_hp_original], [Defender_hp], [Defender_damage], [xp_total], [xp_earned], [notes] ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )"
        self.db.cursor.execute(sql, [encounter, round, Attacker_type, Attacker_Abbr, Attacker_seq, Attacker_group, Attacker_initiative, Attacker_attack_number, Defender_type, Defender_Abbr, Defender_seq, Defender_group, Defender_initiative, Defender_hp_original, Defender_hp, Defender_damage, xp_total, xp_earned, notes])
        self.db.cursor.commit()
        
    def close(self) -> None:
        """close database connection"""
        self.db.close()
