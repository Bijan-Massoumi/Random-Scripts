
import sys

file = open(sys.argv[1])
new_file = open("new_" + sys.argv[1],"w+")

lines = file.readlines()

for i, line in enumerate(lines):
    splitted = line.split()
    if i == 0:
        for k, term in enumerate(splitted):
            if k < len(splitted) - 1:
                splitted[k] = '"' + term + '", '
            else:
                splitted[k] = '"' + term + '"'
    else:
        for k, term in enumerate(splitted):
            if k < len(splitted) - 1:
                splitted[k] = term + ", "



    joined = "".join(splitted)
    new_file.write(joined + "\n")
