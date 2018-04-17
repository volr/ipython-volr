from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)

import re
import subprocess
import json
import numpy as np
from subprocess import PIPE

class ParseException(Exception):
    pass

class ExecutionException(Exception):
    pass

@magics_class
class VolrMagic(Magics):

    json_pattern = "(\[\[.*\]\])"

    @cell_magic('volr')
    def execute(self, line, cell):
        return self.process_volr(cell, line)

    @cell_magic('volr-debug')
    def execute(self, line, cell):
        return self.process_volr(cell, line, debug = True)

    def process_volr(self, volr, command, debug = False):
        myelin_json = self.parse_volr(volr)
        result = self.send_to_backend(myelin_json, command)

        if (debug):
            print(result)

        json_string = re.search(self.json_pattern, result.decode()).group(1)
        return np.array(json.loads(json_string))

    def send_to_backend(self, myelin_json, command):
        process = subprocess.Popen(command.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            result, errors = process.communicate(input = myelin_json)
        except subprocess.TimeoutExpired:
            result, errors = process.communicate()

        if errors:
            raise ExecutionException(str(result) + "\n" + str(errors))

        return result

    def parse_volr(self, content):
        process = subprocess.Popen(["volr"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            result, errors = process.communicate(input = content.encode())
        except subprocess.TimeoutExpired:
            result, errors = process.communicate()

        if errors:
            raise ParseException(content + "\nProcess timed out: " + errors.decode())

        return result


def load_ipython_extension(ipython):
    """Load the extension into IPython"""
    ipython.register_magics(VolrMagic)
