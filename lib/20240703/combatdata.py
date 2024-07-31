#combatdata.py

import pyodbc as py1

class CombatData():
    participant_data = {}

    def __init__(self):
        """connect to database"""
        connect_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\users\jkraxberger\pyproj\pvt\mm\meleemanager.accdb'
        self.conn = py1.connect(connect_string)
        self.load_participants()
    
    def load_participants(self):
        """load participants from database into dictionary"""
        cursor = self.conn.cursor()
    
        sql = "select * from Participant" # where abbr in ( 'ALIEL', 'DORAN')"
        cursor.execute(sql)

        data_dict = {}
        columns = [description[0] for description in cursor.description]
        
        for row in cursor.fetchall():
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
                
            data_dict[row[0]] = row_dict
            
        self.participant_data = data_dict

    def load_combatants(self):
        """load encounter combatants"""
        cursor = self.conn.cursor()
    
        sql = "select [Abbr], [combattype], [seq], switch([combattype] = 'FRIEND', 'a0', [combattype] = 'FOE', 'o0') as [group] from [Combatant] where [isactive] = True" # where abbr in ( 'ALIEL', 'DORAN')"
        cursor.execute(sql)
            
        data_dict = {}
        columns = [description[0] for description in cursor.description]
        
        for row in cursor.fetchall():
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
                
            data_dict[row.Abbr + str(row.seq)] = row_dict
            
        return data_dict

    def update_hp(self, Abbr, seq, hp):
        cursor = self.conn.cursor()
        sql = "update [Combatant] set [hp] = "+str(hp)+" where [Abbr] = '"+Abbr+"' and seq = "+str(seq)
        cursor.execute(sql)
        cursor.commit()

    def delete_dead_foes(self):
        cursor = self.conn.cursor()
        sql = "delete from [Combatant] where [CombatType] = 'FOE' and [hp] <= 0"
        cursor.execute(sql)
        cursor.commit()
        
    def get_participant(self, abbr):
        return self.participant_data.get(abbr)
    
    def log_initiative(self, encounter: int, round: int, type: str, Abbr: str, seq: int, group:str, initiative: int):
        self.log_action(encounter, round, type, Abbr, seq, group, initiative, 0, 'N/A', 'N/A', 0, 'N/A', 0, 0, 0, 0, 0, 0, 'initiative')
        
    def log_action(self, encounter: int, round: int, Attacker_type: str, Attacker_Abbr: str, Attacker_seq: int, Attacker_group:str, Attacker_initiative: int, Attacker_attack_number: int, Defender_type: str, Defender_Abbr: str, Defender_seq: int, Defender_group: str, Defender_initiative: int, Defender_hp_original: int, Defender_hp_start: int, Defender_damage: int, xp_total: int, xp_earned: int, notes: str):
        """log actions to database log table"""
        cursor = self.conn.cursor()
        sql = "insert into [Log] ([encounter], [round], [Attacker_type], [Attacker_Abbr], [Attacker_seq], [Attacker_group], [Attacker_initiative], [Attacker_attack_number], [Defender_type], [Defender_Abbr], [Defender_seq], [Defender_group], [Defender_initiative], [Defender_hp_original], [Defender_hp_start], [Defender_damage], [xp_total], [xp_earned], [notes] ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )"
        cursor.execute(sql, [encounter, round, Attacker_type, Attacker_Abbr, Attacker_seq, Attacker_group, Attacker_initiative, Attacker_attack_number, Defender_type, Defender_Abbr, Defender_seq, Defender_group, Defender_initiative, Defender_hp_original, Defender_hp_start, Defender_damage, xp_total, xp_earned, notes])
        cursor.commit()
        
    def close(self):
        """close database connection"""
        self.conn.close()
