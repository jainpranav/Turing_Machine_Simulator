# :floppy_disk: Turing Machine Simulator

![alt tag](http://i.imgur.com/xPOtWac.jpg)

![alt tag](http://i.imgur.com/jYJuFzI.jpg)



##About this Project 

This project simulates a basic Turing Machine


##Features :

 - Written in Python
 - Code is highly `Modularized`
 - Abstraction Maintained
 - Readability due to `inline comments`
 - Works like a charm :smiley:
 

## How to Use ?

- Download the [Pre-Release Version] (https://github.com/jainpranav/Turing_Machine_Simulator/releases/tag/v1.0)
 

## How to Use The Code From source ?
```bash
$ cd Simulator
$ python utm.py
```


## Language Specification 

- Comments: Lines beginning with '%' are ignored

- It is mandatory to specify a HALT state and an INITIAL state 

- `HALT <state>`
- `INITIAL <state>`
Where <state> is any text without spaces. It is not possible to specify more than one HALT/INITIAL state.

- A state can be marked as a final state with the syntax: `FINAL <state>`

- To go from one state to an other it is necessary to specify the proper transitions

- Transitions are specified as :

`<from_state>, <symbol_on_tape> -> <to_state>, <symbol_to_write>, <head_movement>`

<from_state> and <to_state> can be any text without spaces
<symbol_on_tape> and <symbol_to_write> can be any one character
<head_movement> must be one of the following characters :

- '<' -- Move to the left  
- '>' -- Move to the right 
- '_' -- No movement

## Contributing

#### Bug Reports & Feature Requests

Please use the [issue tracker](https://github.com/jainpranav/Turing_Machine_Simulator/issues) to report any bugs or file feature requests


