
'''
 soubor:   token.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    23.1.2009 - 26.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''


class Token:
    '''
    self.code nabyva hodnot (retezcovych):
        CINT CDOUBLE CSTRING ID
        begin div do double else end find if integer readln
        sort string then var while write
        + - * < <= > >= = <> := : ; . , ( )
        (prazdny retezec znamena EOF token)
    self.value ma smysl pouze kdyz self.code in ("CINT", "CDOUBLE", "CSTRING", "ID"):
        - u konstant predstavuje konkretni hodnotu
        - u identifikatoru predstavuje jmeno promenne
    '''

    def __init__(self, code="", value=None):
        self.code = code
        self.value = value
    
    def __str__(self):
        return "[%s: %s]" % (self.code, self.value)
