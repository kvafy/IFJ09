
'''
 soubor:   interpret.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    27.1.2009 - 31.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''

from exceptions import RuntimeError
import buildin
import re
import sys


operationDict = {"<": lambda x,y: x < y,   "<=": lambda x,y: x <= y,
                 ">": lambda x,y: x > y,   ">=": lambda x,y: x >= y,
                 "=": lambda x,y: x == y,  "<>": lambda x,y: x != y,
                 "+": lambda x,y: x + y,   "-":  lambda x,y: x - y,
                 "*": lambda x,y: x * y,   "div":lambda x,y: x // y,}

_inputBuffer = None # vyrovnavaci pamet pro vstup ze stdin (None znaci ze nemame uz nic v bufferu)

# pro simulaci scanf
_intMatcher = re.compile(r"\s*([-+]?\d+)")
_doubleMatcher = re.compile(r"\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)")


def _readLine():
    global _inputBuffer
    _inputBuffer = ""
    c = sys.stdin.read(1)
    while c not in ("\n", ""):
        _inputBuffer += c
        c = sys.stdin.read(1)
    if c == "": # EOF bez konce souboru
        raise RuntimeError("input for readline must end with \\n character")


def interpret(instructionsList, symbolTable):
    global _inputBuffer, _intMatcher, _doubleMatcher
    
    pc = 0 # program counter
    while pc < len(instructionsList):
        inst = instructionsList[pc]
        
        # operator prirazeni
        if inst.operation == ":=":
            symbolTable[inst.dst].value = symbolTable[inst.src1].value
        
        # binarni operatory
        elif inst.operation in ("+", "-", "*", "div"):
            if inst.operation == "div" and symbolTable[inst.src2].value == 0:
                raise RuntimeError("integer division by zero")
            # vykonani pozadovane operace (v pythonu jsou stejne typy vysledku operaci jako v jazyce IFJ09
            # (napr. int + int -> int ; double + int -> double ...) 
            symbolTable[inst.dst].value = operationDict[inst.operation](symbolTable[inst.src1].value, symbolTable[inst.src2].value)
            
        # relacni operatory
        elif inst.operation in ("<", "<=", ">", ">=", "<>", "="):
            # provedeni dane operace
            if operationDict[inst.operation](symbolTable[inst.src1].value, symbolTable[inst.src2].value):
                symbolTable[inst.dst].value = 1
            else:
                symbolTable[inst.dst].value = 0
        
        # IO operace
        elif inst.operation == "write":
            if type(symbolTable[inst.src1].value) == type(0.0): # doubly tiskneme jako %g v jazyce C
                print(format(symbolTable[inst.src1].value, "g"), end="")
            else:
                print(symbolTable[inst.src1].value, end="")
        elif inst.operation in ("read", "readln"):
            if _inputBuffer is None: # nemame nic v zasobe => nacteme si radek
                _readLine()
            # cisel muzeme nacitat libovolny pocet v jednom volani
            if symbolTable[inst.dst].isInt() or symbolTable[inst.dst].isDouble():
                while _inputBuffer.strip() == "": # radky s bilymi znaky nas u cisel nezajimaji
                    _readLine()
                if symbolTable[inst.dst].isInt():      matcher = _intMatcher
                elif symbolTable[inst.dst].isDouble(): matcher = _doubleMatcher
                
                matchObj = matcher.match(_inputBuffer)
                if matchObj:
                    if symbolTable[inst.dst].isInt():      symbolTable[inst.dst].value = int(matchObj.group(0))
                    elif symbolTable[inst.dst].isDouble(): symbolTable[inst.dst].value = float(matchObj.group(0))
                    _inputBuffer = _inputBuffer[len(matchObj.group(0)):] # umazeme z bufferu zpracovane znaky
                    if not len(_inputBuffer): _inputBuffer = None # zpracovali jsme vsechny znaky => buffer je prazdny coz indikuje None
                else:
                    raise RuntimeError("failed to read value of type %s" % type(symbolTable[inst.dst].value))
            else: # symbolTable[inst.dst].isString()
                symbolTable[inst.dst].value = _inputBuffer
                _inputBuffer = None # umazeme z bufferu zpracovane znaky
            
            if inst.operation == "readln": # zbytek radku zahodime
                _inputBuffer = None
        
        
        # vestavene funkce
        elif inst.operation == "sort":
            # zdrojovy string se nesmi zmenit => vytvorime docasnou promennou
            tmpList = list(symbolTable[inst.src1].value)            
            symbolTable[inst.dst].value = "".join(buildin.sort(tmpList))
        elif inst.operation == "find":
            if symbolTable[inst.src2].value == "": # special feature by zadani
                symbolTable[inst.dst].value = 0
            else:
                symbolTable[inst.dst].value = buildin.find(symbolTable[inst.src1].value, symbolTable[inst.src2].value) + 1
            
        # nepodmineny skok
        elif inst.operation == "goto":
            pc = inst.dst
            continue # vyhneme se inkrementaci pc
        # podmineny skok
        elif inst.operation == "goto-if-zero":
            if symbolTable[inst.src1].value == 0:
                pc = inst.dst
                continue # vyhneme se inkrementaci pc
        
        elif inst.operation == "label":
            pass
        else:
            raise Error("unknown operation %s" % inst.operation)
        
        pc += 1
