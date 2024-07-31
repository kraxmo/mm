#combatmodel.py

from enum import Enum
from lib.dice import Dice

class CharacterType(Enum):
    """defines type of character"""
    PC = 1
    NPC = 2
    M = 3
    
    def __str__(self):
        return f'{self.name.title()}'

class ClassType(Enum):
    """defines class of PC/NPC"""
    MONSTER = 0,
    CLERIC = 1,
    DRUID = 2,
    FIGHTER = 3,
    PALADIN = 4,
    RANGER = 5,
    MAGICUSER = 6,
    ILLUSIONIST = 7,
    THIEF = 8,
    ASSASSIN = 9,
    CAVALIER = 10,
    BARBARIAN = 11,
    THIEFACROBAT = 12,
    
    def __str__(self):
        return f'{self.name.title()}'
    
class HitDiceType(Enum):
    """defines type of hit dice calculation to perform"""
    DF = 1      # Die Fixed
    DFPF = 2    # Die Fixed Points Fixed
    DFPV = 3    # Die Fixed Points Variable
    DV = 4      # Die Variable
    PF = 5      # Points Fixed
    PV = 6      # Points Variable

    def __str__(self):
        return f'{self.name.title()}'

class Participant:
    """defines partipant settings loaded from database"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Combatant(Participant):
    """defines combatants that are participants with combat settings"""
    def __init__(self, combattype, group, seq, initiative = 0, damage = 0, tohitmodifier = 0, **kwargs):
        super(Combatant, self).__init__(**kwargs)
        self.combattype = combattype
        self.group = group
        self.seq = seq
        self.abbrseq = self.Abbr + str(self.seq)
        self.initiative = initiative
        self.damage = damage
        self.tohitmodifier = tohitmodifier
        self.hp = self.calculate_hitpoints( self.HitDiceTypeCode, self.HitDie, self.HitDice, self.HitDiceMin, self.HitDiceMax, self.HitDiceModifier, self.HitDieValue, self.HitPointStart, self.HitPointMin, self.HitPointMax )
        self.hpstarting = self.hp
        self.defender_abbrseq = ''
        self.xp = self.ExperienceBase + self.ExperienceAdjustment + (self.hp * self.ExperienceHitPointMultiplier)
        if self.ExperienceAddHitPoint == True:
            self.xp += self.hp
        
        self.inactivereason = ''
            
    def calculate_hitpoints(self, hitdicetypecode, hitdie, hitdice, hitdicemin, hitdicemax, hitdicemodifier, hitdievalue, hitpointstart, hitpointmin, hitpointmax) -> int:
        hitpoints = -999
        variablehitpointrange = hitpointmax - hitpointmin + 1

        if hitdicetypecode in [ 'DF', 'DFPF', 'DFPV']:
            if hitdievalue == 0:
                hitpoints = Dice.roll_dice(hitdice, hitdie, hitdicemodifier, 0)
            else:
                hitpoints = hitdice * hitdievalue
                
            if hitdicetypecode == 'DFPF':
                hitpoints = hitpoints + hitpointstart
                
            if hitdicetypecode == 'DFPV':
                hitpoints = hitpoints + hitpointmin + Dice.roll_die(variablehitpointrange, 0)
                
            return hitpoints

        if hitdicetypecode == "DV":
            variablehitdicerange = (hitdicemin - 1) + Dice.roll_die(hitdicemax - hitdicemin + 1)
            if hitdievalue == 0:
                hitpoints = Dice.roll_dice(variablehitdicerange, hitdie, hitdicemodifier, 0)
            else:
                hitpoints = variablehitdicerange * hitdievalue
            
            return hitpoints
    
        if hitdicetypecode == "PF":
            hitpoints = hitpointstart
            return hitpoints
        
        if hitdicetypecode == "PV":
            hitpoints = hitpointmin + Dice.roll_die(variablehitpointrange, 0)

        return hitpoints

    def get_level(self, level) -> list:
        """get level of each class"""
        if level is None:
            return list('0')
        else:
            return list(l for l in level.split(','))

    def get_attacks(self, round) -> int:
        """get number of attacks per round"""
        # check for either 1 or 2 attacks per round
        if self.attacks_per_round % 2 == 0:
            attacks = self.attacks_per_round
        else:
            # Process split round attacks (such as 3 attacks every 2 rounds)
            
            # check if round is even
            if round % 2 == 0:
                # subtract 1 from attacks_per_round
                attacks = int(self.attacks_per_round) - 1
            else:
                attacks = 1
        
        return attacks

    def is_active(self) -> bool:
        return ( self.initiative >= Encounter.INITIATIVE_ACTIVE_MINIMUM ) and (self.can_attack())

    def is_inactive(self) -> bool:
        return ( self.initiative < Encounter.INITIATIVE_ACTIVE_MINIMUM )

    def take_damage(self, damage):
        """record damage taken"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def to_hit(self, hitroll, defenderarmorclass, modifier = 0) -> bool:
        """determine 'to hit' value"""
        if hitroll >= (self.THAC0 - defenderarmorclass - modifier):
            return True
        else:
            return False

    def can_attack(self) -> bool:
        """check if combatant can attack"""
        return self.hp > 0
    
    def is_alive(self) -> bool:
        """check if combatant is alive"""
        return not self.is_dead()
    
    def is_dead(self) -> bool:
        """check if combatant is dead"""
        if self.CharacterType == CharacterType.M.name:
            return self.hp <= 0
        else:
            return self.hp <= -10
    
    def is_unconscious(self) -> bool:
        """check if combatant is unconscious"""
        return -10 < self.hp <= 0
    
    def is_spellcaster(self) -> bool:
        """check if combatant could be a spell caster"""
        for classtype in self.ClassType.split(","):
            if classtype == ClassType.CLERIC.name or classtype == ClassType.DRUID.name or classtype == ClassType.MAGICUSER.name or classtype == ClassType.ILLUSIONIST.name or classtype == ClassType.RANGER.name or classtype == ClassType.PALADIN.name:
                return True
            
        return False

class Encounter():
    """Encounter container for tracking all combatant attacks by round"""

    # Constants
    INITIATIVE_DIE_MAJOR         = 6
    INITIATIVE_DIE_MINOR         = 999
    INITIATIVE_INACTIVE_MINIMUM  = 1
    INITIATIVE_INACTIVE_MAXIMUM  = 999
    INITIATIVE_ACTIVE_MINIMUM    = 1000
    INITIATIVE_ACTIVE_MAXIMUM    = 6999
    INITIATIVE_NONE              = 0
    INITIATIVE_MINIMUM           = INITIATIVE_INACTIVE_MINIMUM
    INITIATIVE_MAXIMUM           = INITIATIVE_ACTIVE_MAXIMUM
    TO_HIT_DIE                   = 20
    
    # Attributes
    friend_count = 0
    foe_count = 0
    combatant_attack_number = 1

    def __init__(self, combatdata, combatants) -> None:
        self.encounter = 1
        self.combatdata = combatdata
        self.round = 1
        self.initiative = self.INITIATIVE_ACTIVE_MAXIMUM
        self.combatants = combatants
        self.ismissileattack = True
        
    class ActionType(Enum):
        """defines type of action to be tracked"""
        ADJUSTMENT = 0
        ATTACK = 1
        SPELL = 2
        WANDERING_MONSTER_CHECK = 3
        GROUP = 4
        RELOAD_COMBATANTS = 5
        QUIT = 99

        def __str__(self):
            return f'{self.name.title()}'
        
    class CombatSpellType(Enum):
        """defines type of combat spell type"""
        NONE = 0
        INDIVIDUAL = 1
        GROUP = 2
        OTHER = 3
        
        def __str__(self):
            return f'{self.name.title()}'

    class CombatType(Enum):
        """defines type of combat combatant"""
        FRIEND = 1
        FOE = 2
        
        def __str__(self):
            return f'{self.name.title()}'

    def roll_nonplayer_initiative(self) -> int:
        """determine initiative value for non-players (Non-Player Characters [NPC] and Monsters [M])"""
        return Dice.roll_die(self.INITIATIVE_DIE_MAJOR) * 1000 + Dice.roll_die(self.INITIATIVE_DIE_MINOR)

    def sort_combatants_by_initative(self):
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)

    def check_duplicate_initiative(self):
        """check for duplicate initiative and adjust"""
        self.sort_combatants_by_initative()

        # Detect duplicate initiative and esequence
        initiative = set()
        duplicates_exist = False
        for i in range(len(self.combatants)):
            while self.combatants[i].initiative in initiative:
                self.combatants[i].initiative += 1
                if duplicates_exist == False:
                    duplicates_exist = True
                
            initiative.add(self.combatants[i].initiative)

        if duplicates_exist:
            # re-sort combatants by initiative
            self.sort_combatants_by_initative()
            
    def count_combatants(self, combattype) -> int:
        """count number of available combatants"""
        combatant_count = 0
        for combatant in self.combatants:
            if combatant.combattype == combattype.name:
                if combatant.combattype == self.CombatType.FRIEND.name:
                    if combatant.can_attack():
                        combatant_count += 1
                else:
                    if combatant.is_alive():
                        combatant_count += 1

        return combatant_count    

    def count_available_combatants(self) -> int:
        self.friend_count = self.count_combatants(self.CombatType.FRIEND)
        self.foe_count = self.count_combatants(self.CombatType.FOE)
    
    def find_next_attacker(self) -> Combatant:
        """find next available attacker"""
        for attacker in self.combatants:
            # Exclude if attacker's initiative > event's
            if attacker.initiative > self.initiative:
                continue

            elif self.friend_count == 0 or self.foe_count == 0:
                continue

            # Exclude dead attackers or unconscious attackers
            elif attacker.can_attack() == False:
                continue
                        
            # inactive attackers
            # even though they are unable to attack (due to choice, wounded, healing, spell-prep, retreating, etc.)
            # they still should be have a chance to respond and possibly change their initiative and/or inactivereason
            elif attacker.initiative < self.INITIATIVE_ACTIVE_MINIMUM:
                return attacker

            elif self.ismissileattack == True:
                if attacker.MissileAttack == False:
                    continue

            # set event initiative to attacker's
            self.initiative = attacker.initiative
            
            # return attacker
            return attacker

    def get_hit_roll(self, combatant) -> int:
        """get to hit roll"""
        if combatant.CharacterType == CharacterType.PC.name:
            to_hit_input = ''
            while to_hit_input == '':
                to_hit_input = input(f"      -- Enter 'To Hit' d{self.TO_HIT_DIE} result: ")
                if to_hit_input.isnumeric() == False:
                    print(f"         -+ 'To Hit' roll of '{to_hit_input}' is not a number.")
                    to_hit_input = ''
                    continue
                
                to_hit_roll = int(to_hit_input)
                if to_hit_roll < 1 or to_hit_roll > self.TO_HIT_DIE:
                    print(f"         -+ 'To Hit' roll must be between 1 and {self.TO_HIT_DIE}. {to_hit_roll} entered.")
                    to_hit_input = ''
                    continue

        else: # automatically roll To Hit roll
            to_hit_roll = Dice.roll_die(self.TO_HIT_DIE)
            print(f'      -- Rolled {to_hit_roll}')

        return to_hit_roll

    def calculate_xp(self, originalhp, hp, damage, xp) -> int:
        if damage > hp:
            value = hp
        else:
            value = damage
            
        returnvalue = int((value / originalhp) * xp)
        return returnvalue
    
    def prepare_next_round(self):
        """prepare next round for attack"""
        self.round += 1
        self.initiative = self.INITIATIVE_ACTIVE_MAXIMUM

    def prepare_next_encounter(self):
        """prepare next round for attack"""
        self.encounter += 1
        self.prepare_next_round()

# class Rule():
#     def __init__(self, type, condition, key, value, modifier):
#         self.type = type
#         self.key = key
#         self.condition = condition
#         self.value = value
#         self.modifier = modifier
