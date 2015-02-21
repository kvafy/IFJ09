
'''
 soubor:   symboltable.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    25.1.2009 - 28.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''


class SymbolTableRecord():
    '''
    id (retezec) - u programatorem definovanych promennych se jedna o nazev, ktery je ve zdrojaku
                 - u konstant a docasnych promennych je to jmeno pridelene tabulkou symbolu
    '''
    def __init__(self, id="", value=None):
        self.id = ""
        self.value = value
    
    def isInt(self):
        return type(self.value) == type(0)
    def isDouble(self):
        return type(self.value) == type(0.0)
    def isString(self):
        return type(self.value) == type("")


class SymbolTable():
    '''
    self._records - Obsahuje zaznamy tvaru klic : id (string)
                                           hodnota : SymbolTableRecord
    '''
    def __init__(self):
        def gen():
            i = 0
            while True:
                yield i
                i += 1
        self._records = {}
        self._constantCounter = gen()
        self._tempCounter = 0
    
    def __contains__(self, key):
        return key in self._records.keys()
        
    def __getitem__(self, key):
        return self._records[key]
    
    # addX operace vraci identifikator nove vytvorene promenne
    def add(self, key, value):
        if key not in self._records:
            self._records.setdefault(key, SymbolTableRecord(id=key, value=value))
        else: # toto se tyka docasnych (temp) promennych, ktere po resetu jsou v tabulce
            self._records[key].value = value
        return key
        
    def addVariable(self, key, value):
        return self.add(key, value)
    
    def addConstant(self, value):
        '''
        Vytvori v tabulce symbolu zaznam pro danou konstantu pod jmenem ve tvaru regexp "\d+-cons",
        Vrati adresu konstanty v tabulce symbolu (tj. jeji pridelene jmeno).
        '''
        key = "%d-const" % next(self._constantCounter)
        return self.add(key, value)
    
    def addTemp(self, value=None):
        '''
        Vytvori v tabulce symbolu zaznam docasne promenne pod jmenem ve tvaru regexp "\d+-temp".
        Vrati adresu docasne promenne v tabulce symbolu (tj. jeji pridelene jmeno).
        '''
        key = "%d-temp" % self._tempCounter
        self._tempCounter += 1
        return self.add(key, value)
    
    def resetTemps(self):
        '''
        Dosud vytvorene docasne promenne v tabulce zustavaji, jejich hodnota je vsak
        prepsana na None (aby promenna nemela definovany typ). Zpusobi to, ze nehrozi
        neomezeny rust poctu docasnych promennych.
        (Idealne resetTemps() volat co nejcasteji, napr. pri dokonceni zpracovani prikazu.)
        '''
        for i in range(self._tempCounter):
            self._records["%d-temp" % i].value = None # zrusime hodnoty
        self._tempCounter = 0
