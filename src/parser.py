
'''
 soubor:   parser.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    23.1.2009 - 28.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''


from scanner import Scanner
from exceptions import SyntacticError, SemanticError
from instruction import Instruction
from token import Token
import language


class StackItem:
    '''
    Instance tridy predstavuje objekt na zasobniku pri precedencni syntakticke analyze (analyza vyrazu).
    
    self.code nabyva hodnot (retezcovych):
        ID expr <delimiter>
        + - * div < <= > >= = <> ( )
    self.address
        Jedna se o retezec, ktery je klicem do tabulky symbolu.
        Ma smysl pouze pokud self.code in ("ID", "expr").
    self.type
        Nabyva hodnot (retezcovych): CINT, CDOUBLE, CSTRING.
        Je definovan pouze pro self.code in ("expr", "ID").
    '''
    def __init__(self, code="", address=None, variableType=None):
        self.code = code
        self.address = address
        self.variableType = variableType
    
    def __str__(self):
        return "[%s] \"%s\"" % (self.code, self.address)


class Stack():
    '''
    Zasobnik pro precedencni syntaktickou analyzu.
    '''
    def __init__(self):
        self._stack = []    
    def __getitem__(self, index):
        return self._stack[index]    
    def __len__(self):
        return len(self._stack)
    
    def insert(self, index, object):
        '''
        Pred objekt na pozici index vlozi parametr object.
        '''
        return self._stack.insert(index, object)

    def push(self, *args):
        # napushuje agrumenty v tom poradi, ze args[0] bude na vrcholu zasobniku
        for i in range(len(args) - 1, -1, -1):
            self._stack.append(args[i])

    def pop(self, count=1):
        self._stack = self._stack[0:-count]

    def top(self):
        return self._stack[-1]
    
    def topTerminal(self):
        '''
        Vraci usporadanou dvojici (StackItem, index) terminalu, ktery je nejbliz vrcholu zasobniku
        nebo (StackItem(code=""), -1), pokud na zasobniku zadny terminal neni.
        Za terminal se povazuje vse co je platne jako StackItem.code krome "<delimiter>" a "expr".
        '''
        for i in range(1, len(self._stack)):
            if self._stack[-i].code != "expr" and self._stack[-i].code[0] != "<delimiter>":
                return (self._stack[-i], len(self._stack) - i)
        return (StackItem(code=""), -1)

    def empty(self):
        return len(self._stack) == 0


    def topMatches(self, seq):
        '''
        Vraci True, kdyz seq[0]. == _stack[-1].code and seq[1] == _stack[-2].code ...
        Jinak vraci false.
        '''
        if len(seq) > len(self._stack):
            return False
        for i in range(len(seq)):
            if seq[i] != self._stack[-(i+1)].code:
                return False
        else:
            return True



##############################################################################################


class Parser():
    def __init__(self, fileObj, symbolTable):
        self._srcFile = fileObj
        self._symbolTable = symbolTable
        self._instructionsList = []
        self._scanner = Scanner(fileObj)
        self._currentToken = None
        
        # self._precedenceTable[nejvrchnejsi_terminal_zasobniku][aktualni_token] -> akce
        self._precedenceTable = {
            "*":   dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "=", "<>", ")", "") + ("(", "ID"), (">", )*12 + ("<", )*2)  ),
            "div": dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "=", "<>", ")", "") + ("(", "ID"), (">", )*12 + ("<", )*2)  ),
            "+":   dict(  zip(("+", "-", "<", "<=", ">", ">=", "=", "<>", ")", "") + ("*", "div", "(", "ID"), (">", )*10 + ("<", )*4)  ),
            "-":   dict(  zip(("+", "-", "<", "<=", ">", ">=", "=", "<>", ")", "") + ("*", "div", "(", "ID"), (">", )*10 + ("<", )*4)  ),            
            "<":   dict(  zip(("*", "div", "+", "-", "(", "ID") + ("<", "<=", ">", ">=", "=", "<>", ")", ""), ("<", )*6 + (">", )*8)  ),
            ">":   dict(  zip(("*", "div", "+", "-", "(", "ID") + ("<", "<=", ">", ">=", "=", "<>", ")", ""), ("<", )*6 + (">", )*8)  ),
            "<=":  dict(  zip(("*", "div", "+", "-", "(", "ID") + ("<", "<=", ">", ">=", "=", "<>", ")", ""), ("<", )*6 + (">", )*8)  ),
            ">=":  dict(  zip(("*", "div", "+", "-", "(", "ID") + ("<", "<=", ">", ">=", "=", "<>", ")", ""), ("<", )*6 + (">", )*8)  ),            
            "=":   dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "(", "ID") + (")", "=", "<>", ""), ("<", )*10 + (">", )*4)  ),
            "<>":  dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "(", "ID") + (")", "=", "<>", ""), ("<", )*10 + (">", )*4)  ),            
            "(":   dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "=", "<>", "(", "ID") + (")", ""), ("<", )*12 + ("=", ""))  ),              
            ")":   dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "=", "<>", ")", "") + ("(", "ID"), (">", )*12 + ("", )*2)  ),            
            "ID":  dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "=", "<>", ")", "") + ("(", "ID"), (">", )*12 + ("", )*2)  ),            
            "":    dict(  zip(("*", "div", "+", "-", "<", "<=", ">", ">=", "=", "<>", "(", "ID") + (")", ""), ("<", )*12 + ("OK", )*2)  ),
        }
        
        # signatury binarnich operatoru pro kontorlu spravne semantiky v dobe prekladu ve tvaru:
        #       _operationSignatures[(operace, typeOperand1, typeOperand2)] == typeResult
        # Pokud (operace, typeOperand1, typeOperand2) not in _operationSignatures ==> tato kombinace operandu neni povolena.
        self._operationSignatures = {
            ("+", "CSTRING", "CSTRING"): "CSTRING", # konkatenace retezcu
            ("div", "CINT", "CINT"): "CINT",        # div akceptuje pouze integery
            # aritmeticke operace na ciselnymi typy (kdyz je aspon jeden operand double, je vysledek double; jinak je vysledek int)
            ("+", "CINT", "CINT"): "CINT", ("+", "CINT", "CDOUBLE"): "CDOUBLE", ("+", "CDOUBLE", "CINT"): "CDOUBLE", ("+", "CDOUBLE", "CDOUBLE"): "CDOUBLE",
            ("-", "CINT", "CINT"): "CINT", ("-", "CINT", "CDOUBLE"): "CDOUBLE", ("-", "CDOUBLE", "CINT"): "CDOUBLE", ("-", "CDOUBLE", "CDOUBLE"): "CDOUBLE",
            ("*", "CINT", "CINT"): "CINT", ("*", "CINT", "CDOUBLE"): "CDOUBLE", ("*", "CDOUBLE", "CINT"): "CDOUBLE", ("*", "CDOUBLE", "CDOUBLE"): "CDOUBLE",
            # relacni operatory porovnavaji pouze promenne tehoz typu, vysledkem porovnani je int
            ("<", "CINT", "CINT"): "CINT", ("<", "CDOUBLE", "CDOUBLE"): "CINT", ("<", "CSTRING", "CSTRING"): "CINT",
            (">", "CINT", "CINT"): "CINT", (">", "CDOUBLE", "CDOUBLE"): "CINT", (">", "CSTRING", "CSTRING"): "CINT",
            ("=", "CINT", "CINT"): "CINT", ("=", "CDOUBLE", "CDOUBLE"): "CINT", ("=", "CSTRING", "CSTRING"): "CINT",
            ("<=", "CINT", "CINT"): "CINT", ("<=", "CDOUBLE", "CDOUBLE"): "CINT", ("<=", "CSTRING", "CSTRING"): "CINT",
            (">=", "CINT", "CINT"): "CINT", (">=", "CDOUBLE", "CDOUBLE"): "CINT", (">=", "CSTRING", "CSTRING"): "CINT",
            ("<>", "CINT", "CINT"): "CINT", ("<>", "CDOUBLE", "CDOUBLE"): "CINT", ("<>", "CSTRING", "CSTRING"): "CINT",
        }

    
    def _generateInstruction(self, operation, dest, src1, src2):
        '''
        Prida instrukci do self._instructionsList a vrati adresu vlozene instrukce
        (tzn. jeji index v self._instructionsList).
        '''
        self._instructionsList.append(Instruction(operation, dest, src1, src2))
        return len(self._instructionsList) - 1
    
    def getInstruction(self, address):
        return self._instructionsList[address]
    
    def getInstructions(self):
        return self._instructionsList
    
    def _actualToken(self):
        # vrati soucasny token bez toho aby se prechazelo na dalsi
        if self._currentToken is None:
            self._currentToken = self._scanner.getNextToken()
        return self._currentToken
    
    def _nextToken(self):
        # precte dalsi token a ten vrati
        self._currentToken = self._scanner.getNextToken()
        return self._currentToken
        
        
    def parse(self):
        self._ruleProg()
        return self._instructionsList
    
    
    #################################################
    ## metody simulujici stavbu derivacniho stromu ##
    #################################################
    def _ruleProg(self):
        token = self._actualToken()
        if token.code in ("begin", "var"): # 1. <prog> -> <declarations> <body>
            self._ruleDeclarations()
            self._ruleBody()
        else:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(token)))
    
    def _ruleDeclarations(self):
        token = self._actualToken()
        if token.code in ("var", ): # 2. <declarations> -> var <declaration> <decl-list>
            self._nextToken() # "smazeme"/zpracujeme aktualni token "var"
            self._ruleDeclaration()
            self._ruleDeclList()
        elif token.code in ("begin", ): # 3. <declarations> -> eps
            return
        else:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(token)))
    
    def _ruleDeclaration(self):
        ok = False
        idToken = self._actualToken()
        if idToken.code == "ID": # 4. <declaration> -> id : <type> ;
            if self._nextToken().code == ":":
                typeToken = self._nextToken()
                if typeToken.code in ("integer", "double", "string"):
                    if self._nextToken().code == ";":
                        ok = True
                        self._nextToken() # pripravime novy token, protoze strednik se v tomto pravidle zpracuje
                        # vlozeni promenne prislusneho typu do tabulky symbolu
                        if idToken.value not in self._symbolTable:
                            if typeToken.code == "integer":  self._symbolTable.addVariable(idToken.value, 0)
                            elif typeToken.code == "double": self._symbolTable.addVariable(idToken.value, 0.0)
                            else:                            self._symbolTable.addVariable(idToken.value, "")
                        else:
                            raise SemanticError("%s: redefinition of variable \"%s\"" % (self._scanner.getLineNumber(), idToken.value))
        if not ok:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
            
    def _ruleDeclList(self):
        if self._actualToken().code == "ID": # 5. <decl-list> -> <declaration> <decl-list>
            self._ruleDeclaration()
            self._ruleDeclList()
        elif self._actualToken().code == "begin": # 6. <decl-list> -> eps
            return
        else:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
    
    def _ruleBody(self):
        ok = False
        if self._actualToken().code == "begin": # pokus rozvinout 7. <body> -> begin <statements> end .
            self._nextToken() # zpracovali jsme token "begin"
            self._ruleStatements()
            if (self._actualToken().code == "end" and self._nextToken().code == "." and self._nextToken().code == ""):
                ok = True
        if not ok:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
    
    def _ruleStatements(self):
        if self._actualToken().code in ("begin", "readln", "write", "ID", "if", "while"): # 8. <statements> -> <statement> <st-list>
            self._ruleStatement()
            self._ruleStList()
        elif self._actualToken().code == "end": # 9. <statements> -> eps
            return
        else:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
    
    
    def _ruleStatement(self):
        ok = False
        
        if self._actualToken().code == "begin": # 12. <statement> -> begin <statements> end
            self._nextToken() # zpracujeme token "begin"
            self._ruleStatements()
            if self._actualToken().code == "end":
                self._nextToken() # zpracujeme token "end"
                ok = True
        # #end of# if self._actualToken().code == "begin":
        elif self._actualToken().code == "readln": # 13. <statement> -> readln ( id <id-list> )
            def _ruleIdList(): # pomocna fce pro zpracovani <id-list>
                if self._actualToken().code == ",": # <id-list> -> , id <id-list>  (vraci identifikator promenne)
                    if self._nextToken().code == "ID": # zpracujeme token ","
                        ret = self._actualToken().value
                        self._nextToken() # zpracujeme token "ID"
                        return ret
                elif self._actualToken().code == ")": # <id-list> -> eps  (vraci None)
                    return None
                else:
                    raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
            idList = []
            self._nextToken() # zpracujeme token "readln"
            if self._actualToken().code == "(":
                self._nextToken() # zpracujeme token "("
                if self._actualToken().code == "ID":
                    idList.append(self._actualToken().value)
                    self._nextToken() # zpracuje token "ID"
                    while True: # nacteme vsechny nasledujici identifikatory (zpracujeme <id-list>)
                        id = _ruleIdList()
                        if id: idList.append(id)
                        else: break
                    if self._actualToken().code == ")":
                        self._nextToken() # zpracujeme token ")"
                        # semanticka kontrola - vsechny identifikatory musi byt definovany
                        if not all(map(lambda id: id in self._symbolTable, idList)):
                            raise SemanticError("%s: variable \"%s\" isn't defined" % (self._scanner.getLineNumber(), id))
                        # semanticka kontrola - pokud je identifikatoru vice, musi byt pouze ciselne (zadny string)
                        if len(idList) > 1 and any(map(lambda id: self._symbolTable[id].isString(), idList)):
                            raise SemanticError("%s: when using multiple identifiers in readln, no string type variable is allowed" % (self._scanner.getLineNumber()))
                        # prvni az predposledni promenne ctou jen to, co je zajima
                        for i in range(0, len(idList)-1): self._generateInstruction("read", idList[i], None, None)
                        # s posledni promennou se docte vsechno az do konce radku
                        self._generateInstruction("readln", idList[-1], None, None)
                        ok = True
        # #end of# elif self._actualToken().code == "readln":
        elif self._actualToken().code == "write": # 14. <statement> -> write ( expr <expr-list> )
            def _ruleExprList():
                if self._actualToken().code == ",": # 18. <expr-list> -> , expr <expr-list>
                    self._nextToken() # zpracovani tokenu ","
                    exprAddress = self._symbolTable.addTemp()
                    self._parseExpr(exprAddress)
                    return exprAddress
                elif self._actualToken().code == ")": # 19. <expr-list> -> eps
                    return None
                else:
                    raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
            if self._nextToken().code == "(": # zpracovani tokenu "write"
                self._nextToken() # zpracovani tokenu "("
                exprAddress = self._symbolTable.addTemp()
                self._parseExpr(exprAddress)
                self._generateInstruction("write", None, exprAddress, None)
                while True:
                    exprAddress = _ruleExprList()
                    if exprAddress: self._generateInstruction("write", None, exprAddress, None)
                    else: break
                if self._actualToken().code == ")":
                    self._nextToken() # zpracovani tokenu ")"
                    ok = True
        # #end of# elif self._actualToken().code == "write":        
        elif self._actualToken().code == "ID": # 15. <statement> -> ID := expr
            destinationID = self._actualToken().value
            # semanticka kontrola - destination ID musi predstavovat definovanou promennou
            if destinationID not in self._symbolTable:
                raise SemanticError("%s: variable \"%s\" isn't defined" % (self._scanner.getLineNumber(), destinationID))
            if self._nextToken().code == ":=":
                self._nextToken() # zpracujeme token ":="
                exprResultID = self._symbolTable.addTemp()
                self._parseExpr(exprResultID)
                # semanticka kontrola - zdroj a cil musi byt stejneho typu
                if type(self._symbolTable[destinationID].value) != type(self._symbolTable[exprResultID].value):
                    raise SemanticError("%s: incompatible types for assign" % self._scanner.getLineNumber())
                self._generateInstruction(":=", destinationID, exprResultID, None)
                ok = True
        # #end of# elif self._actualToken().code == "ID":
        elif self._actualToken().code == "if": # 16. <statement> -> if integer_expr then <statement> else <statement>
            # cilena struktura sledu instrukci je nasledujici:
            #     if not expr goto labelElse
            #     <statement>
            #     goto labelAfterElse
            # labelElse:
            #     <statement>
            # labelAfterElse:
            self._nextToken() # zpracovani tokenu "if"
            # zpracovani "expr"
            conditionAddress = self._symbolTable.addTemp()
            self._parseExpr(conditionAddress)
            # semanticka kontrola - vyraz v podmince musi byt typu integer
            if not self._symbolTable[conditionAddress].isInt():
                raise SemanticError("%s: condition in if statement must be of integer type" % self._scanner.getLineNumber())
            instGotoLabelElseAddress = self._generateInstruction("goto-if-zero", 0, conditionAddress, None)
            if self._actualToken().code == "then":
                self._nextToken() # zpracovani tokenu "then"
                self._ruleStatement() # zpracovani <statement>
                instGotoAfterElseAddress = self._generateInstruction("goto", 0, None, None)
                labelElseAddress = self._generateInstruction("label", None, None, None)
                if self._actualToken().code == "else":
                    self._nextToken() # zpracovani tokenu "else"
                    self._ruleStatement() # zpracovani <statement>
                    labelAfterElseAddress = self._generateInstruction("label", None, None, None)
                    # napojeni skoku na labely
                    self.getInstruction(instGotoLabelElseAddress).dst = labelElseAddress
                    self.getInstruction(instGotoAfterElseAddress).dst = labelAfterElseAddress
                    ok = True
        # #end of# elif self._actualToken().code == "if":
        elif self._actualToken().code == "while": # 17. <statement> -> while integer_expr do <statement>
            # cilena struktura sledu instrukci je nasledujici:
            # labelBeforeWhile:
            #     if not expr goto labelAfterWhile
            #     <statement>
            #     goto labelBeforeWhile
            # labelAfterWhile:
            self._nextToken() # zpracujeme token "while"
            condVariableAddress = self._symbolTable.addTemp() # ridici promenna cyklu
            labelBeforeWhileAdr = self._generateInstruction("label", None, None, None)
            self._parseExpr(condVariableAddress) # zpracujeme "expr"
            # semanticka kontrola - vyraz v podmince musi byt typu integer
            if not self._symbolTable[condVariableAddress].isInt():
                raise SemanticError("%s: condition in while statement must be of integer type" % self._scanner.getLineNumber())
            conditionalJumpInstAddress = self._generateInstruction("goto-if-zero", 0, condVariableAddress, None) # konec cykleni
            if self._actualToken().code == "do":
                self._nextToken() # zpracujeme token "do"
                self._ruleStatement()
                self._generateInstruction("goto", labelBeforeWhileAdr, None, None) # nepodmineny skok na podminku while
                # label za cyklem
                labelAfterWhileAdr = self._generateInstruction("label", None, None, None)
                # napojeni podmineneho skoku na zacatku while (ukonceni while)
                self.getInstruction(conditionalJumpInstAddress).dst = labelAfterWhileAdr
                ok = True
        # #end of# elif self._actualToken().code == "while":
        if not ok:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
    # #end of# def _ruleStatement(self):
    
    
    def _ruleStList(self):
        # zpracovali jsme prikaz => muzeme zacit s docasnymi promennymi pracovat odznova
        self._symbolTable.resetTemps()
        if self._actualToken().code == ";": # 10. <st-list> -> ; <statement> <st-list>
            self._nextToken() # zpracujeme token ";"
            self._ruleStatement()
            self._ruleStList()
        elif self._actualToken().code == "end": # 11. <st-list> -> eps
            return
        else:
            raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
    
    
    
    ##########################################################################################
    ###########################          gramatika vyrazu          ###########################
    ##########################################################################################
    
    def _parseExpr(self, destinationAdr):
        '''
        Zpracovava vyraz, vygeneruje instrukce ukladajici vysledek do destination.address.
        @param destinationAdr        adresa promenne v ramci tabulky symbolu kam se ulozi hodnota celeho vyrazu
        '''
        exprStack = Stack()
        
        def isExprToken(token):
            return token.code in ("ID", "CINT", "CDOUBLE", "CSTRING", "expr", "(", ")") + language.RELATION_OPERATORS + language.ARITMETIC_OPERATORS
        def variableType(varAddress):
            if self._symbolTable[varAddress].isInt(): return "CINT"
            elif self._symbolTable[varAddress].isDouble(): return "CDOUBLE"
            elif self._symbolTable[varAddress].isString(): return "CSTRING"
            else:
                raise KeyError("%d: warning: unknown variable type for variable %s" % (self._scanner.getLineNumber(), varAddress))
                return None
        
        resultTypeToValue = {"CINT": 0, "CDOUBLE": 0.0, "CSTRING": ""}
        
        while True:
            token = self._actualToken()
            
            # zvlastni osetreni vestavenych funkci (volani funkce prevedeme na promennou (jako by ve zdrojaku byl
            # misto volani funkce bezny identifikator)
            #   => zpracujeme ji a na zasobnik vlozime docasnou promennou (ID) s navratovou hodnotou vestavene funkce
            if token.code == "sort": # sort ( string_expr ) -> string
                ok = False
                if self._nextToken().code == "(": # zpracovani tokenu "sort"
                    self._nextToken() # zpracovani tokenu "("
                    sortArgument = self._symbolTable.addTemp()
                    self._parseExpr(sortArgument) # vyhodnotime argument funkce sort
                    if variableType(sortArgument) != "CSTRING": # argument sortu musi byt string
                        raise SemanticError("%s: sort argument must be string" % self._scanner.getLineNumber())
                    if self._actualToken().code == ")":
                        #self._nextToken() # zpracovani tokenu ")" !!!! VYNECHAME protoze precedenci analyza vysledek
                        #                                          !!!! sortu (ID) nashiftuje a posune se na dalsi token
                        # vygeneruje instrukci pro sort
                        sortResult = self._symbolTable.addTemp(value="") # sort vraci string => nastavime retezcovou hodnotu
                        self._generateInstruction("sort", sortResult, sortArgument, None)
                        # z hlediska precedencni analyzy jsme zpracovanim funkce sort ziskali
                        # novou retezcovou promennou (ID) => upravime token a ten dal muze precedencni anazyla zpracovat
                        # jako bezny identifikator
                        token.code, token.value = "ID", sortResult
                        ok = True
                if not ok:
                    raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
            elif token.code == "find": # find ( string_expr , string_expr ) -> integer
                ok = False
                if self._nextToken().code == "(": # smazeme token "find"
                    self._nextToken() # smazeme token "("
                    findResult, arg1, arg2 = self._symbolTable.addTemp(value=0), self._symbolTable.addTemp(), self._symbolTable.addTemp()
                    self._parseExpr(arg1)
                    if variableType(arg1) != "CSTRING": # argument findu musi byt string
                        raise SemanticError("%s: finds first argument must be string" % self._scanner.getLineNumber())
                    if self._actualToken().code == ",":
                        self._nextToken() # smazeme token ","
                        self._parseExpr(arg2)
                        if variableType(arg2) != "CSTRING": # argument findu musi byt string
                            raise SemanticError("%s: finds second argument must be string" % self._scanner.getLineNumber())
                        if self._actualToken().code == ")":
                            #self._nextToken() # token ")" nemazeme, protoze to obsatara precedencni analyza po zashiftovani
                            self._generateInstruction("find", findResult, arg1, arg2)
                            # z hlediska precedencni analyzy jsme vyhodnocenim funkce find ziskali novou hodnotu
                            # typu CINT => upravime token a muzeme s nim dal v ramci precedencni analyzy pracovat
                            # jako s beznym identifikatorem
                            token.code, token.value = "ID", findResult
                            ok = True
                if not ok:
                    raise SyntacticError("%s: unexpected token %s" % (self._scanner.getLineNumber(), str(self._actualToken())))
            # #end of# zvlastni osetreni vestavenych funkci (funkce je vlastne vyraz)
            
            
            precedenceCode = token.code
            if not isExprToken(token): # token uz nepatri do vyrazu => nahradime jej pro ucely precedencni analyzy prazdnym tokenem
                precedenceCode = ""
            elif token.code in ("CINT", "CDOUBLE", "CSTRING"): # pro ucely precedencni analyzy je to ID
                precedenceCode = "ID"

            (topTerminal, topTerminalIndex) = exprStack.topTerminal()

            # shiftovani
            if self._precedenceTable[topTerminal.code][precedenceCode] in ("<", "="):
                if self._precedenceTable[topTerminal.code][precedenceCode] == "<":
                    exprStack.insert(topTerminalIndex + 1, StackItem(code="<delimiter>")) # vlozime si "zarazku" pro lehci zpracovani vyrazu
                
                if token.code == "ID":
                    # semanticka kontrola - je identifikator definovan?
                    if token.value not in self._symbolTable:
                        raise SemanticError("%s: variable \"%s\" isn't defined" % (self._scanner.getLineNumber(), token.value))
                    exprStack.push(StackItem(code="ID", address=token.value, variableType=variableType(token.value)))
                elif token.code in ("CINT", "CDOUBLE", "CSTRING"): # konstantu vlozime do tabulky symbolu
                    address = self._symbolTable.addConstant(token.value)
                    exprStack.push(StackItem(code="ID", address=address, variableType=variableType(address)))
                else: # operator
                    exprStack.push(StackItem(code=token.code))
                # cteme dalsi token (kvuli tomuto se ve zpracovani find a sort nepreskakuje posledni token)
                self._nextToken()
                    
            # redukce
            elif self._precedenceTable[topTerminal.code][precedenceCode] == ">":
                # E -> id
                if exprStack.topMatches(("ID", "<delimiter>")):
                    resultAddress = exprStack[-1].address
                    removeCount = 2
                # E -> (E)
                elif exprStack.topMatches((")", "expr", "(", "<delimiter>")):
                    resultAddress = exprStack[-2].address
                    removeCount = 4
                # E -> E op E
                elif (len(exprStack) >= 4 and exprStack[-1].code == exprStack[-3].code == "expr" and exprStack[-4].code == "<delimiter>" 
                        and exprStack[-2].code in ("+", "-", "*", "div", "<", "<=", ">", ">=", "<>", "=")):
                    # kontrola spravnych typu operandu
                    operationDescription = (exprStack[-2].code, exprStack[-3].variableType, exprStack[-1].variableType) # (operace, 1. operand, 2. operand)
                    if operationDescription not in self._operationSignatures:
                        raise SemanticError("%s: invalid operand types for operation %s" % (self._scanner.getLineNumber(), exprStack[-2].code))
                    resultType = self._operationSignatures[operationDescription]
                    resultAddress = self._symbolTable.addTemp(value=resultTypeToValue[resultType])
                    removeCount = 4
                    operation = exprStack[-2].code
                    self._generateInstruction(operation, resultAddress, exprStack[-3].address, exprStack[-1].address)
                else:
                    raise SyntacticError("%s: no reduction rule" % (self._scanner.getLineNumber()))
                exprStack.pop(count=removeCount) # vymazeme ("vyredukujeme")
                exprStack.push(StackItem(code="expr", address=resultAddress, variableType=variableType(resultAddress))) # na zasobnik vlozime vysledek redukce
            # dokonceni zpracovani vyrazu
            elif self._precedenceTable[topTerminal.code][precedenceCode] == "OK":
                # na zasobniku je pouze finalni vyraz => uspesne dokonceni zpracovani vyrazu
                if len(exprStack) == 1 and exprStack[0].code == "expr":
                    self._generateInstruction(":=", destinationAdr, exprStack[0].address, None)
                    # nastavime vysledku spravy typ
                    self._symbolTable[destinationAdr].value = resultTypeToValue[exprStack[0].variableType]
                    break
                else:
                    raise SyntacticError("%s: unexpected end of expression processing" % (self._scanner.getLineNumber()))
            # neuspesne dokonceni zpracovani vyrazu (pravidlo v precedencni tabulce je prazdne)
            else:
                raise SyntacticError("%s: unexpected token (%s) in expression" % (self._scanner.getLineNumber(), str(token)))
