# ieml-dictionary

This is the repository for the IEML (information economy metalanguage) dictionary.

The `dictionary` folder contains the ieml dictionary definition, as a collection of yaml files.
The [file structure](https://github.com/IEMLdev/ieml-dictionary/blob/master/dictionary_paradigm_schema.yaml) is expressed in the [kwalify](http://www.kuwata-lab.com/kwalify/) schema syntax.
Each file from the `dictionary` folder defines a root paradigm.
It is composed of:
 - __root paradigm definition__ : a semantic opposition system
 - __semes definitions__ : the different positions in this system
 - __paradigms definitions__ : semantic opposition subsystems
 
 Each root paradigm defines a semantic opposition system, and a set of semes, representing the different positions in the system. 

## Dictionary visualization

The `server.py` run a webserver using [flask](http://flask.pocoo.org/) to display the state of the `dictionary` folder.
next soon
