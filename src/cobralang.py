from cobralang.interpreter.interpreter import Context
from cobralang.interpreter.nodes import Null
from os.path import isfile, isdir, split, join
from pathlib import Path
import cobralang.parser as parser
import cobralang.lexer as lexer
import logging
from argparse import ArgumentParser
from time import perf_counter
from os import environ


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

argparser.add_argument('filepath', nargs="?", default=None, help="The path to the file to be interpreted.", type=str)
argparser.add_argument('--logging_level', default="NONE", help="The logging level to use. Defaults to NONE (no logs).", choices=log_levels.keys(), type=str)
argparser.add_argument('--logging_path', default=None, help="The path to the log file. Leave unspecified to log to console.", type=str)
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

    try:
        tokens = lexer.Lexer(code, filename=filename, logger=log, logging_level=log.getEffectiveLevel()).tokenize()
        log.info("File opened successfully, attempting to parse...")
        program = parser.Parser(tokens, filename=filename, logger=log, logging_level=log.getEffectiveLevel()).parse()
        log.info("File parsed successfully, attempting to run...")

        output = program.run(Context())

        if output is not None:
            print(output)
    except Exception as e:
        log.exception(e)
        raise e
else:
    def count_token(token_type: lexer.TokenKind, token_list: list[lexer.Token]) -> int:
        return sum([1 for token in token_list if token.kind == token_type])

    from time import sleep
    log.info("Entering repl mode...")
    context = Context()
    print("CobraLang (v0.0.1) repl mode. Type 'exit()' to exit, 'clear()' to clear the context.")
    while True:
        try:
            sleep(0.1)
            code = input(">>> ")
            if code == "":
                continue
            tmp = lexer.Lexer(code).tokenize()
            while (count_token(lexer.TokenKind.LeftParen, tmp) > count_token(lexer.TokenKind.RightParen, tmp))\
                    or (count_token(lexer.TokenKind.LeftBracket, tmp) > count_token(lexer.TokenKind.RightBracket, tmp))\
                    or (count_token(lexer.TokenKind.LeftBrace, tmp) > count_token(lexer.TokenKind.RightBrace, tmp)):
                new = input("... ")
                code += "\n" + new
                if new == "":
                    break
                tmp = lexer.Lexer(code).tokenize()
            tokens = lexer.Lexer(code, filename="<stdin>", logger=log, logging_level=log.getEffectiveLevel()).tokenize()
            program = parser.Parser(tokens, filename="<stdin>", logger=log, logging_level=log.getEffectiveLevel()).parse()
            sleep(0.1)
            log.debug("Running program...")
            start = perf_counter()
            try:
                output = program.run(context)
            except KeyboardInterrupt as e:
                print("KeyboardInterrupt")
                continue
            end = perf_counter()
            if end - start > 0.2:
                print(f"Program ran in {end - start:.2f}s")
            if output is not None and not isinstance(output, Null):
                print(output)
        except Exception as e:
            log.exception(e)
            sleep(0.1)
            print(e)
