import os
from pathlib import Path

import lizard
import uuid
import configparser






def hello_world():
    return "Hello from the Cyclomatic Complexity Service!"

def get_cc(code):
    myuuid = uuid.uuid4()

    threshold = 0

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cc_config.cfg")


    config = configparser.ConfigParser()


    if(os.path.exists(config_path)):
        config.read(config_path)
        print("Path read successfully")

        threshold = int(config['cc']['cc-threshold'])

    temp_file = str(myuuid) +".java"
    result = []

    result.append({"threshold": threshold})

    try:
        with open(temp_file, "w") as f:
            f.write(code)
        f.close()
        analysis = lizard.analyze_file(temp_file)
        sum = 0
        num = 0
        maxCyclo = float('-inf')
        for function in analysis.function_list:

            if(function.cyclomatic_complexity > threshold):
                sum += function.cyclomatic_complexity
                num += 1
                maxCyclo = max(maxCyclo, function.cyclomatic_complexity)
                result.append({
                    "Function name" : function.name,
                    "Cyclomatic complexity" : function.cyclomatic_complexity
                })

        avg = sum/num
        result.append({"average cyclomatic complexity" : avg})
        result.append({"total cyclomatic complexity" : sum})
        result.append({"functions evaluated" : num})
        result.append({"max cyclomatic complexity" : maxCyclo})




    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return result
