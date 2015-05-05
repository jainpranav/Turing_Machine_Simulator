# -*- coding: utf-8 -*-

from tm import TuringMachine

class TuringMachineBuilder:
    """
    Creates a turing machine step by step by retrieving all the necessary 
    information.
    
    By default (can be specified) sets the halt state to 'HALT and the
    blank symbol to '#'
    """
    
    def __init__(self):
        """
        Initialize a new TuringMachineBuilder with the specified haltstate and
        blank symbol.
        
        haltstate takes as default value 'HALT'
        blnak takes as default value '#' and must be one char length
        """
        self._states = set()
        self._in_alphabet = set()
        self._trans_function = {}
        self._istate = None
        self._fstates = set()
        
        self._blank = None
        self._haltstate = None
        
    #
    #
    def clean(self):
        """
        Clear all the previous stored data
        """
        self._states = set()
        self._in_alphabet = set()
        self._trans_function = {}
        self._istate = None
        self._fstates = set()
        
        self._blank = None
        self._haltstate = None
        
    #
    #    
    def addTransition(self, state, symbol, new_state, new_symbol, movement):
        """
        addTransition(state, symbol, new_state, new_symbol, movement)
                
        Adds the transition:
            From state,symbol To new_state writing new_symbol at the current 
            possition and moving the head in movement direction
             
        - state: something that represents a state, must be hashable
        - symbol: something that represents a symbol, must be hashable
        - new_state: something that represents a state, must be hashable
        - new_symbol: something that represents a symbol, must be hashable
        - movement: TuringMachine.MOVE_LEFT or TuringMachine.MOVE_RIGHT or 
                    TuringMachine.NON_MOVEMENT
                    
        Raise Exception if symbols have more than one char length
        """
        
        if movement not in TuringMachine.HEAD_MOVEMENTS:        
            raise Exception('Invalid movement')
        
        if (hasattr(symbol, 'len') and len(symbol) > 1) or \
            (hasattr(new_symbol, 'len') and len(new_symbol) > 1):
            raise Exception('Symbol length > 1')
        
        if state not in self._states:
            self._states.add(state)
            
        if symbol != self._blank and symbol not in self._in_alphabet:
            self._in_alphabet.add(symbol)
            
        if new_state not in self._states:
            self._states.add(new_state)
            
        if new_symbol != self._blank and new_symbol not in self._in_alphabet:
            self._in_alphabet.add(new_symbol)
            
        self._trans_function[(state,symbol)] = (new_state, new_symbol,
                                                 movement)
    #
    #                                             
    def addFinalState(self, state):
        """
        Adds the specified state to the set of final states
        """
        if state not in self._states:
            self._states.add(state)
        if state not in self._fstates:
            self._fstates.add(state)
           
    #
    #      
    def setInitialState(self, state):
        """
        Set the specified state as the initial. Mandatory operation
        """
        if state not in self._states:
            self._states.add(state)
        self._istate = state
        
     
    #
    #
    def hasInitialState(self):
        """
        Returns True if the initial state was specified on a previous call
        to setInitialState
        """
        return self._istate != None
        
    #
    #
    def hasHaltState(self):
        """
        Returns True if the halt state was specified on a preivous call to
        setHaltState
        """
        return self._haltstate != None
        
    #
    #
    def hasBlankSymbol(self):
        """
        Returns True if the halt state was specified on a preivous call to
        setBlankSymbol
        """
        return self._blank != None
        
        
    #
    #
    def setBlankSymbol(self, blank_sym):
        """
        Specifies a new blank symbol
            - The blank symbol must be one char length
            
        Raise Exception if blank_sym has more than one char length
        """
        if not blank_sym or len(blank_sym) > 1:
            raise Exception('Symbol must be one char length')
            
        self._blank = blank_sym
        
    #
    #
    def setHaltState(self, haltstate):
        """
        Specifies a new halt state
        """
        
        # If there are a previous halt state. Check if it appears in some
        # transition otherwise delete it from the list of states
        if self.hasHaltState():
            old_remains = False
            for k, v in self._trans_function.iteritems():
                if k[0] == self._haltstate or v[0] == self._haltstate:
                    old_remains = True
                    break
                
            if not old_remains:
                self._states.remove(self._haltstate)
                     
        self._haltstate = haltstate
        self._states.add(self._haltstate)                
    
    #
    #
    def create(self):
        """
        Creates a turing machine instance with the collected information.
        
        Raises an Exception if:
            The initial state remains unset
            The halt state remains unset
            The blank symbol remains unset
        
        At this point the tape_alphabet is set to be: in_alphabet U {blank}
        """
        if not self.hasInitialState():
            raise Exception('It is necessary to specify an initial state')
            
        if not self.hasBlankSymbol():
            raise Exception('It is necessary to specify the blank symbol')
            
        if not self.hasHaltState():
            raise Exception('It is necessary to specify the halt state')
        
        
        tape_alphabet = set(self._in_alphabet)
        tape_alphabet.add(self._blank)
        
        return TuringMachine(self._states, self._in_alphabet, tape_alphabet,
                             self._trans_function, self._istate, 
                             self._fstates, self._haltstate, self._blank)
                             
    #
    #
    def getHaltState(self):
        """
        Returns the halt state specified or assigned by default on the 
        initialization of this Builder
        """
        return self._haltstate
            

if __name__ == '__main__':
    tmb = TuringMachineBuilder()
    
    tmb.setBlankSymbol('#')
    tmb.setHaltState('HALT')
    
    tmb.addTransition(1, 0, 2, 1, TuringMachine.MOVE_RIGHT)
    tmb.addTransition(1, 1, 2, 0, TuringMachine.MOVE_RIGHT)
    tmb.addTransition(2, 0, 1, 0, TuringMachine.NON_MOVEMENT)
    tmb.addTransition(2, 1, 3, 1, TuringMachine.MOVE_RIGHT)
    tmb.addTransition(3, 0, 'HALT', 0, TuringMachine.NON_MOVEMENT)
    tmb.addTransition(3, 1, 'HALT', 1, TuringMachine.NON_MOVEMENT)
    tmb.addTransition(3, '#', 'HALT', '#', TuringMachine.NON_MOVEMENT)
    
    tmb.setInitialState(1)
    tmb.addFinalState(2)
    
    print tmb.create()
