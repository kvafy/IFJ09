
'''
 soubor:   buildin.py
 projekt:  solo remake IFJ semestralniho projektu 2009
 autor:    David Chaloupka
 datum:    28.1.2009 - 31.1.2009
 kodovani: ASCII znaky do hodnoty 127
'''

import collections


def sort(array):
    '''
    Vestavena funkce jazyka IFJ09 pro razeni retezcu.
    Implementuje nerekurzivni quicksort. In-place seradi prvky pole.
    '''
    def partition(left, right):
        i = left
        j = right
        median = array[(left + right) // 2]
        while True:
            while array[i] < median: i += 1
            while array[j] > median: j -= 1
            if i <= j:
                array[i], array[j] = array[j], array[i]
                i += 1
                j -= 1
            else:
                return ((left, j), (i, right))
    
    stack = [(0, len(array)-1)]
    
    while len(stack):
        left, right = stack.pop()
        while left < right:
            (l1, r1), (l2, r2) = partition(left, right)
            if r1 - l1 > r2 - l2: # leva cast je delsi nez prava
                stack.append((l1, r1)) # delsi cast zpracujeme pozdeji
                left, right = l2, r2 # kratsi cast pri dalsim pruchodu cyklu
            else:
                stack.append((l2, r2))
                left, right = l1, r1
    return array



def find(strHaystack, strNeedle):
    '''
    Implementuje vyhledavani podretezce v retezci Boyer-Moore algoritmem se dvema heuristikami.
    Vraci index, na kterem se nachazi strNeedle nebo -1, pokud podretezec nebyl nalezen.
    '''
    def constructBadCharacterTable(pattern):
        ret = collections.defaultdict(lambda: len(pattern))
        for i in range(len(pattern) - 1):
            ret[pattern[i]] = len(pattern) - 1 - i
        return ret
    def constructGoodSuffixTable(pattern):
        ret = collections.defaultdict(lambda: len(pattern))
        ret[0] = 1 # pri shode nula znaku se posouvame o jeden (toto vyresi prvni heuristika)
        for tableIndex in range(1, len(pattern)): # tableIndex = delka suffixu ktery hledame jako podretezec v pattern
            i = len(pattern) - 2 # i = mozna pozice konce (casti) suffixu pattern uvnitr pattern
            done = False # mame pro tento tableIndex vysledek?
            while i >= 0 and not done:
                couldBeHere = True
                j = 0 # citac porovnavaneho znaku
                while j < tableIndex and i - j >= 0 and couldBeHere:
                    if pattern[i - j] != pattern[len(pattern) - 1 - j]:
                        couldBeHere = False # tady suffix neni
                    j += 1 # mozna suffix je, pokracujeme kontrolou dalsiho znaku
                # jestli muzeme porovnat znak pred suffixem (popr. jeho casti), musi byt znaky ruzne
                if couldBeHere and (i - j < 0 or pattern[i - j] != pattern[len(pattern) - 1 - j]):
                    ret[tableIndex] = len(pattern) - 1 - i
                    done = True
                else:
                    i -= 1
        return ret
        
    # indexem do tabulky je znak v textu, na kterem doslo k neshode
    badCharTable = constructBadCharacterTable(strNeedle)
    # indexem do tabulky je pocet shodujicich se znaku nez doslo k neshode mezi textem a vzorkem
    goodSuffixTable = constructGoodSuffixTable(strNeedle)

    if not len(strNeedle) or len(strNeedle) > len(strHaystack): # special feature by zadani
        return -1
    
    pos = len(strNeedle) - 1
    while pos <= len(strHaystack) - 1: # pos je pozice mozneho konce podretezce strNeedle v strHaystack
        for i in range(0, len(strNeedle)):
            if strHaystack[pos - i] != strNeedle[-(i+1)]:
                pos += max(badCharTable[strHaystack[pos - i]] - i, goodSuffixTable[i])
                break
        else:
            return pos - (len(strNeedle) - 1) # podretezec nalezen
    return -1 # podretezec nenalezen
