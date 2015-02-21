
'''
 soubor:   instruction.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    26.1.2009 - 26.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''


class Instruction():
    '''
    self.dst, self.src1, self.src2
        Adresa do tabulky symbolu (tj. retezcovy identifikator) nebo None
    self.operation - hodnoty dle vyuziti poli dst,src1,src2:
          s s
        d r r
        s c c
        t 1 2  operation(s)
        ===================
        0 0 0  label
        1 0 0  goto (dst = label kam skocit) read readln
        0 1 0  write
        1 1 0  := sort
        1 1 0  goto-if-zero (dst = adresa labelu kam skocit, src1 = ridici promenna)
        1 1 1  + - * div < <= > >= = <>
    '''
    def __init__(self, operation, dst, src1, src2):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2        
        self.operation = operation
        
    def __str__(self):
        return "inst: %s %s with %s  ->  %s" % (self.operation, self.src1, self.src2, self.dst)
