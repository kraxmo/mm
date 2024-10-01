#mm.py

import abc
import lib.combatmodel as cm1
from lib.dice import Dice

EXIT_TO_MENU = "@@"

class Action(metaclass=abc.ABCMeta):
    def __init__(self, code, label):
        self.code = code
        self.label = label

    @abc.abstractmethod
    def process(self, ui, encounter):
        pass

class ExitToMenuException(Exception):
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

class MeleeManager():
    def __init__(self):
        self.ui = UI()

        print('')
        self.ui.print_separator_line('=')
        print('MELEE MANAGER')
        self.ui.print_separator_line('-')
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
            SetInitiativeAction(),
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
class QuitAction(Action):
    def __init__(self):
        super().__init__(99, 'Quit')

    def process(self, ui, encounter):
        encounter.data.close()
        raise QuitException

    def __str__(self):
        return f'{__class__.__name__}'

class QuitException(Exception):
    pass

class SetInitiativeAction(Action):
    def __init__(self):
        super().__init__(5, 'Set Encounter Initiative')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        return process_set_initiative(ui, encounter)
    
class UI:
    SEPARATOR_LINE_LENGTH = 97
    INDENT_LEVEL_01 = '- '
    INDENT_LEVEL_02 = '  + '
    INDENT_LEVEL_03 = '    * '
    INDENT_LEVEL_04 = '      -- '
    
    def print_separator_line(self, value, newlinebefore = False):
        newline = ''
        if newlinebefore == True:
            newline = '\n'
            
        print(f"{newline}{value*self.SEPARATOR_LINE_LENGTH}")
    
    def get_input(self, action_prompt):
        value = input(action_prompt)
        
        # If exit to menu value is encountered, raise error
        if value.find(EXIT_TO_MENU) > -1:
            raise ExitToMenuException
    
        return value.upper()    # force uppercase values
    
    def get_numeric_input(self, action_prompt):
        while True:
            try:
                value = self.get_input(action_prompt)
                return int(value)
            except ValueError:
                print("Entered value must be numeric")

def find_next_defender(ui, encounter, attacker, combatants) -> cm1.Combatant:
    """find next available defender"""
    defender_abbrseq = ''
    while defender_abbrseq == '':
        if len(attacker.defender_abbrseq) == 0:
            message = f'{ui.INDENT_LEVEL_03}Who is {attacker.abbrseq} attacking? (abbrseq) '
        else:
            message = f'{ui.INDENT_LEVEL_03}Is {attacker.abbrseq} attacking {attacker.defender_abbrseq}? (<Enter> for existing or type new abbrseq) '
    
        defender_abbrseq = ui.get_input(message)
        if len(defender_abbrseq) == 0:
            if len(attacker.defender_abbrseq) == 0:
                print(f'{ui.INDENT_LEVEL_04}Please enter a defender abbrseq')
                defender_abbrseq = ''
                continue
            
            defender_abbrseq = attacker.defender_abbrseq
        elif defender_abbrseq == attacker.abbrseq:
                print(f'{ui.INDENT_LEVEL_04}{attacker.abbrseq} cannot self-attack. Try again')
                defender_abbrseq = ''
                continue
        else:
            if encounter.is_combatant(defender_abbrseq) == False:
                print(f'{ui.INDENT_LEVEL_04}defender {defender_abbrseq} does not exist. Try again')
                defender_abbrseq = ''
                continue
        
        defender_count = 0
        defender_is_invalid = False
        defender_is_dead = False
        for defender in combatants:
            defender_count += 1
            if defender.abbrseq == defender_abbrseq:
                if defender.combattype == attacker.combattype:
                    friend_prompt = f'{ui.INDENT_LEVEL_04}{attacker.abbrseq} and {defender.abbrseq} are both friends. Are you sure? (<Enter> for No, y for Yes) '
                    if len(ui.get_input(friend_prompt)) == 0:
                        defender_is_invalid = True
                        attacker.defender_abbrseq = ''
                        defender_abbrseq = ''
                        break

                if defender.is_alive():
                    attacker.defender_abbrseq = defender_abbrseq
                    return defender
                else:
                    defender_is_dead = True
                    print(f'{ui.INDENT_LEVEL_04}{defender.abbrseq} is dead')
                    attacker.defender_abbrseq = ''
                    defender_abbrseq = ''

                break

        if defender_is_dead or defender_is_invalid:
            continue
            
        if defender_count == len(combatants) and defender_abbrseq == '':
            return None

def get_all_combatants_initiative(ui, encounter) -> None:
    """get initiative for all combatants"""
    if encounter.round > 1:
        initiative_prompt = f'{ui.INDENT_LEVEL_01}Re-roll initiative? (<Enter> for No, Y for Yes) '
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
    """get combatant initiative values"""
    initiative_prompt = f"{ui.INDENT_LEVEL_01}{combatant.name}'s initiative? (<Enter> for previous value {combatant.initiative}) "
    while True:
        initiative = ui.get_input(initiative_prompt)
        if len(initiative) == 0:
            initiative = combatant.initiative
            return
        
        elif initiative.isnumeric() == False:
            print(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is not numeric')
            initiative = ''
            continue
        
        if int(initiative) < encounter.INITIATIVE_MINIMUM:
            print(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is less than {encounter.INITIATIVE_MINIMUM}')
            initiative = ''
            continue

        elif int(initiative) > encounter.INITIATIVE_MAXIMUM:
            print(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is more than {encounter.INITIATIVE_MAXIMUM}')
            initiative = ''
            continue

        elif int(initiative) < encounter.INITIATIVE_ACTIVE_MINIMUM:
            inactive_initiative_prompt = f'{ui.INDENT_LEVEL_03}Initiative value {initiative} is for inactive combatants. Keep it? (<Enter> = Yes, N = No) '
            if len(ui.get_input(inactive_initiative_prompt)) == 0:
                combatant.initiative = int(initiative)
                inactivereason = ''
                while len(inactivereason) == 0:
                    message = f'{ui.INDENT_LEVEL_04}Reason for inactivity? '
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

def get_to_hit_roll(ui, encounter, combatant) -> int:
    """get to-hit roll value"""
    message = f"\n{ui.INDENT_LEVEL_02}Enter 'To Hit' d{encounter.TO_HIT_DIE} result: "
    if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
        message += f"({encounter.TO_HIT_DIE_SPECIAL_ATTACK} = special attack, {encounter.TO_HIT_DIE_MINIMUM}-{encounter.TO_HIT_DIE_MAXIMUM} manual entry) "
    else:
        message += f"(<Enter> = autoroll, {encounter.TO_HIT_DIE_SPECIAL_ATTACK} = special attack, {encounter.TO_HIT_DIE_MINIMUM}-{encounter.TO_HIT_DIE_MAXIMUM} manual entry) "
        
    to_hit_input = ''
    while to_hit_input == '':
        to_hit_input = ui.get_input(message)
        if to_hit_input.isnumeric() == False:
            if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
                print(f"{ui.INDENT_LEVEL_03}'To Hit' roll of '{to_hit_input}' is not a number.")
                to_hit_input = ''
                continue
            else:
                to_hit_roll = Dice.roll_die(encounter.TO_HIT_DIE)
                break

        to_hit_roll = int(to_hit_input)
        if to_hit_roll < encounter.TO_HIT_DIE_MINIMUM or to_hit_roll > encounter.TO_HIT_DIE_MAXIMUM:
            print(f"{ui.INDENT_LEVEL_03}'To Hit' roll must be between {encounter.TO_HIT_DIE_MINIMUM} and {encounter.TO_HIT_DIE_MAXIMUM}. Entered {to_hit_roll} value.")
            to_hit_input = ''
            continue
        
    print(f'\n{ui.INDENT_LEVEL_02}Rolled {to_hit_roll}')
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
    """process each attack: Return True for additional post-attacks check or False for no post-attack checks"""
    attacker = encounter.find_next_attacker()
    if attacker == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    print(f"{encounter.format_encounter()} | {encounter.format_attack_type()} Attacks")
    print(encounter.format_combatants())
    if attacker.is_inactive():
        message = f'\n{ui.INDENT_LEVEL_01}{attacker.abbrseq} is currently inactive.'
        if len(attacker.inactivereason) > 0:
            message += f' (last status: {attacker.inactivereason})'
            
        message += 'Should this change? (<Enter> = No, Y = Yes) '
        if len(ui.get_input(message)) > 0:
            status_prompt = f'{ui.INDENT_LEVEL_02}Change initiative or inactive status? (<Enter> for initiative, new inactive status) '
            status = ui.get_input(status_prompt)
            if len(status) == 0:
                get_combatant_initiative(ui, encounter, attacker)
                encounter.check_duplicate_initiative()
                if (attacker.initiative >= encounter.INITIATIVE_ACTIVE_MINIMUM):
                    attacker.inactivereason = ''
                    print(f'{ui.INDENT_LEVEL_02}{attacker.abbrseq} will be able to attack next round')
                else:
                    print(f'{ui.INDENT_LEVEL_02}{attacker.abbrseq} will remain inactive')
                    
                return True
            else:
                attacker.inactivereason = status

        encounter.initiative = attacker.initiative - 1
        return False

    print(f'\n{ui.INDENT_LEVEL_01}{attacker.abbrseq} turn: {attacker.AttacksPerRound} attack(s)/round')
    print(f'{ui.INDENT_LEVEL_02}{encounter.format_attack_type()} Attack #{encounter.combatant_attack_number}')

    skip_attack_prompt = f'{ui.INDENT_LEVEL_02}Skip attack? (<Enter> = No, y = Yes) '
    skip_attack = ui.get_input(skip_attack_prompt)
    if len(skip_attack) > 0:
        print(f'{ui.INDENT_LEVEL_02}ATTACK SKIPPED')
        process_attack_end(ui, encounter)
        return False

    print(f'{ui.INDENT_LEVEL_02}ATTACKING...')
    special_attack_message = attacker.format_special_attacks()
    if len(special_attack_message): print(special_attack_message)

    defender = ''
    defender = find_next_defender(ui, encounter, attacker, encounter.combatants)
    if defender == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    special_defense_message = defender.format_special_defense()
    if len(special_defense_message): print(special_defense_message)
    
    to_hit_roll = get_to_hit_roll(ui, encounter, attacker)
    if to_hit_roll == encounter.TO_HIT_DIE_SPECIAL_ATTACK:    # special attack
        process_attack_special(ui, encounter, attacker, defender, )
    elif (to_hit_roll == encounter.ATTACK_CRITICAL_HIT) or (attacker.was_hit_successful(to_hit_roll, defender.ac, defender.defensemodifier)):
        process_attack_hit(ui, encounter, attacker, defender, to_hit_roll)
    else:
        process_attack_miss(ui, encounter, attacker, defender, to_hit_roll)
    
    if defender.is_alive() == False:
        encounter.foe_count -= 1
        attacker.defender_abbrseq = ''

    attack_prompt = f'\n{ui.INDENT_LEVEL_02}Attack again? (<Enter> = No, y = Yes) '
    attack_again = ui.get_input(attack_prompt)
    if len(attack_again) == 0:
        process_attack_end(ui, encounter)
        return True
    else:
        encounter.combatant_attack_number += 1
        return False

def process_attack_end(ui, encounter) -> None:
    """process end of attack activities"""
    encounter.initiative -= 1
    encounter.combatant_attack_number = 1
    ui.print_separator_line('-', True)

def process_attack_hit(ui, encounter, attacker, defender, to_hit_roll) -> None:
    """process attack hit"""
    print(attacker.format_damage())
    message = encounter.format_attack_type()
    if to_hit_roll == encounter.ATTACK_CRITICAL_HIT:
        message += " *Critical Hit*"
    else:
        message += " hit"
        
    raw_damage = ''
    raw_damage_prompt = f'\n{ui.INDENT_LEVEL_02}Enter {message} damage: '
    while raw_damage == '':
        raw_damage = ui.get_input(raw_damage_prompt)
        if raw_damage.isnumeric():
            damage = int(raw_damage)
        else:
            print(f'{ui.INDENT_LEVEL_03}{raw_damage} is not numeric. Try again')
            raw_damage = ''
            
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, damage, defender.xp, encounter.calculate_earned_xp(defender.hpmax, defender.hp, damage, defender.xp), message+' BEFORE')
    defender.take_damage(damage)
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, 0, 0, message+' AFTER')
    encounter.data.update_combatant_hit_points(defender.abbr, defender.seq, defender.hpmax, defender.hp)    # update db with new post-damage hp
    print(f'{ui.INDENT_LEVEL_03}{message} {defender.combattype} {defender.abbrseq} for {damage} points damage ({defender.hp} remaining)')
    return

def process_attack_miss(ui, encounter, attacker, defender, to_hit_roll) -> None:
    """process attack miss"""
    message = encounter.format_attack_type() + " missed"
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, defender.xp, 0, message)
    print(f'{ui.INDENT_LEVEL_03}{message} {defender.combattype} {defender.abbrseq}')
    if ( to_hit_roll != encounter.ATTACK_CRITICAL_FUMBLE ):
        return

    # check if critically fumbled attack
    if len(input(f'{ui.INDENT_LEVEL_04}Is attack fumbled/cursed? ([Enter] for No, Y for Yes) ')) == 0:
        return

    # process critical fumble
    raw_damage = ''
    penalty_xp = 0
    while raw_damage == '':
        raw_damage_prompt = f'\n{ui.INDENT_LEVEL_02}Enter {attacker.abbr}{attacker.seq} self damage: '
        raw_damage = ui.get_input(raw_damage_prompt)
        if raw_damage.isnumeric():
            damage = int(raw_damage)
        else:
            print(f'{ui.INDENT_LEVEL_03}{raw_damage} is not numeric. Try again')
            raw_damage = ''

        if attacker.combattype == encounter.COMBATTYPE_FRIEND:
            raw_xp = ''
            raw_xp_prompt = '{ui.INDENT_LEVEL_03}Enter penalty xp (-number): '
            while raw_xp == '':
                raw_xp = ui.get_input(raw_xp_prompt)
                if is_negative_number_digit(raw_xp):
                    penalty_xp = int(raw_xp)
                else:
                    print(f'{ui.INDENT_LEVEL_04}{raw_xp} is not numeric. Try again')
                    raw_xp = ''

    message = encounter.format_attack_type() + " fumbled/cursed damage"
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, defender.initiative, attacker.hpmax, attacker.hp, damage, 0, penalty_xp, message+' BEFORE')
    attacker.take_damage(damage)
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, defender.initiative, attacker.hpmax, attacker.hp, 0, 0, 0, message+' AFTER')
    encounter.data.update_combatant_hit_points(attacker.abbr, attacker.seq, attacker.hpmax, attacker.hp)    # update db with new post-damage hp
    return

def process_attack_special(ui, encounter, attacker, defender) -> None:
    """process special attack (spell, multiple defenders, multiple groups)"""
    special_attack_prompt = '{ui.INDENT_LEVEL_03}Enter special attack name: '
    special_attack = ui.get_input(special_attack_prompt)
    raw_damage = ''
    raw_special_attack_damage_prompt = '{ui.INDENT_LEVEL_03}Enter special attack damage (+/-number): '
    while raw_damage == '':
        raw_damage = ui.get_input(raw_special_attack_damage_prompt)
        if is_negative_number_digit(raw_damage):
            damage = int(raw_damage)
        else:
            print(f'{ui.INDENT_LEVEL_04}{raw_damage} is not numeric. Try again')
            raw_damage = ''

    # prompt if special attack only affects defender or others (can include defender)
    opponents = []
    special_attack_opponents_message = f"{ui.INDENT_LEVEL_02}Does special attack only affect {defender.abbrseq}? ([Enter] = yes, N = No) "
    if len(ui.get_input(special_attack_opponents_message)) == 0:
        opponents.append(defender)
    else:
        special_attack_opponents = []
        special_attack_opponents_message = f"{ui.INDENT_LEVEL_02}Enter comma-delimited opponents by abbrseq and/or #group: "
        special_attack_opponents_raw = ''
        while len(special_attack_opponents_raw) == 0:
            special_attack_opponents_raw = ui.get_input(special_attack_opponents_message)
            if len(special_attack_opponents_raw) == 0:
                print('{ui.INDENT_LEVEL_01}No opponents entered. Try again!')
                continue
        
        special_attack_opponents_raw
        for opponent_raw in special_attack_opponents_raw.split(','):
            opponent_raw = opponent_raw.strip()
            
            # skip if empty value
            if len(opponent_raw) == 0:
                continue
            
            # if opponent_raw is not a group
            if opponent_raw[0:1] == '#':
                special_attack_opponents.append(opponent_raw)
                continue
            
            # if opponent_raw is in the combatant list
            if encounter.is_combatant(opponent_raw):
                special_attack_opponents.append(opponent_raw)
                continue
            
            # handle missing opponent
            missing_opponent = ''
            missing_opponent_message = f"{ui.INDENT_LEVEL_03}Opponent \'{opponent_raw}\' is not in the combatant list. Re-enter abbrseq or [Enter] to ignore? "
            while missing_opponent == '':
                missing_opponent = ui.get_input(missing_opponent_message).strip()
                # exclude opponent_raw
                if len(missing_opponent) == 0:
                    break
                
                # accept entered group as-is
                if missing_opponent[0:1] == '#':
                    continue
                
                # validate missing_opponent is in combatant list
                if encounter.is_combatant(missing_opponent) == False:
                    missing_opponent = ''
                    continue

                special_attack_opponents.append(missing_opponent)
            
        # exit if no special_attack_opponents after validation
        if len(special_attack_opponents) == 0:
            return
        
        # build opponent group list
        special_attack_groups = [group[1:] for group in special_attack_opponents if group[0:1] == '#']
        
        # append unique group opponents to opponent list
        [special_attack_opponents.append(combatant.abbrseq) for combatant in encounter.combatants if (combatant.group in special_attack_groups) and (combatant.abbrseq not in special_attack_opponents)]

        # get opponents (ignoring groups)
        [opponents.append(combatant) for combatant in encounter.combatants if combatant.abbrseq in special_attack_opponents]

        # exit if no opponents after validation
        if len(opponents) == 0:
            return

    # process individual special attack vs. opponent
    for opponent in opponents:
        if attacker.combattype == encounter.COMBATTYPE_FRIEND and opponent.combattype == encounter.COMBATTYPE_FRIEND:
            # Attacker is performing special attack on opponent friend (typically healing)
            raw_xp = ''
            raw_xp_prompt = '{ui.INDENT_LEVEL_03}Enter xp: '
            while raw_xp == '':
                raw_xp = ui.get_input(raw_xp_prompt)
                if raw_xp.isnumeric():
                    earned_xp = int(raw_xp)
                else:
                    print(f'{ui.INDENT_LEVEL_04}{raw_xp} is not numeric. Try again')
                    raw_xp = ''
        else:
            # Calculate xp
            earned_xp = encounter.calculate_earned_xp(opponent.hpmax, opponent.hp, damage, opponent.xp)
            
        message = encounter.format_attack_type() + " special attack: "+special_attack
        encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, opponent.combattype, opponent.abbr, opponent.seq, opponent.group, opponent.initiative, opponent.hpmax, opponent.hp, damage, opponent.xp, earned_xp, message+' BEFORE')
        opponent.take_damage(damage)
        encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, opponent.combattype, opponent.abbr, opponent.seq, opponent.group, opponent.initiative, opponent.hpmax, opponent.hp, 0, 0, 0, message+' AFTER')
        encounter.data.update_combatant_hit_points(opponent.abbr, opponent.seq, opponent.hpmax, opponent.hp)    # update db with new post-damage hp
        print(f'{ui.INDENT_LEVEL_03}Executed special attack {special_attack} on {opponent.abbrseq} for {damage} points damage ({opponent.hp} remaining)')
    
    return
  
    # KEEP  
    # damage factor = 1.0
    # input: special attack need saving throw checks?
    # If YES:
    # - input: type of saving throw?
    # - input: saving throw for PC, and autoroll for NPC/M
    # - check result vs. check saving throw table to determine damage factor
    # Apply int(total damage * damage factor) across all opponents
            
def process_combatant_initiative(ui, encounter) -> bool:
    """process getting initiative for all combatants"""
    print('\nEnter Initiative:')
    if encounter.round > 1:
        rollinitiative_prompt = f'{ui.INDENT_LEVEL_01}Re-roll initiative? (<Enter> for No, Y for Yes) '
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

def process_set_initiative(ui, encounter) -> None:
    """process setting current encounter's initiative"""
    raw_initiative = ''
    initiative_prompt = f'\nSet Initiative: (<Enter> for current: {encounter.initiative}, min/max: {encounter.INITIATIVE_MINIMUM}/{encounter.INITIATIVE_MAXIMUM}) '
    while len(raw_initiative) == 0:
        raw_initiative = ui.get_input(initiative_prompt)
        if len(raw_initiative) == 0:
            return
        
        if raw_initiative.isnumeric() == False:
            print('{ui.INDENT_LEVEL_01}Initiative must be numeric. Try again')
            raw_initiative = ''
            continue
        
        if (int(raw_initiative) < encounter.INITIATIVE_MINIMUM) or (int(raw_initiative) > encounter.INITIATIVE_MAXIMUM):
            print(f'{ui.INDENT_LEVEL_01}Initiative must be between {encounter.INITIATIVE_MINIMUM} and {encounter.INITIATIVE_MAXIMUM}. Try again')
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
    round_type_prompt = f'Is round missile or melee? [Enter] for missile, m for melee '
    continue_attack_prompt = f'Continue attacking? (<Enter> for Yes, N for No) '
    while True:
        initialize_round(ui, encounter)
        round_raw = ''
        round_raw = ui.get_input(round_type_prompt)
        encounter.ismissileattack = (len(round_raw) == 0)
        
        while encounter.initiative > encounter.INITIATIVE_NONE:
            encounter.count_available_combatants()
            if encounter.foe_count == 0:
                round_no_foes_prompt = f'{ui.INDENT_LEVEL_01}Encounter: {encounter.encounter} Round: {encounter.round} has no FOES. Continue? ([Enter] for No, y for Yes) '
                if len(ui.get_input(round_no_foes_prompt)) == 0:
                    encounter.delete_dead_oponents()
                    print(f'\n Encounter: {encounter.encounter} Round: {encounter.round} END:')
                    print(encounter.format_encounter())
                    print(encounter.format_combatants())
                    ui.print_separator_line('-', True)
                    encounter.prepare_next_encounter()
                    print(encounter.format_encounter())
                    return
            
            checkforanotherattack = process_attack_sequence(ui, encounter)
            
            # check for end of normal round (initiative is set to NONE after last attacker's attack)
            if encounter.initiative == encounter.INITIATIVE_NONE:
                break
            
            if checkforanotherattack == True:
                if len(ui.get_input(continue_attack_prompt)) > 0:
                    encounter.delete_dead_oponents()
                    print(f'\nRound {encounter.round} ENDED *PREMATURALLY*')
                    encounter.prepare_next_round()
                    print(encounter.format_encounter())
                    return

        encounter.delete_dead_oponents()
        print(f'\nRound {encounter.round} END:')
        continue_prompt = f'\nBegin next round? (<Enter> = Yes, n = No) '
        next_round = ui.get_input(continue_prompt)
        if len(next_round) == 0:
            ui.print_separator_line('-', True)
            encounter.prepare_next_round()
            print(encounter.format_encounter())
            print(encounter.format_combatants())
            continue

        continue_prompt = f'\nBegin next encounter? (<Enter> = Yes, n = No) '
        next_encounter = ui.get_input(continue_prompt)
        if len(next_encounter) == 0:
            encounter.prepare_next_encounter()
        
        ui.print_separator_line('-', True)
        print(encounter.format_encounter())
        print(encounter.format_combatants())
        return                

if __name__ == '__main__':
    mm = MeleeManager()
    mm.main()
