#!/usr/bin/env python

POKUSU = 10000
TEXT_LENGTH = 120
PATTERN_LENGTH = 8

import random
import buildin


def generateText(length):
    return "".join((chr(random.randint(ord("a"),ord("z"))) for counter in range(length)))


zeros = 0
nonzeros = 0

for i in range(POKUSU):
    text = generateText(TEXT_LENGTH)
    pattern = generateText(PATTERN_LENGTH)
    # vlozime pattern na nahodne misto do textu => match vzdy
    insertionPos = random.randint(0, TEXT_LENGTH - 1)
    text = text[:insertionPos] + pattern + text[insertionPos:]

    posA = text.find(pattern)
    posB = buildin.find(text, pattern)
    if posA != posB:
        print("error for %s in %s" % (pattern, text))
        print("boyer-moore: %d; actual: %d" % (posB, posA))
        break
    if posB == -1: zeros += 1
    else: nonzeros += 1
else:
    print("OK (%.4f %% non-zeros)" % (100.0 * nonzeros/POKUSU))
    print("%d matches out of %d" % (nonzeros, POKUSU))

