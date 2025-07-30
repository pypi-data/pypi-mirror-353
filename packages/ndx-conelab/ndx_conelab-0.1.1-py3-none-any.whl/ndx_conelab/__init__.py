import os
from pynwb import load_namespaces, get_class

# Get the path to the spec files
HERE = os.path.dirname(__file__)
SPEC_PATH = os.path.join(HERE, "spec")

# Load the namespace
load_namespaces(os.path.join(SPEC_PATH, "conelab.namespace.yaml"))

# Import the TaskParameters class so it can be directly imported from the package
from .conelab_extension import TaskParameters

__all__ = ["TaskParameters"] 