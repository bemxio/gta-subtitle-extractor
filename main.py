import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from datetime import timedelta
from typing import Optional
from pathlib import Path

import srt

def main(oxt_path: Path, xml_path: Path, output: Optional[Path] = None):
    # parse the .oxt text table and make a dict with the text bindings
    with open(oxt_path, "r", encoding="utf-8") as file:
        texttable = file.read()

    texttable = texttable.splitlines()
    bindings = {}

    for line in texttable:
        if not line.startswith("\t"):
            continue

        bind = line[1:].split(" = ")
        bindings[bind[0]] = bind[1].replace("~z~", "")

    # parse the .xml metadata file containing the time and duration of the text
    tree = ET.parse(xml_path)
    root = tree.getroot()

    args = root[1] # pCutsceneEventArgsList
    events = root[2] # pCutsceneEventList

    subtitles = []

    for event in events:
        time = float(event[0].get("value"))
        index = int(event[2].get("value"))

        arg = args[index]

        text = bindings.get(arg[0].text)
        duration = float(arg[1].get("value"))

        subtitles.append(srt.Subtitle(
            index=index,
            start=timedelta(seconds=time),
            end=timedelta(seconds=time + duration),
            content=text
        ))

    # write the subtitles to an output file
    output = output or oxt_path.with_suffix(".srt")

    with open(output, "w", encoding="utf-8") as file:
        file.write(srt.compose(subtitles))

if __name__ == "__main__":
    parser = ArgumentParser(description="A script for generating an .srt file out of an .xml & .oxt file, retrieved from GTA V's game files.")
    
    parser.add_argument("oxt_path", type=Path, help="The input path for an '.oxt' file.")
    parser.add_argument("xml_path", type=Path, help="The input path for an '.xml' file.")
    
    parser.add_argument("--output", "-o", type=Path,
        help="The output path for an '.srt' file. Defaults to the path of the '.oxt' file.", 
        default=None
    )

    main(**vars(parser.parse_args()))