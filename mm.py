#mm.py

import abc
import lib.combatmodel as cm1
from lib.dice import Dice
import lib.ui as ui1

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
        ui.output(encounter.format_encounter())
        ui.output(encounter.format_combatants())
        return

class ListCombatantsInformation(Action):
    def __init__(self):
        super().__init__(6, 'List Combatant Information')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        ui.output(f"\nCombatant Information:")
        for combatant in encounter.combatants:
            if combatant.combattype != encounter.COMBATTYPE_FRIEND:
                continue
            
            if combatant.charactertype == cm1.Combatant.TYPE_MONSTER:
                continue
            
            special_attacks = combatant.format_special_attacks()
            special_defense = combatant.format_special_defense()
            notes = combatant.format_notes()
            if (len(special_attacks) + len(special_defense) + len(notes)) > 0:
                ui.output(f"{ui.INDENT_LEVEL_02}{combatant.abbrseq}:")
                if len(special_attacks) > 0:
                    ui.output(f"{special_attacks}")
                    
                if len(special_defense) > 0:
                    ui.output(f"{special_defense}")
                    
                if len(notes) > 0:
                    ui.output(f"{notes}")

        return

class LoadCombatParticipantsAction(Action):
    def __init__(self):
        super().__init__(0, 'Load Combat Participants')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        process_load_participants(ui, encounter)
        return

class LoadCombatantsAction(Action):
    def __init__(self):
        super().__init__(1, 'Load Combatants')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        process_load_combatants(ui, encounter)
        return 

class MeleeManager():
    def __init__(self):
        self.ui = ui1.UI
        self.ui.output('')
        self.ui.output_separator_line('=')
        self.ui.output('MELEE MANAGER')
        self.ui.output_separator_line('-')
        self.ui.output("Press '@@' at any input prompt to return to menu")
        self.ui.output_separator_line('=')

        self.encounter = cm1.Encounter()
        process_load_participants(self.ui, self.encounter)
        process_load_combatants(self.ui, self.encounter)
        
        # define actions
        self.actions = [
            LoadCombatParticipantsAction(),
            LoadCombatantsAction(),
            ListCombatantsAction(),
            NextEncounterAction(),
            NextAttackAction(),
            SetInitiativeAction(),
            ListCombatantsInformation(),
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
            action_code = get_numeric_input(self.ui, self.action_prompt)
            try:
                action = self.actions_map[action_code]
            except KeyError:
                ui1.UI.output(f'*{action_code}* not a valid action\n')
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
        ui.output(encounter.format_encounter())
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
    
def get_input(ui, action_prompt, response_option = EXIT_TO_MENU, response_exception = ExitToMenuException):
    return ui.get_input(action_prompt, response_option, response_exception)
    
def get_numeric_input(ui, action_prompt, response_prefix='', response_option = EXIT_TO_MENU, response_exception = ExitToMenuException):
    return ui.get_numeric_input(action_prompt, response_prefix, response_option, response_exception)

def find_next_defender(ui, encounter, attacker, combatants) -> cm1.Combatant:
    """find next available defender"""
    defender_abbrseq = ''
    while defender_abbrseq == '':
        if len(attacker.defender_abbrseq) == 0:
            message = f'{ui.INDENT_LEVEL_02}Who is {attacker.abbrseq} attacking? (abbrseq) '
        else:
            message = f'{ui.INDENT_LEVEL_02}Is {attacker.abbrseq} attacking {attacker.defender_abbrseq}? (<Enter> for existing or type new abbrseq) '
    
        defender_abbrseq = get_input(ui, message)
        if len(defender_abbrseq) == 0:
            if len(attacker.defender_abbrseq) == 0:
                ui.output(f'{ui.INDENT_LEVEL_03}Please enter a defender abbrseq')
                defender_abbrseq = ''
                continue
            
            defender_abbrseq = attacker.defender_abbrseq
        elif defender_abbrseq == attacker.abbrseq:
                ui.output(f'{ui.INDENT_LEVEL_03}{attacker.abbrseq} cannot self-attack. Try again')
                defender_abbrseq = ''
                continue
        else:
            if encounter.is_combatant(defender_abbrseq) == False:
                ui.output(f'{ui.INDENT_LEVEL_03}defender {defender_abbrseq} does not exist. Try again')
                defender_abbrseq = ''
                continue
        
        defender_count = 0
        defender_is_invalid = False
        defender_is_dead = False
        for defender in combatants:
            defender_count += 1
            if defender.abbrseq == defender_abbrseq:
                if defender.combattype == attacker.combattype:
                    friend_prompt = f'{ui.INDENT_LEVEL_03}{attacker.abbrseq} and {defender.abbrseq} are both friends. Are you sure? (<Enter> for No, y for Yes) '
                    if len(get_input(ui, friend_prompt)) == 0:
                        defender_is_invalid = True
                        attacker.defender_abbrseq = ''
                        defender_abbrseq = ''
                        break

                if defender.is_alive():
                    attacker.defender_abbrseq = defender_abbrseq
                    return defender
                else:
                    defender_is_dead = True
                    ui.output(f'{ui.INDENT_LEVEL_03}{defender.abbrseq} is dead')
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
        rollinitiative = get_input(ui, initiative_prompt)
        if rollinitiative.lower() != 'y':
            return

    ui.output('\nEnter Initiative:')            
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
        initiative = get_input(ui, initiative_prompt)
        if len(initiative) == 0:
            initiative = combatant.initiative
            return
        
        elif initiative.isnumeric() == False:
            ui.output(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is not numeric')
            initiative = ''
            continue
        
        if int(initiative) < encounter.INITIATIVE_MINIMUM:
            ui.output(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is less than {encounter.INITIATIVE_MINIMUM}')
            initiative = ''
            continue

        elif int(initiative) > encounter.INITIATIVE_MAXIMUM:
            ui.output(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is more than {encounter.INITIATIVE_MAXIMUM}')
            initiative = ''
            continue

        elif int(initiative) < encounter.INITIATIVE_ACTIVE_MINIMUM:
            inactive_initiative_prompt = f'{ui.INDENT_LEVEL_03}Initiative value {initiative} is for inactive combatants. Keep it? (<Enter> = Yes, N = No) '
            if len(get_input(ui, inactive_initiative_prompt)) == 0:
                combatant.initiative = int(initiative)
                inactivereason = ''
                while len(inactivereason) == 0:
                    message = f'{ui.INDENT_LEVEL_04}Reason for inactivity? '
                    if len(combatant.inactivereason) > 0:
                        message += f'(<Enter> = keep previous value {combatant.inactivereason}, <Reason> = new inactive reason) '

                    inactivereason = get_input(ui, message)
                    
                combatant.inactivereason = inactivereason
                break
            else:
                continue
        else:
            combatant.initiative = int(initiative)
            break

def get_opponents(ui, encounter, attacker) -> list:
    opponents = []
    special_attack_opponents_message = f"{ui.INDENT_LEVEL_02}Enter comma-delimited opponents by abbrseq and/or #group: "
    special_attack_opponents_raw = ''
    while len(special_attack_opponents_raw) == 0:
        special_attack_opponents_raw = get_input(ui, special_attack_opponents_message)
        if len(special_attack_opponents_raw) == 0:
            ui.output(f"{ui.INDENT_LEVEL_03}No opponents entered. Try again!")
            continue
    
    special_attack_opponents = []
    for special_attack_opponent_raw in special_attack_opponents_raw.split(','):
        special_attack_opponent_raw = special_attack_opponent_raw.strip()
        
        # skip if empty value
        if len(special_attack_opponent_raw) == 0:
            continue
        
        # if special_attack_opponent_raw is not a group
        if special_attack_opponent_raw[0:1] == '#':
            special_attack_opponents.append(special_attack_opponent_raw)
            continue
        
        # if special_attack_opponent_raw is in the combatant list
        if encounter.is_combatant(special_attack_opponent_raw):
            special_attack_opponents.append(special_attack_opponent_raw)
            continue
        
        # handle missing opponent
        missing_opponent = ''
        missing_opponent_message = f"{ui.INDENT_LEVEL_03}Opponent \'{special_attack_opponent_raw}\' is not in the combatant list. Re-enter abbrseq or [Enter] to ignore? "
        while missing_opponent == '':
            missing_opponent = get_input(ui, missing_opponent_message).strip()
            # exclude special_attack_opponent_raw
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
    
    if len(special_attack_opponents) == 0:
        return
    
    # build opponent group list
    special_attack_groups = [group[1:] for group in special_attack_opponents if group[0:1] == '#']
    
    # append unique group opponents to opponent list
    [special_attack_opponents.append(combatant.abbrseq) for combatant in encounter.combatants if (combatant.abbrseq != attacker.abbrseq) and (combatant.group in special_attack_groups) and (combatant.abbrseq not in special_attack_opponents)]

    # get opponents (ignoring groups)
    [opponents.append(combatant) for combatant in encounter.combatants if combatant.abbrseq in special_attack_opponents]
    
    return opponents

def get_to_hit_roll(ui, encounter, combatant) -> int:
    """get to-hit roll value"""
    message = f"\n{ui.INDENT_LEVEL_02}Enter 'To Hit' d{encounter.TO_HIT_DIE} result: "
    if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
        message += f"({encounter.TO_HIT_DIE_SPECIAL_ATTACK} = special attack, {encounter.TO_HIT_DIE_MINIMUM}-{encounter.TO_HIT_DIE_MAXIMUM} manual entry) "
    else:
        message += f"(<Enter> = autoroll, {encounter.TO_HIT_DIE_SPECIAL_ATTACK} = special attack, {encounter.TO_HIT_DIE_MINIMUM}-{encounter.TO_HIT_DIE_MAXIMUM} manual entry) "
        
    to_hit_input = ''
    while to_hit_input == '':
        to_hit_input = get_input(ui, message)
        if to_hit_input.isnumeric() == False:
            if combatant.charactertype == combatant.TYPE_PLAYER_CHARACTER:
                ui.output(f"{ui.INDENT_LEVEL_03}'To Hit' roll of '{to_hit_input}' is not a number.")
                to_hit_input = ''
                continue
            else:
                to_hit_roll = Dice.roll_die(encounter.TO_HIT_DIE)
                break

        to_hit_roll = int(to_hit_input)
        if to_hit_roll < encounter.TO_HIT_DIE_MINIMUM or to_hit_roll > encounter.TO_HIT_DIE_MAXIMUM:
            ui.output(f"{ui.INDENT_LEVEL_03}'To Hit' roll must be between {encounter.TO_HIT_DIE_MINIMUM} and {encounter.TO_HIT_DIE_MAXIMUM}. Entered {to_hit_roll} value.")
            to_hit_input = ''
            continue
    
    ui.output(f'\n{ui.INDENT_LEVEL_02}Rolled {to_hit_roll}')    
    return to_hit_roll
    
def initialize_round(ui, encounter) -> None:
    """initialize round for attacks"""
    ui.output(encounter.format_encounter())
    ui.output(encounter.format_combatants())

    message = '\nRoll initiative for all combatants? (<Enter> = Yes, N = No) '
    if len(get_input(ui, message)) == 0:
        # Determine initiative for all combatants
        get_all_combatants_initiative(ui, encounter)

    ui.output(encounter.format_encounter())
    ui.output(encounter.format_combatants())
    encounter.combatant_attack_number = 1
    
def is_negative_number_digit(n: str) -> bool:
    """check for negative number in passed string value"""
    try:
        int(n)
        return True
    except ValueError:
        return False

def log_hit_action(ui, encounter, attacker, defender, damage, xp_total, xp_earned, message):
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, damage, defender.xp, encounter.calculate_earned_xp(defender.hpmax, defender.hp, damage, defender.xp), message+' BEFORE')
    defender.take_damage(damage)
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, 0, 0, message+' AFTER')
    encounter.data.update_combatant_hit_points(defender.abbr, defender.seq, defender.hpmax, defender.hp)    # update db with new post-damage hp

def process_attack_sequence(ui, encounter) -> bool:
    """process each attack: Return True for additional post-attacks check or False for no post-attack checks"""
    attacker = encounter.find_next_attacker()
    if attacker == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    ui.output(f"{encounter.format_encounter()} | {encounter.format_attack_type()} Attacks")
    ui.output(encounter.format_combatants())
    if attacker.is_inactive():
        message = f'\n{ui.INDENT_LEVEL_01}{attacker.abbrseq} is currently inactive.'
        if len(attacker.inactivereason) > 0:
            message += f' (last status: {attacker.inactivereason})'
            
        message += 'Should this change? (<Enter> = No, Y = Yes) '
        if len(get_input(ui, message)) > 0:
            status_prompt = f'{ui.INDENT_LEVEL_02}Change initiative or inactive status? (<Enter> for initiative, new inactive status) '
            status = get_input(ui, status_prompt)
            if len(status) == 0:
                get_combatant_initiative(ui, encounter, attacker)
                encounter.check_duplicate_initiative()
                if (attacker.initiative >= encounter.INITIATIVE_ACTIVE_MINIMUM):
                    attacker.inactivereason = ''
                    ui.output(f'{ui.INDENT_LEVEL_02}{attacker.abbrseq} will be able to attack next round')
                else:
                    ui.output(f'{ui.INDENT_LEVEL_02}{attacker.abbrseq} will remain inactive')
                    
                return True
            else:
                attacker.inactivereason = status

        encounter.initiative = attacker.initiative - 1
        return False

    ui.output(f'\n{ui.INDENT_LEVEL_01}{attacker.abbrseq} turn: {attacker.AttacksPerRound} attack(s)/round')
    ui.output(f'{ui.INDENT_LEVEL_02}{encounter.format_attack_type()} Attack #{encounter.combatant_attack_number}')

    skip_attack_prompt = f'{ui.INDENT_LEVEL_02}Skip attack? (<Enter> = No, y = Yes) '
    skip_attack = get_input(ui, skip_attack_prompt)
    if len(skip_attack) > 0:
        ui.output(f'{ui.INDENT_LEVEL_02}ATTACK SKIPPED')
        process_attack_end(ui, encounter)
        return False

    ui.output(f'{ui.INDENT_LEVEL_02}ATTACKING...')
    special_attack_message = attacker.format_special_attacks()
    if len(special_attack_message):
        ui.output(special_attack_message)

    defender = ''
    defender = find_next_defender(ui, encounter, attacker, encounter.combatants)
    if defender == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    special_defense_message = defender.format_special_defense()
    if len(special_defense_message): 
        ui.output(special_defense_message)
    
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
    attack_again = get_input(ui, attack_prompt)
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
    ui.output_separator_line('-', True)

def process_attack_hit(ui, encounter, attacker, defender, to_hit_roll) -> None:
    """process attack hit"""
    ui.output(attacker.format_damage_per_attack())
    message = encounter.format_attack_type()
    if to_hit_roll == encounter.ATTACK_CRITICAL_HIT:
        message += " *Critical Hit*"
    else:
        message += " hit"
        
    damage_raw = ''
    damage_raw_prompt = f'{ui.INDENT_LEVEL_02}Enter {message} damage: '
    while damage_raw == '':
        damage_raw = get_input(ui, damage_raw_prompt)
        if damage_raw.isnumeric():
            damage = int(damage_raw)
        else:
            ui.output(f'{ui.INDENT_LEVEL_03}{damage_raw} is not numeric. Try again')
            damage_raw = ''
            
    log_hit_action(ui, encounter, attacker, defender, damage, defender.xp, encounter.calculate_earned_xp(defender.hpmax, defender.hp, damage, defender.xp), message)
    ui.output(f'{ui.INDENT_LEVEL_03}{message} {defender.combattype} {defender.abbrseq} for {damage} points damage ({defender.hp} remaining)')
    return

def process_attack_miss(ui, encounter, attacker, defender, to_hit_roll) -> None:
    """process attack miss"""
    message = encounter.format_attack_type() + " missed"
    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, defender.xp, 0, message)
    ui.output(f'{ui.INDENT_LEVEL_03}{message} {defender.combattype} {defender.abbrseq}')
    if ( to_hit_roll != encounter.ATTACK_CRITICAL_FUMBLE ):
        return

    # check if critically fumbled attack
    fumbled_prompt = f"{ui.INDENT_LEVEL_04}Is attack fumbled/cursed? ([Enter] for No, Y for Yes) "
    if len(get_input(ui, fumbled_prompt)) == 0:
        return

    # process critical fumble
    damage_raw = ''
    penalty_xp = 0
    while damage_raw == '':
        damage_raw_prompt = f'\n{ui.INDENT_LEVEL_02}Enter {attacker.abbr}{attacker.seq} self damage: '
        damage_raw = get_input(ui, damage_raw_prompt)
        if damage_raw.isnumeric():
            damage = int(damage_raw)
        else:
            ui.output(f'{ui.INDENT_LEVEL_03}{damage_raw} is not numeric. Try again')
            damage_raw = ''

        if attacker.combattype == encounter.COMBATTYPE_FRIEND:
            raw_xp = ''
            raw_xp_prompt = '{ui.INDENT_LEVEL_03}Enter penalty xp (-number): '
            while raw_xp == '':
                raw_xp = get_input(ui, raw_xp_prompt)
                if is_negative_number_digit(raw_xp):
                    penalty_xp = int(raw_xp)
                else:
                    ui.output(f'{ui.INDENT_LEVEL_04}{raw_xp} is not numeric. Try again')
                    raw_xp = ''

    message = encounter.format_attack_type() + " fumbled/cursed damage"
    log_hit_action(ui, encounter, attacker, defender, damage, 0, penalty_xp, message)
    return

def process_attack_special(ui, encounter, attacker, defender) -> None:
    """process special attack (spell, multiple defenders, multiple groups)"""
    special_attack_prompt = f"{ui.INDENT_LEVEL_03}Enter special attack name: "
    special_attack = get_input(ui, special_attack_prompt)

    # prompt if special attack only affects defender or others (can include defender)
    opponents = []
    special_attack_opponents_message = f"{ui.INDENT_LEVEL_02}Does special attack only affect {defender.abbrseq}? ([Enter] = yes, N = No) "
    if len(get_input(ui, special_attack_opponents_message)) == 0:
        opponents.append(defender)
    else:
        # build multiple opponent list (can include FRIEND and FOE!!!)
        opponent_list_verified = False
        while opponent_list_verified == False:
            opponents = get_opponents(ui, encounter, attacker)
            opponent_list = [opponent.abbrseq for opponent in opponents]
            opponent_list_prompt = f"{ui.INDENT_LEVEL_03}Opponent list:"
            opponent_list_prompt += f"\n{ui.INDENT_LEVEL_04}{('\n'+ui.INDENT_LEVEL_04).join(opponent_list)}"
            opponent_list_prompt += f"\n{ui.INDENT_LEVEL_03}Is this opponent list correct? ([Enter = Yes, N = No]) "
            if len(ui.get_input(opponent_list_prompt)) == 0:
                opponent_list_verified = True
            
        if len(opponents) == 0:
            return

    # process saving throw
    saving_throw_permitted = False
    saving_throw_half_damage = False
    saving_throw_prompt = f"{ui.INDENT_LEVEL_03}Is saving throw allowed? ([Enter] for Yes, N for No) "
    if len(get_input(ui, saving_throw_prompt)) == 0:
        saving_throw_permitted = True
        saving_throw_prompt = f"{ui.INDENT_LEVEL_03}If save successful, opponent takes no damage or 50% damage? ([Enter] = None, Y = 50%) "
        if len(get_input(ui, saving_throw_prompt)) > 0:
            saving_throw_half_damage = True
        
        ui.output(f'{ui.INDENT_LEVEL_03}Saving Throw Types:')
        saving_throw_types = ''
        for index, saving_throw_type in enumerate(cm1.Saving_Throw.SAVING_THROW_TYPE, 1):
            saving_throw_types += f'{ui.INDENT_LEVEL_04}{str(index)}: {saving_throw_type}\n'
        
        ui.output(saving_throw_types)
        saving_throw_prompt = f'{ui.INDENT_LEVEL_03}Select saving throw type: '
        saving_throw_type = 0
        while saving_throw_type == 0:
            saving_throw_type_raw = get_numeric_input(ui, saving_throw_prompt, ui.INDENT_LEVEL_04)
            if (saving_throw_type_raw > 0) and (saving_throw_type_raw <= len(cm1.Saving_Throw.SAVING_THROW_TYPE)):
                saving_throw_type = saving_throw_type_raw - 1
                break

    opponent_list = [opponent.abbrseq for opponent in opponents]
    ui.output(f"{ui.INDENT_LEVEL_03}Opponent List: {', '.join(opponent_list)}")

    is_damage_variable = True
    if len(opponent_list) > 1:
        # for multiple opponents, check for variable damage by opponent
        if len(get_input(ui, f"{ui.INDENT_LEVEL_02}Enter damage for each opponent? [Enter = No, Y = Yes] ")) == 0:
            is_damage_variable = False

    # process individual special attack vs. opponent
    for index, opponent in enumerate(opponents, 1):
        ui.output(f"{ui.INDENT_LEVEL_02}Opponent: {opponent.abbrseq}")
        saving_throw_modifier = 1.0
        if saving_throw_permitted == True:
            saving_throw = encounter.get_saving_throw(opponent.savingthrowclasstype, opponent.savingthrowlevel, opponent.savingthrowlevelpdm, cm1.Saving_Throw.SAVING_THROW_TYPE[saving_throw_type])
            if opponent.charactertype == opponent.TYPE_PLAYER_CHARACTER:
                saving_throw_prompt = f"{ui.INDENT_LEVEL_03}Enter {opponent.abbrseq}'s save vs. {cm1.Saving_Throw.SAVING_THROW_TYPE[saving_throw_type]}: ({saving_throw} needed) "
                saving_throw_value = 0
                while saving_throw_value == 0:
                    saving_throw_value_raw = get_numeric_input(ui, saving_throw_prompt, ui.INDENT_LEVEL_04)
                    if (saving_throw_value_raw > 0) and (saving_throw_value_raw <= encounter.TO_HIT_DIE):
                        saving_throw_value = saving_throw_value_raw
                        break
            else:
                saving_throw_value = Dice.roll_die(encounter.TO_HIT_DIE)

            if saving_throw_value >= saving_throw:
                if saving_throw_half_damage:
                    saving_throw_modifier = 0.5
                else:
                    saving_throw_modifier = 0

        message = f"{encounter.format_attack_type()} special attack: \'{special_attack}\'"
        ui.output(ui.INDENT_LEVEL_03+message)
        
        # enter damage if it varies for opponent or if first opponent (does not vary)
        if (is_damage_variable == True) or (index == 1):
            damage_base_raw = ''
            raw_special_attack_damage_prompt = f"{ui.INDENT_LEVEL_03}Enter special attack damage (+/-number): "
            while damage_base_raw == '':
                damage_base_raw = get_input(ui, raw_special_attack_damage_prompt)
                if is_negative_number_digit(damage_base_raw):
                    damage_base = int(damage_base_raw)
                else:
                    ui.output(f'{ui.INDENT_LEVEL_04}{damage_base_raw} is not numeric. Try again')
                    damage_base_raw = ''

        damage = int(damage_base * saving_throw_modifier)

        output_message = '~~'
        if (saving_throw_permitted):
            if saving_throw_modifier == 0:
                output_message = f"Saving throw made (rolled {saving_throw_value} needed {saving_throw})"
                message += f" (Save GOOD: {saving_throw_value} >= {saving_throw})"
            elif saving_throw_modifier == 1.0:
                output_message = f"Saving throw failed (rolled {saving_throw_value} needed {saving_throw}) Full damage {damage}"
                message += f" (Save FAIL: {saving_throw_value} > {saving_throw}) Full damage taken"
            else:
                output_message = f"Saving throw made (rolled {saving_throw_value} needed {saving_throw}) Half damage {damage}"
                message += f" (Save GOOD: {saving_throw_value} >= {saving_throw}) Half damage taken"

        if attacker.combattype == encounter.COMBATTYPE_FRIEND and opponent.combattype == encounter.COMBATTYPE_FRIEND:
            # Attacker is performing special attack on opponent friend (typically healing)
            xp_prompt = f'{ui.INDENT_LEVEL_03}Enter {opponent.abbrseq} xp for {cm1.Saving_Throw.SAVING_THROW_TYPE[saving_throw_type]}: '
            earned_xp_base = get_numeric_input(ui, xp_prompt)
        else:
            # Calculate xp
            earned_xp_base = encounter.calculate_earned_xp(opponent.hpmax, opponent.hp, damage, opponent.xp)
        
        earned_xp = int(earned_xp_base * saving_throw_modifier)
        log_hit_action(ui, encounter, attacker, defender, damage, opponent.xp, earned_xp, message)
        ui.output(ui.INDENT_LEVEL_04+output_message.replace('~~', 'Damage: '+str(damage))+f' Hit points remaining: {opponent.hp}')

    return

def process_combatant_initiative(ui, encounter) -> bool:
    """process getting initiative for all combatants"""
    ui.output('\nEnter Initiative:')
    if encounter.round > 1:
        rollinitiative_prompt = f'{ui.INDENT_LEVEL_01}Re-roll initiative? (<Enter> for No, Y for Yes) '
        rollinitiative = get_input(ui, rollinitiative_prompt)
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
        raw_initiative = get_input(ui, initiative_prompt)
        if len(raw_initiative) == 0:
            return
        
        if raw_initiative.isnumeric() == False:
            ui.output('{ui.INDENT_LEVEL_01}Initiative must be numeric. Try again')
            raw_initiative = ''
            continue
        
        if (int(raw_initiative) < encounter.INITIATIVE_MINIMUM) or (int(raw_initiative) > encounter.INITIATIVE_MAXIMUM):
            ui.output(f'{ui.INDENT_LEVEL_01}Initiative must be between {encounter.INITIATIVE_MINIMUM} and {encounter.INITIATIVE_MAXIMUM}. Try again')
            raw_initiative = ''
            continue
        
    encounter.initiative = int(raw_initiative)

def process_load_combatants(ui, encounter) -> None:
    """load combatants into encounter"""
    ui.output(encounter.format_encounter())
    encounter.load_combatants()
    
def process_load_participants(ui, encounter) -> None:
    """load participant data from database into encounter"""
    encounter.load_participants()

def process_round(ui, encounter) -> None:
    """process round for each combatant"""
    round_type_prompt = f'Is round missile or melee? [Enter] for missile, m for melee '
    continue_attack_prompt = f'Continue attacking? (<Enter> for Yes, N for No) '
    while True:
        initialize_round(ui, encounter)
        round_raw = ''
        round_raw = get_input(ui, round_type_prompt)
        encounter.ismissileattack = (len(round_raw) == 0)
        
        while encounter.initiative > encounter.INITIATIVE_NONE:
            encounter.count_available_combatants()
            if encounter.foe_count == 0:
                round_no_foes_prompt = f'{ui.INDENT_LEVEL_01}Encounter: {encounter.encounter} Round: {encounter.round} has no FOES. Continue? ([Enter] for No, y for Yes) '
                if len(get_input(ui, round_no_foes_prompt)) == 0:
                    encounter.delete_dead_oponents()
                    ui.output(f'\n Encounter: {encounter.encounter} Round: {encounter.round} END:')
                    ui.output(encounter.format_encounter())
                    ui.output(encounter.format_combatants())
                    ui.output_separator_line('-', True)
                    encounter.prepare_next_encounter()
                    ui.output(encounter.format_encounter())
                    return
            
            checkforanotherattack = process_attack_sequence(ui, encounter)
            
            # check for end of normal round (initiative is set to NONE after last attacker's attack)
            if encounter.initiative == encounter.INITIATIVE_NONE:
                break
            
            if checkforanotherattack == True:
                if len(get_input(ui, continue_attack_prompt)) > 0:
                    encounter.delete_dead_oponents()
                    ui.output(f'\nRound {encounter.round} ENDED *PREMATURALLY*')
                    encounter.prepare_next_round()
                    ui.output(encounter.format_encounter())
                    return

        encounter.delete_dead_oponents()
        ui.output(f'\nRound {encounter.round} END:')
        continue_prompt = f'\nBegin next round? (<Enter> = Yes, n = No) '
        next_round = get_input(ui, continue_prompt)
        if len(next_round) == 0:
            ui.output_separator_line('-', True)
            encounter.prepare_next_round()
            ui.output(encounter.format_encounter())
            ui.output(encounter.format_combatants())
            continue

        continue_prompt = f'\nBegin next encounter? (<Enter> = Yes, n = No) '
        next_encounter = get_input(ui, continue_prompt)
        if len(next_encounter) == 0:
            encounter.prepare_next_encounter()
        
        ui.output_separator_line('-', True)
        ui.output(encounter.format_encounter())
        ui.output(encounter.format_combatants())
        return                

if __name__ == '__main__':
    mm = MeleeManager()
    mm.main()
