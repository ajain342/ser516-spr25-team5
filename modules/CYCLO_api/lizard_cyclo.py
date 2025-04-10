import os
import sys
from pathlib import Path
import lizard



def analyze_cyclo(directory_name):

    directory = Path(directory_name)

    code_list = []

    for file_path in directory.iterdir():
        if file_path.is_file():
            with open(file_path, "r") as file:
                content = file.read()
                code_list.append(content)


    return code_list

def get_cc(code_list):

    temp_file = "tempfile.java"

    try:
        while len(code_list) > 0:
            code = code_list.pop()

            with open(temp_file, "w") as f:
                f.write(code)
            f.close()
            analysis = lizard.analyze_file(temp_file)
            for function in analysis.function_list:
                print(f"Function: {function.name}")
                print(f"Cyclomatic complexity: {function.cyclomatic_complexity}")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)



if __name__ == "__main__":
    list = analyze_cyclo(sys.argv[1])
    get_cc(list)

    


