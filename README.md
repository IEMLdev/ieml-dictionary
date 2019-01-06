# ieml-dictionary

## Overview

This is the repository for the IEML (information economy metalanguage) library.

This repository is composed of:
 - __the dictionary definition__ : all the files that defines the basic semantic units of the IEML language. 
    These files are located in the `definition/dictionary` folder.
 - __the python library__ : the python `ieml` module that contains the algorithm to parse and use the IEML language.
    It is located in the `ieml` folder.
 - __the dictionary visualisation__: the dictionary can be easily visualised by browsing the `docs` folder. 
  The current dictionary state can be accessed at the url [https://iemldev.github.io/ieml-dictionary/](https://iemldev.github.io/ieml-dictionary/).


## The dictionary definition

All the dictionary files in the `definition/dictionary` folder are written in yaml and must conform to a syntax.
The syntax is described in the file at `definition/dictionary/dictionary_paradigm_schema.yaml` and is expressed in the 
[kwalify](http://www.kuwata-lab.com/kwalify/) schema syntax.

Each file from the `dictionary` folder defines a root paradigm.
A dictionary file is composed of multiple entries types :
 - __RootParadigm__ : the main opposition system, it implicitly defines a set of semes.
 - __Semes__ : the different positions in this RootParadigm system.
 - __Paradigms__ : additional semantic opposition systems between these semes.

Each of these entries are composed of the following fields:
 - __ieml__ : the IEML script of this entry
 - __translations__ : a french and an english translation

From these information, the function of the library are able to compute the structure of the dictionary.


### Editing the dictionary

#### Installation

To edit the dictionary, you must have the following program installed :
 - __python__ : `sudo apt install python`
 - __make__ : `sudo apt install make`
 - __git__ : `sudo apt install make`

First clone this repository and create a virtual env, this has to be done only the first time :
```bash
git clone https://github.com/IEMLdev/ieml-dictionary
cd ieml-dictionary
sudo pip install virtualenv # install virtualenv command
virtualenv -ppython3.6 venv # create a virtualenv, that install python3.6 in the folder venv
source venv/bin/activate # use that newly installed python
pip install -r requirements.txt # install the project dependencies
```

Then to check if everything went well, run 
```bash
make validate
```

#### Making changes

You can use this repository to edit the dictionary. 
Then you have to edit the files in the `definition/dictionary` folder by using a text editor.
To visualise the dictionary with your change, run:
```bash
make site-debug
``` 
This `Makefile` target will create a folder named `docs-debug` in the root folder with a dictionary website.
To navigate this website, go the following address in your browser (http://localhost:8000/)[http://localhost:8000/].

#### Publishing the changes

To normalize the dictionary files, run
```bash
make normalize
```
This `Makefile` target normalize the spaces and the orders of the fields to prevent future issues with git. 


You can check the validity of the dictionary files by typing in the root folder:
```bash
make validate
```
This `Makefile` target check the syntax correctness, the dictionary structure correctness and the file normalisation 
correctness for git.

To publish the files to github :
```bash
git add definition/dictionary
git commit -m "Your modification description message"
git push
```
The files have to be validated before being pushed.


#### Adding a root paradigm

To add a new root paradigm, you have to create a new file in the `dictionary/definition` folder.

By convention, the file name must be of the format `{paradigm layer}_{paradigm name in english}.yaml`
 
Then, add the following text:
```yaml
RootParadigm:
    ieml: "..."
    translations:
        fr: >
            ...
        en: >
            ...
    inhibitions: []
```
Fill the `ieml`, `fr` and `en` field, with the IEML of the desired root paradigm, and its french and english translation.
Writing all the IEML of the semes by hand can be tedious, so there is a program to do it : save and close the file and run the following command to automatically generate the semes of this paradigm :
```bash
make expand_semes
```
After that, you can fill the `fr` and `en` field of the semes.
