#rule

import random as r1
from combatdata import CombatData

def die(sides, modifier = 0):
    """calculate random die roll based on die sides and modifier"""
    return r1.randint(1, sides) + modifier

def dice(number, sides, diemodifier = 0, rollmodifier = 0):
    """calculate random dice roll based on die sides and modifiers"""
    value = 0
    for _ in range(0, number):
        value += die(sides, diemodifier)
        
    return value + rollmodifier

class Rule():
    def __init__(self, type, condition, key, value, modifier, durationtype = 'ALL', duration = 0, function = ''):
        self.type = type
        self.key = key
        self.condition = condition
        self.value = value
        self.modifier = modifier
        self.durationtype = durationtype
        self.duration = duration
        self.function = function

class Participant:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.hp = self.calculate_hitpoints( self.HitDiceTypeCode, self.HitDie, self.HitDice, self.HitDiceMin, self.HitDiceMax, self.HitDiceModifier, self.HitDieValue, self.HitPointStart, self.HitPointMin, self.HitPointMax )
        
    def calculate_hitpoints(self, hitdicetypecode, hitdie, hitdice, hitdicemin, hitdicemax, hitdicemodifier, hitdievalue, hitpointstart, hitpointmin, hitpointmax):
        hitpoints = -999
        variablerange = hitpointmax - hitpointmin + 1

        if hitdicetypecode in [ 'DF', 'DFPF', 'DFPV']:
            if hitdievalue == 0:
                hitpoints = dice(hitdice, hitdie, hitdicemodifier, 0)
            else:
                hitpoints = hitdice * hitdievalue
                
            if hitdicetypecode == 'DFPF':
                hitpoints = hitpoints + hitpointstart
                
            if hitdicetypecode == 'DFPV':
                hitpoints = hitpoints + hitpointmin + die(variablerange, 0)
                
            return hitpoints

        if hitdicetypecode == "DV":
            if hitdievalue == 0:
                hitpoints = dice(variablerange, hitdie, hitdicemodifier, 0)
            else:
                hitpoints = variablerange * hitdievalue
            
            return hitpoints
    
        if hitdicetypecode == "PF":
            hitpoints = hitpointstart
            return hitpoints
        
        if hitdicetypecode == "PV":
            hitpoints = hitpointmin + die(variablerange, 0)

        return hitpoints        

class Combatant(Participant):
    seq = 1
    def __init__(self, type, group, initiative = 0, damage = 0, tohitmodifier = 0, **kwargs):
        super(Combatant, self).__init__(**kwargs)
        self.type = type
        self.group = group
        self.abbrseq = self.Abbr + str(self.seq)
        self.initiative = initiative
        self.damage = damage
        self.tohitmodifier = tohitmodifier
        self.seq += 1

    def roll_initiative(self, die):
        # Simulate rolling a die for initiative
        self.initiative = r1.randint(1, die)

# class CombatData():
#     @classmethod
#     def connect_db(self):
#         """Connect to database"""
#         connect_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\users\jkraxberger\pyproj\pvt\mm\meleemanager.accdb;autocommit=True'
#         return py1.connect(connect_string)
    
#     @classmethod    
#     def load_participants(self, conn):
#         """Load participants from database into dictionary"""
#         cursor = conn.cursor()
#         sql = "select * from Participant" # where abbr in ( 'ALIEL', 'DORAN')"
#         cursor.execute(sql)

#         data_dict = {}
#         columns = [description[0] for description in cursor.description]
        
#         for row in cursor.fetchall():
#             row_dict = {}
#             for i, column in enumerate(columns):
#                 row_dict[column] = row[i]
                
#             data_dict[row[0]] = row_dict
        
#         return data_dict

#     @classmethod
#     def log_action(conn, encounter, round, group, type, initiative, Abbr, seq, hp, damage, hpremaining, notes):
#         """Log actions"""
#         sql = ("insert into [Log] (encounter, round, group, type, initiative, Abbr, seq, hp, damage, hpremaining, notes) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )", [encounter, round, group, type, initiative, Abbr, seq, hp, damage, hpremaining, notes])
#         cursor = conn.cursor()
#         cursor.execute(sql)
    
def apply_rules(rules, combatants):
    """Apply rules to combatants based on predefined conditions"""
    
    print('Apply Rules:')
    for rule in rules:
        if rule['category'] == 'combat':
            if rule['condition'] == 'all':
                for combatant in combatants:
                    combatant.__dict__[rule['attribute']] += rule['modifier']
                    # print(f'- ALL RULE: combatant {combatant.Abbr} initiative {combatant.initiative}')
                    print(f"- {rule['condition']} RULE: combatant {combatant.Abbr} {rule['attribute']} {combatant.__dict__[rule['attribute']]}")

            elif rule['condition'] == 'group':
                for combatant in combatants:
                    for group in combatant.group.split(','):
                        if group in rule['affected_combatants']:
                            combatant.__dict__[rule['attribute']] += rule['modifier']
                            # print(f'- GROUP {group} RULE: combatant {combatant.Abbr} initiative {combatant.initiative}')
                            print(f"- {rule['condition']} {group} RULE: combatant {combatant.Abbr} {rule['attribute']} {combatant.__dict__[rule['attribute']]}")
            
            elif rule['condition'] == 'individual':
                for combatant in combatants:
                    if combatant.Abbr == rule['affected_combatant']:
                        combatant.__dict__[rule['attribute']] += rule['modifier']
                        # print(f'- individuals RULE: combatant {combatant.Abbr} initiative {combatant.initiative}')
                        print(f"- {rule['condition']} {group} RULE: combatant {combatant.Abbr} {rule['attribute']} {combatant.__dict__[rule['attribute']]}")

        # elif rule['category'] == 'dual':
        #     if rule['condition'] == 'group':
        #         for combatant in combatants:
        #             for group in combatant.group.split(','):
        #                 if group in rule['affected_combatants']:
        #                     combatant.__dict__[rule['attribute']] += rule['modifier']
        #                     # print(f"- GROUP {group} RULE: combatant {combatant.Abbr} {rule['attribute']} {combatant.__dict__[rule['attribute']]}")
        #                     print(f"- {rule['condition']} {group} RULE: combatant {combatant.Abbr} {rule['attribute']} {combatant.__dict__[rule['attribute']]}")

def main():
    combatdata = CombatData()
    # combatdata.participants_data = combatdata.load_participants()

    # Define Participants
    participants = [
        Participant(**combatdata.get_participant('ALIEL')),
        Participant(**combatdata.get_participant('DORAN')),
        Participant(**combatdata.get_participant('ANTG')),
    ]

    groups = [
        {'group': 'a0,a1', 'participants': [participants[0]]},
        {'group': 'a0', 'participants': [participants[1]]},
        {'group': 'o1', 'participants': [participants[2]]},
    ]

    for group in groups:
        print(f'Group: {group['group']}') 
        for participant in group['participants']:
            print(f'- {participant.Abbr}')

    combatants = [
        Combatant('friend', 'a0,a1', 0, 0, 0, **combatdata.get_participant(participants[0].Abbr)),
        Combatant('friend', 'a0', 0, 0, 0, **combatdata.get_participant(participants[1].Abbr)),
        Combatant('foe', 'o0', 0, 0, 0, **combatdata.get_participant(participants[2].Abbr)),
    ]
        
    for combatant in combatants:
        print(f'{combatant.type} group: {combatant.group} {combatant.abbrseq} {combatant.Name} hp: {combatant.hp} ac: {combatant.AC} thac0: {combatant.THAC0} init: {combatant.initiative} tohitmodifier: {combatant.tohitmodifier}')

    # Define rules
    rules = [
        # Example rule: +1 to all player attacks
        {'category': 'config', 'attribute': 'initiative', 'condition': 'die', 'value': 6999},
        # Example rule: +1 to all player attacks
        {'category': 'combat', 'attribute': 'initiative', 'condition': 'all', 'modifier': 100},
        # Example rule: -1 to all player attacks for a group
        {'category': 'combat', 'attribute': 'initiative', 'condition': 'group', 'affected_combatants': ['a0'], 'modifier': -200},
        # Example rule: -1 to one opponent's attacks
        {'category': 'combat', 'attribute': 'initiative', 'condition': 'individual', 'affected_combatant': 'ALIEL', 'modifier': -300},
        # Example rule: +1 to all player attacks for a group
        {'category': 'combat', 'attribute': 'tohitmodifier', 'condition': 'group', 'affected_combatants': ['a1'], 'modifier': 1},
    ]

    # Simulate rolling initiative for each participant
    for rule in rules:
        if rule['category'] == 'config':
            if rule['condition'] == 'die':
                initiative_die = int(rule['value'])
                exit
                
    for combatant in combatants:
        combatant.roll_initiative(initiative_die)
        print(f'- combatant {combatant.Abbr} initiative {combatant.initiative}')

    # Apply rules
    apply_rules(rules, combatants)

    # Sort participants by initiative
    combatants.sort(key=lambda x: x.initiative, reverse=True)

    # Print order of play
    print("Order of play:")
    # cursor = conn.cursor()
    for i, combatant in enumerate(combatants, 1):
        print(f"{i}. {combatant.Abbr} - Initiative: {combatant.initiative}")
        combatdata.log_action(1, 1, combatant.type, combatant.Abbr, combatant.seq, combatant.group, combatant.initiative, 'N/A', 'N/A', 0, 'N/A', 0, 0, 0, 0, 0, 'initiative')
    
    combatdata.close()

if __name__ == "__main__":
    main()

"""
Rule Types:
Category    Type    SubType     Attribute   Condition   Group1  Value1  Modifier1   Group2  Value2  Modifier2
combat        config  die         initiative  all         {}      6       0           {}      0       0
combat        attack  -           initiative  all         {}      0       1           {}      0       0
combat        attack  -           initiative  group       {a0}    0       -2          {}      0       0
combat        attack  -           initiative  individuals {Player1}   0   -3          {}      0       0
dual        attack  -           tohitmodifier group     {a0}    0       1           {o0}    0       -1
"""
