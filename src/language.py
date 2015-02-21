
'''
 soubor:   language.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    25.1.2009 - 25.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''


KEYWORDS = ("begin", "div", "do", "double", "else", "end", "find", "if",
            "integer", "readln", "sort", "string", "then", "var", "while", "write")

DATA_TYPES = ("integer", "double", "string")

RELATION_OPERATORS = ("<", "<=", ">", ">=", "<>", "=")
ARITMETIC_OPERATORS = ("+", "-", "*", "div")
OTHER_OPERATORS = (",", ".", ":", ";", "(", ")", ":=")

OPERATORS = RELATION_OPERATORS + ARITMETIC_OPERATORS + OTHER_OPERATORS
