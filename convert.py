#!/usr/bin/python

import argparse
import os
import ast
import json
import shutil
from jinja2 import Template

def generateDecoderWrapper(decoder, type, outputDir, sourcefile):
    name = ""
    for attr in ast.walk(decoder):
        if isinstance(attr, ast.Assign) and isinstance(attr.targets[0], ast.Name) and isinstance(attr.value, ast.Str):
            if attr.targets[0].id == "name":
                name = attr.value.s

    if (not name == "") :
        name = name.replace("/", "_")
        name = name.replace("²", "2") # wah fancy I2C naming...
        print("generating " + name)
        decoderDir = os.path.join(outputDir, name)
        if (not os.path.isdir(decoderDir)) :
            os.mkdir(decoderDir)

        # generate extension.json
        entryPointName = name.replace(" ", "_")
        if (entryPointName[0].isnumeric()) :
            entryPointName = "_" + entryPointName
        jsonData = {
          "version": "0.0.1",
          "apiVersion": "1.0.0",
          "author": "sigrok2logic converter",
          "name": name,
          "extensions": {
            name: {
              "type": "HighLevelAnalyzer",
              "entryPoint": "Hla."+entryPointName
            }
          }
        }
        with open(os.path.join(decoderDir, "extension.json"), 'w') as outfile:
            json.dump(jsonData, outfile, indent=4)

        # copy over the sigrok analyzer and other python files not __init__.py
        shutil.copyfile(sourcefile, os.path.join(decoderDir, os.path.basename(sourcefile)))
        sigrokDir = os.path.dirname(sourcefile)
        for r, d, f in os.walk(sigrokDir):
            for file in f:
                if (".py" in file):
                    shutil.copyfile(os.path.join(sigrokDir, file), os.path.join(decoderDir, file))


        # generate the wrapper python class
        with open('hla_template.j2') as file_:
            data = file_.read()
            template = Template(data)

        with open(os.path.join(decoderDir, "Hla.py"), 'w') as hlapy:
            hlapy.write(template.render(
                entryName=entryPointName,
                decodeBody="self.sigrokDecoder.process" + type.upper() + "(data)"
            ))


def main(input, output):
    logicSupportedDecoders = ['uart', 'spi', 'i2c']
    input = os.path.join(input, "decoders")
    for dir in os.listdir(input) :
        subdir = os.path.join(input, dir)
        if (os.path.isdir(subdir)) :
            decoderpy = os.path.join(subdir, "pd.py")
            if (os.path.isfile(decoderpy)) :
                classList = []
                className = None
                methodName = None
                fileObject = open(decoderpy, "r")
                text = fileObject.read()
                p = ast.parse(text)
                decoder = ast.NodeVisitor()
                for decoder in ast.walk(p):
                    if isinstance(decoder, ast.ClassDef) and decoder.name == "Decoder":
                        for attr in ast.walk(decoder):
                            if isinstance(attr, ast.Assign)  and attr.targets[0].id == "inputs":
                                if (attr.value.elts[0].s in logicSupportedDecoders) :
                                    generateDecoderWrapper(decoder, attr.value.elts[0].s, output, decoderpy)
                                break
                        break



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--libsigrokdecode", help="Path to the libsigrokdecode folder")
    parser.add_argument("--output", help="path where the Logic2 analyzers will be generated")
    args = parser.parse_args()
    main(args.libsigrokdecode, args.output)
