# -*- coding: utf-8 -*-

from tm import TuringMachine
from tmbuilder import TuringMachineBuilder

import re
import sys
import logging

class TuringMachineParser:
    """
    Proportionate methods to parse a Turing Machine.
    
    The allowed expresions are:
        
        - empty line
        - comment line: '% any text that comes after it's ignored'
        - initial state: 'INITIAL <state>'        
        - blank symbol: 'BLANK <symbol>'
        - final state: 'FINAL <state>'        
        - halt state: 'HALT <state>'
        - transition: '<state>, <symbol> -> <new_state>, <new_symbol>, <movement>
        
    It is not possible to add comments at the end of any line, comments must
    be on a standalone line
    """
    
    MOVE_RIGHT = '>'
    MOVE_LEFT = '<'
    NON_MOVEMENT = '_'    
    
    #
    #
    def __init__(self):
        self._builder = TuringMachineBuilder()        
                
        # Regular expresions
        self._comment_line_re = re.compile('[ ]*%\s*') 
        self._blank_symbol_re = re.compile('[\s]*BLANK[\s]+(?P<symbol>.)\s*$')
        self._halt_state_re = re.compile('[ ]*HALT[ ]+(?P<state>\w+)\s*$')
        self._final_state_re = re.compile('[ ]*FINAL[ ]+(?P<state>\w+)\s*$')
        self._inital_state_re = re.compile('[ ]*INITIAL[ ]+(?P<state>\w)\s*$'
        )
        self._transition_re = re.compile('\s*(?P<state>\w+)\s*,\s*'
                                         '(?P<symbol>.)\s*->\s*'
                                         '(?P<nstate>\w+)\s*,\s*'
                                         '(?P<nsymbol>.)\s*,\s*'
                                         '(?P<movement>[%s%s%s])\s*$' %
                                         (TuringMachineParser.MOVE_LEFT,
                                          TuringMachineParser.MOVE_RIGHT,
                                          TuringMachineParser.NON_MOVEMENT)
                                        )
                                        
                                         
    #
    #
    def clean(self):
        """
        Cleans all the previos parsed data
        """
        self._builder.clean()
         
    #
    #
    def parseString(self, string_data):
        """
        Parses the given string an add the information to the Turing Machine
        builder
        
        Raise an exception if the given data is not an string
        """
        if type(string_data) != str:
            raise Exception('Expected an string')
        
        self._parse(string_data.splitlines())
        
        
    #
    #
    def parseLine(self, data):
        """
        Parse the given line of data
        """
        # The most expected expresions are in order:
        # - Transition
        # - Comments
        # - Final States
        # - Initial State, Halt State, Blank Symbol
        
        if not self._parseTransition(data):
            if not self._parseComment(data):
                if not self._parseFinalState(data):
                    if not self._parseInitialState(data):
                        if not self._parseBlankSymbol(data):
                            if not self._parseHaltState(data):                                                
                                raise Exception('Unrecognized pattern: %s' 
                                                % data)
                                                
    #
    #
    def create(self):
        """
        Attempts to create a Turing Machine with the parsed data until the
        call to this function
        
        Can raise any of the TuringMachineBuilder an TuringMachine exceptions
        """
        return self._builder.create()
                                                
    #
    #
    def _parseComment(self, data):
        """
        Returns True if the given data is a comment expresion, otherwise
        returns False
        """
        mc = self._comment_line_re.match(data)
        if mc:
            return True
        return False

    #
    #
    def _parseBlankSymbol(self, data):
        """
        Returns True if the given data is a blank symbol expresion, otherwise
        returns False
        """
        mbs = self._blank_symbol_re.match(data)
        if mbs:   
            if self._builder.hasBlankSymbol():
                raise Exception('Blank symbol can only be defined once')                            
            
            self._builder.setBlankSymbol( mbs.group('symbol') )
            return True
            
        return False
        
    #
    #
    def _parseHaltState(self, data):
        """
        Returns True if the given data is a halt state expresion, otherwise
        returns False
        
        Throws
            Exception if Halt is already defined or if the builder fails when setting the halt state
        """
        mhs = self._halt_state_re.match(data)                    
        if mhs:
            if self._builder.hasHaltState():
                raise Exception('Halt state can only be defined once')
            
            self._builder.setHaltState( mhs.group('state') )
            return True
            
        return False
        
    #
    #
    def _parseFinalState(self, data):
        """
        Returns True if the given data is a final state expresion, otherwise
        returns False
        """
        mfs = self._final_state_re.match(data)                    
        if mfs:            
            self._builder.addFinalState( mfs.group('state') )
            return True
            
        return False
        
    #
    #
    def _parseInitialState(self, data):
        """
        Returns True if the given data is an initial state expresion, otherwise
        returns False
        """
        mis = self._inital_state_re.match(data)                    
        if mis:
            if self._builder.hasInitialState():
                raise Exception('Initial state can only be defined once')
                
            self._builder.setInitialState( mis.group('state') )
            return True
            
        return False
        
    #
    #
    def _parseTransition(self, data):
        """
        Returns True if the given data is a transition state expresion,
        otherwise returns False
        """
        mt = self._transition_re.match(data)                    
        if mt:            
            # Filter movement
            move_sym = mt.group('movement')
            move = TuringMachine.NON_MOVEMENT
            if move_sym == TuringMachineParser.MOVE_LEFT:
                move = TuringMachine.MOVE_LEFT
            elif move_sym == TuringMachineParser.MOVE_RIGHT:
                move = TuringMachine.MOVE_RIGHT
            
            self._builder.addTransition(mt.group('state'),
                                        mt.group('symbol'),
                                        mt.group('nstate'),
                                        mt.group('nsymbol'),
                                        move)            
            return True
            
        return False
                                
    #
    #
    def _parse(self, parse_data):
        """
        Parses the specified data
        
            - parse_data: must be an iterable that returns a new line of data on each iteration
        """
        
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        
        for line, data in enumerate(parse_data):
            # The execution flow it's ugly
            # But personally I hate the idea of have a lot of indentation levels
            
            if not data:
                continue
            try:
                self.parseLine(data)
            except Exception as e:
                raise Exception('Line %d, %s' % (line+1, e.message))
    
#
# Test                    
if __name__ == '__main__':
    
    parser = TuringMachineParser()
    test_str = '% Start with a comment line\n' \
               '  % Another comment line\n' \
               'HALT HALT\n' \
               'BLANK #\n' \
               'INITIAL 1\n' \
               'FINAL 2\n' \
               '1, 0 -> 2, 1, >\n' \
               '1, 1 -> 2, 0, > \n' \
               '2, 0 -> 1, 0, _\n' \
               ' 2,1->3,1,>\n '\
               '3, 0 -> HALT, 0, _\n' \
               '3, 1 -> HALT, 1, _\n' \
               '3, # -> HALT, #, _\n'
    parser.parseString(test_str)
    
    tm = parser.create()
    
    print tm
