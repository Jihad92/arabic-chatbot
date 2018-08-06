# Arabic chatbot for cloths store

A simple website featuring a chatbot for hypothetical clothing store.

## Getting Started

### Prerequisites

The core of the bot is built using python 3.5.1 with keras library, so you should have python installed.

### Installing

You should install the libraries written in recs.txt

Warning: If you have h5py library version 2.8.0 or higher, it may not load the weights correctly.

You may first create a virtual environment for the project:

# On Windows 7:
Open a new cmd window and run:

```
cd path/to/project
python -m venv my_env         \\ Create venv
my_env\Scripts\activate.bat   \\ Activate venv
```

Before installing libraries, you should upgrade ```pip``` to the latest version to avoid potential errors:

```
python -m pip install --upgrade pip
```

Then, install required libraries:

```
pip install –r recs.txt
```

To run the website, right-click at ```server.py```  and choose Edit with IDLE, then run the script ```F5```.
Or, you may run it from cmd by running the following command at the same project directory:

```
python server.py
```

# On Ubuntu:

comming soon..


## Built With

* [python]( https://www.python.org/) - interpreted high-level programming language for general-purpose programming.
* [keras]( https://keras.io/) - a high-level neural networks API.

## Contributing

I appreciate any effort to improve the project and would be grateful for any small note that makes the project better and more professional.

## TODO

* Additional commenting needed
* Fix running with cmd
* Use Reactjs for frontend
* Use Django or Symfony for backend
* Enhancing the keras model
