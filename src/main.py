#!/usr/bin/env python3

'''
 soubor:    main.py
 projekt:   solo remake IFJ semestralniho projektu 2009
 autor:     David Chaloupka
 datum:     25.1.2009 - 27.1.2009
 kodovani:  ASCII znaky do hodnoty 127
 pozadavky: Python 3
'''

if __name__ == "__main__":
    import sys

    from parser import Parser
    from symboltable import SymbolTable
    from interpret import interpret
    from exceptions import LexicalError, SyntacticError, SemanticError, RuntimeError
    

    if len(sys.argv) == 2:
        ret = 0
        try:
            srcFile = None
            srcFile = open(sys.argv[1], "r")        
            symbolTable = SymbolTable()        
            
            parser = Parser(srcFile, symbolTable)
            instructions = parser.parse()
            
            interpret(instructions, symbolTable)            
        except LexicalError as lexicalError:
            sys.stderr.write("lexical error: %s\n" % str(lexicalError))
            ret = 1
        except SyntacticError as syntacticError:
            sys.stderr.write("syntactic error: %s\n" % str(syntacticError))
            ret = 2
        except SemanticError as semanticError:
            sys.stderr.write("semantic error: %s\n" % str(semanticError))
            ret = 3
        except RuntimeError as runtimeError:
            sys.stderr.write("runtime error: %s\n" % str(runtimeError))
            ret = 4
        except IOError as ioerror:
            sys.stderr.write("IOError: %s\n" % str(ioerror))
            ret = 5
            
        finally:
            if srcFile: srcFile.close()
    else:
        sys.stderr.write("error: invalid parametres\n")
        ret = 5

    sys.exit(ret)
