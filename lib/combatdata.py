#combatdata.py

class CombatData():
    def __init__(self):
        self.is_core   = False
        self.is_odbc   = False
        self.is_orm    = False        
        self.is_native = False

    def close(self) -> None:
        """close database connection"""
        self.db.close()

    def load_combatants(self) -> None:
        """load encounter combatants"""
        self.combatants: dict = self.load_sql('Combatant')

    def load_participants(self) -> None:
        """load participants from database into dictionary"""
        self.participants: dict = self.load_sql('Participant')

    def load_saving_throws(self) -> None:
        """load saving throws from database into dictionary"""
        self.savingthrows: dict = self.load_sql('SavingThrow')

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
