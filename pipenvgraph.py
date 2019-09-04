# -*- coding: utf-8 -*-
import re
import os
import subprocess as sp
from link import Link
from node import Node
import argparse
import logging

logger = logging.getLogger()

def parse_dependencies(output):
    """ parse the ligne of the pipenv graph output """

    modulePat = re.compile("(?P<name>[^=]+)==(?P<version>.*)$")
    dependPat = re.compile(
        "^(?P<level> *)(?:- )?(?P<name>[^ ]+) \[required: (?P<required>[^,]+), installed: (?P<version>[^]]+)]$"
    )

    parsed_dependencies = []
    parsed_modules = []
    most_recent_ancestor = {}

    for ligne in output:
        foundModule = modulePat.search(ligne) or dependPat.search(ligne)
        if foundModule:
            foundModule = foundModule.groupdict()

            if foundModule.get("required", False):
                required = foundModule.pop("required")
                level = len(foundModule.pop("level"))
                ancestor = most_recent_ancestor[level - 2]

                # in foundModule we only have name and version
                module = Node(pkgtype="branch", ancestor=ancestor, **foundModule)

                # adding a new dependency and saving it
                dependence = Link(required=required, source=module, target=ancestor)
                if dependence not in parsed_dependencies:
                    parsed_dependencies.append(dependence)

            else:
                # in foundModule we only have name and version
                module = Node(pkgtype="root", **foundModule)
                level = 0

            # update the most recent ancestor at current "level"
            most_recent_ancestor[level] = module

            # keeping track of parsed modules
            if module not in parsed_modules:
                parsed_modules.append(module)
            else:
                # if already parsed we increas it's importance which can be taken in account in the display
                module.importance += 1

    return parsed_dependencies, parsed_modules


def main(output, filename, loglevel='INFO'):
    """parse the local PipFile.lock and generate a dot file for graphviz and then a png file"""

    logging.basicConfig(level=loglevel)
    logger = logging.getLogger()

    
    # run pipenv graph and get the output
    cmd = 'pipenv graph'
    logger.info(f'Runing {cmd}')
    stdout = sp.run(cmd.split(), stdout=sp.PIPE).stdout.split(b"\n")
    stdout = list(map(lambda x: x.decode("utf8"), stdout))

    # parse the output to a graph
    logger.info(f'Parsing the output...')
    parsed_dependencies, parsed_nodes = parse_dependencies(stdout)

    # parse the graph to a temporay dot file
    tmpfile = f"./.{filename}.gv"
    sp.run(f'touch {tmpfile}'.split())

    logger.info(f'Writting the graph in {tmpfile}')
    with open(tmpfile, "w") as f:

        python_name = os.environ.get("VIRTUAL_ENV", "default python install")
        f.write(f'strict digraph "{python_name}"' + " { \n")
        for module in parsed_nodes:
            f.writelines(f"{module}\n")

        for dep in parsed_dependencies:
            f.writelines(f"{dep}\n")

        f.write("}")

    # run the dot program on the temporary file

    dotcmd = f"dot -T{output} {tmpfile} -o {filename}.{output}"
    logger.info(f'Runing dot cmd {dotcmd}')
    stdout = sp.run(dotcmd.split(), stdout=sp.PIPE).stdout
    
    #os.remove(tmpfile)


def get_args():
    description = """Generate a graph as a picture from pipenv graph command"""
    outputFormatDef = "png"
    outputFormatHelp = f"Select any dot accepted out format (eg png, pdf...) (default {outputFormatDef})"

    logLevelDef = "INFO"
    logLevelHelp = f"set the log level (default {logLevelDef})"

    filenameDef = "pipenvgraph"
    filenameHelp = f"the ouptput format base name (default {filenameDef})"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output", "-o", help=outputFormatHelp, default=outputFormatDef)
    parser.add_argument("--filename", "-f", help=filenameHelp, default=filenameDef)
    parser.add_argument("--loglevel", "-l", help=logLevelHelp, default=logLevelDef)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    main(output=args.output, filename=args.filename, loglevel=args.loglevel)
    exit()
