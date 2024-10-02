class UI:
    SEPARATOR_LINE_LENGTH = 97
    INDENT_LEVEL_01 = '- '
    INDENT_LEVEL_02 = '  + '
    INDENT_LEVEL_03 = '    * '
    INDENT_LEVEL_04 = '      -- '
    
    @classmethod
    def get_input(self, action_prompt, response_option = "", response_exception = Exception):
        value = input(action_prompt)
        
        # If exit to menu value is encountered, raise error
        if value.find(response_option) > -1:
            raise response_exception
    
        return value.upper()    # force uppercase values
    
    @classmethod
    def get_numeric_input(self, action_prompt, response_option = "", response_exception = Exception):
        while True:
            try:
                value = self.get_input(action_prompt, response_option, response_exception)
                return int(value)
            except ValueError:
                print("Entered value must be numeric")

    @classmethod
    def print_separator_line(self, value, newlinebefore = False):
        newline = ''
        if newlinebefore == True:
            newline = '\n'
            
        print(f"{newline}{value*self.SEPARATOR_LINE_LENGTH}")
    
    