
'''
 soubor:   scanner.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    23.1.2009 - 28.1.2009
 kodovani: ASCII znaky do hodnoty 127
 
  rozsireni:
      - zpracovani radkovych komentaru FreePascalu (od "//" do konce radku)
      - zadavani cisel v soustavach o zakladu 2,8,16
      - pratelske chybove hlasky o pravdepodobnych lexikalnich chybach
'''

import re
import string
import functools

import language
from exceptions import LexicalError
from token import Token


class Scanner:
    def __init__(self, file):
        self._file = file
        self._lineNumber = 1
        self._starterAlphabets = { # znaky, kterymi mohou tokeny zacinat
                          "ID": "_" + string.ascii_letters,
                          "CINT2": "%",
                          "CINT8": "&",
                          "CINT10": string.digits,
                          "CINT16": "$", 
                          "CSTRING": "'",
                          "OPERATOR": functools.reduce(lambda x,y: x+y, (x for x in language.OPERATORS if not x.isalpha())),
                          }
        self._insiderAlphabets = { # znaky, ktere mohou byt v tokenech na 2. pozici a dale
                          "ID": string.ascii_letters + string.digits,
                          "CINT2": "01",
                          "CINT8": string.octdigits,
                          "CINT10": string.digits,
                          "CINT16": string.hexdigits,
                         }
                        
    def getLineNumber(self):
        return self._lineNumber
        
    def _parseInt(self, str, base):
        if base != 10: str = str[1:]
        return int(str, base=base)
    
    def getNextToken(self):
        nextToken = Token()
        currentString = "" # co jsme v tomto volani doposud precetli a povazujeme to za soucast tokenu (ne komentar, ne bily znak...)
        state = "START"    # stav FSM
        tokenComplete = False
        
        while not tokenComplete:
            char = self._file.read(1)
            append = True # ma se char konkatenovat s currentString?
            unget = False # ma se char vracet zpet do soubotu? (jako bychom ho neprecetli)
            if state == "START":
                if char.isspace(): # preskocime bile znaky pred tokenem
                    append = False
                elif char == "{": # zacatek blokoveho komentare
                    append = False
                    state = "BLOCK_COMMENT"
                elif char == "/": # mozny zacatek radkoveho komentare
                    append = False
                    state = "POSSIBLE_LINE_COMMENT"
                elif not char:
                    nextToken = Token() # Token(code="EOF")
                    tokenComplete = True
                else: # hledani zacatku ruznych tokenu
                    for tokenType in self._starterAlphabets:
                        if char in self._starterAlphabets[tokenType]:
                            state = tokenType
                            break
                    else: # zacatek tokenu nebyl rozpoznan
                        raise LexicalError("%d: \"%s\" is not a valid token" % (self._lineNumber, currentString + char))
            # blokovy komentar
            elif state == "BLOCK_COMMENT":
                append = False
                if char == "}":
                    state = "START"
            # prislo nam jedno lomitko a cekame na druhe
            elif state == "POSSIBLE_LINE_COMMENT":
                append = False
                if char == "/":
                    state = "LINE_COMMENT"
                else: # ve zdrojaku se vyskytovalo pouze jedno lomitko
                    raise LexicalError("%d: \"%s\" is not a valid token" % (self._lineNumber, "/"))
            # preskakujeme znaky do konce radku
            elif state == "LINE_COMMENT":
                append = False
                if char == "\n":
                    state = "START"
                    
            elif state == "ID":
                if char not in self._insiderAlphabets["ID"]:
                    unget = True
                    tokenComplete = True
                    if currentString in language.KEYWORDS + language.OPERATORS:
                        nextToken = Token(code=currentString)
                    else:
                        nextToken = Token(code="ID", value=currentString)
                        
            elif state in ("CINT2", "CINT8", "CINT10", "CINT16"):
                if char not in self._insiderAlphabets[state]:
                    if char in ".eE":
                        if state != "CINT10":
                            raise LexicalError("%d: \"%s\" is not a valid float constant" % (self._lineNumber, currentString + char))
                        else: # lze prejit do stavu cteni doublu
                            if char == ".": state = "CDOUBLE_FRAC"
                            else: state = "CDOUBLE_EXP_E"
                    else:
                        if state != "CINT10":
                            # kontrola jestli se krome indikatoru ciselne soustavy nacetlo vubec i nejake cislo
                            if len(currentString) == 1:
                                raise LexicalError("%d: \"%s\" is not a valid integer constant" % (self._lineNumber, currentString))
                        # kontrola rozsahu
                        if self._parseInt(currentString, base=int(state[4:])) < 2**31 - 1: # maximalni hodnota C integeru
                            nextToken = Token(code="CINT", value=self._parseInt(currentString, base=int(state[4:])))
                            tokenComplete = True
                            unget = True
                        else:
                            raise LexicalError("%d: \"%s\" integer constant out of allowed range" % (self._lineNumber, currentString))
            
            elif state == "CDOUBLE_FRAC":
                if char not in string.digits:
                    if char in "eE" and currentString[-1] != ".": # desetinna cast nesmi byt prazdna
                        state = "CDOUBLE_EXP_E"
                    else:
                        # kontrolujeme i rozsah promenne (nesmi byt nekonecno)
                        if currentString[-1] != "." and abs(float(currentString)) != float("inf"):
                            nextToken = Token(code="CDOUBLE", value=float(currentString))
                            tokenComplete = True
                            unget = True
                        else:
                            raise LexicalError("%d: \"%s\" is not a valid float constant (empty fraction)" % (self._lineNumber, currentString))
            
            elif state == "CDOUBLE_EXP_E":                
                if char not in "+-": # pokud se nejedna o znamenko, zpracujeme znak az v CDOUBLE_EXP
                    unget = True
                state = "CDOUBLE_EXP"
            
            elif state == "CDOUBLE_EXP":
                if char not in string.digits:
                    unget = True
                    # kontrolujeme i rozsah promenne (nesmi byt nekonecno)
                    if currentString[-1].isdigit() and abs(float(currentString)) != float("inf"):
                        nextToken = Token(code="CDOUBLE", value=float(currentString))
                        tokenComplete = True
                    else:
                        raise LexicalError("%d: \"%s\" is not a valid float constant (empty exponent)" % (self._lineNumber, currentString))
                    
            elif state == "CSTRING":
                if char == "'":
                    state = "CSTRING_APOSTROPH"
                    append = False
                elif ord(char) < 32:
                    raise LexicalError("%d: string characters must have ordinal value at least 32" % (self._lineNumber))
            elif state == "CSTRING_APOSTROPH":
                if char == "'": # tento apostrof do retezce pridame ('' je v pascalu escape pro ')
                    state = "CSTRING"
                elif char == "#":
                    append = False
                    state = "CSTRING_ESCAPE"
                    escape = None
                else: # docetli jsme string
                    nextToken = Token(code="CSTRING", value=currentString[1:]) # umazeme uvodni apostrof
                    tokenComplete = True
                    unget = True
            elif state == "CSTRING_ESCAPE":
                append = False
                if char in string.digits: # dalsi cislice escape sekvence
                    if escape is None: escape = 0
                    escape = escape * 10 + ord(char[0]) - b'0'[0]
                elif char == "'": # konec escape sekvence
                    if escape is None or escape > 31 or escape < 1:
                        raise LexicalError("%d: invalid escape sequence %d in string constant" % (self._lineNumber, escape))
                    else:
                        currentString += chr(escape)
                        state = "CSTRING"
                    
            elif state == "OPERATOR":
                if (currentString + char) not in language.OPERATORS:
                    nextToken = Token(code=currentString)
                    tokenComplete = True
                    unget = True
            else:
                print("!!! UNKNOWN SCANNER STATE %s" % state)
            
            
            if not char and not tokenComplete:
                raise LexicalError("%d: invalid token \"%s\"at the end of file" % (self._lineNumber, currentString))
                nextToken = Token(code="")
            
            if append and not unget:
                currentString += char
            if not unget and char == "\n":
                    self._lineNumber += 1
            if unget: # jako bysme soucasny znak neprecetli
                self._file.seek(self._file.tell() - 1)
        return nextToken
    # #end of# def getNextToken(self):
