# -*- coding: utf-8 -*-

#
#
class HaltStateException(Exception):
    """
    Exception thrown when trying to continue execution from halt state
    """
    pass

#
#
class UnsetTapeException(Exception):
    """
    Exception thrown when the tape is not set
    """
    pass

#
#
class InvalidSymbolException(Exception):
    """
    Exception thrown when a symbol is not valid
    """
    pass

#
#
class UnknownTransitionException(Exception):
    """
    Exception thrown when there are no specified transition with a given
    (state, symbol) tuple
    """
    pass
