from .builtins import std_functions
from pathlib import Path
path = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
all_builtins = {
    "math":Path(path+"/src/cobralang/interpreter/builtins/math.cb"),
    "utils":Path(path+"/src/cobralang/interpreter/builtins/utils.cb"),
}
