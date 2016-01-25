#!/usr/bin/env python3

class CoffeeCommand(object):
    """
    Command list of coffee machine
    """

    # Coffee machine built-in commands
    AN01 = b'AN:01'
    AN02 = b'AN:02'
    AN03 = b'AN:03'
    AN05 = b'AN:05'
    AN06 = b'AN:06'
    AN0A = b'AN:0A'
    AN0C = b'AN:0C'
    AN0D = b'AN:0D'
    FA01 = b'FA:01'
    FA02 = b'FA:02'
    FA03 = b'FA:03'
    FA04 = b'FA:04'
    FA05 = b'FA:05'
    FA06 = b'FA:06'
    FA07 = b'FA:07'
    FA08 = b'FA:08'
    FA09 = b'FA:09'
    FA0B = b'FA:0B'
    FN01 = b'FN:01'
    FN02 = b'FN:02'
    FN03 = b'FN:03'
    FN04 = b'FN:04'
    FN05 = b'FN:05'
    FN06 = b'FN:06'
    FN07 = b'FN:07'
    FN08 = b'FN:08'
    FN09 = b'FN:09'
    FN0A = b'FN:0A'
    FN0B = b'FN:0B'
    FN0C = b'FN:0C'
    FN0D = b'FN:0D'
    FN0E = b'FN:0E'
    FN0F = b'FN:0F'
    FN11 = b'FN:11'
    FN12 = b'FN:12'
    FN13 = b'FN:13'
    FN14 = b'FN:14'
    FN15 = b'FN:15'
    FN16 = b'FN:16'
    FN17 = b'FN:17'
    FN1D = b'FN:1D'
    FN1E = b'FN:1E'
    FN22 = b'FN:22'
    FN24 = b'FN:24'
    FN25 = b'FN:25'
    FN26 = b'FN:26'
    FN27 = b'FN:27'
    FN28 = b'FN:28'
    FN29 = b'FN:29'

    RE = b'RE:'
    RT = b'RT:'
    TY = b'TY:'
    WE = b'WE:'
    RE31 = b'RE:31'
    WE31 = b'WE:31'
    IC = b'IC:'
    RR = b'RR'

    # Protocol defined commands
    # Alias
    TURN_ON = AN01
    TURN_OFF = AN02
    PRODUCT = [FA04, FA05, FA06, FA07]
    FLUSHING = FA0B

    # New defined
    # Requesting program list
    REQ_LIST = b'ND:01'
