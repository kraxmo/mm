#mm.py

import abc
import lib.combatmodel as cm

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
        return list_combatants(encounter)

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
        print(__class__.__name__)
        encounter.prepare_next_encounter()
        return list_encounter(encounter) 
    
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

class InitializeAttackRoundAction(Action):
    """initialize round for attacks"""

    def __init__(self):
        super().__init__(7, 'Initialize Attack Round')

    def __str__(self):
        return f'{__class__.__name__}'

    def process(self, ui, encounter):
        return initialize_attack_round(ui, encounter)
    
class QuitAction(Action):
    def __init__(self):
        super().__init__(99, 'Quit')

    def process(self, ui, encounter):
        raise QuitException

    def __str__(self):
        return f'{__class__.__name__}'
    
class UI:
    def get_input(self, action_prompt):
        return input(action_prompt)
    
    def get_numeric_input(self, action_prompt):
        while True:
            try:
                value = self.get_input(action_prompt)
                return int(value)
            except ValueError:
                print("Entered value must be numeric")

class MeleeManager():
    def __init__(self):
        print('\n','='*100,'\nMELEE MANAGER','\n'+'='*100)
        self.encounter = cm.Encounter()
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
        ui = UI()
        while True:
            action_code = ui.get_numeric_input(self.action_prompt)
            try:
                action = self.actions_map[action_code]
            except KeyError:
                print(f'*{action_code}* not a valid action\n')
                continue

            try:
                action.process(ui, self.encounter)
                continue
            except QuitException:
                break

def delete_dead_opponents(encounter):
    encounter.data.delete_dead_foes()
    for combatant in encounter.combatants:
        if combatant.combattype == encounter.COMBATTYPE_FOE and combatant.is_dead():
            encounter.combatants.remove(combatant)

def determine_attack_damage(ui, encounter, to_hit_roll, attacker, defender):
    """determine attacker damage to defender"""
    spell_prompt = '    * Enter spell name: '
    raw_spell_damage_prompt = '    * Enter spell damage (+/-number): '
    raw_xp_prompt = '    * Enter xp: '
    if to_hit_roll == encounter.TO_HIT_DIE_SPELL:    # spell is cast
        spell = ui.get_input(spell_prompt)
        raw_damage = ''
        while raw_damage == '':
            raw_damage = ui.get_input(raw_spell_damage_prompt)
            if is_negative_number_digit(raw_damage):
                damage = int(raw_damage)
            else:
                print(f'      -- {raw_damage} is not numeric. Try again')
                raw_damage = ''

        if defender.combattype == encounter.COMBATTYPE_FOE:
            earned_xp = encounter.calculate_xp(defender.hpmax, defender.hp, damage, defender.xp)
        else:
            raw_xp = ''
            while raw_xp == '':
                raw_xp = ui.get_input(raw_xp_prompt)
                if raw_xp.isnumeric():
                    earned_xp = int(raw_xp)
                else:
                    print(f'      -- {raw_xp} is not numeric. Try again')
                    raw_xp = ''
            
        encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, damage, defender.xp, earned_xp, 'spell: '+spell+' BEFORE')
        defender.take_damage(damage)
        encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, 0, 0, 'spell: '+spell+' AFTER')
        encounter.data.update_combatant_hit_points(defender.abbr, defender.seq, defender.hpmax, defender.hp)    # update db with new post-damage hp
        print(f'    * Cast spell {spell} on {defender.combattype} {defender.abbrseq} for {damage} points damage ({defender.hp} remaining)')
    else:
        message = 'missed'
        if (to_hit_roll == encounter.ATTACK_CRITICAL_HIT) or (attacker.was_hit_successful(to_hit_roll, defender.ac)):
            if (attacker.damageperattack == None) or (len(str(attacker.damageperattack)) == 0):
                pass
            else:
                damageperattack = '\n    * ' + attacker.abbrseq + ' Damage Per Attack:\n      -- '+'\n      -- '.join(attacker.damageperattack.lstrip().split('|'))
                print(damageperattack)
                
            if to_hit_roll == encounter.ATTACK_CRITICAL_HIT:
                message = '*Critical Hit*'
            else:
                message = "hit"
                
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
        else:
            encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, defender.combattype, defender.abbr, defender.seq, defender.group, defender.initiative, defender.hpmax, defender.hp, 0, defender.xp, 0, message)
            print(f'    * {message} {defender.combattype} {defender.abbrseq}')
            if ( to_hit_roll == encounter.ATTACK_MISSED ):
                if len(input(f'      -- Is attack cursed? ([Enter] for No, Y for Yes) ')) > 0:
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

                    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, defender.initiative, attacker.hpmax, attacker.hp, damage, 0, penalty_xp, 'cursed damage BEFORE')
                    attacker.take_damage(damage)
                    encounter.data.log_action(encounter.encounter, encounter.round, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, attacker.initiative, encounter.combatant_attack_number, attacker.combattype, attacker.abbr, attacker.seq, attacker.group, defender.initiative, attacker.hpmax, attacker.hp, 0, 0, 0, 'cursed damage AFTER')

def find_next_defender(ui, attacker, combatants):
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
                    if (defender.specialdefense == None) or (len(str(defender.specialdefense)) == 0):
                        pass
                    else:
                        specialdefense = '\n    * ' + defender_abbrseq + ' Special Defenses:\n      -- '+'\n      -- '.join(defender.specialdefense.lstrip().split('|'))
                        print(specialdefense)
                        
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

def get_all_combatants_initiative(ui, encounter):
    """get initiative for each combatant"""
    print('\nEnter Initiative:')
    if encounter.round > 1:
        initiative_prompt = f'- Re-roll initiative? (<Enter> for No, Y for Yes) '
        rollinitiative = ui.get_input(initiative_prompt)
        if rollinitiative.lower() != 'y':
            return False
            
    for combatant in encounter.combatants:
        if combatant.CharacterType == combatant.TYPE_PLAYER_CHARACTER:
            get_combatant_initiative(ui, encounter, combatant)
        else:
            combatant.initiative = encounter.roll_nonplayer_initiative()

    encounter.check_duplicate_initiative()
    for combatant in encounter.combatants:
        encounter.data.log_initiative(encounter.encounter, encounter.round, combatant.combattype, combatant.abbr, combatant.seq, combatant.group, combatant.initiative)
        
    return True

def get_combatant_initiative(ui, encounter, combatant):
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

def initialize_attack_round(ui, encounter):
    """initialize round for attacks"""

    print(f'\nRound {encounter.round} START:')

    # Determine initiative for all combatants
    if get_all_combatants_initiative(ui, encounter):
        list_combatants(encounter)

    encounter.combatant_attack_number = 1
    return True
    
def is_negative_number_digit(n: str) -> bool:
    """check for negative number in passed string value"""
    try:
        int(n)
        return True
    except ValueError:
        return False

def list_combatants(encounter):
    """list all combatant information"""

    list_encounter(encounter)
    print(f'\nCombatants:')
    for combatant in encounter.combatants:
        print(f'- init: {combatant.initiative} group: {combatant.group} {combatant.abbrseq} ({combatant.name} {combatant.combattype}) hp: {combatant.hp} ac: {combatant.ac} thac0: {combatant.thac0} tohitmodifier: {combatant.tohitmodifier}')

def list_encounter(encounter):
    """list encounter information"""
    print(f'\nEncounter: {encounter.encounter} Round: {encounter.round} Initiative: {encounter.initiative}')

def process_combatant_initiative(ui, encounter):
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

def process_encounter_initiative(ui, encounter):
    raw_initiative = ''
    initiative_prompt = f'\nSet Initiative: (<Enter> for {encounter.initiative}) '
    while len(raw_initiative) == 0:
        raw_initiative = ui.get_input(initiative_prompt)
        if len(raw_initiative) == 0:
            return
        
        if raw_initiative.isnumeric() == False:
            print('- Initiative must be numeric. Try again')
            raw_initiative = ''
            continue
        
        if (int(raw_initiative) < encounter.INITIATIVE_MINIMUM) or (int(raw_initiative) > encounter.INITIATIVE_ACTIVE):
            print(f'- Initiative must be between {encounter.INITIATIVE_MINIMUM} and {encounter.INITIATIVE_ACTIVE}. Try again')
            raw_initiative = ''
            continue
        
    encounter.initiative = int(raw_initiative)

def process_load_combatants(encounter):
    """load combatants into encounter"""
    encounter.get_combatants()
    for combatant in encounter.combatants:
        # update FOE combatants hit points
        if combatant.combattype == encounter.COMBATTYPE_FOE:
            encounter.data.update_combatant_hit_points(combatant.abbr, combatant.seq, combatant.hpmax, combatant.hp)

    print(f'\n{len(encounter.combatants)} combatants loaded')
    list_combatants(encounter)

def process_load_participants(encounter):
    """load participant data from database into encounter"""
    encounter.data.load_participants()
    print(f'\n{len(encounter.data.participants)} participants loaded')

def process_round(ui, encounter):
    """process round for each combatant"""
    print(f'\nEncounter {encounter.encounter} START')
    round_type_prompt = f'\n- Is round missile or melee? [Enter] for missile, m for melee '
    continue_attack_prompt = f'Continue attacking? (<Enter> for Yes, N for No) '
    while True:
        if initialize_attack_round(ui, encounter) == False:
            print('\nNo FOEs were detected')
            break
        
        round_raw = ''
        round_raw = ui.get_input(round_type_prompt)
        encounter.ismissileattack = (len(round_raw) == 0)

        while encounter.initiative > encounter.INITIATIVE_NONE:
            encounter.count_available_combatants()
            if encounter.foe_count == 0:
                round_no_foes_prompt = f'- Encounter: {encounter.encounter} Round: {encounter.round} has no FOES. Continue? ([Enter] for No, y for Yes) '
                if len(ui.get_input(round_no_foes_prompt)) == 0:
                    delete_dead_opponents(encounter)
                    print(f'\n Encounter: {encounter.encounter} Round: {encounter.round} END:')
                    list_combatants(encounter)
                    print('\n'+'-'*75)
                    encounter.prepare_next_encounter()
                    list_encounter(encounter)
                    return
            
            checkforanotherattack = process_attack(ui, encounter)
            
            # check for end of normal round (initiative is set to NONE after last attacker's attack)
            if encounter.initiative == encounter.INITIATIVE_NONE:
                break
            
            if checkforanotherattack == True:
                if len(ui.get_input(continue_attack_prompt)) > 0:
                    delete_dead_opponents(encounter)
                    print(f'\nRound {encounter.round} ENDED *PREMATURALLY*')
                    list_combatants(encounter)
                    print('\n'+'-'*75)
                    encounter.prepare_next_round()
                    list_encounter(encounter)
                    return

        delete_dead_opponents(encounter)
        print(f'\nRound {encounter.round} END:')
        continue_prompt = f'\nBegin next round? (<Enter> = Yes, n = No) '
        next_round = ui.get_input(continue_prompt)
        if len(next_round) == 0:
            list_combatants(encounter)
            print('\n'+'-'*75)
            encounter.prepare_next_round()
            list_encounter(encounter)
            continue

        continue_prompt = f'\nBegin next encounter? (<Enter> = Yes, n = No) '
        next_encounter = ui.get_input(continue_prompt)
        if len(next_encounter) == 0:
            encounter.prepare_next_encounter()

        print('\n'+'-'*75)
        list_combatants(encounter)
        return                

def process_attack(ui, encounter) -> bool:
    """process each attack: Return True for additional post-attacks check- or False for no post-attack checks"""
    attacker = encounter.find_next_attacker()
    if attacker == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    list_combatants(encounter)
    
    if attacker.is_inactive():
        message = f'\n- {attacker.abbrseq} is currently inactive.'
        if len(attacker.inactivereason) > 0:
            message += f' (last status: {attacker.inactivereason})'
            
        message += ' Should this change? (<Enter> = No, Y = Yes) '
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
    print(f'  + Attack #{encounter.combatant_attack_number}')

    # KEEP
    # spell_casting_type = 0

    skip_attack_prompt = f'  + Skip attack? (<Enter> = No, y = Yes) '
    skip_attack = ui.get_input(skip_attack_prompt)
    if len(skip_attack) > 0:
        print(f'  + ATTACK SKIPPED')
        process_end_attack(ui, encounter)
        return False

    print(f'  + ATTACKING...')
    defender = ''
    defender = find_next_defender(ui, attacker, encounter.combatants)
    if defender == None:
        encounter.initiative = encounter.INITIATIVE_NONE
        return

    if (attacker.specialattack == None) or (len(str(attacker.specialattack)) == 0):
        pass
    else:
        specialattack = '\n    * ' + attacker.abbrseq + ' Special Attacks:\n      -- '+'\n      -- '.join(attacker.specialattack.lstrip().split('|'))
        print(specialattack)
        
    to_hit_roll = encounter.get_hit_roll(attacker)
    determine_attack_damage(ui, encounter, to_hit_roll, attacker, defender)
    if defender.is_alive() == False:
        encounter.foe_count -= 1
        attacker.defender_abbrseq = ''

    attack_prompt = f'\n  + Attack again? (<Enter> = No, y = Yes) '
    attack_again = ui.get_input(attack_prompt)
    if len(attack_again) == 0:
        process_end_attack(ui, encounter)
        return True
    else:
        encounter.combatant_attack_number += 1
        return False

def process_end_attack(ui, encounter):
    encounter.initiative -= 1
    encounter.combatant_attack_number = 1
    print('\n'+'-'*75)
    
if __name__ == '__main__':
    mm = MeleeManager()
    mm.main()
