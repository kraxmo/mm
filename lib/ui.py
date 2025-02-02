#ui.py

class UI:
    SEPARATOR_LINE_LENGTH = 103
    INDENT_LEVEL_01 = '- '
    INDENT_LEVEL_02 = '  + '
    INDENT_LEVEL_03 = '    * '
    INDENT_LEVEL_04 = '      -- '
    INDENT_LEVEL_05 = '         -+ '
    
    @classmethod
    def get_input(self, action_prompt: str, response_option: str = None, response_exception: Exception = None) -> str:
        """Get input from user
        
        Args:
            action_prompt (str): Prompt message to display to user
            response_option (str): Response option to raise exception
            response_exception (Exception): Exception to raise if response_option found in input
            
        Returns:
            str: User input value
        """
        if response_option is None:
            response_option = "~@~"   # default response option
            
        if response_exception is None:
            response_exception = Exception
            
        value: str = input(action_prompt)
        
        # If response_option specified, raise response error
        if not value.find(response_option):
            raise response_exception
    
        return value.upper()    # force uppercase values
    
    @classmethod
    def get_numeric_input(self, action_prompt: str, response_prefix: str = "", response_option: str = "~@~", response_exception: Exception = Exception) -> int:
        """Get numeric input from user
        
        Args:
            action_prompt (str): Prompt message to display to user
            response_prefix (str): Prefix message to display to user
            response_option (str): Response option to raise exception
            response_exception (Exception): Exception to raise if response_option found in input
            
        Returns:
            int: User numeric input value
        """
        while True:
            try:
                value: str = self.get_input(action_prompt, response_option, response_exception)
                return int(value)
            except ValueError:
                print(f"{response_prefix}Entered value must be numeric")
                continue

    @classmethod
    def output_separator_line(self, value: str, newlinebefore: bool = False) -> None:
        """Send separator line to output"""
        newline: str = ''
        if newlinebefore == True:
            newline = '\n'
            
        self.output(f"{newline}{value*self.SEPARATOR_LINE_LENGTH}")
    
    @classmethod
    def output(self, message) -> None:
        """Send message to specified output device"""
        print(message)