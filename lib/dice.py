from random import randint

class Dice:
    @classmethod        
    def roll_dice(cls, die_sides, dice_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """calculate random dice roll based on die sides, numbers, and modifiers
        
        args:
            die_sides: int - number of sides on the die
            dice_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
        
        returns:
            int - total roll result
        """
        result = 0
        for _ in range(0, dice_number):
            result += randint(1, die_sides + die_modifier)

        result += roll_modifier        
        return result
    
    @classmethod
    def roll_die(cls, die_sides, die_modifier = 0) -> int:
        """calculate random die roll based on die sides and modifier
        
        args:
            die_sides: int - number of sides on the die
            die_modifier: int - modifier to add to the die roll
        
        returns:
            int - die roll result
        """
        return randint(1, die_sides) + die_modifier

    @classmethod
    def roll_d4(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 4-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
        
        returns:
            int - total roll result
        """
        return cls.roll_dice(4, die_number, die_modifier, roll_modifier)

    @classmethod
    def roll_d6(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 6-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
            
        returns:
            int - total roll result
        """
        return cls.roll_dice(6, die_number, die_modifier, roll_modifier)

    @classmethod
    def roll_d8(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 8-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
        
        returns:
            int - total roll result
        """
        return cls.roll_dice(8, die_number, die_modifier, roll_modifier)

    @classmethod
    def roll_d10(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 10-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
            
        returns:
            int - total roll result
        """
        return cls.roll_dice(10, die_number, die_modifier, roll_modifier)

    @classmethod
    def roll_d12(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 12-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
        
        returns:
            int - total roll result
        """
        return cls.roll_dice(12, die_number, die_modifier, roll_modifier)

    @classmethod
    def roll_d20(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 20-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
        
        returns:
            int - total roll result
        """
        return cls.roll_dice(20, die_number, die_modifier, roll_modifier)

    @classmethod
    def roll_d100(cls, die_number = 1, die_modifier = 0, roll_modifier = 0) -> int:
        """roll 100-sided dice
        
        args:
            die_number: int - number of dice to roll
            die_modifier: int - modifier to add to each die roll
            roll_modifier: int - modifier to add to the total roll
            
        returns:
            int - total roll result
        """
        return cls.roll_dice(100, die_number, die_modifier, roll_modifier)
