class UI:
    SEPARATOR_LINE_LENGTH = 103
    INDENT_LEVEL_01 = '- '
    INDENT_LEVEL_02 = '  + '
    INDENT_LEVEL_03 = '    * '
    INDENT_LEVEL_04 = '      -- '
    
    @classmethod
    def get_input(self, action_prompt, response_option = "~@~", response_exception = Exception):
        value = input(action_prompt)
        
        # If response_option specified, raise response error
        if value.find(response_option) > -1:
            raise response_exception
    
        return value.upper()    # force uppercase values
    
    @classmethod
    def get_numeric_input(self, action_prompt, response_prefix = "", response_option = "~@~", response_exception = Exception):
        while True:
            try:
                value = self.get_input(action_prompt, response_option, response_exception)
                return int(value)
            except ValueError:
                print(f"{response_prefix}Entered value must be numeric")

    @classmethod
    def output_separator_line(self, value, newlinebefore = False):
        newline = ''
        if newlinebefore == True:
            newline = '\n'
            
        self.output(f"{newline}{value*self.SEPARATOR_LINE_LENGTH}")
    
    @classmethod
    def output(self, message):
        print(message)