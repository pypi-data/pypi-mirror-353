import sys

__version__ = "0.1.2"

def main(argv=sys.argv):
    import os, subprocess
    argv = [os.path.join(os.path.dirname(__file__), "asimov-jinja-runner"), *argv[1:]]
    subprocess.call(argv)
