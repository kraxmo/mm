#mm.py

import abc
import lib.combatmodel as cm1
from lib.dice import Dice

EXIT_TO_MENU = "@@"

class ExitToMenuException(Exception):
    pass

class QuitException(Exception):
    pass

class Action(metaclass=abc.ABCMeta):
    def __init__(self, code, label):
        self.code = code
        self.label = label

    @abc.abstractmethod
    def process(self, ui, encounter):
        pass

class ListCombatantsAction(Action):
    def __init__(self):
        super().__init__(2, 'List Combatants')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        print(encounter.format_encounter())
        print(encounter.format_combatants())
        return

class LoadCombatParticipantsAction(Action):
    def __init__(self):
        super().__init__(0, 'Load Combat Participants')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        process_load_participants(encounter)
        return

class LoadCombatantsAction(Action):
    def __init__(self):
        super().__init__(1, 'Load Combatants')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        process_load_combatants(encounter)
        return 

class NextEncounterAction(Action):
    def __init__(self):
        super().__init__(3, 'Next Encounter')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        encounter.prepare_next_encounter()
        print(encounter.format_encounter())
        return

class NextAttackAction(Action):
    def __init__(self):
        super().__init__(4, 'Next Attack')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        process_round(ui, encounter)
        return

class SetEncounterInitiativeAction(Action):
    def __init__(self):
        super().__init__(5, 'Set Encounter Initiative')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        return process_encounter_initiative(ui, encounter)

class GetCombatantInitiativeAction(Action):
    def __init__(self):
        super().__init__(6, 'Get Combatant Initiative')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        """get initiative for each combatant"""
        return process_combatant_initiative(encounter)

class InitializeRoundAction(Action):
    """initialize round for attacks"""

    def __init__(self):
        super().__init__(7, 'Initialize Round')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        return initialize_round(ui, encounter)
    
class QuitAction(Action):
    def __init__(self):
        super().__init__(99, 'Quit')

    def process(self, ui, encounter):
        raise QuitException

    def __str__(self):
        return f'{__class__.__name__}'
    
class UI:
    SEPARATOR_LINE_LENGTH = 95
    
    def get_input(self, action_prompt):
        value = input(action_prompt)
        if value.find(EXIT_TO_MENU) > -1:
            raise ExitToMenuException
            
        return value
    
    def get_numeric_input(self, action_prompt):
        while True:
            try:
                value = self.get_input(action_prompt)
                return int(value)
            except ValueError:
                print("Entered value must be numeric")

class MeleeManager():
    def __init__(self):
        self.ui = UI()

        print('')
        print('='*self.ui.SEPARATOR_LINE_LENGTH)
        print('MELEE MANAGER')
        print('-'*self.ui.SEPARATOR_LINE_LENGTH)
        print("Press '@@' at any input prompt to return to menu")
        print('='*self.ui.SEPARATOR_LINE_LENGTH)
        self.encounter = cm1.Encounter()
        process_load_participants(self.encounter)
        process_load_combatants(self.encounter)
        
        # define actions
        self.actions = [
            LoadCombatParticipantsAction(),
            LoadCombatantsAction(),
            ListCombatantsAction(),
            NextEncounterAction(),
            NextAttackAction(),
            SetEncounterInitiativeAction(),
            QuitAction(),
            ]

        self.actions_map = {
            action.code: action
            for action in self.actions
            }

        self.action_prompt = f"\nActions:\n"
        for key, value in self.actions_map.items():
            self.action_prompt += f"\t{key}: {value.label}\n"

        self.action_prompt += "\nEnter Action: "

    def main(self):
        while True:
            action_code = self.ui.get_numeric_input(self.action_prompt)
            try:
                action = self.actions_map[action_code]
            except KeyError:
                print(f'*{action_code}* not a valid action\n')
                continue

            try:
                action.process(self.ui, self.encounter)
                continue
            except ExitToMenuException:
                continue
            except QuitException:
                break

def delete_dead_opponents(encounter) -> None:
    encounter.delete_dead_oponents()

def determine_attack_damage(ui, encounter, to_hit_roll, attacker, defender) -> None:
    """determine attacker damage to defender"""
    raw_xp_prompt = '    * Enter xp: '
    if to_hit_roll == encounter.TO_HIT_DIE_SPELL:    # spell is cast
        process_attack_spell(ui, encounter, attacker, defender, )
        return

    if (to_hit_roll == encounter.ATTACK_CRITICAL_HIT) or (attacker.was_hit_successful(to_hit_roll, defender.ac, defender.defensemodifier)):
        process_attack_hit(ui, encounter, attacker, defender, to_hit_roll)
        return

    process_attack_miss(ui, encounter, attacker, defender, to_hit_roll)

def find_next_defender(ui, attacker, combatants) -> cm1.Combatant:
    """find next available defender"""
    defender_abbrseq = ''
    while defender_abbrseq == '':
        if len(attacker.defender_abbrseq) == 0:
            message = f'    * Who is {attacker.abbrseq} attacking? (abbrseq) '
        else:
            message = f'    * Is {attacker.abbrseq} attacking {attacker.defender_abbrseq}? (<Enter> for existing or type new abbrseq) '
    
        defender_abbrseq = ui.get_input(message).upper()
        if len(defender_abbrseq) == 0:
            if len(attacker.defender_abbrseq) == 0:
                print(f'      -- Please enter a defender abbrseq')
                defender_abbrseq = ''
                continue
            
            defender_abbrseq = attacker.defender_abbrseq
        else:            
            if defender_abbrseq == attacker.abbrseq:
                print(f'      -- {attacker.abbrseq} cannot self-attack. Try again')
                defender_abbrseq = ''
                continue
        
        defender_count = 0
        defender_is_invalid = False
        defender_is_dead = False
        for defender in combatants:
            defender_count += 1
            if defender.abbrseq == defender_abbrseq:
                if defender.combattype == attacker.combattype:
                    friend_prompt = f'      -- {attacker.abbrseq} and {defender.abbrseq} are both friends. Are you sure? (<Enter> for No, y for Yes) '
                    if len(ui.get_input(friend_prompt)) == 0:
                        defender_is_invalid = True
                        attacker.defender_abbrseq = ''
                        defender_abbrseq = ''
                        break

                if defender.is_alive():
                    special_defense_message = defender.format_special_defense()
                    if len(special_defense_message): print(special_defense_message)
                        
                    attacker.defender_abbrseq = defender_abbrseq
                    return defender
                else:
                    defender_is_dead = True
                    print(f'      -- {defender.abbrseq} is dead')
                    attacker.defender_abbrseq = ''
                    defender_abbrseq = ''

                break

        if defender_is_dead or defender_is_invalid:
            continue
            
        if defender_count == len(combatants) and defender_abbrseq == '':
            return None

        print(f'      -- defender {defender_abbrseq} does not exist. Try again')
        defender_abbrseq = ''

def get_all_combatants_initiative(ui, encounter) -> None:
    """get initiative for each combatant"""
    if encounter.round > 1:
        initiative_prompt = f'- Re-roll initiative? (<Enter> for No, Y for Yes) '
        rollinitiative = ui.get_input(initiative_prompt)
        if rollinitiative.lower() != 'y':
            return
            
    print('\nEnter Initiative:')
    for combatant in encounter.combatants:
        if combatant.CharacterType == combatant.TYPE_PLAYER_CHARACTER:
            get_combatant_initiative(ui, encounter, combatant)
        else:
            combatant.initiative = encounter.roll_nonplayer_initiative()

    encounter.check_duplicate_initiative()
    for combatant in encounter.combatants:
        encounter.data.log_initiative(encounter.encounter, encounter.round, combatant.combattype, combatant.abbr, combatant.seq, combatant.group, combatant.initiative)
        
    return

def get_combatant_initiative(ui, encounter, combatant) -> None:
    initiative_prompt = f"- {combatant.name}'s initiative? (<Enter> for previous value {combatant.initiative}) "
    while True:
        initiative = ui.get_input(initiative_prompt)
        if len(initiative) == 0:
            initiative = combatant.initiative
            return
        
        elif initiative.isnumeric() == False:
            print(f'  + An initiative value of {initiative} is not numeric')
            initiative = ''
            continue
        
        if int(initiative) < encounter.INITIATIVE_MINIMUM:
            print(f'  + An initiative value of {initiative} is less than {encounter.INITIATIVE_MINIMUM}')
            initiative = ''
            continue

        elif int(initiative) > encounter.INITIATIVE_MAXIMUM:
            print(f'  + An initiative value of {initiative} is more than {encounter.INITIATIVE_MAXIMUM}')
            initiative = ''
            continue

        elif int(initiative) < encounter.INITIATIVE_ACTIVE_MINIMUM:
            inactive_initiative_prompt = f'     * Initiative value {initiative} is for inactive combatants. Keep it? (<Enter> = Yes, N = No) '
            if len(ui.get_input(inactive_initiative_prompt)) == 0:
                combatant.initiative = int(initiative)
                inactivereason = ''
                while len(inactivereason) == 0:
                    message = f'       -- Reason for inactivity? '
                    if len(combatant.inactivereason) > 0:
                        message += f'(<Enter> = keep previous value {combatant.inactivereason}, <Reason> = new inactive reason) '

                    inactivereason = ui.get_input(message)
                    
                combatant.inactivereason = inactivereason
                break
            else:
                continue
        else:
            combatant.initiative = int(initiative)
            break

def get_hit_roll(ui, encounter, combatant) -> int:
    """get to hit roll"""

    message = f"\n  + Enter 'To Hit' d{encounter.TO_HIT_DIE} result: "
    if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
        message += '(0 = spell) '
    else:
        message += '(<Enter> = autoroll, 0 = spell, 1-20 manual entry) '
        
    to_hit_input = ''
    while to_hit_input == '':
        to_hit_input = ui.get_input(message)
        if to_hit_input.isnumeric() == False:
            if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
                print(f"    * 'To Hit' roll of '{to_hit_input}' is not a number.")
                to_hit_input = ''
                continue
            else:
                to_hit_roll = Dice.roll_die(encounter.TO_HIT_DIE)
                break

        to_hit_roll = int(to_hit_input)
        if to_hit_roll < encounter.TO_HIT_DIE_MINIMUM or to_hit_roll > encounter.TO_HIT_DIE_MAXIMUM:
            print(f"    * 'To Hit' roll must be between {encounter.TO_HIT_DIE_MINIMUM} and {encounter.TO_HIT_DIE}. Entered {to_hit_roll} value.")
            to_hit_input = ''
            continue
        
    print(f'\n  + Rolled {to_hit_roll}')
    return to_hit_roll
    
    # Handle PC to-hit
    if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
        to_hit_input = ''
        while to_hit_input == '':
            to_hit_input = input(f"\n  + Enter 'To Hit' d{encounter.TO_HIT_DIE} result: (0 = spell) ")
            if to_hit_input.isnumeric() == False:
                print(f"    * 'To Hit' roll of '{to_hit_input}' is not a number.")
                to_hit_input = ''
                continue
            
            to_hit_roll = int(to_hit_input)
            if to_hit_roll < encounter.TO_HIT_DIE_MINIMUM or to_hit_roll > encounter.TO_HIT_DIE_MAXIMUM:
                print(f"    * 'To Hit' roll must be between {encounter.TO_HIT_DIE_MINIMUM} and {encounter.TO_HIT_DIE}. Entered {to_hit_roll} value.")
                to_hit_input = ''
                continue
            
        return to_hit_roll

    # Handle NPC/M to-hit missile attack
    if combatant.missileattack:
        to_hit_input = ''
        to_hit_input = input(f"\n  + Spell Attack? (<Enter> = No, Y = Yes) ")
        if len(to_hit_input) > 0:
            to_hit_roll = encounter.TO_HIT_DIE_SPELL
            return to_hit_roll

    # automatically roll to-hit melee roll
    to_hit_roll = Dice.roll_die(encounter.TO_HIT_DIE)
    print(f'\n  + Rolled {to_hit_roll}')
    return to_hit_roll

def initialize_round(ui, encounter) -> None:
    """initialize round for attacks"""

    print(encounter.format_encounter())
    print(encounter.format_combatants())

    message = '\nRoll initiative for all combatants? (<Enter> = Yes, N = No) '
    if len(ui.get_input(message)) == 0:
        # Determine initiative for all combatants
        get_all_combatants_initiative(ui, encounter)

    print(encounter.format_encounter())
    print(encounter.format_combatants())
    encounter.combatant_attack_number = 1
    
def is_negative_number_digit(n: str) -> bool:
    """check for negative number in passed string value"""
    try:
        int(n)
        return True
    except ValueError:
        return False

def process_attack_sequence(ui, encounter) -> bool:
    """process each attack: Return True for additional post-attacks check- or False for no post-attack checks"""
    attacker = encounter.find_next_attacker()
    if attacker == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    print(encounter.format_encounter(), encounter.format_attack_type(), ' Attacks')
    print(encounter.format_combatants())
    
    if attacker.is_inactive():
        message = f'\n- {attacker.abbrseq} is currently inactive.'
        if len(attacker.inactivereason) > 0:
            message += f' (last status: {attacker.inactivereason})'
            
        message += 'Should this change? (<Enter> = No, Y = Yes) '
        if len(ui.get_input(message)) > 0:
            status_prompt = f'  + Change initiative or inactive status? (<Enter> for initiative, new inactive status) '
            status = ui.get_input(status_prompt)
            if len(status) == 0:
                get_combatant_initiative(ui, encounter, attacker)
                encounter.check_duplicate_initiative()
                if (attacker.initiative >= encounter.INITIATIVE_ACTIVE_MINIMUM):
                    attacker.inactivereason = ''
                    print(f'  + {attacker.abbrseq} will be able to attack next round')
                else:
                    print(f'  + {attacker.abbrseq} will remain inactive')
                    
                return True
            else:
                attacker.inactivereason = status

        encounter.initiative = attacker.initiative - 1
        return False

    print(f'\n- {attacker.abbrseq} turn: {attacker.AttacksPerRound} attack(s)/round')
    print(f'  + {encounter.format_attack_type()} Attack #{encounter.combatant_attack_number}')

    # KEEP
    # spell_casting_type = 0

    skip_attack_prompt = f'  + Skip attack? (<Enter> = No, y = Yes) '
    skip_attack = ui.get_input(skip_attack_prompt)
    if len(skip_attack) > 0:
        print(f'  + ATTACK SKIPPED')
        process_attack_end(ui, encounter)
        return False

    print(f'  + ATTACKING...')
    defender = ''
    defender = find_next_defender(ui, attacker, encounter.combatants)
    if defender == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    special_attack_message = attacker.format_special_attacks()
    if len(special_attack_message): print(special_attack_message)
    
    to_hit_roll = get_hit_roll(ui, encounter, attacker)
    determine_attack_damage(ui, encounter, to_hit_roll, attacker, defender)
    if defender.is_alive() == False:
        encounter.foe_count -= 1
        attacker.defender_abbrseq = ''

    attack_prompt = f'\n  + Attack again? (<Enter> = No, y = Yes) '
    attack_again = ui.get_input(attack_prompt)
    if len(attack_again) == 0:
        process_attack_end(ui, encounter)
        return True
    else:
        encounter.combatant_attack_number += 1
        return False

def process_attack_end(ui, encounter) -> None:
    encounter.initiative -= 1
    encounter.combatant_attack_number = 1
    print('\n'+'-'*ui.SEPARATOR_LINE_LENGTH)

def process_attack_hit(ui, encounter, attacker, defender, to_hit_roll) -> None:
    if (attacker.damageperattack == None) or (len(str(attacker.damageperattack)) == 0):
        pass
    else:
        damageperattack = '\n    * ' + attacker.abbrseq + ' Damage Per Attack:\n      -- '+'\n      -- '.join(attacker.damageperattack.lstrip().split('|'))
        print(damageperattack)

    message = encounter.format_attack_type()
    if to_hit_roll == encounter.ATTACK_CRITICAL_HIT:
        message += " *Critical Hit*"
    else:
        message += " hit"
        
    raw_damage = ''
    raw_damage_prompt = f'\n  + Enter {message} damage: '
    while raw_damage == '':
        raw_damage = ui.get_input(raw_damage_prompt)
        if raw_damage.isnumeric():
            damage = int(raw_damage)
        else:
            print(f'    * {raw_damage} is not numeric. Try again')
            raw_damage = ''
            
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, damage, defender.xp, encounter.calculate_xp(defender.hpmax, defender.hp, damage, defender.xp), message+' BEFORE')
    defender.take_damage(damage)
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, 0, 0, message+' AFTER')
    encounter.data.update_combatant_hit_points(defender.abbr, defender.seq, defender.hpmax, defender.hp)    # update db with new post-damage hp
    print(f'    * {message} {defender.combattype} {defender.abbrseq} for {damage} points damage ({defender.hp} remaining)')
    return

def process_attack_miss(ui, encounter, attacker, defender, to_hit_roll) -> None:
    message = encounter.format_attack_type() + " missed"
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, defender.xp, 0, message)
    print(f'    * {message} {defender.combattype} {defender.abbrseq}')
    if ( to_hit_roll != encounter.ATTACK_CRITICAL_FUMBLE ):
        return

    # check if critically fumbled attack
    if len(input(f'      -- Is attack fumbled/cursed? ([Enter] for No, Y for Yes) ')) == 0:
        return

    # process critical fumble
    raw_damage = ''
    while raw_damage == '':
        raw_damage_prompt = f'\n  + Enter {attacker.abbr}{attacker.seq} self damage: '
        raw_damage = ui.get_input(raw_damage_prompt)
        if raw_damage.isnumeric():
            damage = int(raw_damage)
        else:
            print(f'    * {raw_damage} is not numeric. Try again')
            raw_damage = ''

        if attacker.combattype == encounter.COMBATTYPE_FRIEND:
            raw_xp = ''
            raw_xp_prompt = '    * Enter penalty xp (-number): '
            while raw_xp == '':
                raw_xp = ui.get_input(raw_xp_prompt)
                if is_negative_number_digit(raw_xp):
                    penalty_xp = int(raw_xp)
                else:
                    print(f'      -- {raw_xp} is not numeric. Try again')
                    raw_xp = ''

    message = encounter.format_attack_type() + " fumbled/cursed damage"
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, defender.initiative, attacker.hpmax, attacker.hp, damage, 0, penalty_xp, message+' BEFORE')
    attacker.take_damage(damage)
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, defender.initiative, attacker.hpmax, attacker.hp, 0, 0, 0, message+' AFTER')
    encounter.data.update_combatant_hit_points(attacker.abbr, attacker.seq, attacker.hpmax, attacker.hp)    # update db with new post-damage hp
    return

def process_attack_spell(ui, encounter, attacker, defender) -> None:
    spell_prompt = '    * Enter spell name: '
    spell = ui.get_input(spell_prompt)
    raw_damage = ''
    raw_spell_damage_prompt = '    * Enter spell damage (+/-number): '
    while raw_damage == '':
        raw_damage = ui.get_input(raw_spell_damage_prompt)
        if is_negative_number_digit(raw_damage):
            damage = int(raw_damage)
        else:
            print(f'      -- {raw_damage} is not numeric. Try again')
            raw_damage = ''

    if attacker.combattype == encounter.COMBATTYPE_FRIEND and defender.combattype == encounter.COMBATTYPE_FRIEND:
        # Attacker is performing spell on defender friend (typically healing)
        raw_xp = ''
        raw_xp_prompt = '    * Enter xp: '
        while raw_xp == '':
            raw_xp = ui.get_input(raw_xp_prompt)
            if raw_xp.isnumeric():
                earned_xp = int(raw_xp)
            else:
                print(f'      -- {raw_xp} is not numeric. Try again')
                raw_xp = ''
    else:
        # Calculate xp
        earned_xp = encounter.calculate_xp(defender.hpmax, defender.hp, damage, defender.xp)
        
    message = encounter.format_attack_type() + " spell: "+spell
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, damage, defender.xp, earned_xp, message+' BEFORE')
    defender.take_damage(damage)
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, 0, 0, message+' AFTER')
    encounter.data.update_combatant_hit_points(defender.abbr, defender.seq, defender.hpmax, defender.hp)    # update db with new post-damage hp
    print(f'    * Cast spell {spell} on {defender.abbrseq} for {damage} points damage ({defender.hp} remaining)')
    return

def process_combatant_initiative(ui, encounter) -> bool:
    print('\nEnter Initiative:')
    if encounter.round > 1:
        rollinitiative_prompt = f'- Re-roll initiative? (<Enter> for No, Y for Yes) '
        rollinitiative = ui.get_input(rollinitiative_prompt)
        if rollinitiative.lower() != 'y':
            return False
            
    for combatant in encounter.combatants:
        if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
            get_combatant_initiative(ui, encounter, combatant)
        else:
            combatant.initiative = encounter.roll_nonplayer_initiative()

    encounter.check_duplicate_initiative()
    for combatant in encounter.combatants:
        encounter.data.log_initiative(encounter.encounter, encounter.round, combatant.combattype, combatant.Abbr, combatant.seq, combatant.group, combatant.initiative)

def process_encounter_initiative(ui, encounter) -> None:
    raw_initiative = ''
    initiative_prompt = f'\nSet Initiative: (<Enter> for current: {encounter.initiative}, min/max: {encounter.INITIATIVE_MINIMUM}/{encounter.INITIATIVE_MAXIMUM}) '
    while len(raw_initiative) == 0:
        raw_initiative = ui.get_input(initiative_prompt)
        if len(raw_initiative) == 0:
            return
        
        if raw_initiative.isnumeric() == False:
            print('- Initiative must be numeric. Try again')
            raw_initiative = ''
            continue
        
        if (int(raw_initiative) < encounter.INITIATIVE_MINIMUM) or (int(raw_initiative) > encounter.INITIATIVE_MAXIMUM):
            print(f'- Initiative must be between {encounter.INITIATIVE_MINIMUM} and {encounter.INITIATIVE_MAXIMUM}. Try again')
            raw_initiative = ''
            continue
        
    encounter.initiative = int(raw_initiative)

def process_load_combatants(encounter) -> None:
    """load combatants into encounter"""
    print(encounter.format_encounter())
    encounter.load_combatants()
    
def process_load_participants(encounter) -> None:
    """load participant data from database into encounter"""
    encounter.load_participants()

def process_round(ui, encounter) -> None:
    """process round for each combatant"""
    round_type_prompt = f'\n- Is round missile or melee? [Enter] for missile, m for melee '
    continue_attack_prompt = f'Continue attacking? (<Enter> for Yes, N for No) '
    while True:
        initialize_round(ui, encounter)
        round_raw = ''
        round_raw = ui.get_input(round_type_prompt)
        encounter.ismissileattack = (len(round_raw) == 0)
        print(encounter.format_encounter(), encounter.format_attack_type(), ' Attacks')
        
        while encounter.initiative > encounter.INITIATIVE_NONE:
            encounter.count_available_combatants()
            if encounter.foe_count == 0:
                round_no_foes_prompt = f'- Encounter: {encounter.encounter} Round: {encounter.round} has no FOES. Continue? ([Enter] for No, y for Yes) '
                if len(ui.get_input(round_no_foes_prompt)) == 0:
                    delete_dead_opponents(encounter)
                    print(f'\n Encounter: {encounter.encounter} Round: {encounter.round} END:')
                    print(encounter.format_encounter())
                    print(encounter.format_combatants())
                    print('\n'+'-'*ui.SEPARATOR_LINE_LENGTH)
                    encounter.prepare_next_encounter()
                    print(encounter.format_encounter())
                    return
            
            checkforanotherattack = process_attack_sequence(ui, encounter)
            
            # check for end of normal round (initiative is set to NONE after last attacker's attack)
            if encounter.initiative == encounter.INITIATIVE_NONE:
                break
            
            if checkforanotherattack == True:
                if len(ui.get_input(continue_attack_prompt)) > 0:
                    delete_dead_opponents(encounter)
                    print(f'\nRound {encounter.round} ENDED *PREMATURALLY*')
                    print(encounter.format_encounter())
                    print(encounter.format_combatants())
                    print('\n'+'-'*ui.SEPARATOR_LINE_LENGTH)
                    encounter.prepare_next_round()
                    print(encounter.format_encounter())
                    return

        delete_dead_opponents(encounter)
        print(f'\nRound {encounter.round} END:')
        continue_prompt = f'\nBegin next round? (<Enter> = Yes, n = No) '
        next_round = ui.get_input(continue_prompt)
        if len(next_round) == 0:
            print('\n'+'-'*ui.SEPARATOR_LINE_LENGTH)
            encounter.prepare_next_round()
            print(encounter.format_encounter())
            print(encounter.format_combatants())
            continue

        continue_prompt = f'\nBegin next encounter? (<Enter> = Yes, n = No) '
        next_encounter = ui.get_input(continue_prompt)
        if len(next_encounter) == 0:
            encounter.prepare_next_encounter()

        print('\n'+'-'*ui.SEPARATOR_LINE_LENGTH)
        print(encounter.format_encounter())
        print(encounter.format_combatants())
        return                

if __name__ == '__main__':
    mm = MeleeManager()
    mm.main()
