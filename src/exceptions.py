
'''
 soubor:   exceptions.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    25.1.2009 - 26.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''

class LexicalError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)
    def __str__(self):
        return self.msg

class SyntacticError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)
    def __str__(self):
        return self.msg

class SemanticError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)
    def __str__(self):
        return self.msg

class RuntimeError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)
    def __str__(self):
        return self.msg
