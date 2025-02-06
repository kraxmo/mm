#combatmodel.py

from lib.dice import Dice
import lib.combatdata as cd1
import lib.ui as ui1

class Combatant():
    """defines combatants that are participants with combat settings"""

    TYPE_PLAYER_CHARACTER = 'PC'
    TYPE_NON_PLAYER_CHARACTER = 'NPC'
    TYPE_MONSTER = 'M'
    
    DUNGEON_MASTER = "AAA_DM"
    
    CLASSTYPE = {
            "MO": "MONSTER",
            "CL":  "CLERIC",
            "DR": "DRUID",
            "FI": "FIGHTER",
            "PA": "PALADIN",
            "RA": "RANGER",
            "MU": "MAGICUSER",
            "IL": "ILLUSIONIST",
            "TH": "THIEF",
            "AS": "ASSASSIN",
            "CA": "CAVALIER",
            "BA": "BARBARIAN",
            "TA": "THIEFACROBAT",
        }

    CLASSTYPE_SPELLCASTER = ["CL", "DR", "PA", "RA", "MU", "IL"]

    RACETYPE = {
        "MO": "MONSTER",
        "DW": "DWARF",
        "EL": "ELF",
        "GN": "GNOME",
        "HE": "HALF-ELF",
        "HL": "HALFLING",
        "HO": "HALF-ORC",
        "HU": "HUMAN",
    }
    
    def __init__(self, combattype: str, group: str, seq: int, hp: int, initiative: int = None, damage: int = None, attackmodifier: int = None, defensemodifier: int = None, **kwargs):
        # Load all raw participant values
        self.load_participant_values(**kwargs)
        
        # Assign member variables to database-retrieved values
        self.abbr: str = self.Abbr
        self.name: str = self.Name
        self.charactertype: str = self.CharacterType
        self.racetype: str = self.RaceType
        self.classtype: str  = self.ClassType
        self.level: str  = self.Level
        self.savingthrowclasstype: str  = self.SavingThrowClassType
        self.savingthrowlevel: int = self.SavingThrowLevel
        self.savingthrowlevelpdm: int = self.SavingThrowLevelPDM
        self.size: int = self.Size
        self.attacksperround: str = self.AttacksPerRound
        self.ac: int = self.AC
        self.thac0: int = self.THAC0
        self.defensiveadjustment: int = self.DefensiveAdjustment
        self.missileattack: int = self.MissileAttack
        self.damageperattack: int = self.DamagePerAttack
        self.specialattack: str  = self.SpecialAttack
        self.specialdefense: str  = self.SpecialDefense
        self.notes: str  = self.Notes
        self.regenerationroundstart: int = self.RegenerationRoundStart
        self.regenerationhitpoint: int = self.RegenerationHitPoint
        self.regenerateafterdamage: int = self.RegenerateAfterDamage
        
        # Assign member variables to parameters        
        self.combattype: str = combattype
        self.group: str = group
        self.seq: int = seq
        self.abbrseq: str = self.abbr + str(self.seq)
        if initiative is None:
            self.initiative: int = 0
        else:
            self.initiative: int = initiative

        if damage is None:
            self.damage: int = 0
        else:
            self.damage: int = damage
            
        if attackmodifier is None:
            self.attackmodifier: int = 0
        else:
            self.attackmodifier: int = attackmodifier
        
        if defensemodifier is None:
            self.defensemodifier: int = 0
        else:
            self.defensemodifier: int = defensemodifier

        if hp == 0:
            self.hp: int = self.calculate_hitpoints( self.HitDiceTypeCode, self.HitDie, self.HitDice, self.HitDiceMin, self.HitDiceMax, self.HitDiceModifier, self.HitDieValue, self.HitPointStart, self.HitPointMin, self.HitPointMax )
        else:
            self.hp: int = hp
        
        if self.HitPointStart == 0:    
            self.hpmax: int = self.hp
        else:
            self.hpmax: int = self.HitPointStart
        
        self.xp: int = self.ExperienceBase + self.ExperienceAdjustment + (self.hp * self.ExperienceHitPointMultiplier)
        if self.ExperienceAddHitPoint:
            self.xp += self.hp
        
        self.defender_abbrseq: str = ''
        self.inactivereason: str  = ''
        self.regenerationround: int = 0
        
    def calculate_hitpoints(self, hitdicetypecode: str, hitdie: int, hitdice: int, hitdicemin: int, hitdicemax: int, hitdicemodifier: int, hitdievalue: int, hitpointstart: int, hitpointmin: int, hitpointmax: int) -> int:
        """calculate hit points based on variable hit point rules
        
        args:
            hitdicetypecode: str
            hitdie: int
            hitdice: int
            hitdicemin: int
            hitdicemax: int
            hitdicemodifier: int
            hitdievalue: int
            hitpointstart: int
            hitpointmin: int
            hitpointmax: int
        returns:
            hitpoints: int
        """
        DIE_FIXED                 = 'DF'   # Die Fixed
        DIE_FIXED_POINTS_FIXED    = 'DFPF' # Die Fixed Points Fixed
        DIE_FIXED_POINTS_VARIABLE = 'DFPV' # Die Fixed Points Variable
        DIE_VARIABLE              = 'DV'   # Die Variable
        POINTS_FIXED              = 'PF'   # Points Fixed
        POINTS_VARIABLE           = 'PV'   # Points Variable

        hitpoints: int = -999
        variablehitpointrange: int = hitpointmax - hitpointmin + 1

        # Process hit point fixed die values
        if hitdicetypecode in [ DIE_FIXED, DIE_FIXED_POINTS_FIXED, DIE_FIXED_POINTS_VARIABLE]:
            if hitdievalue == 0:
                hitpoints: int = Dice.roll_dice(hitdice, hitdie, hitdicemodifier, 0)
            else:
                hitpoints: int = hitdice * hitdievalue
                
            if hitdicetypecode == DIE_FIXED_POINTS_FIXED:
                hitpoints: int = hitpoints + hitpointstart
                
            if hitdicetypecode == DIE_FIXED_POINTS_VARIABLE:
                hitpoints: int = hitpoints + hitpointmin + Dice.roll_die(variablehitpointrange, 0)
                
            return hitpoints

        # Process hit point variable die values
        if hitdicetypecode == DIE_VARIABLE:
            variablehitdicerange: int = (hitdicemin - 1) + Dice.roll_die(hitdicemax - hitdicemin + 1)
            if hitdievalue == 0:
                hitpoints: int = Dice.roll_dice(variablehitdicerange, hitdie, hitdicemodifier, 0)
            else:
                hitpoints: int = variablehitdicerange * hitdievalue
            
            return hitpoints
    
        # Process hit point fixed point values
        if hitdicetypecode == POINTS_FIXED:
            hitpoints: int = hitpointstart
            return hitpoints
        
        # Process hit point variable point values        
        if hitdicetypecode == POINTS_VARIABLE:
            hitpoints: int = hitpointmin + Dice.roll_die(variablehitpointrange, 0)

        return hitpoints

    def can_attack(self) -> bool:
        """check if combatant can attack
        
        returns:
            bool: True if combatant can attack, False otherwise
        """
        return self.hp > 0

    def format_charactertype(self) -> str:
        """format charactor type information
        
        returns:
            str: formatted character type information
        """
        if self.is_player_character():
            charactertype: str  = "Player Character"
        elif self.is_non_player_character():
            charactertype: str  = "Non-Player Character"
        else:
            charactertype: str  = "Monster"

        return charactertype

    def format_classtype(self) -> str:
        """format class type information
        
        returns:
            str: formatted class type information
        """
        classtypes: list = [self.CLASSTYPE.get(name) for name in self.classtype.split(',')]
        classtype: str   = ','.join(classname for classname in classtypes) 
        return classtype

    def format_damage_per_attack(self) -> str:
        """format damage per attack information
        
        returns:
            str: formatted damage per attack information
        """
        damage: str = ''
        if self.damageperattack:
            damage += f"{ui1.UI.INDENT_LEVEL_03}Damage Per Attack:"
            damage += f"\n{ui1.UI.INDENT_LEVEL_04}"
            damage += ('\n' + ui1.UI.INDENT_LEVEL_04).join(self.damageperattack.lstrip().split('|'))
            damage += '\n'
        
        return damage

    def format_notes(self) -> str:
        """format notes information
        
        returns:
            str: formatted notes information
        """
        notes: str  = ''
        if self.notes:
            notes += ui1.UI.INDENT_LEVEL_03 + 'Notes:'
            notes += '\n' + ui1.UI.INDENT_LEVEL_04
            notes += ('\n' + ui1.UI.INDENT_LEVEL_04).join(self.notes.lstrip().split('|'))
            notes += '\n'

        return notes

    def format_saving_throw(self) -> str:
        """format special attack information
        
        returns:
            str: formatted special attack information
        """
        savingthrow: str  = f'{ui1.UI.INDENT_LEVEL_03} Saving Throw:'
        savingthrow += ('\n' + ui1.UI.INDENT_LEVEL_04).join(self.specialattack.lstrip().split('|'))
        savingthrow += '\n'

        return savingthrow

    def format_special_attacks(self) -> str:
        """format special attack information
        
        returns:
            str: formatted special attack information"""
        specialattack: str  = ''
        if (self.specialattack == None) or (len(str(self.specialattack)) == 0):
            pass
        else:
            specialattack += ui1.UI.INDENT_LEVEL_03 + 'Special Attacks:'
            specialattack += '\n' + ui1.UI.INDENT_LEVEL_04
            specialattack += ('\n' + ui1.UI.INDENT_LEVEL_04).join(self.specialattack.lstrip().split('|'))
            specialattack += '\n'

        return specialattack+self.format_damage_per_attack()

    def format_special_defense(self) -> str:
        """format special defense information
        
        returns:
            str: formatted special defense information
        """
        specialdefense: str  = ''
        if (self.specialdefense == None) or (len(str(self.specialdefense)) == 0):
            pass
        else:
            specialdefense += ui1.UI.INDENT_LEVEL_03 + 'Special Defenses:'
            specialdefense += '\n' + ui1.UI.INDENT_LEVEL_04
            specialdefense += ('\n' + ui1.UI.INDENT_LEVEL_04).join(self.specialdefense.lstrip().split('|'))
            specialdefense += '\n'

        return specialdefense

    def get_level(self, level) -> list:
        """get level of each class
        
        args:
            level: str
        returns:
            list: list of levels for each class
    """
        if level:
            return list(l for l in level.split(','))

        return list('0')


    # ***KEEP***
    # def get_attacks(self, round) -> int:
    #     """get number of attacks per round"""
    #     # check for either 1 or 2 attacks per round
    #     if self.attacksperround % 2 == 0:
    #         attacks = self.attacksperround
    #     else:
    #         # Process split round attacks (such as 3 attacks every 2 rounds)
            
    #         # check if round is even
    #         if round % 2 == 0:
    #             # subtract 1 from attacksperround
    #             attacks = int(self.attacksperround) - 1
    #         else:
    #             attacks = 1
        
    #     return attacks

    def is_active(self) -> bool:
        """is combatant active?
        
        returns:
            bool: True if combatant is active, False otherwise
        """
        return ( self.initiative >= Encounter.INITIATIVE_ACTIVE_MINIMUM ) and (self.can_attack())

    def is_inactive(self) -> bool:
        """is combatant inactive?
        
        returns:
            bool: True if combatant is inactive, False otherwise
        """
        return ( self.initiative < Encounter.INITIATIVE_ACTIVE_MINIMUM )

    def is_alive(self) -> bool:
        """check if combatant is alive
        
        returns:
            bool: True if combatant is alive, False otherwise
        """
        return not self.is_dead()
    
    def is_dead(self) -> bool:
        """check if combatant is dead
        
        returns:
            bool: True if combatant is dead, False otherwise
        """
        if self.is_monster():
            return self.hp <= 0
        else:
            return self.hp <= -10

    def is_dungeon_master(self) -> bool:
        """check if combatant is dungeon master
        
        returns:
            bool: True if combatant is dungeon master, False otherwise
        """
        return self.abbr == self.DUNGEON_MASTER
    
    def is_player_character(self) -> bool:
        """check if combatant is a player character
        
        returns:
            bool: True if combatant is a player character, False otherwise
        """
        return self.charactertype == self.TYPE_PLAYER_CHARACTER

    def is_non_player_character(self) -> bool:
        """check if combatant is a non-player character
        
        returns:
            bool: True if combatant is a non-player character, False otherwise
        """
        return self.charactertype == self.TYPE_NON_PLAYER_CHARACTER

    def is_monster(self) -> bool:
        """check if combatant is a monster
        
        returns:
            bool: True if combatant is a monster, False otherwise
        """
        return self.charactertype == self.TYPE_MONSTER
    
    def is_spellcaster(self) -> bool:
        """check if combatant could be a spell caster
        
        returns:
            bool: True if combatant could be a spell caster, False otherwise
        """
        for classtype in self.ClassType.split(','):
            if classtype in self.CLASSTYPE_SPELLCASTER:
                return True
            
        return False

    def is_unconscious(self) -> bool:
        """check if combatant is unconscious
        
        returns:
            bool: True if combatant is unconscious, False otherwise
        """
        return -10 < self.hp <= 0
    
    def load_participant_values(self, **kwargs) -> None:
        """load participant key-valued pairs into member variables
        
        args:
            kwargs: dict of participant key-valued pairs
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def regenerate_hitpoints(self) -> None:
        """regenerate combatant hit points"""
        self.hp += self.regenerationhitpoint
        if self.hp > self.hpmax:
            self.hp = self.hpmax

    def take_damage(self, damage: int) -> None:
        """record damage taken
        
        args:
            damage: int
        """
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
            return
            
        if self.hp > self.hpmax:
            self.hp = self.hpmax

    def was_hit_successful(self, hitroll: int, defenderarmorclass: int, defensemodifier: int) -> bool:
        """determine 'to hit' value
        
        args:
            hitroll: int
            defenderarmorclass: int
            defensemodifier: int
        returns:
            bool: True if hit was successful, False otherwise
        """
        if hitroll >= (self.thac0 - defenderarmorclass + defensemodifier - self.attackmodifier):
            return True
        else:
            return False

class Encounter():
    """Encounter container for tracking all combatant attacks by round"""

    # Constants
    INITIATIVE_DIE_MAJOR         = 6
    INITIATIVE_DIE_MINOR         = 999
    INITIATIVE_INACTIVE_MINIMUM  = 0
    INITIATIVE_INACTIVE_MAXIMUM  = 999
    INITIATIVE_ACTIVE_MINIMUM    = 1000
    INITIATIVE_ACTIVE_MAXIMUM    = 7000
    INITIATIVE_NONE              = -1
    INITIATIVE_MINIMUM           = INITIATIVE_INACTIVE_MINIMUM
    INITIATIVE_MAXIMUM           = INITIATIVE_ACTIVE_MAXIMUM
    TO_HIT_DIE                   = 20
    TO_HIT_DIE_MINIMUM           = 1
    TO_HIT_DIE_MAXIMUM           = 30

    ATTACK_CRITICAL_FUMBLE       = 1
    ATTACK_CRITICAL_HIT          = 20

    COMBATTYPE_FRIEND            = 'FRIEND'
    COMBATTYPE_FOE               = 'FOE'
    
    # Attributes
    friend_count: int = 0
    foe_count: int = 0
    combatant_attack_number: int = 1
    combatants: list = []

    def __init__(self) -> None:
        self.encounter: int = 1
        self.round: int = 1
        self.initiative: int = self.INITIATIVE_ACTIVE_MAXIMUM
        self.ismissileattack: bool = True
        self.data = cd1.CombatData()
        self.load_saving_throws()

    def calculate_earned_xp(self, originalhp: int, hp: int, damage: int, xp: int) -> int:
        """calculate experience points earned based upon total hit points and damage inflicted
        
        args:
            originalhp: int
            hp: int
            damage: int
            xp: int
        returns:
            int: experience points earned
        """
        if damage > hp:
            value: int = hp
        else:
            value: int = damage
            
        returnvalue = int((value / originalhp) * xp)
        return returnvalue
    
    def check_duplicate_initiative(self) -> None:
        """check for duplicate initiative and adjust if necessary"""
        self.sort_combatants_by_initiative()

        # Detect duplicate initiative and esequence
        initiative = set()
        for i in range(len(self.combatants)):
            while self.combatants[i].initiative in initiative:
                self.combatants[i].initiative += 1
                
            initiative.add(self.combatants[i].initiative)

        self.sort_combatants_by_initiative()
            
    def count_combatants(self, combattype: str) -> int:
        """count number of available combatants
        
        args:
            combattype: str
        returns:
            int: number of available combatants
        """
        combatant_count: int = 0
        for combatant in self.combatants:
            if combatant.abbr == Combatant.DUNGEON_MASTER:
                continue
            
            if combatant.combattype == combattype:
                if combatant.combattype == self.COMBATTYPE_FRIEND:
                    if combatant.can_attack():
                        combatant_count += 1
                else:
                    if combatant.is_alive():
                        combatant_count += 1

        return combatant_count    

    def count_available_combatants(self) -> None:
        """count available combatants"""
        self.friend_count: int = self.count_combatants(self.COMBATTYPE_FRIEND)
        self.foe_count: int = self.count_combatants(self.COMBATTYPE_FOE)
    
    def delete_dead_oponents(self) -> None:
        """delete dead opponents from database and active combat list"""
        self.data.delete_dead_foes()
        for combatant in self.combatants:
            if combatant.combattype == self.COMBATTYPE_FOE and combatant.is_dead():
                self.combatants.remove(combatant)

    def find_combatant(self, abbrseq) -> Combatant:
        """find combatant using abbrseq key
        
        args:
            abbrseq: str
        returns:
            Combatant: combatant object
        """
        for combatant in self.combatants:
            if combatant.abbrseq == abbrseq:
                return Combatant
            
        return None
    
    def find_next_attacker(self) -> Combatant:
        """find next available attacker
        
        returns:
            Combatant: attacker combatant object
        """
        for attacker in self.combatants:
            # Exclude if attacker's initiative > event's
            if attacker.initiative > self.initiative:
                continue

            # Exclude dead attackers or unconscious attackers
            elif attacker.can_attack() == False:
                continue
                        
            # inactive attackers
            # even though they are unable to attack (due to choice, wounded, healing, spell-prep, retreating, etc.)
            # they still should be have a chance to respond and possibly change their initiative and/or inactivereason
            elif attacker.initiative < self.INITIATIVE_ACTIVE_MINIMUM:
                return attacker

            elif self.ismissileattack:
                if attacker.missileattack == False:
                    continue

            # set event initiative to attacker's
            self.initiative: int = attacker.initiative
            
            # return attacker
            return attacker

    def format_attack_type(self) -> str:
        """format attack type
        
        returns:
            str: formatted attack type
        """
        message: str = f"{'Missile' if self.ismissileattack else 'Melee'}"
        return message

    def format_combatants(self) -> str:
        """format combatant information
        
        returns:
            str: formatted combatant information
        """
        SEPARATOR_LINE_LENGTH = 103
        SIZE = {"S": "SMALL", "M": "MEDIUM", "L": "LARGE"}
        
        """format all combatant information"""
        message: str = '\nCombatants:'
        message += '\n'+'='*SEPARATOR_LINE_LENGTH
        message += f'\n       |                                 |    SIZE     |      |       |       |    |        | ATT | DEF'
        message += f'\n TYPE  | ABBRSEQ  NAME                   | RAC:CLS-LVL | INIT | GROUP | THAC0 | AC | HP/MAX | +/- | +/-'
        linecount = 0
        for combatant in self.combatants:
            if linecount % 3 == 0:
                message += f'\n------ | -------- ---------------------- | ----------- | ---- | ----- | ----- | -- | ------ | --- | ---'

            if combatant.is_monster():
                message += f'\n{combatant.combattype.ljust(6)} | {combatant.abbrseq.ljust(8)} {combatant.name.ljust(22)} |    {SIZE[combatant.size].ljust(6)}   | {str(combatant.initiative).rjust(4)} | {str(combatant.group).rjust(5)} |  {str(combatant.thac0).rjust(3)}  |{str(combatant.ac).rjust(3)} |{str(combatant.hp).rjust(3)}/{str(combatant.hpmax).ljust(4)}|  {str(combatant.attackmodifier).rjust(2)} | {str(combatant.defensemodifier).rjust(2)}'
            else:
                message += f'\n{combatant.combattype.ljust(6)} | {combatant.abbrseq.ljust(8)} {combatant.name.ljust(22)} |   {combatant.racetype}:{combatant.classtype}-{combatant.level.ljust(2)}  | {str(combatant.initiative).rjust(4)} | {str(combatant.group).rjust(5)} |  {str(combatant.thac0).rjust(3)}  |{str(combatant.ac).rjust(3)} |{str(combatant.hp).rjust(3)}/{str(combatant.hpmax).ljust(4)}|  {str(combatant.attackmodifier).rjust(2)} | {str(combatant.defensemodifier).rjust(2)}'
                
            linecount += 1
        
        message += '\n'+'='*SEPARATOR_LINE_LENGTH
        return message
    
    def format_encounter(self) -> str:
        """format encounter information
        
        returns:
            str: formatted encounter information
        """
        message: str = f'\nEncounter: {self.encounter} | Round: {self.round} | Initiative: {self.initiative}'
        return message

    def get_combatants(self) -> dict:
        """get combatants from participant database"""
        self.data.load_combatants()
        combatantdata: dict = self.data.combatants
        combatants = []
        for combatant in combatantdata:
            abbr: str = combatantdata[combatant].get("Abbr")
            participant: str = self.data.participants.get(abbr)
            combattype: str = combatantdata[combatant].get("CombatType")
            combatgroup: str = combatantdata[combatant].get("group")
            combatsequence: int = combatantdata[combatant].get("seq")
            combathitpoints: int = combatantdata[combatant].get("hp")
            combatattackmodifier: int = combatantdata[combatant].get("attackmodifier")
            combatdefensemodifier: int = combatantdata[combatant].get("defensemodifier")
            combatinitiative: int = 0
            combatdamage: int = 0
        
            # instantiate new combatant
            preparedcombatant = Combatant(combattype, combatgroup, combatsequence, combathitpoints, combatinitiative, combatdamage, combatattackmodifier, combatdefensemodifier, **participant)
            
            # append combatant to combatants list
            combatants.append(preparedcombatant)
            
        return combatants

    def get_saving_throw(self, savingthrowclasstype: str, savingthrowlevel: int, savingthrowlevelpdm: int, attacktype: str):
        """get saving throw value
        
        args:
            savingthrowclasstype: str
            savingthrowlevel: int
            savingthrowlevelpdm: int
            attacktype: str
        returns:
            int: saving throw value
        """
        savingthrowvalue: int = 0
        for savingthrow in self.savingthrows:
            if savingthrow.classtype == savingthrowclasstype:
                if attacktype in Saving_Throw.SAVING_THROW_POISON_DEATH_MAGIC:
                    if savingthrow.level == savingthrowlevelpdm:
                        savingthrowvalue = savingthrow.detail[attacktype]
                        break
                        
                if savingthrow.level == savingthrowlevel:
                    savingthrowvalue = savingthrow.detail[attacktype]
                    break
                
        return savingthrowvalue
            
    def is_combatant(self, abbrseq: str) -> bool:
        """check if passed abbrseq key is in the active combatant list
        
        args:
            abbrseq: str
        returns:
            bool: True if abbrseq key is in the active combatant list, False otherwise
        """
        for combatant in self.combatants:
            if combatant.abbrseq == abbrseq:
                return True
            
        return False
    
    def load_combatants(self) -> None:
        """load combatant information"""
        if len(self.combatants) > 0:
            combatant_saved_initiative: dict = {combatant.abbrseq: combatant.initiative for combatant in self.combatants}
            
        self.combatants = self.get_combatants()
        if self.combatants:
            for combatant in self.combatants:
                # update FOE combatants hit points
                if combatant.combattype == self.COMBATTYPE_FOE:
                    self.data.update_combatant_hit_points(combatant.combattype, combatant.abbr, combatant.seq, combatant.hpmax, combatant.hp)

                # save combatant initiative (if exists)
                try:
                    saved_initiative: int = combatant_saved_initiative[combatant.abbrseq]
                    if saved_initiative > self.INITIATIVE_INACTIVE_MINIMUM:
                        combatant.initiative = saved_initiative
                except:
                    # combatant does not exist
                    pass

            ui1.UI.output(self.format_encounter())
            ui1.UI.output(self.format_combatants())
            
        ui1.UI.output(f'\nCombatants loaded: {len(self.combatants)}')

    def load_participants(self) -> None:
        """load participant information"""
        self.data.load_participants()
        ui1.UI.output(f'\nParticipants loaded: {len(self.data.participants)}')
        
    def load_saving_throws(self) -> None:
        """load savings throw information"""
        self.savingthrows = []
        self.data.load_saving_throws()
        savingthrowdata: int = self.data.savingthrows
        for savingthrow in savingthrowdata:
            classtype: str = savingthrowdata[savingthrow].get("ClassType")
            level: int = savingthrowdata[savingthrow].get("Level")
            ppdm: int = savingthrowdata[savingthrow].get("PPDM")
            pp: int = savingthrowdata[savingthrow].get("PP")
            rsw: int = savingthrowdata[savingthrow].get("RSW")
            bw: int = savingthrowdata[savingthrow].get("BW")
            s: int = savingthrowdata[savingthrow].get("S")
            
            # instantiate new saving throw
            preparedsavingthrows = Saving_Throw(classtype, level, ppdm, pp, rsw, bw, s)
            
            # append saving throw to saving throw list
            self.savingthrows.append(preparedsavingthrows)

        ui1.UI.output(f'\nSaving Throws loaded: {len(self.savingthrows)}')
    
    def prepare_next_encounter(self) -> None:
        """prepare next round for attack"""
        self.encounter += 1
        self.prepare_next_round(True)
        
    def prepare_next_round(self, reset: bool = None) -> None:
        """prepare next round for attack
        
        args:
            reset: bool
        """
        if reset is None:
            reset = False
        
        if reset:
            self.round = 1
        else:
            self.round += 1
            
        self.initiative = self.INITIATIVE_ACTIVE_MAXIMUM
        self.regenerate_combatants()

    def regenerate_combatants(self) -> None:
        """regenerate hit points for regenerative combatants"""
        for combatant in self.combatants:        
            # No regeneration
            if combatant.regenerationhitpoint == 0:
                continue

            # If combatant can regenerate hp but has no damage
            if combatant.hp == combatant.hpmax:
                combatant.regenerationround = 0
                continue
            
            combatant.regenerationround += 1

            # (No regeneration starting round specified and can regenerate without waiting) or (regeneration round specified and regeneration round >= regeneration round start
            if ((combatant.regenerationroundstart == 0) and (combatant.regenerateafterdamage == False)) or ((combatant.regenerationroundstart > 0) and (combatant.regenerationround >= combatant.regenerationroundstart)):
                self.data.log_action(self.encounter, self.round, None, None, None, None, None, None, combatant.combattype, combatant.abbr, combatant.seq, combatant.group, combatant.initiative, combatant.hpmax, combatant.hp, combatant.regenerationhitpoint, 0, 0, 'regenerate hit point BEFORE')
                combatant.regenerate_hitpoints()
                self.data.update_combatant_hit_points(combatant.abbr, combatant.seq, combatant.hpmax, combatant.hp)    # update db with new regenerated hp
                self.data.log_action(self.encounter, self.round, None, None, None, None, None, None, combatant.combattype, combatant.abbr, combatant.seq, combatant.group, combatant.initiative, combatant.hpmax, combatant.hp, 0, 0, 0, 'regenerate hit point AFTER')

    def roll_nonplayer_initiative(self) -> int:
        """determine initiative value for non-players (Non-Player Characters [NPC] and Monsters [M])
        
        returns:
            int: initiative value
        """
        return Dice.roll_die(self.INITIATIVE_DIE_MAJOR) * 1000 + Dice.roll_die(self.INITIATIVE_DIE_MINOR)

    def sort_combatants_by_initiative(self) -> None:
        """sort combatant list"""
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)

# class Rule():
#     def __init__(self, type, condition, key, value, modifier):
#         self.type = type
#         self.key = key
#         self.condition = condition
#         self.value = value
#         self.modifier = modifier

class Saving_Throw():
    SAVING_THROW_TYPE = ['paralyze', 'poison', 'death magic', 'petrify', 'polymorph', 'rod staff wand', 'breath weapon', 'spell']
    SAVING_THROW_POISON_DEATH_MAGIC = ['poison', 'death magic']
    
    def __init__(self, classtype: str, level: int, ppdm: int, pp: int, rsw: int, bw: int, s: int) -> None:
        self.classtype                = classtype
        self.level                    = level
        self.detail                   = {}
        self.detail['paralyze']       = ppdm
        self.detail['poison']         = ppdm
        self.detail['death magic']    = ppdm
        self.detail['petrify']        = pp
        self.detail['polymorph']      = pp
        self.detail['rod staff wand'] = rsw
        self.detail['breath weapon']  = bw
        self.detail['spell']          = s

    def __str__(self) -> str:
        message: str = f'Class: {self.classtype} Level: {self.level}'
        return message
