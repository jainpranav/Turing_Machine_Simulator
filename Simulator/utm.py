#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import tm
import tmparser
import tmexceptions
import highlighters


from PyQt4 import QtGui
from PyQt4.QtCore import Qt

__prog__='Turing Machine Simulator'


#
#
def main():

    # Initialized the qt application    
    app = QtGui.QApplication(sys.argv)    
    gui = GUI()
    gui.initGUI()
    gui.installHandlers()    
    gui.show()    
    sys.exit(app.exec_())

#
#
class GUI(QtGui.QWidget):
    
    TAPE_SIZE = 31
    TAPE_HEAD = int(round(TAPE_SIZE / 2))
    TAPE_HEAD_LEFT = TAPE_HEAD - 1
    TAPE_HEAD_RIGHT = TAPE_HEAD + 1
    DEF_WIDTH = 800
    DEF_HEIGHT = 600
    HSPACING = 10
    VSPACING = 5
    ICON = 'icon.png'
    
    # Tape style(s)
    TAPE_HEAD_STYLE = 'QLineEdit { border: 2px solid red; background: white;}'
        
    #
    #
    def __init__(self):
        super(GUI, self).__init__()
        # Turing machine and Turing machine parser
        self.parser = tmparser.TuringMachineParser()
        self.turing_machine = None
        
    #
    #
    def initGUI(self):
        
        # Configure window
        self.setMinimumSize(GUI.DEF_WIDTH, GUI.DEF_HEIGHT)   
        self.setWindowTitle(__prog__)
        self.setWindowIcon(QtGui.QIcon(GUI.ICON))
        
        self.main_vbox = QtGui.QVBoxLayout(self)
        
        # Add Tape widgets
        self._initTape()        
        # Add log text box
        self._initLogArea()
        
        # Add controls
        self._initControlArea()
        
        self.resize(GUI.DEF_WIDTH, GUI.DEF_HEIGHT)
        
        
    #
    #
    def installHandlers(self):
        self.set_tm_btn.clicked.connect(self.onSetTuringMachineClicked)
        self.set_tape_btn.clicked.connect(self.onSetTapeClicked)
        self.run_step_btn.clicked.connect(self.onRunStepClicked)
        self.run_all_btn.clicked.connect(self.onRunUntilHaltClicked)  
        self.src_load_btn.clicked.connect(self.onLoadClicked)
        self.src_save_btn.clicked.connect(self.onSaveClicked)
        self.clear_log_btn.clicked.connect(self.onClearLogClicked)
        self.print_all_tape_btn.clicked.connect(self.onPrintAllTape)
        
        
    #
    # QtGui event handlers
    #
    
    #
    #
    def onSetTuringMachineClicked(self):
        
        tmstr = str(self.src_textbox.toPlainText())
        try:
            self.parser.clean()
            self.parser.parseString(tmstr)
            self.turing_machine = self.parser.create()
            self.turing_machine.attachObserver(self)
            
            self._printInfoLog('Turing machine created')
            self._printInfoLog('Current state: ' + 
                                str(self.turing_machine.getCurrentState()))
                                
            #sys.stderr.write(str(self.turing_machine) + '\n')
        except Exception, e:
            self._printErrorLog('Error: %s' % str(e))
            
    #
    #
    def onSetTapeClicked(self):
        tapestr = str(self.tape_textbox.toPlainText())
        if self.turing_machine != None:
            self.turing_machine.setTape(tapestr)
            self.turing_machine.setAtInitialState()
            self._printInfoLog('Tape value established')
        else:
            self._printErrorLog('Error: The Turing machine must be set before'
                                ' set the tape')
            
    #
    #
    def onRunStepClicked(self):
        
        try:
            self.turing_machine.step()
            
        except tmexceptions.HaltStateException, e:
            self._printErrorLog(str(e))
            
        except tmexceptions.UnsetTapeException, e:
            self._printErrorLog(str(e))
            
        except tmexceptions.UnknownTransitionException, e:
            self._printErrorLog(str(e))
            
        except AttributeError:
            self._printErrorLog('Error: Turing machine is unset')
            
    #
    #            
    def onRunUntilHaltClicked(self):
        
        try:
            
            if self.turing_machine.isAtHaltState():
                self._printErrorLog('Error: The Turing Machine is on halt state')
                
            else:
                self._printInfoLog('---------- Run Until Halt ----------')
                
                try:
                    while not self.turing_machine.isAtHaltState():
                        self.turing_machine.step()
                    
                except tmexceptions.UnsetTapeException, e:
                    self._printErrorLog(str(e))
                    
                except tmexceptions.UnknownTransitionException, e:
                    self._printErrorLog(str(e))
                
        except AttributeError:
            self._printErrorLog('Error: Turing machine is unset')
    #
    #
    def onLoadClicked(self):
        
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Load file',
                                                  os.path.expanduser('~'))
                                                  
        if fname:
            f = open(fname, 'r')
            fstr = f.read()
            self.src_textbox.setPlainText(fstr)
            f.close()
            
            self._printInfoLog('Loaded file: %s' % fname)            
    #
    #
    def onSaveClicked(self):
        
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file',
                                                  os.path.expanduser('~'))
                                                  
        if fname:
            f = open(fname, 'w')
            fstr = str(self.src_textbox.toPlainText())
            f.write(fstr)
            f.close()
            
            self._printInfoLog('Saved file: %s' % fname)
            
    #
    #
    def onClearLogClicked(self):
    
        self.log_textbox.clear()
        
    #
    #
    def onPrintAllTape(self):
        if self.turing_machine:
            try:
                tape_value = ' '.join(self.turing_machine.getTapeIterator())
                self._printInfoLog('***************************************')
                self._printInfoLog('Tape Values:')
                self._printStrikingInfoLog(tape_value)
                self._printInfoLog('***************************************')
            except Exception, e:
                self._printErrorLog(str(e))
        else:
            self._printErrorLog('Error: The Turing Machine must be set '
                                'before print the tape')
        
            
    #
    # Turing Machine observer methods
    #

    #
    #
    def onStepStart(self, current_state, current_tape_symbol):
        self._printInfoLog('+++++++++++++++++++++++++++++++++++++++++++++++')
        self._printInfoLog('Started step at state "%s" with tape symbol "%s"'
                            % ( str(current_state), str(current_tape_symbol)))
    #
    #
    def onStepEnd(self, new_state, writed_symbol, movement):
        self._printInfoLog('-----------------------------------------------')
        
        self._printInfoLog('Writed Symbol: ' + str(writed_symbol) )
        
        if movement == tm.TuringMachine.MOVE_LEFT:            
            self._printInfoLog('Head moved to the left')
        elif movement == tm.TuringMachine.MOVE_RIGHT:
            self._printInfoLog('Head moved to the right')            
        else:
            self._printInfoLog('Head remains at the same position')
                   
        self._printInfoLog('Current state: ' + str(new_state) + 
            (' (FINAL)' if self.turing_machine.isAtFinalState() else '') ) 
    
    #
    #
    def onTapeChanged(self, head_pos):
        self._redrawTape(head_pos)
    
    #
    #
    def onHeadMoved(self, head_pos, old_head_pos):
        self._redrawTape(head_pos)

        
    #
    # 'Private'
    #
    
    #
    # Creates and adds the tape widgets
    def _initTape(self):
        self.tape_label = QtGui.QLabel('Tape', self)   
        
        self.tape_hbox = QtGui.QHBoxLayout()
                
#        self.tape_lbutton = QtGui.QPushButton('<', self)
#        self.tape_rbutton = QtGui.QPushButton('>', self)        
        self.tape_textboxes = self._createTape()
        
        
#        self.tape_hbox.addWidget(self.tape_lbutton)
        for txbx in self.tape_textboxes:
            self.tape_hbox.addWidget(txbx)
#        self.tape_hbox.addWidget(self.tape_rbutton)
        
        
        self.main_vbox.addWidget(self.tape_label, 0, Qt.AlignCenter)        
        self.main_vbox.addLayout(self.tape_hbox, 1)
        self.main_vbox.addSpacing(GUI.VSPACING)
        
        
    #
    #
    def _createTape(self):
        tptx = [QtGui.QLineEdit(self) for i in xrange(GUI.TAPE_SIZE)]
        for txbx in tptx:            
            txbx.setReadOnly(True)
            txbx.setFocusPolicy(Qt.NoFocus)
            txbx.setAlignment(Qt.AlignHCenter)
            
        tptx[GUI.TAPE_HEAD].setStyleSheet(GUI.TAPE_HEAD_STYLE)
        return tptx
        
    #
    #
    def _initLogArea(self):
        
        log_vbox = QtGui.QVBoxLayout()
                
        # Add log text box
        log_label = QtGui.QLabel('Activity Log', self)
        self.log_textbox = QtGui.QTextEdit(self)
        self.log_textbox.setReadOnly(True)
        log_vbox.addWidget(log_label, 0, Qt.AlignCenter)
        log_vbox.addWidget(self.log_textbox)
        
        # Add some control buttons
        log_hbox = QtGui.QHBoxLayout() 
        self.clear_log_btn = QtGui.QPushButton('Clear Log', self)
        self.print_all_tape_btn = QtGui.QPushButton('Print All Tape', self)

        log_hbox.addWidget(self.print_all_tape_btn)        
        log_hbox.addWidget(self.clear_log_btn)
        
        log_vbox.addLayout(log_hbox)        
        
        # Add all the previous stuff to the window layout
        self.main_vbox.addLayout(log_vbox, 1)
        self.main_vbox.addSpacing(GUI.VSPACING)
        
    #
    #
    def _initControlArea(self):
        self.ctrl_hbox = QtGui.QHBoxLayout()
        
        # Add source text box and load/save buttons
        ctrl_llabel = QtGui.QLabel("TM Source Code", self)
        self.src_textbox = QtGui.QTextEdit(self)
        highlighters.TMSourceHightlighter(self.src_textbox, "Classic" )
        self.src_load_btn = QtGui.QPushButton('Load', self)
        self.src_save_btn = QtGui.QPushButton('Save', self)
        
        self.ctrl_lvbox = QtGui.QVBoxLayout()
        self.ctrl_lvbox.addWidget(ctrl_llabel, 0, Qt.AlignCenter)
        self.ctrl_lvbox.addWidget(self.src_textbox)
        ctrl_btn_hbox = QtGui.QHBoxLayout()
        ctrl_btn_hbox.addWidget(self.src_load_btn)
        ctrl_btn_hbox.addWidget(self.src_save_btn)
        self.ctrl_lvbox.addLayout(ctrl_btn_hbox)
        
        # Add control buttons
        ctrl_rlabel = QtGui.QLabel("Tape's Initial Value", self)
        self.tape_textbox = QtGui.QPlainTextEdit(self)
        self.set_tm_btn = QtGui.QPushButton('Set TM', self)
        self.set_tape_btn = QtGui.QPushButton('Set Tape', self)
        self.run_step_btn = QtGui.QPushButton('Run Step', self)
        self.run_all_btn = QtGui.QPushButton('Run Until Halt', self)
        
        self.ctrl_rvbox = QtGui.QVBoxLayout()
        self.ctrl_rvbox.addWidget(ctrl_rlabel, 0, Qt.AlignCenter)
        self.ctrl_rvbox.addWidget(self.tape_textbox)
        self.ctrl_rvbox.addWidget(self.set_tm_btn)
        self.ctrl_rvbox.addWidget(self.set_tape_btn)
        self.ctrl_rvbox.addWidget(self.run_step_btn)
        self.ctrl_rvbox.addWidget(self.run_all_btn)
        
        # Add some tooltips
        self.set_tape_btn.setToolTip('Sets the tape values and forces the TM '
                                     'to be at the initial state')
       
        # Add the control area to the main layout
        self.ctrl_hbox.addLayout(self.ctrl_lvbox, 2)
        self.ctrl_hbox.addSpacing(GUI.HSPACING)
        self.ctrl_hbox.addLayout(self.ctrl_rvbox, 1)
        self.main_vbox.addLayout(self.ctrl_hbox, 2)
        
    #
    #
    def _redrawTape(self, head_pos):
        blank = self.turing_machine.getBlankSymbol()        
        
        sym = self.turing_machine.getSymbolAt(head_pos)
        self.tape_textboxes[GUI.TAPE_HEAD].setText('' if sym == blank 
                                                    else str(sym))
        
        for i in xrange(1, GUI.TAPE_HEAD + 1):
            txtbx_index = GUI.TAPE_HEAD - i
            tape_index = head_pos - i
            sym = self.turing_machine.getSymbolAt(tape_index)
            self.tape_textboxes[txtbx_index].setText('' if sym == blank
                                                    else str(sym))
                                
        for inc, i in enumerate(xrange(GUI.TAPE_HEAD + 1, GUI.TAPE_SIZE)):
            tape_index = head_pos + inc + 1
            sym = self.turing_machine.getSymbolAt(tape_index)
            self.tape_textboxes[i].setText('' if sym == blank else str(sym))
                                                  
    #
    #
    def _printErrorLog(self, error):
        """
        Prints a message on the log_textbox
        Text Color: RED
        """
        self.log_textbox.setTextColor(Qt.red)
        self.log_textbox.setFontWeight( QtGui.QFont.Normal )
        self.log_textbox.append(error)
    
    #
    #        
    def _printInfoLog(self, msg):
        """
        Prints a message on the log_textbox
        Text Color: BLACK
        """
        self.log_textbox.setTextColor(Qt.black)
        self.log_textbox.setFontWeight( QtGui.QFont.Normal )
        self.log_textbox.append(msg)
        
    #
    #
    def _printStrikingInfoLog(self, msg):
        """
        Prints a message on the log_textbox makeing it more visible than a
        normal log
        """
        self.log_textbox.setTextColor( Qt.darkBlue )
        self.log_textbox.setFontWeight( QtGui.QFont.Bold )
        self.log_textbox.append(msg)
#
#
if __name__ == '__main__':    
    main()
