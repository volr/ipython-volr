from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)

import subprocess
from subprocess import PIPE

@magics_class
class VolrMagic(Magics):

    @cell_magic('volr')
    def execute(self, line, cell):
        content = cell
        json, errors = self.process_script(content)
        if errors:
            return json + "\nProcess timed out: " + errors

        process = subprocess.Popen(line.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            result, errors = process.communicate(input = json)
        except subprocess.TimeoutExpired:
            result, errors = process.communicate()

        if errors:
            return str(result) + "\n" + str(errors)

        return result

    def process_script(self, content):
        process = subprocess.Popen(["volr"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            result, errors = process.communicate(input = content.encode())
        except subprocess.TimeoutExpired:
            result, errors = process.communicate()

        return result, errors

def load_ipython_extension(ipython):
    """Load the extension into IPython"""
    ipython.register_magics(VolrMagic)
