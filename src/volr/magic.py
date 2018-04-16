from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)

import re
import subprocess
import json
from subprocess import PIPE

@magics_class
class VolrMagic(Magics):

    json_pattern = "({.*})"

    @cell_magic('volr')
    def execute(self, line, cell):
        content = cell
        myelin_json, errors = self.process_script(content)
        if errors:
            return myelin_json + "\nProcess timed out: " + errors

        process = subprocess.Popen(line.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            result, errors = process.communicate(input = myelin_json)
        except subprocess.TimeoutExpired:
            result, errors = process.communicate()

        if errors:
            return str(result) + "\n" + str(errors)

        json_string = re.search(self.json_pattern, result.decode()).group(1)

        return json.loads(json_string)

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
