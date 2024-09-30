#combatmodel.py

from lib.dice import Dice
import lib.combatdata as cd1

class Combatant():
    """defines combatants that are participants with combat settings"""

    TYPE_PLAYER_CHARACTER = 'PC'
    TYPE_NON_PLAYER_CHARACTER = 'NPC'
    TYPE_MONSTER = 'M'

    CLASS_MONSTER = 0
    CLASS_CLERIC = 1
    CLASS_DRUID = 2
    CLASS_FIGHTER = 3
    CLASS_PALADIN = 4
    CLASS_RANGER = 5
    CLASS_MAGICUSER = 6
    CLASS_ILLUSIONIST = 7
    CLASS_THIEF = 8
    CLASS_ASSASSIN = 9
    CLASS_CAVALIER = 10
    CLASS_BARBARIAN = 11
    CLASS_THIEFACROBAT = 12
    
    def __init__(self, combattype, group, seq, hp, initiative = 0, damage = 0, attackmodifier = 0, defensemodifier = 0, **kwargs):
        # Load all raw participant values
        self.load_participant_values(**kwargs)
        
        # Assign member variables to database-retrieved values
        self.abbr = self.Abbr
        self.name = self.Name
        self.ac = self.AC
        self.missileattack = self.MissileAttack
        self.charactertype = self.CharacterType
        self.thac0 = self.THAC0
        self.attacksperround = self.AttacksPerRound
        self.damageperattack = self.DamagePerAttack
        self.specialattack = self.SpecialAttack
        self.specialdefense = self.SpecialDefense
        self.regenerationroundstart = self.RegenerationRoundStart
        self.regenerationhitpoint = self.RegenerationHitPoint
        self.regenerateafterdamage = self.RegenerateAfterDamage
        
        # Assign member variables to parameters        
        self.combattype = combattype
        self.group = group
        self.seq = seq
        self.abbrseq = self.abbr + str(self.seq)
        self.initiative = initiative
        self.damage = damage
        self.attackmodifier = attackmodifier
        self.defensemodifier = defensemodifier

        if hp == 0:
            self.hp = self.calculate_hitpoints( self.HitDiceTypeCode, self.HitDie, self.HitDice, self.HitDiceMin, self.HitDiceMax, self.HitDiceModifier, self.HitDieValue, self.HitPointStart, self.HitPointMin, self.HitPointMax )
        else:
            self.hp = hp
            
        self.hpmax = self.hp
        
        self.xp = self.ExperienceBase + self.ExperienceAdjustment + (self.hp * self.ExperienceHitPointMultiplier)
        if self.ExperienceAddHitPoint == True:
            self.xp += self.hp
        
        self.defender_abbrseq = ''
        self.inactivereason = ''
        self.regenerationround = 0
        
    def calculate_hitpoints(self, hitdicetypecode, hitdie, hitdice, hitdicemin, hitdicemax, hitdicemodifier, hitdievalue, hitpointstart, hitpointmin, hitpointmax) -> int:
        """calculate hit points based on variable hit point rules"""
        DIE_FIXED                 = 'DF'   # Die Fixed
        DIE_FIXED_POINTS_FIXED    = 'DFPF' # Die Fixed Points Fixed
        DIE_FIXED_POINTS_VARIABLE = 'DFPV' # Die Fixed Points Variable
        DIE_VARIABLE              = 'DV'   # Die Variable
        POINTS_FIXED              = 'PF'   # Points Fixed
        POINTS_VARIABLE           = 'PV'   # Points Variable

        hitpoints = -999
        variablehitpointrange = hitpointmax - hitpointmin + 1

        # Process hit point fixed die values
        if hitdicetypecode in [ DIE_FIXED, DIE_FIXED_POINTS_FIXED, DIE_FIXED_POINTS_VARIABLE]:
            if hitdievalue == 0:
                hitpoints = Dice.roll_dice(hitdice, hitdie, hitdicemodifier, 0)
            else:
                hitpoints = hitdice * hitdievalue
                
            if hitdicetypecode == DIE_FIXED_POINTS_FIXED:
                hitpoints = hitpoints + hitpointstart
                
            if hitdicetypecode == DIE_FIXED_POINTS_VARIABLE:
                hitpoints = hitpoints + hitpointmin + Dice.roll_die(variablehitpointrange, 0)
                
            return hitpoints

        # Process hit point variable die values
        if hitdicetypecode == DIE_VARIABLE:
            variablehitdicerange = (hitdicemin - 1) + Dice.roll_die(hitdicemax - hitdicemin + 1)
            if hitdievalue == 0:
                hitpoints = Dice.roll_dice(variablehitdicerange, hitdie, hitdicemodifier, 0)
            else:
                hitpoints = variablehitdicerange * hitdievalue
            
            return hitpoints
    
        # Process hit point fixed point values
        if hitdicetypecode == POINTS_FIXED:
            hitpoints = hitpointstart
            return hitpoints
        
        # Process hit point variable point values        
        if hitdicetypecode == POINTS_VARIABLE:
            hitpoints = hitpointmin + Dice.roll_die(variablehitpointrange, 0)

        return hitpoints

    def can_attack(self) -> bool:
        """check if combatant can attack"""
        return self.hp > 0

    def format_damage(self) -> str:
        damage = ''
        if (self.damageperattack == None) or (len(str(self.damageperattack)) == 0):
            pass
        else:
            damage += '    * ' + self.abbrseq + ' Damage Per Attack:\n      -- '+'\n      -- '.join(self.damageperattack.lstrip().split('|'))
        
        return damage

    def format_special_attacks(self) -> str:
        """format special attack information"""
        specialattack = ''
        if (self.specialattack == None) or (len(str(self.specialattack)) == 0):
            pass
        else:
            specialattack = '    * ' + self.abbrseq + ' Special Attacks:\n      -- '+'\n      -- '.join(self.specialattack.lstrip().split('|'))

        return specialattack+self.format_damage()

    def format_special_defense(self) -> str:
        """format special defense information"""
        specialdefense = ''
        if (self.specialdefense == None) or (len(str(self.specialdefense)) == 0):
            pass
        else:
            specialdefense = '    * ' + self.abbrseq + ' Special Defenses:\n      -- '+'\n      -- '.join(self.specialdefense.lstrip().split('|'))

        return specialdefense

    def get_level(self, level) -> list:
        """get level of each class"""
        if level is None:
            return list('0')
        else:
            return list(l for l in level.split(','))

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
        """is combatant active?"""
        return ( self.initiative >= Encounter.INITIATIVE_ACTIVE_MINIMUM ) and (self.can_attack())

    def is_inactive(self) -> bool:
        """is combatant inactive?"""
        return ( self.initiative < Encounter.INITIATIVE_ACTIVE_MINIMUM )

    def is_alive(self) -> bool:
        """check if combatant is alive"""
        return not self.is_dead()
    
    def is_dead(self) -> bool:
        """check if combatant is dead"""
        if self.CharacterType == self.TYPE_MONSTER:
            return self.hp <= 0
        else:
            return self.hp <= -10
    
    def is_unconscious(self) -> bool:
        """check if combatant is unconscious"""
        return -10 < self.hp <= 0
    
    # ***KEEP***
    # def is_spellcaster(self) -> bool:
    #     """check if combatant could be a spell caster"""
    #     for classtype in self.ClassType.split(","):
    #         if classtype == CLASSTYPE_CLERIC or classtype == CLASSTYPE_DRUID or classtype == CLASSTYPE_MAGICUSER or classtype == CLASSTYPE_ILLUSIONIST or classtype == CLASSTYPE_RANGER or classtype == CLASSTYPE_PALADIN:
    #             return True
    #     return False

    def load_participant_values(self, **kwargs) -> None:
        """load participant key-valued pairs into member variables"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def regenerate_hitpoints(self) -> None:
        """regenerate combatant hit points"""
        self.hp += self.regenerationhitpoint
        if self.hp > self.hpmax:
            self.hp = self.hpmax

    def take_damage(self, damage) -> None:
        """record damage taken"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
            return
            
        if self.hp > self.hpmax:
            self.hp = self.hpmax

    def was_hit_successful(self, hitroll, defenderarmorclass, defensemodifier) -> bool:
        """determine 'to hit' value"""
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
    INITIATIVE_ACTIVE_MAXIMUM    = 6999
    INITIATIVE_NONE              = -1
    INITIATIVE_MINIMUM           = INITIATIVE_INACTIVE_MINIMUM
    INITIATIVE_MAXIMUM           = INITIATIVE_ACTIVE_MAXIMUM
    TO_HIT_DIE                   = 20
    TO_HIT_DIE_MAXIMUM           = 30
    TO_HIT_DIE_MINIMUM           = 0
    TO_HIT_DIE_SPECIAL_ATTACK    = 0

    ATTACK_CRITICAL_FUMBLE       = 1
    ATTACK_CRITICAL_HIT          = 20

    COMBATTYPE_FRIEND = 'FRIEND'
    COMBATTYPE_FOE    = 'FOE'
    
    # Attributes
    friend_count = 0
    foe_count = 0
    combatant_attack_number = 1
    combatants = []

    def __init__(self) -> None:
        self.data = cd1.CombatData()
        self.get_combatants()

        self.encounter = 1
        self.round = 1
        self.initiative = self.INITIATIVE_ACTIVE_MAXIMUM
        self.ismissileattack = True

    # *** KEEP ***        
    # class CombatSpellType(Enum):
    #     """defines type of combat spell type"""
    #     NONE = 0
    #     INDIVIDUAL = 1
    #     GROUP = 2
    #     OTHER = 3
        
    #     def __str__(self):
    #         return f'{self.name.title()}'

    def calculate_xp(self, originalhp, hp, damage, xp) -> int:
        if damage > hp:
            value = hp
        else:
            value = damage
            
        returnvalue = int((value / originalhp) * xp)
        return returnvalue
    
    def check_duplicate_initiative(self) -> None:
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
        self.friend_count = self.count_combatants(self.COMBATTYPE_FRIEND)
        self.foe_count = self.count_combatants(self.COMBATTYPE_FOE)
    
    def delete_dead_oponents(self) -> None:
        self.data.delete_dead_foes()
        for combatant in self.combatants:
            if combatant.combattype == self.COMBATTYPE_FOE and combatant.is_dead():
                self.combatants.remove(combatant)

    def find_combatant(self, abbrseq) -> Combatant:
        for combatant in self.combatants:
            if combatant.abbrseq == abbrseq:
                return Combatant
            
        return None
    
    def find_next_attacker(self) -> Combatant:
        """find next available attacker"""
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

            elif self.ismissileattack == True:
                if attacker.missileattack == False:
                    continue

            # set event initiative to attacker's
            self.initiative = attacker.initiative
            
            # return attacker
            return attacker

    def format_attack_type(self) -> str:
        """format attack type"""
        message = f"{'Missile' if self.ismissileattack else 'Melee'}"
        return message

    def format_combatants(self) -> str:
        SEPARATOR_LINE_LENGTH = 97
        
        """format all combatant information"""
        message = '\nCombatants:'
        message += '\n'+'='*SEPARATOR_LINE_LENGTH
        message += f'\n       |                                         |      |       |       |    |        | ATT | DEF'
        message += f'\n TYPE  | ABBRSEQ  NAME                           | INIT | GROUP | THAC0 | AC | HP/MAX | +/- | +/-'
        message += f'\n------ | -------- ------------------------------ | ---- | ----- | ----- | -- | ------ | --- | ---'
        for combatant in self.combatants:
            message += f'\n{combatant.combattype.ljust(6)} | {combatant.abbrseq.ljust(8)} {combatant.name.ljust(30)} | {str(combatant.initiative).rjust(4)} | {str(combatant.group).rjust(5)} |   {str(combatant.thac0).rjust(2)}  | {str(combatant.ac).rjust(2)} |{str(combatant.hp).rjust(3)}/{str(combatant.hpmax).ljust(4)}|  {str(combatant.attackmodifier).rjust(2)} |  {str(combatant.defensemodifier).rjust(2)}'
        
        message += '\n'+'='*SEPARATOR_LINE_LENGTH
        return message
    
    def format_encounter(self) -> str:
        """format encounter information"""
        message = f'\nEncounter: {self.encounter} | Round: {self.round} | Initiative: {self.initiative}'
        return message

    def get_combatants(self) -> None:
        """get combatants from participant database"""
        self.combatants = []
        self.data.load_combatants()
        combatantdata = self.data.combatants
        for combatant in combatantdata:
            abbr = combatantdata[combatant].get("Abbr")
            participant = self.data.participants.get(abbr)
            combattype = combatantdata[combatant].get("combattype")
            combatgroup = combatantdata[combatant].get("group")
            combatsequence = combatantdata[combatant].get("seq")
            combathitpoints = combatantdata[combatant].get("hp")
            combatattackmodifier = combatantdata[combatant].get("attackmodifier")
            combatdefensemodifier = combatantdata[combatant].get("defensemodifier")
            combatinitiative = 0
            combatdamage = 0
        
            # instantiate new combatant
            preparedcombatant = Combatant(combattype, combatgroup, combatsequence, combathitpoints, combatinitiative, combatdamage, combatattackmodifier, combatdefensemodifier, **participant)
            
            # append combatant to combatants list
            self.combatants.append(preparedcombatant)
    
    def is_combatant(self, abbrseq) -> bool:
        for combatant in self.combatants:
            if combatant.abbrseq == abbrseq:
                return True
            
        return False
    
    def load_combatants(self) -> None:
        """load combatant information"""
        if len(self.combatants) > 0:
            combatant_saved_initiative = {combatant.abbrseq: combatant.initiative for combatant in self.combatants}
            
        self.get_combatants()
        for combatant in self.combatants:
            # update FOE combatants hit points
            if combatant.combattype == self.COMBATTYPE_FOE:
                self.data.update_combatant_hit_points(combatant.abbr, combatant.seq, combatant.hpmax, combatant.hp)

            # save combatant initiative (if exists)
            try:
                saved_initiative = combatant_saved_initiative[combatant.abbrseq]
                if saved_initiative > self.INITIATIVE_INACTIVE_MINIMUM:
                    combatant.initiative = saved_initiative
            except:
                pass

        print(self.format_combatants())
        print(f'\nCombatants loaded: {len(self.combatants)}')

    def load_participants(self) -> None:
        self.data.load_participants()
        print(f'\nParticipants loaded: {len(self.data.participants)}')
        
    def prepare_next_encounter(self) -> None:
        """prepare next round for attack"""
        self.encounter += 1
        self.prepare_next_round(True)
        
    def prepare_next_round(self, reset=False) -> None:
        """prepare next round for attack"""
        if reset:
            self.round = 1
        else:
            self.round += 1
            
        self.initiative = self.INITIATIVE_ACTIVE_MAXIMUM
        self.regenerate_combatants()

    def regenerate_combatants(self) -> None:
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
        """determine initiative value for non-players (Non-Player Characters [NPC] and Monsters [M])"""
        return Dice.roll_die(self.INITIATIVE_DIE_MAJOR) * 1000 + Dice.roll_die(self.INITIATIVE_DIE_MINOR)

    def sort_combatants_by_initative(self) -> None:
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)

# class Rule():
#     def __init__(self, type, condition, key, value, modifier):
#         self.type = type
#         self.key = key
#         self.condition = condition
#         self.value = value
#         self.modifier = modifier
