#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import inspect
import tmexceptions


class TuringMachine:
    """
    Represents a turing machine, to work propertly there are some restrictions:
        - symbols on input alphabet and tape alphabet must be one char length
        - transition function must be a dictionary with the following format:
                        (state, symbol) : (state, symbol, movement)
        - tape movements are defined by the following "constants":
            - MOVE_LEFT
            - MOVE_RIGHT
            - NON_MOVEMENT
    """

    MOVE_RIGHT = 1
    MOVE_LEFT = 2
    NON_MOVEMENT = 3
    HEAD_MOVEMENTS = frozenset((MOVE_LEFT, MOVE_RIGHT, NON_MOVEMENT))

    #
    #
    def __init__(self, states, in_alphabet, tape_alphabet, trans_function,
                 istate, fstates, hstate, blank):
        """
        TuringMachine(states, in_alphabet, tape_alphabet, trans_function,
                    istate, fstate, hstate, blank)
        Initialize an instance of TuringMachine with the given data
            - states:
                Iterable with the possible states
            - in_alphabet:
                Iterable with the input alphabet
            - tape_alphabet:
                Iterable with the machine tape alphabet
            - trans_function:
                Dictionary representing the transition function
                    (state, symbol) : (state, symbol, movement)
            - istate: 
                Initial state
            - fstates:
                Iterable with the possible final states
            - hstate:
                Halt state. If reached, execution stops inmediatly
            - blank: 
                Default symbol in all unespecified tape possitions
        """
        self._states = frozenset(states)
        self._in_alphabet = frozenset(in_alphabet)
        self._tape_alphabet = frozenset(tape_alphabet)
        self._trans_function = copy.copy(trans_function)
        self._istate = istate
        self._fstates = frozenset(fstates)
        self._hstate = hstate
        self._blank = blank

        self._checkData()
        
        # Machine tape, head and current state
        self._tape = None
        self._head = 0
        self._cur_state = istate
        self._nexecuted_steps = 0
        
        # Set of observers
        # is a list because other structures like set forces to implement
        # the __hash__ operation
        self._observers = []

    #
    #
    def step(self):
        """
        Performs one execution step.
            
            - If it's at Halt state raises HaltStateException
            - If tape is unset raises UnsetTapeException
            - If there are no specified transition for the current state and
              symbol, raises UnknownTransitionException
        """
        if self.isAtHaltState():
            raise tmexceptions.HaltStateException('Current state is halt state')
        if self._tape == None:
            raise tmexceptions.UnsetTapeException(
                'Tape must be set before perform an step')
                
        cur = (self._cur_state, self._tape[self._head])
        for obs in self._observers:
            obs.onStepStart(cur[0], cur[1])
            
        try:
            state, sym, movement = self._trans_function[cur]
            
            self._tape[self._head] = sym
            self._cur_state = state
            
            prev_head_pos = self._head
            
            if movement == TuringMachine.MOVE_LEFT:
                if self._head == 0:
                    self._tape.insert(0, self._blank)
                else:
                    self._head -= 1                    
                    
            elif movement == TuringMachine.MOVE_RIGHT:
                self._head += 1
                if self._head == len(self._tape):
                    self._tape.append(self._blank)                
        
            # Notify observers
            for obs in self._observers:
                obs.onStepEnd(state, sym, movement)
                
                if prev_head_pos != self._head:
                    obs.onHeadMoved(self._head, prev_head_pos)
                
            self._nexecuted_steps += 1        
        
        except KeyError:
            raise tmexceptions.UnknownTransitionException(
                'There are no transition for %s' % str(cur))

    #
    #
    def run(self, max_steps=None):
        """
        run(max_steps=None): int
        
        Perform steps until 'halt' or 'max steps'        
        
        Return values:
            0 - Ends by halt state
            1 - Ends by max steps limit
            2 - Ends by unknown transition
        """
        try:
            if max_steps:
                try:
    
                    for i in xrange(max_steps):
                        self.step()
                    return  1
                except tmexceptions.HaltStateException:
                    return 0
                    
            else:
                
                while not self.isAtHaltState():
                    self.step()
                return 0
                
        except tmexceptions.UnknownTransitionException:
            return 2

    #
    #
    def getCurrentState(self):
        """
        Returns the current state (Cpt. Obvious)
        """
        return self._cur_state
        
    #
    #
    def getBlankSymbol(self):
        """
        Returns the blank symbol
        """
        return self._blank
        
    #
    #
    def getHaltState(self):
        """
        Returns the halt state
        """
        return self._hstate

    #
    #
    def getInitialState(self):
        """
        Returns the initial state
        """
        return self._istate

    #
    #
    def getSymbolAt(self, pos):
        """
        Returns the symbol at the specified position
        
        The internal symbols goes from 0 to getInternalTapeSize() - 1
        for any other position out of this range the blank symbol is returned
        """
        if pos < 0 or pos >= len(self._tape):
            return self._blank
            
        return self._tape[pos]
        
    #
    #
    def getInternalTapeSize(self):
        """
        Returns the size of the internal tape representation
        """
        return len(self._tape)
            
    
    #
    #
    def getHeadPosition(self):
        """
        Returns the current head position
        """
        return self._head
        
    #
    #
    def getTapeIterator(self):
        """
        Returns an iterator of the internal tape
        """
        if self._tape:
            return iter(self._tape)
        else:
            raise Exception('Tape must be set before try to get its iterator')
        
    #
    #
    def getExecutedStepsCounter(self):
        """
        Return the amount of steps executed until the creation of the machine
        or the last call to resetExecutedStepsCounter()
        """
        return self._nexecuted_steps
        
    #
    #
    def isAtHaltState(self):
        """
        Returns true only if current state is the halt state
        """
        return self._cur_state == self._hstate
        
    #
    #
    def isAtFinalState(self):
        """
        Returns true only if current state is a final state
        """
        return self._cur_state in self._fstates

    #
    #
    def isTapeSet(self):
        """
        Returns true only if tape is set        
        """
        return self._tape != None

    #
    #
    def isWordAccepted(self, word, max_steps=None):
        """
        Return values are:
            True - Ends by halt state or undefined transition at a final state
            False - Ends by halt state or undefined transition at a non final state
            None - Ends by max_steps
        """
        
        old_tape = self._tape
        old_state = self._cur_state
        old_head = self._head
        
        self.setTape(word)
        end_cond = self.run(max_steps)
        self._tape = old_tape
        
        if end_cond == 0 or end_cond == 2:        
            accepted = self.isAtFinalState()
        else:
            accepted = None
        
        self._tape = old_tape
        self._cur_state = old_state
        self._head = old_head
        
        return accepted

    #
    #
    def setTape(self, tape, head_pos=0):
        """
        setTape(tape:[], head_pos:int)
        Set tape and head position
        Head position takes as default value 0
        If head position is negative or greater than tape length the tape is
        filled with blanks
        
        If tape contains an invalid symbol raises an InvalidSymbolException
        
        WARNING: 
            It is recomended that the tape symbols are inmutable types
            Does not reset the executed steps counter
        """
        
        for s in tape:
            if s not in self._tape_alphabet:
                raise tmexceptions.InvalidSymbolException(
                    'Invalid tape symbol %s' % str(s))
        
        # If head pos is out of tape make tape grow with blanks 
        if head_pos < 0:
            self._tape = [self._blank] * (-head_pos)
            self._tape.extend(tape)
            self._head = 0
        elif head_pos >= len(tape):
            self._tape = list(tape)
            if not self._tape: self._tape = [self._blank] # Empty tape
            self._tape.extend( [self._blank] * (head_pos - len(tape)) )
            self._head = head_pos
        else:
            self._tape = list(tape)
            self._head = head_pos
            
        for obs in self._observers:
            obs.onTapeChanged(head_pos)

    #
    #
    def setAtInitialState(self):
        """
        Forces the machine state to be the initial state
        """
        self._cur_state = self._istate

    #
    #
    def attachObserver(self, observer):
        """
        Attach an observer to this Turing Machine
        
        Observers must implement the following methods:
            
            onStepStart(current_state, current_tape_symbol)
                Called at the beggining of a new state, after check if exists
                a transition for the current (state, symbol)
                
                - current_state is the state after perform the transition
                - current_tape_symbol is the symbol at the head position
                
            onStepEnd(new_state, writed_symbol, movement)
                Called when an steps end succesfully
                
                - new_state is the state after perform the transition
                - writed_symbol is the symbol writed to the tape at the previous head position
                - movement is the head move direction after write new_symbol
                
            onTapeChanged(head_pos)
                Called after a succesful call to setTape
                
                - head_pos is the specified position on the call to setTape
                
            onHeadMoved(head_pos, old_head_pos)
                Called when the head position changes
                
                - head_pos is the actual head position (after movement)
                - old_head_pos is the previous head position (before movement)
        """
        # Observer must have the following method
        if not hasattr(observer, 'onStepStart'): 
            raise Exception('Observer must have an onStepStart method')
        if not hasattr(observer, 'onStepEnd'):
            raise Exception('Observer must have an onStepEnd method')
        if not hasattr(observer, 'onTapeChanged'):
            raise Exception('Observer must have an onTapeChanged method')
        if not hasattr(observer, 'onHeadMoved'):
            raise Exception('Observer must have an onHeadMoved method')
        # onStepStart and onStepEnd must accept the following amount of parameters
        if not _getNumArguments(observer.onStepStart) == 2:
            raise Exception('Observer onStepStart method must have 2 parameters')    
        if not _getNumArguments(observer.onStepEnd) == 3:
            raise Exception('Observer onStepEnd method must have 3 parameters')    
        if not _getNumArguments(observer.onTapeChanged) == 1:
            raise Exception('Observer onTapeChanged method must have 1 parameters')    
        if not _getNumArguments(observer.onHeadMoved) == 2:
            raise Exception('Observer onHeadMoved method must have 2 parameters')    
        
        if observer not in self._observers:
            self._observers.append(observer)
        
    #
    #
    def detachObserver(self, observer):
        """
        Remove the specified observer
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
        
    #
    #
    def resetExecutedStepsCounter(self):
        """
        Set the executed steps counter to 0
        """
        self._nexecuted_steps = 0

    #
    #
    def _checkData(self):
        """
        Checks if the given information is correct
            1- Input alphabet is subset of tape alphabet
            2- Blank symbol is into the tape alphabet
            3- Initial state is in states
            4- Final states are all in states            
            5- Transition states are defined in states
            6- Transition symbols are defined in tape alphabet
            7- Transition is composed by elements with the specified format:
                    (state, symbol) : (nstate, nsymbol, movement)
            
        If one of the above fails raises an exception
        """
        movements = frozenset([TuringMachine.MOVE_LEFT, 
                                TuringMachine.MOVE_RIGHT,
                                TuringMachine.NON_MOVEMENT])


        if not self._in_alphabet.issubset(self._tape_alphabet):
            raise Exception('Input alphabet is not subset of tape alphabet')

        if self._blank not in self._tape_alphabet:
            raise Exception('Blank symbol is not into the tape alphabet')

        if self._istate not in self._states:
            raise Exception('Initial state is not a valid state')

        if not self._fstates.issubset(self._states):
            raise Exception('Final states are not a subset of states')

        for k, v in self._trans_function.iteritems():
            if len(k) != 2 or len(v) != 3: 
                raise Exception('Invalid format in transition %s -> %s' %
                                (str(k), str(v)))

            inv_state = None
            if k[0] not in self._states:    inv_state = k[0]
            if v[0] not in self._states:    inv_state = v[0]
            if inv_state:
                raise Exception('Invalid state %s in transition %s -> %s' %
                                (str(inv_state), str(k), str(v)))
                
            inv_sym = None
            if k[1] not in self._tape_alphabet: inv_sym = k[1]
            if v[1] not in self._tape_alphabet: inv_sym = v[1]
            if inv_sym:
                raise Exception('Invalid symbol %s in transition %s -> %s' %
                                (str(inv_sym), str(k), str(v)))

            if v[2] not in movements:
                raise Exception('Invalid movement %s in transition %s -> %s' %
                                (str(v[2]), str(k), str(v)))

    #
    #
    def __str__(self):
        return  'States: %s\n' \
                'Input alphabet: %s\n' \
                'Tape alphabet: %s\n' \
                'Blank symbol: %s\n' \
                'Initial state: %s\n' \
                'Final states: %s\n' \
                'Halt state: %s\n\n' \
                'Transition Function:\n%s' \
                 % (
                    str(self._states), str(self._in_alphabet), 
                    str(self._tape_alphabet), str(self._blank), str(self._istate),
                    str(self._fstates), str(self._hstate), 
                    str(self._trans_function)
                    )

#
#                    
def _getNumArguments(func):
    """
    Return the number of arguments of the specified function
    
    If the functions belongs to an instance of any class the self parameter
    is ignored
    """
    argspec = inspect.getargspec(func)
    args = argspec[0]
    
    if args.index('self') == 0:
        return len(args) - 1
        
    return len(args)
    


# Test class
if __name__ == '__main__':

    print 'Turing Machine class Test'

    hstate = 'HALT'
    states = set([1,2, hstate])
    in_alphabet = set([0,1])
    tape_alphabet = set([0,1,'#'])
    istate = 1
    fstates = set([2])
    blank = '#'
    trans_function = {
                    (1,0): (2, 1, TuringMachine.MOVE_RIGHT),
                    (1,1): (2, 0, TuringMachine.MOVE_RIGHT),
                    (2,0): (1, 0, TuringMachine.NON_MOVEMENT),
                    (2,1): (3, 1, TuringMachine.MOVE_RIGHT),
                    (3,0): (hstate, 0, TuringMachine.NON_MOVEMENT),
                    (3,1): (hstate, 1, TuringMachine.NON_MOVEMENT),
                    (3,blank): (hstate, blank, TuringMachine.NON_MOVEMENT)
                }


    try:
        tm = TuringMachine(states, in_alphabet, tape_alphabet, trans_function,
                        istate, fstates, hstate, blank)
    except Exception as e:
        print 'Error:', e

    print 'Adding state 3 to the machine states'
    states.add(3)

    tm = TuringMachine(states, in_alphabet, tape_alphabet, trans_function,
                        istate, fstates, hstate, blank)

    print 'Turing Machine'
    print tm
    
    print '\nSet Tape'
    tape = [1,0,1,0,0,1,0,3]
    try:
        tm.setTape(tape)
    except tmexceptions.InvalidSymbolException as e:
        print 'Error', e
        
    print 'Removing state 3 from the tape'
    
    tape = [1,0,0,0,0,1]
    tm.setTape(tape)
    for i in tm.getTapeIterator():
        print i,
    print

    print '\nCheck words'
    print 'Is word 1010 accepted?', tm.isWordAccepted([1,0,1,0])
    print 'Is word 1000 accepted?', tm.isWordAccepted([1, 0, 0, 0])
    
    print '\nTape after checks (Should be the old set values)'
    for i in tm.getTapeIterator():
        print i,
    print

    print '\nRunning tm until halt state or undefined transition'
    print 'Run status code:', tm.run()
    print 'Expected tape symbols:', 0, 1, 1, 1, 1, 1, blank
    print ' Tape after execution:',
    for i in tm.getTapeIterator():
        print i,
    print
