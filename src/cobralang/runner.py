from interpreter.interpreter import Context
from os.path import isfile, split
from pathlib import Path
import parser
import lexer
from argparse import ArgumentParser
import logging


log_levels = {
    'NONE': 51,
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
}

argparser = ArgumentParser(
    prog="CobraLang Interpreter",
    description="A simple interpreter for the CobraLang programming language.",
)

argparser.add_argument('filepath', help="The path to the file to be interpreted.", type=str)
argparser.add_argument('--logging_level', default='', help="The logging level to use. Defaults to 51 (no logs).", choices=log_levels.keys(), type=str)

args = argparser.parse_args()
print(args)

log = logging.getLogger("CobraLang")
log.setLevel(log_levels[args.logging_level])

formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

if log_levels[args.logging_level] <= 10:
    log.debug(f"Debug mode enabled. Note that this will not show what the interpreter is doing, only what the parser/lexer is doing.")

log.info("CobraLang Interpreter started successfully, attempting to open file...")
log.debug(f"{args!r}")

filepath = Path(args.filepath).absolute()

if not isfile(filepath):
    log.error(f"File not found: {filepath}")
    raise FileNotFoundError(f"File not found: {filepath}")

with open(filepath, 'r') as file:
    code = file.read()

filename = f"<{split(filepath)[1]}>"

tokens = lexer.Lexer(code, filename=filename, logger=log, logging_level=log.getEffectiveLevel()).tokenize()

log.info("File opened successfully, attempting to parse...")

program = parser.Parser(tokens, filename=filename, logger=log, logging_level=log.getEffectiveLevel()).parse()

log.info("File parsed successfully, attempting to run...")

output = program.run(Context())
print(output)

log.info("File run successfully, exiting...")
