"""
This module handles the functionality for saving and loading simulation states from defaults and user_states
"""
import backend as b_end
import pprint
import defaults
import os

# Check if user_states,py exists, If it doesn't, create the file
try:
    import user_states
except ImportError:
    with open("user_states.py", "w") as fp:
        pass
    import user_states

def save_state(state):
    pass

def load_state(state):
    pass
