from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)

import re
import subprocess
import json
import numpy as np
from matplotlib import pyplot as plt
from subprocess import PIPE

class ParseException(Exception):
    pass

class ExecutionException(Exception):
    pass

@magics_class
class VolrMagic(Magics):

    json_pattern = "\\n({.*})\\n"
    variable_pattern = "(\$\w*)"

    @cell_magic('volr')
    def execute(self, line, cell):
        arguments = self.parse_command(line)
        command = arguments[0]
        variable = arguments[1]

        script = self.replace_user_variables(cell, self.shell.user_ns)

        try:
            spikes, myelin_json = self.process_volr(script, command)
            self.shell.user_ns.update({variable: spikes})
        except Exception as e:
            print("Error sending code to backend")
            raise e

        print("Spikes stored in variable `{}`".format(variable))

        try:
            runtime = int(json.loads(myelin_json)["simulation_time"])
            self.show_spikes(spikes, runtime)
        except Exception as e:
            print("Failed to plot spikes ")
            raise e

        return None

    def send_to_backend(self, myelin_json, command):
        process = subprocess.Popen(command.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        result, errors = process.communicate(input = myelin_json)

        # Ignore errors, unless they contain some form of 'error'
        if re.search('error', errors.decode(), re.IGNORECASE):
            raise ExecutionException(str(result) + "\n" + str(errors))

        return result

    def show_spikes(self, population_spikes, end_range):
        figure, plots = plt.subplots(len(population_spikes), sharex=True)
        figure.set_size_inches(16, 8 * (len(population_spikes)))
        # Rearrange plots to become an array, regardless of the number of plots
        if not isinstance(plots, np.ndarray):
            plots = np.array([plots])
        # Plot the spikes of each population
        for plot_index, label in enumerate(population_spikes):
            neuron_spikes = population_spikes[label]
            neurons = len(neuron_spikes)
            try:
                hist2d = np.array([np.histogram(neuron_spikes[i], bins=end_range, range=(0, end_range))[0] for i in range(0, neurons)])
                plots[plot_index].imshow(hist2d, plt.get_cmap('gray'))
                plots[plot_index].set_title(label)
            except:
                # This fails when there're no spikes
                return

    def parse_command(self, line):
        if "<" in line:
            return line.split("<")
        else:
            return [line, "spikes"]

    def parse_volr(self, content):
        process = subprocess.Popen(["volr"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            result, errors = process.communicate(input = content.encode())
        except subprocess.TimeoutExpired:
            result, errors = process.communicate()

        if errors:
            raise ParseException(content + "\nProcess timed out: " + errors.decode())

        return result

    def process_volr(self, volr, command):
        myelin_json = self.parse_volr(volr)
        result = self.send_to_backend(myelin_json, command)

        try:
            json_string = re.search(self.json_pattern, result.decode("utf8"), re.MULTILINE).group(1)
            data = json.loads(json_string)
            for index in data:
                data[index] = np.array(data[index])
            return (data, myelin_json)
        except Exception as e:
            raise ExecutionException(e, result)

    def python_content_to_string(self, content):
        if isinstance(content, np.ndarray):
            return str(content.tolist())
        else:
            return str(content)

    def replace_user_variables(self, script, namespace):
        for variable in re.findall(self.variable_pattern, script):
            name = variable[1:]
            replacement = self.python_content_to_string(namespace[name])
            script = script.replace(variable, replacement)
        return script

def load_ipython_extension(ipython):
    """Load the extension into IPython"""
    ipython.register_magics(VolrMagic)
