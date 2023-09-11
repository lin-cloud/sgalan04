import json
import time
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
from skfuzzy import control as ctrl


def readjsonfis(file):
    path = "config/fis/{0}".format(file)
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def fis2fcl(fis, filename):
    filename = './config/fcl/' + filename + '.fcl'
    varnames_input = fis['fis']['input']['name']
    varnames_ouput = fis['fis']['output']['name']
    numvar_input = len(fis['fis']['input']['name'])
    numvar_output = 1
    nombre = fis['fis']['name']

    fout = open(filename, 'w')
    # WRITE BLOCK DEFINITION FCL
    fout.write('FUNCTION_BLOCK %s\n\n' % nombre)
    #
    # Define input variables
    fout.write('VAR_INPUT                // Define input variables\n')
    for i in range(numvar_input):
        fout.write('    %s : REAL;\n' % varnames_input[i])
    fout.write('END_VAR\n\n')
    #
    # Define output variables
    fout.write('VAR_OUTPUT              // Define output variables\n')
    fout.write('    %s : REAL;\n' % varnames_ouput)
    fout.write('END_VAR\n\n')
    #
    # Fuzzifie input variables
    for i in range(numvar_input):
        fout.write('FUZZIFY %s\n' % varnames_input[i])
        mf_input = fis['fis']['input']['mf'][i]['name']
        nummf_input = len(mf_input)
        mfparams_input = fis['fis']['input']['mf'][i]['params']
        for j in range(nummf_input):
            fout.write('    TERM %s := ' % mf_input[j])
            fout.write('(%s,0) (%s,1) (%s,0) ;\n' % tuple(mfparams_input[j]))
        fout.write('END_FUZZIFY\n\n')
    #
    # Defuzzifie output variables
    mf_output = fis['fis']['output']['mf']['name']
    nummf_output = len(mf_output)
    mfparams_output = fis['fis']['output']['mf']['params']
    fout.write('DEFUZZIFY %s\n' % varnames_ouput)
    for j in range(nummf_output):
        fout.write('    TERM %s := ' % mf_output[j])
        fout.write('(%s,0) (%s,1) (%s,0) ;\n' % tuple(mfparams_output[j]))
    fout.write('    METHOD : COG;       // Use Center Of Gravity defuzzification method\n')
    fout.write('    DEFAULT := 0;       // Default value is 0 (if no rule activates defuzzifier\n')
    fout.write('END_DEFUZZIFY\n\n')
    #
    # Write Rule Block
    fout.write('RULEBLOCK RuleBlock1\n')
    fout.write('    AND : MIN;       // Use min for and\n')
    fout.write('    ACT : MIN;       // Use min activation method\n')
    fout.write('    ACCU : MAX;      // Use max accumulation method\n')
    fout.write('END_RULEBLOCK\n\n')
    #
    # End Function Block
    fout.write('END_FUNCTION_BLOCK\n')
    fout.close()
    return 1


def rules2json(fis, rules, filename):
    tam = len(rules)
    varnames_input = fis['fis']['input']['name']
    varnames_ouput = fis['fis']['output']['name']

    res = {"rules": [{}]}
    jsonrules = []
    for i in range(tam):
        r = rules[i]
        jsonrule = {varnames_input[0]: str(r[0]),
                    varnames_input[1]: str(r[1]),
                    varnames_input[2]: str(r[2]),
                    varnames_input[3]: str(r[3]),
                    varnames_input[4]: str(r[4]),
                    varnames_ouput: str(r[5]),
                    'connection': str(r[7])
                    }
        jsonrules.append(jsonrule)
    res['rules'] = jsonrules

    fout = open(filename, 'w')
    fout.write("%s" % json.dumps(res))
    fout.close()
    return res


def rulessave(rules, filename):
    fout = open(filename, 'w')
    fout.write("%s" % json.dumps(rules))
    fout.close()


def readfis(fis):
    system = readjsonfis(fis)
    switcher = {
        'zmf': fuzz.zmf,
        'gaussmf': fuzz.gaussmf,
        'smf': fuzz.smf,
        'trimf': fuzz.trimf,
        'trapmf': fuzz.trapmf
    }

    # Defuzzificacion methods
    # 'centroid', 'bisector', 'mom' (mean of maximum),
    # 'som' (smallest of maximum), 'lom' (largest of maximum)
    defuzz_method = input_names = system['fis']['defuzzMethod']

    # input variables
    input_names = system['fis']['input']['name']
    input_ranges = system['fis']['input']['range']
    input_mf = system['fis']['input']['mf']
    step = 0.001
    num_vars_input = np.size(input_names)
    input_variables = [None] * num_vars_input
    matrix = [None] * num_vars_input
    for i in range(0, num_vars_input):
        input_variables[i] = ctrl.Antecedent(np.arange(input_ranges[i][0], input_ranges[i][1], step), input_names[i])
        input_mf_names = input_mf[i]['name']
        input_mf_types = input_mf[i]['type']
        input_mf_params = input_mf[i]['params']
        num_mfs_input = len(input_mf_names)
        matrix[i] = input_mf_names
        for j in range(0, num_mfs_input):
            func = switcher.get(input_mf_types[j])
            if input_mf_types[j] == 'trimf' or input_mf_types[j] == 'trapmf':
                input_variables[i][input_mf_names[j]] = func(input_variables[i].universe, input_mf_params[j])
            else:
                input_variables[i][input_mf_names[j]] = func(input_variables[i].universe, input_mf_params[j][0],
                                                             input_mf_params[j][1])

    # output variables
    output_names = system['fis']['output']['name']
    output_ranges = system['fis']['output']['range']
    output_mf = system['fis']['output']['mf']
    step = 0.001
    output_variables = ctrl.Consequent(np.arange(output_ranges[0], output_ranges[1], step),
                                       output_names, defuzzify_method=defuzz_method)
    output_mf_names = output_mf['name']
    output_mf_types = output_mf['type']
    output_mf_params = output_mf['params']
    num_mfs_output = len(output_mf_names)
    for j in range(0, num_mfs_output):
        func = switcher.get(output_mf_types[j])
        if output_mf_types[j] == 'trimf':
            output_variables[output_mf_names[j]] = func(output_variables.universe, output_mf_params[j])
        else:
            output_variables[output_mf_names[j]] = func(output_variables.universe, output_mf_params[j][0],
                                                        output_mf_params[j][1])

    # Rules
    system_rules = system['fis']['rule']
    num_rules = np.size(system_rules, 0)
    num_antecedents = np.size(system_rules, 1) - 3
    num_consequentes = 1
    conector_index = np.size(system_rules, 1) - 1

    rules = [None] * num_rules
    for i in range(0, num_rules):
        terms = ''
        conn = system_rules[i][conector_index]
        output = system_rules[i][num_antecedents]
        negated = ''
        if output < 0:
            output = -output
            negated = '~'
        consequent = "{1}output_variables['{0}']".format(output_mf_names[output - 1], negated)
        if conn == 2:
            conector = '|'
        else:
            conector = '&'
        for j in range(0, num_antecedents):
            value = system_rules[i][j]
            negated = ''
            if value < 0:
                value = -value
                negated = '~'
            if value != 0:
                s = "{3}input_variables[{0}]['{1}'] {2} ".format(j, matrix[j][value - 1], conector, negated)
                terms = terms + s
        terms = terms[:-2]
        # print("{0} --> {1}".format(terms, consequent))
        rules[i] = ctrl.Rule(eval(terms), eval(consequent))

    # print("-------------------------------------------")

    tipping_ctrl = ctrl.ControlSystem(rules)
    tipping = ctrl.ControlSystemSimulation(tipping_ctrl)

    return tipping, input_names, output_names, input_variables, output_variables


def evalfis(inputs, fis):
    tipping = fis[0]
    input_names = fis[1]
    output_names = fis[2]
    tam = np.size(inputs, 0)
    for i in range(0, tam):
        tipping.input[input_names[i]] = inputs[i]

    # Crunch the numbers
    tipping.compute()

    return tipping.output[output_names]


"""
Plot membership functions for input or output variable

Syntax:  
            plotfm(fis,type,variable_id)
Description:
            fis: fuzzy controller
            type: 'input'|'output'
            variable_id: 1, 2, etc..
Example: 
            fis.plotmf(FIS, 'input', 1)
            plt.show()
"""


def plotmf(fis, tipo, index=1):
    if tipo == 'input':
        fis[3][index - 1].view()
    else:
        fis[4].view()

