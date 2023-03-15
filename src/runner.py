from cobralang.interpreter.interpreter import Context
from os.path import isfile, isdir, split, join
from pathlib import Path
import cobralang.parser as parser
import cobralang.lexer as lexer
import logging
from argparse import ArgumentParser


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

argparser.add_argument('--filepath', help="The path to the file to be interpreted.", type=str, default=None)
argparser.add_argument('--logging_level', default="NONE", help="The logging level to use. Defaults to 51 (no logs).", choices=log_levels.keys(), type=str)
argparser.add_argument('--logging_path', default=None, help="The path to the log file. Defaults to the current directory.", type=str)
args = argparser.parse_args()

log = logging.getLogger("CobraLang")
log.setLevel(log_levels[args.logging_level])

formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
if args.logging_path is None:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
else:
    logging_path = Path(args.logging_path).absolute()
    if not isdir(join(*split(logging_path)[:-1])):
        raise FileNotFoundError(f"Logging path not found: {logging_path}")
    file_handler = logging.FileHandler(logging_path)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

if log.getEffectiveLevel() <= 10:
    log.debug(f"Debug mode enabled. Note that this will not show what the interpreter is doing, only what the parser/lexer is doing.")

log.info("CobraLang runner started successfully")
log.debug(f"{args!r}")

if args.filepath is not None:
    log.info("File specified, attempting to open...")
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
else:
    from time import sleep
    log.info("No file specified, entering repl mode...")
    context = Context()
    while True:
        sleep(0.1)
        code = input(">>> ")
        if code == "exit()":
            break
        elif code == "clear()":
            context = Context()
            continue
        elif code == "":
            continue

        try:
            tokens = lexer.Lexer(code, filename="<stdin>", logger=log, logging_level=log.getEffectiveLevel()).tokenize()
            program = parser.Parser(tokens, filename="<stdin>", logger=log, logging_level=log.getEffectiveLevel()).parse()
            sleep(0.1)
            log.debug("Running program...")
            output = program.run(context)
            log.debug("Program ran successfully")
            print(output)
        except Exception as e:
            log.exception(e)
            print(e)
