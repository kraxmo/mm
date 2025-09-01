#mm.py

from abc import(
    ABCMeta,
    abstractmethod,
)
import lib.combatmodel as cm1
from lib.dice import Dice
import lib.ui as ui1

EXIT_TO_MENU = "@@"

class Action(metaclass=ABCMeta):
    """Abstract class for Actions"""
    def __init__(self, code, label):
        self.code = code
        self.label = label

    @abstractmethod
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
        if encounter.combatants:
            ui.output(encounter.format_encounter())
            ui.output(encounter.format_combatants())
        else:
            ui.output('\nNo combatants loaded')
        return

class ListCombatantsInformation(Action):
    def __init__(self):
        super().__init__(6, 'List Combatant Information')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        if encounter.combatants:
            ui.output(f"\nCombatant Information:")
            for combatant in encounter.combatants:
                if combatant.combattype != encounter.COMBATTYPE_FRIEND:
                    continue
                
                if combatant.is_monster():
                    continue
                
                special_attacks = combatant.format_special_attacks()
                special_defense = combatant.format_special_defense()
                notes           = combatant.format_notes()
                if (len(special_attacks) + len(special_defense) + len(notes)) > 0:
                    ui.output(f"{ui.INDENT_LEVEL_02}{combatant.typeabbrseq}:")
                    if len(special_attacks) > 0:
                        ui.output(f"{special_attacks}")
                        
                    if len(special_defense) > 0:
                        ui.output(f"{special_defense}")
                        
                    if len(notes) > 0:
                        ui.output(f"{notes}")
        else:
            ui.output('\nNo combatants loaded')
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
    @property
    def config_file(self):
        return r'C:\users\jkraxberger\pyproj\github\mm\config.ini'
    
    def __init__(self):
        self.ui = ui1.UI
        self.ui.output('')
        self.ui.output_separator_line('=')
        self.ui.output('MELEE MANAGER')
        self.ui.output_separator_line('-')
        self.ui.output("Press '@@' at any input prompt to return to menu")
        self.ui.output_separator_line('=')

        # get database reference
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
        if encounter.combatants:
            encounter.prepare_next_encounter()
            ui.output(encounter.format_encounter())
        else:
            ui.output('\nNo combatants loaded')
        return

class NextAttackAction(Action):
    def __init__(self):
        super().__init__(4, 'Next Attack')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        if encounter.combatants:
            process_round(ui, encounter)
        else:
            ui.output('\nNo combatants loaded')
        return

class QuitAction(Action):
    def __init__(self):
        super().__init__(99, 'Quit')

    def process(self, ui, encounter):
        encounter.combat_data.close()
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
        if encounter.combatants:
            process_set_initiative(ui, encounter)
        else:
            ui.output('\nNo combatants loaded')
        return

def get_input(ui, action_prompt, response_option = EXIT_TO_MENU, response_exception = ExitToMenuException) -> str:
    """get input from keyboard"""
    return ui.get_input(action_prompt, response_option, response_exception)
    
def get_numeric_input(ui, action_prompt, response_prefix='', response_option = EXIT_TO_MENU, response_exception = ExitToMenuException) -> int:
    """get numeric input from keyboard"""
    return ui.get_numeric_input(action_prompt, response_prefix, response_option, response_exception)

def find_next_defender(ui, encounter, attacker) -> cm1.Combatant:
    """find next available defender
    
    Args:
        ui: user interface
        encounter: current encounter
        attacker: current attacker
        
    Returns:
        defender: next Combatant defender
    """
    defender_typeabbrseq = ''
    while defender_typeabbrseq == '':
        if len(attacker.defender_typeabbrseq):
            message = f'{ui.INDENT_LEVEL_02}Is {attacker.typeabbrseq} attacking {attacker.defender_typeabbrseq}? (<Enter> for existing or type new typeabbrseq) '
        else:
            message = f'{ui.INDENT_LEVEL_02}Who is {attacker.typeabbrseq} attacking? (typeabbrseq) '

        # get defender typeabbrseq
        if len(defender_typeabbrseq := get_input(ui, message)) == 0:
            # no defender inputted
            if len(attacker.defender_typeabbrseq) == 0:
                # no previously entered defender
                ui.output(f'{ui.INDENT_LEVEL_03}Please enter a defender typeabbrseq')
                defender_typeabbrseq = ''
                continue
            
            defender_typeabbrseq = attacker.defender_typeabbrseq
            
        elif defender_typeabbrseq == attacker.typeabbrseq:
                ui.output(f'{ui.INDENT_LEVEL_03}{attacker.typeabbrseq} cannot self-attack. Try again')
                defender_typeabbrseq = ''
                continue
            
        else:
            if encounter.is_combatant(defender_typeabbrseq) == False:
                ui.output(f'{ui.INDENT_LEVEL_03}defender {defender_typeabbrseq} does not exist. Try again')
                defender_typeabbrseq = ''
                continue
        
        # check if defender is in combatant list        
        defender_count      = 0
        defender_is_invalid = False
        defender_is_dead    = False
        for defender in encounter.combatants:
            defender_count += 1
            if defender.typeabbrseq == defender_typeabbrseq:
                if defender.combattype == attacker.combattype:
                    if len(get_input(ui, f'{ui.INDENT_LEVEL_03}{attacker.typeabbrseq} and {defender.typeabbrseq} are both friends. Are you sure? (<Enter> for No, y for Yes) ')) == 0:
                        defender_is_invalid       = True
                        attacker.defender_typeabbrseq = ''
                        defender_typeabbrseq          = ''
                        break

                if defender.is_alive():
                    attacker.defender_typeabbrseq = defender_typeabbrseq
                    return defender
                else:
                    defender_is_dead = True
                    ui.output(f'{ui.INDENT_LEVEL_03}{defender.typeabbrseq} is dead')
                    attacker.defender_typeabbrseq = ''
                    defender_typeabbrseq = ''

                break

        if defender_is_dead or defender_is_invalid:
            continue
            
        if defender_count == len(encounter.combatants) and defender_typeabbrseq == '':
            return None

def get_all_combatants_initiative(ui, encounter) -> None:
    """get initiative for all combatants
    
    Args:
        ui: user interface
        encounter: current Encounter
    """
    if encounter.round == 1:
        if len(get_input(ui, f'Roll initiative? (<Enter> for Yes, N for No) ')) > 0:
            encounter.sort_combatants_by_initiative()
            return
    else:
        if len(get_input(ui, f'Re-roll initiative? (<Enter> for No, Y for Yes) ')) == 0:
            encounter.sort_combatants_by_initiative()
            return
    
    ui.output('\nEnter Initiative:')            
    for combatant in encounter.combatants:
        if combatant.is_dungeon_master():
            combatant.initiative = encounter.INITIATIVE_ACTIVE_MAXIMUM
            continue

        if combatant.is_player_character():
            get_combatant_initiative(ui, encounter, combatant)
        else:
            if (combatant.initiative >= encounter.INITIATIVE_ACTIVE_MINIMUM):
                initiative_reroll = get_input(ui, f"{ui.INDENT_LEVEL_01}Re-roll {combatant.typeabbrseq}'s {combatant.initiative} initiative? (<Enter> for No, A for Auto-roll, M for Manual-entry) ")
                if len(initiative_reroll) == 0: # keep existing initiative
                    continue
                elif initiative_reroll == 'M':  # manually enter new initiative
                    get_combatant_initiative(ui, encounter, combatant)
                    continue
            
            # auto-roll new initiative
            combatant.initiative = encounter.roll_nonplayer_initiative()
            ui.output(f"{ui.INDENT_LEVEL_01}{combatant.typeabbrseq}'s initiative set to {combatant.initiative}")

    encounter.check_duplicate_initiative()
    for combatant in encounter.combatants:
        encounter.combat_data.log_initiative(encounter.encounter, encounter.round, combatant.combattype, combatant.abbr, combatant.seq, combatant.group, combatant.initiative, combatant.hpmax, combatant.hp)
        
    return

def get_combatant_initiative(ui, encounter, combatant) -> None:
    """get combatant initiative values
    
    Args:
        ui: user interface
        encounter: current Encounter
        combatant: current Combatant
    """
    initiative_prompt = f"{ui.INDENT_LEVEL_01}{combatant.typeabbrseq}'s initiative? "
    if combatant.initiative > 0:
        initiative_prompt += f"(<Enter> for previous value {combatant.initiative}) "
        
    while True:
        if len(initiative_raw := get_input(ui, initiative_prompt)) == 0:    # Use previous value?
            if combatant.initiative:                   # non-zero previous initiative value exists
                initiative = combatant.initiative
                ui.output(f'{ui.INDENT_LEVEL_02}Keeping previous initiative value of {combatant.initiative}')
                return
            
            continue    # no initiative entered; try again

        if not initiative_raw.isnumeric():             # check if initiative is not numeric
            ui.output(f'{ui.INDENT_LEVEL_02}Initiative value of {initiative} is not a number')
            continue

        initiative = int(initiative_raw)
        if initiative < encounter.INITIATIVE_MINIMUM:  # check if initiative is less than minimum
            ui.output(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is less than {encounter.INITIATIVE_MINIMUM}')
            continue

        if initiative > encounter.INITIATIVE_MAXIMUM:  # check if initiative is greater than maximum
            ui.output(f'{ui.INDENT_LEVEL_02}An initiative value of {initiative} is more than {encounter.INITIATIVE_MAXIMUM}')
            continue

        if initiative < encounter.INITIATIVE_ACTIVE_MINIMUM:   # check if initiative is less than active minimum
            if len(get_input(ui, f'{ui.INDENT_LEVEL_03}Initiative value {initiative} is for inactive combatants. Keep it? (<Enter> for Yes, N for No) ')):
                continue

            combatant.initiative = initiative
            inactivereason = ''
            while len(inactivereason) == 0:
                message = f'{ui.INDENT_LEVEL_04}Reason for inactivity? '
                if len(combatant.inactivereason) > 0:
                    message += f'(<Enter> to keep previous value {combatant.inactivereason}, <Reason> for new inactive reason) '

                inactivereason = get_input(ui, message)
                
            combatant.inactivereason = inactivereason
        
        combatant.initiative = initiative
        break

def get_defenders(ui, encounter, attacker) -> list:
    """get a list of defenders by typeabbrseq and/or group
    This function allows the user to enter a comma-delimited list of defenders by typeabbrseq and/or group.
    
    Args:
        ui: user interface
        encounter: current Encounter
        attacker: current Combatant
        
    Returns:
        defenders: list of Combatant defenders
    """
    defenders = []
    special_attack_defenders_message = f"{ui.INDENT_LEVEL_02}Enter comma-delimited defenders by typeabbrseq and/or #group: "
    special_attack_defenders_raw = ''
    while len(special_attack_defenders_raw) == 0:
        if len(special_attack_defenders_raw := get_input(ui, special_attack_defenders_message)) == 0:
            ui.output(f"{ui.INDENT_LEVEL_03}No defenders entered. Try again!")
            continue
    
    special_attack_defenders = []
    for special_attack_defender_raw in special_attack_defenders_raw.split(','):
        special_attack_defender_raw = special_attack_defender_raw.strip()
        
        # skip if empty value
        if len(special_attack_defender_raw) == 0:
            continue
        
        # if special_attack_defender_raw is a group
        if special_attack_defender_raw[0:1] == '#':
            special_attack_defenders.append(special_attack_defender_raw)
            continue
        
        # if special_attack_defender_raw is in the combatant list
        if encounter.is_combatant(special_attack_defender_raw):
            special_attack_defenders.append(special_attack_defender_raw)
            continue
        
        # handle missing defender
        missing_defender = ''
        missing_defender_message = f"{ui.INDENT_LEVEL_03}defender \'{special_attack_defender_raw}\' is not in the combatant list. Re-enter typeabbrseq or [Enter] to ignore? "
        while missing_defender == '':
            missing_defender = get_input(ui, missing_defender_message).strip()
            
            # exclude special_attack_defender_raw
            if len(missing_defender) == 0:
                break
            
            # accept entered group as-is
            if missing_defender[0:1] == '#':
                continue
            
            # validate missing_defender is in combatant list
            if encounter.is_combatant(missing_defender) == False:
                missing_defender = ''
                continue

        special_attack_defenders.append(missing_defender)
    
    if len(special_attack_defenders) == 0:
        return []
    
    # remove duplicates
    special_attack_defenders = list(set(special_attack_defenders))
    
    # build list of defender groups
    special_attack_groups = [group[1:] for group in special_attack_defenders if group[0:1] == '#']
    
    # append group defenders to defender list
    [special_attack_defenders.append(combatant.typeabbrseq) 
        for combatant in encounter.combatants 
            if (has_common_substring_elements(combatant.group.split(','), special_attack_groups))
                and (combatant.typeabbrseq not in special_attack_defenders) 
                and (combatant.is_alive())
    ]

    # remove attacker from defender list
    special_attack_defenders = [defender for defender in special_attack_defenders if defender != attacker.typeabbrseq]
    
    # get defenders (ignoring groups)
    [defenders.append(combatant) for combatant in encounter.combatants if combatant.typeabbrseq in special_attack_defenders]
    
    return defenders

def get_to_hit_roll(ui, encounter, combatant) -> int:
    """get to-hit roll value
    
    args:
        ui: user interface
        encounter: current Encounter
        combatant: current Combatant
        
    returns:
        to_hit_roll: int value of to-hit roll
    """
    message = f"{ui.INDENT_LEVEL_02}Enter 'To Hit' d{encounter.TO_HIT_DIE} result: ("
    if not combatant.is_player_character():
        message += "<Enter> for autoroll, "

    message += f"{encounter.TO_HIT_DIE_MINIMUM}-{encounter.TO_HIT_DIE_MAXIMUM} manual entry) "
    to_hit_input = ''
    to_hit_roll = encounter.TO_HIT_DIE_MINIMUM
    while to_hit_input == '':
        to_hit_input = get_input(ui, message)   # allow empty input for auto-roll
        if not to_hit_input.isnumeric():
            if combatant.is_player_character():
                ui.output(f"{ui.INDENT_LEVEL_03}'To Hit' roll must be numeric.")
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

    ui.output(f'{ui.INDENT_LEVEL_02}ROLLED {to_hit_roll}')    
    return to_hit_roll

def has_common_substring_elements(list1: list, list2: list) -> bool:
    """check if two lists have common substring elements
    This function checks if any element in list1 is a substring of any element in list2 or vice versa.

    Args:
        list1 (_type_): list of elements to check against list2
        list2 (_type_): list of elements to check against list1

    Returns:
        bool: True if any element in list1 is a substring of any element in list2 or vice versa, False otherwise
    """
    for item1 in list1:
        for item2 in list2:
            if str(item1) == str(item2) or str(item2) == str(item1):
                return True

    return False
    
def initialize_round(ui, encounter) -> None:
    """initialize round for attacks
    args:
        ui: user interface
        encounter: current Encounter
    """
    ui.output(encounter.format_encounter())
    ui.output(encounter.format_combatants())

    get_all_combatants_initiative(ui, encounter)

    ui.output(encounter.format_encounter())
    ui.output(encounter.format_combatants())
    encounter.combatant_attack_number = 1
    
def log_hit_action(encounter, attacker, defender, damage: int, isdefenderdamaged: bool, xp_total: int, xp_earned: int, message: str):
    """log hit action
    Args:
        encounter: current Encounter
        attacker: current Combatant attacker
        defender: current Combatant defender
        damage: int value of damage
        isdefenderdamaged: bool value of defender damaged
        xp_total: int value of total xp
        xp_earned: int value of earned xp
        message: str message to log
    """
    encounter.combat_data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, damage, xp_total, xp_earned, message+' BEFORE')
    if isdefenderdamaged:
        defender.take_damage(damage)
    else:
        attacker.take_damage(damage)
        
    encounter.combat_data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, 0, 0, message+' AFTER')
    if isdefenderdamaged:
        encounter.combat_data.update_combatant_hit_points(defender.combattype, defender.abbr, defender.seq, defender.hpmax, defender.hp)    # update db with new post-damage hp
    else:
        encounter.combat_data.update_combatant_hit_points(attacker.combattype, attacker.abbr, attacker.seq, attacker.hpmax, attacker.hp)

def process_attack_sequence(ui, encounter) -> bool:
    """process each attack: Return True for additional post-attacks check or False for no post-attack checks
    
    Args:
        ui: user interface
        encounter: current Encounter
    returns:
        True if additional post-attacks check, False otherwise
    """
    if (attacker := encounter.find_next_attacker()) == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return False

    ui.output(f"{encounter.format_encounter()} | {encounter.format_attack_type()} Attacks")
    ui.output(encounter.format_combatants())
    if attacker.is_inactive():
        message = f'\n{ui.INDENT_LEVEL_01}{attacker.typeabbrseq} is currently inactive.'
        if len(attacker.inactivereason) > 0:
            message += f' (last status: {attacker.inactivereason})'
            
        message += 'Should this change? (<Enter> for No, Y for Yes) '
        if len(get_input(ui, message)) > 0:
            status_prompt = f'{ui.INDENT_LEVEL_02}Change initiative or inactive status? (<Enter> for initiative, new inactive status) '
            if len(status := get_input(ui, status_prompt)) == 0:
                get_combatant_initiative(ui, encounter, attacker)
                encounter.check_duplicate_initiative()
                if (attacker.initiative >= encounter.INITIATIVE_ACTIVE_MINIMUM):
                    attacker.inactivereason = ''
                    ui.output(f'{ui.INDENT_LEVEL_02}{attacker.typeabbrseq} will be able to attack next round')
                else:
                    ui.output(f'{ui.INDENT_LEVEL_02}{attacker.typeabbrseq} will remain inactive')
                    
                return True
            else:
                attacker.inactivereason = status

        encounter.initiative = attacker.initiative - 1
        return False

    ui.output(f'\n{ui.INDENT_LEVEL_01}{attacker.typeabbrseq} turn: {attacker.AttacksPerRound} attack(s)/round')
    ui.output(f'{ui.INDENT_LEVEL_02}{encounter.format_attack_type()} Attack #{encounter.combatant_attack_number}')

    if attacker.is_dungeon_master():
        prompt = f"{ui.INDENT_LEVEL_02}Skip attack? (<Enter> = Yes, N = No) "
        prompt_default = 'Yes'
    else:
        prompt = f"{ui.INDENT_LEVEL_02}Skip attack? (<Enter> = No, Y = Yes) "
        prompt_default = ''
        
    if len(get_input(ui, prompt) or prompt_default) > 0:
        ui.output(f'{ui.INDENT_LEVEL_02}ATTACK SKIPPED')
        process_attack_end(ui, encounter)
        return False

    ui.output(f'{ui.INDENT_LEVEL_02}ATTACKING...')
    if len(special_attack_message := attacker.format_special_attacks()):
        ui.output(special_attack_message)

    if len(ui.get_input(f'{ui.INDENT_LEVEL_02}Attack type: ([Enter] for regular, S for special) ')) == 0:
        process_attack_regular(ui, encounter, attacker)
    else:
        process_attack_special(ui, encounter, attacker)

    if len(get_input(ui, f'{ui.INDENT_LEVEL_02}Attack again? (<Enter> for No, y for Yes) ')) == 0:
        process_attack_end(ui, encounter)
        return True
    else:
        encounter.combatant_attack_number += 1
        return False

def process_attack_end(ui, encounter) -> None:
    """process end of attack activities
    
    args:
        ui: user interface
        encounter: current Encounter
    """
    encounter.initiative -= 1
    encounter.combatant_attack_number = 1
    ui.output_separator_line('-', True)

def process_attack_regular(ui, encounter, attacker) -> None:
    """process regular (non-special) attack
    
    args:
        ui: user interface
        encounter: current Encounter
        attacker: current Combatant
    """
    if (defender := find_next_defender(ui, encounter, attacker)) == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    message = encounter.format_attack_type()
    if  (
            (to_hit_roll := get_to_hit_roll(ui, encounter, attacker)) == encounter.ATTACK_CRITICAL_HIT) or \
            (attacker.was_hit_successful(to_hit_roll, defender.ac, defender.defensemodifier)
        ):
        # hit defender
        if len(special_defense_message := defender.format_special_defense()): 
            ui.output(special_defense_message)

        ui.output(attacker.format_damage_per_attack())
        if to_hit_roll == encounter.ATTACK_CRITICAL_HIT:
            message += " *Critical Hit*"
        else:
            message += " hit"
            
        damage = get_numeric_input(ui, f'{ui.INDENT_LEVEL_02}Enter {message} damage: ')
        log_hit_action(encounter, attacker, defender, damage, True, defender.xp, encounter.calculate_earned_xp(defender.hpmax, defender.hp, damage, defender.xp), message)
        ui.output(f'{ui.INDENT_LEVEL_03}{message} {defender.typeabbrseq} for {damage} points damage ({defender.hp} remaining)')
        if defender.is_alive() == False:
            encounter.foe_count -= 1
            attacker.defender_typeabbrseq = ''
        
        return
    
    # missed defender
    message += " missed"
    encounter.combat_data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, defender.xp, 0, message)
    ui.output(f'{ui.INDENT_LEVEL_03}{message} {defender.typeabbrseq}')
    if (to_hit_roll != encounter.ATTACK_CRITICAL_FUMBLE):
        return

    # check if critically fumbled attack
    if len(get_input(ui, f"{ui.INDENT_LEVEL_04}Is attack fumbled/cursed? ([Enter] for No, Y for Yes) ")) == 0:
        return

    # process critical fumble
    penalty_xp = 0
    damage = get_numeric_input(ui, f'{ui.INDENT_LEVEL_05}Enter {attacker.typeabbrseq} fumble damage: ')
    if attacker.combattype == encounter.COMBATTYPE_FRIEND:
        penalty_xp = get_numeric_input(ui, f"{ui.INDENT_LEVEL_05}Enter penalty xp (-number): ")

    message = encounter.format_attack_type() + " fumbled/cursed damage"
    log_hit_action(encounter, attacker, defender, damage, False, 0, penalty_xp, message)
    return

def process_attack_special(ui, encounter, attacker) -> None:
    """process special attack (spell, multiple defenders, multiple groups)
    
    args:
        ui: user interface
        encounter: current Encounter
        attacker: current Combatant
    """
    special_attack_prompt = f"{ui.INDENT_LEVEL_03}Enter special attack name: "
    special_attack = get_input(ui, special_attack_prompt)
    
    # get defenders
    defenders = []
    defender_list_verified = False
    while defender_list_verified == False:
        defenders = get_defenders(ui, encounter, attacker)
        if defenders == []:
            ui.output(f"{ui.INDENT_LEVEL_03}No defenders found. Try again!")
            continue

        defender_list_prompt = f"{ui.INDENT_LEVEL_03}defender list:"
        defender_list = [defender.typeabbrseq for defender in defenders]
        defender_list_prompt += f"\n{ui.INDENT_LEVEL_04}{('\n'+ui.INDENT_LEVEL_04).join(defender_list)}\n"
        defender_list_prompt += f"{ui.INDENT_LEVEL_03}Is this defender list correct? ([Enter for Yes, N for No]) "
        if len(ui.get_input(defender_list_prompt)) == 0:
            defender_list_verified = True
        
    if len(defenders) == 0:
        return

    # process saving throw
    saving_throw_permitted = False
    saving_throw_half_damage = False
    saving_throw_type = 0
    if len(get_input(ui, f"{ui.INDENT_LEVEL_03}Is saving throw allowed? ([Enter] for Yes, N for No) ")) == 0:
        saving_throw_permitted = True
        if len(get_input(ui, f"{ui.INDENT_LEVEL_03}If save successful, defender takes no damage or 50% damage? ([Enter] for None, Y for 50%) ")) > 0:
            saving_throw_half_damage = True
        
        ui.output(f'{ui.INDENT_LEVEL_04}Saving Throw Type:')
        saving_throw_types = ''
        for index, type in enumerate(cm1.Saving_Throw.SAVING_THROW_TYPE, 1):
            saving_throw_types += f'{ui.INDENT_LEVEL_05}{str(index)}: {type}\n'
        
        ui.output(saving_throw_types)
        while saving_throw_type == 0:
            saving_throw_type_raw = get_numeric_input(ui, f'{ui.INDENT_LEVEL_04}Select saving throw type: ', ui.INDENT_LEVEL_04)
            if (saving_throw_type_raw > 0) and (saving_throw_type_raw <= len(cm1.Saving_Throw.SAVING_THROW_TYPE)):
                saving_throw_type = saving_throw_type_raw - 1
                break

    is_damage_variable = True
    if len(defender_list) > 1:
        # check for variable damage by defender
        if len(get_input(ui, f"{ui.INDENT_LEVEL_02}Enter damage for each defender? [Enter for No, Y for Yes] ")) == 0:
            is_damage_variable = False

    # process special attack vs. defenders
    for index, defender in enumerate(defenders, 1):
        ui.output(f"{ui.INDENT_LEVEL_02}Defender: {defender.typeabbrseq}")
        saving_throw_modifier = 1.0
        if saving_throw_permitted == True:
            saving_throw = encounter.get_saving_throw(defender.savingthrowclasstype, defender.savingthrowlevel, defender.savingthrowlevelpdm, cm1.Saving_Throw.SAVING_THROW_TYPE[saving_throw_type])
            if defender.is_player_character():
                saving_throw_value = 0
                while saving_throw_value == 0:
                    saving_throw_value_raw = get_numeric_input(ui, f"{ui.INDENT_LEVEL_03}Enter {defender.typeabbrseq}'s save vs. {cm1.Saving_Throw.SAVING_THROW_TYPE[saving_throw_type]}: ({saving_throw} needed) ", ui.INDENT_LEVEL_04)
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
        
        # enter damage if it varies for defender or if first defender (does not vary)
        if (is_damage_variable == True) or (index == 1):
            damage_base = ui.get_numeric_input(f"{ui.INDENT_LEVEL_03}Enter special attack damage (+/-number): ")

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

        if attacker.combattype == encounter.COMBATTYPE_FRIEND and defender.combattype == encounter.COMBATTYPE_FRIEND:
            # Attacker is performing special attack on defender friend (typically healing)
            xp_prompt = f'{ui.INDENT_LEVEL_03}Enter {attacker.typeabbrseq} xp: '
            earned_xp_base = get_numeric_input(ui, xp_prompt)
        else:
            # Calculate xp
            earned_xp_base = encounter.calculate_earned_xp(defender.hpmax, defender.hp, damage, defender.xp)
        
        earned_xp = int(earned_xp_base * saving_throw_modifier)
        log_hit_action(encounter, attacker, defender, damage, True, defender.xp, earned_xp, message)
        ui.output(ui.INDENT_LEVEL_04+output_message.replace('~~', str(damage))+f' points damage ({defender.hp} remaining)\n')

    return

def process_set_initiative(ui, encounter) -> None:
    """process setting current encounter's initiative
    
    args:
        ui: user interface
        encounter: current Encounter
    """
    raw_initiative = ''
    while len(raw_initiative) == 0:
        raw_initiative = get_input(ui, f'\nSet Initiative: (<Enter> for current: {encounter.initiative}, min/max: {encounter.INITIATIVE_MINIMUM}/{encounter.INITIATIVE_MAXIMUM}) ')
        if len(raw_initiative) == 0:
            return
        
        if not raw_initiative.isnumeric():
            ui.output('{ui.INDENT_LEVEL_01}Initiative must be numeric. Try again')
            raw_initiative = ''
            continue
        
        if (int(raw_initiative) < encounter.INITIATIVE_MINIMUM) or (int(raw_initiative) > encounter.INITIATIVE_MAXIMUM):
            ui.output(f'{ui.INDENT_LEVEL_01}Initiative must be between {encounter.INITIATIVE_MINIMUM} and {encounter.INITIATIVE_MAXIMUM}. Try again')
            raw_initiative = ''
            continue
        
    encounter.initiative = int(raw_initiative)

def process_load_combatants(ui, encounter) -> None:
    """load combatants into encounter
    
    args:
        ui: user interface
        encounter: current Encounter
    """
    encounter.load_combatants()
    
def process_load_participants(ui, encounter) -> None:
    """load participant data from database into encounter
    
    args:
        ui: user interface
        encounter: current Encounter
    """
    encounter.load_participants()

def process_round(ui, encounter) -> None:
    """process round for each combatant
    
    args:
        ui: user interface
        encounter: current Encounter
    """
    continue_attack_prompt = f'Continue attacking? (<Enter> for Yes, N for No) '
    while True:
        initialize_round(ui, encounter)
        encounter.ismissileattack = (len(get_input(ui, f'Is round missile or melee? [Enter] for missile, m for melee ')) == 0)
        while encounter.initiative > encounter.INITIATIVE_NONE:
            encounter.count_available_combatants()
            if encounter.foe_count == 0:
                if len(get_input(ui, f'{ui.INDENT_LEVEL_01}Encounter: {encounter.encounter} Round: {encounter.round} has no FOES. Continue? ([Enter] for No, y for Yes) ')) == 0:
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
                    encounter.delete_dead_oponents()
                    encounter.prepare_next_round()
                    ui.output(encounter.format_encounter())
                    return

        encounter.delete_dead_oponents()
        ui.output(f'\nRound {encounter.round} END:')
        if len(get_input(ui, f'\nBegin next round? (<Enter> for Yes, N for No) ')) == 0:
            ui.output_separator_line('-', True)
            encounter.prepare_next_round()
            ui.output(encounter.format_encounter())
            ui.output(encounter.format_combatants())
            continue

        if len(get_input(ui, f'\nBegin next encounter? (<Enter> for Yes, N for No) ')) == 0:
            encounter.prepare_next_encounter()
        
        ui.output_separator_line('-', True)
        ui.output(encounter.format_encounter())
        ui.output(encounter.format_combatants())
        return                

if __name__ == '__main__':
    mm = MeleeManager()
    mm.main()
