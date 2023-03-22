# What is this?
Cobra is a simple (and likely poorly executed) scripting language that I wrote in Python. It's not meant to be used for anything serious, but it's a fun little project that I've been working on for a little over a week.

Cobra is licensed under the [MIT](https://github.com/HavenSelph/cobralang/blob/stable/LICENSE.md) license, learn more about what it permits [here](https://choosealicense.com/licenses/mit/).

# How do I use it?
Cobra can be used in either interactive mode or file mode. In interactive mode, you can type in commands and have them executed, similar to how Python interactive mode works. In file mode, you can run a Cobra script by passing the filepath from your current directory as an argument. 

### Windows
These commands are going to make the assumption you're in this repo's root directory. \
Interactive mode:\
`python ./src/cobralang.py`\
File mode:\
`python ./src/cobralang.py ./examples/hello_world.cobra`\
The runner script also accepts a range of arguments, which can be found by running the following:\
`python ./src/cobralang.py --help`

### Linux
These commands are going to make the assumption you're in this repo's root directory. \
Interactive mode:\
`python3 ./src/cobralang.py`\
File mode:\
`python3 ./src/cobralang.py ./examples/hello_world.cobra`\
The runner script also accepts a range of arguments, which can be found by running the following:\
`python3 ./src/cobralang.py --help`

### Using the included batch file
If you're on Windows, you can use the included batch file in `./bin` to run Cobra. This can make it easier to run Cobra from the command line.

# How to write a script
Using the interactive mode, you can type in commands and have them executed. The interactive mode is a good way to test out Cobra's features.
```commandline
$ python ./src/cobralang.py
CobraLang (v0.1.0) repl mode. Type 'exit()' to exit, 'clear()' to clear the context.
>>> let x = 10
>>> x
10
>>> let y = 20
>>> x + y
30
>>> exit()
```
Once you're ready, you can run a Cobra script by passing the filepath from your current directory as an argument. 
```commandline
$ python ./src/cobralang.py ./examples/hello_world.cobra
Hello, World!
```

# Examples
There are a few examples in the `examples` directory. These are just some simple scripts that demonstrate some of Cobra's features. The following is not an exhaustive list of Cobra's features, but it should give you a good idea of what Cobra can do.
```shell
# Cobra can have comments that look like Python's
let x = 10 # Variables must be declared with the 'let' keyword
let y = x+10 # Variables can be assigned to expressions
let z = Null # Variables can be assigned to the Null value
let a = z or 10 # Variables can be assigned to the result of a logical expression

# Cobra has a variety of data types
let int = 10 # Integer
let flt = 10.0 # Float
let str = "Hello, World!" # String
let bool = True # Boolean
let list = [1, 2, 3] # List
let tup = (1, 2, 3) # Tuple
let dict = {1: "one", 2: "two", 3: "three"} # Dictionary

# Cobra has all simple operators
let x = 10 + 2 - (30*6) / 10 ** 2 // 6
x += 1 # x = x + 1
x -= 1 # x = x - 1

# Cobra has if statements
if x == 5 {
    print("x is 5")
} elif x == 6 {
    print("x is 6")
} else {
    print("x is not 5 or 6")
}

# Cobra has for loops
for i in (1, 2, 3, 4) {
    print(i)
}

# Cobra has while loops
while x < 10 {
    x += 1
}

# Cobra has functions
fn add(a, b) { # Functions are declared with the 'fn' keyword
    a + b # Functions don't need to have a return statement
}

fn add(a, b) {
    return a + b # However, they can.
}

fn add(a, b) { a + b } # Functions can be declared on one line

# Functions can have default arguments, and keyword arguments
fn add(a, b=10, c=20) {
    a + b + c
}

add(10)
add(10, b = 20) # However, keyword arguments must be specified.
add(10, c = 20, b = 30) # But, they can be specified in any order.

# Cobra can even import other scripts
import math # Imports the math module (built-in)

# you can also import specific functions from a module
from math import fn sqrt # Imports the sqrt function from the math module
from math import fn (sqrt, pow) # Imports multiple functions from the math module

# or you can import specific variables from a module
from math import var pi # Imports the pi variable from the math module
from math import var (pi, e) # Imports multiple variables from the math module


#It is worth noting that Cobra will search for imports from the standard library first, and then from the directory you are running the script from.

# Cobra has a few built-in functions
print("Hello, World!") # Prints a string to the console
input() # Gets input from the user
input("Enter a number: ") # Gets input from the user with a prompt

# If you want to learn more about these functions, you can use the help() function
help(print) # Prints the help text for the print function

# To assign text to a function for use with the help command, you can use multi-line strings

fn add(a, b) {
    "*
    Returns the sum of a and b.
    
    a: The first number.
    b: The second number.
    *"
    a + b
}

# Now when you run help(add), you will see the help text you assigned to the function.

# it is also worth noting that you can set variables to multi-line strings
let help_text = "*
multi-line string here
*"
```

# Thanks for checking this project out! :)
There's a lot I learned while doing this, and I'm sure there's a lot I could have done better, but that's okay. If you'd like to know some of the things I learned I'll lay them out here for you so you can avoid making the same mistakes I did.

### Make sure you read about the relationship between a Parser and Interpreter.
When starting this project, I really blurred the line between these two, and it made it extremely difficult down the road to fix bugs. For instance, there is a sneaky bug I found just while writing this readme that makes it impossible to find out why lists end up with Python datatypes in them. I really cannot find the cause of this bug, but I know that if I had done the steps properly, this would probably be trivial! Back to the point, let me explain **MY** understanding of this relationship:
> A parser is a program that takes a stream of tokens produced by a "lexer" or "tokenizer" and produces what's called an Abstract Syntax Tree (AST) This AST is what an interpreter is supposed to parse into a runnable program.

> (Lexer->(stream of tokens)->Parser->(AST)->Interpreter->(Program))

I want to make it clear again, that this is my personal understanding of it. My understanding might not exactly cut it for some people, so here's a link to a [Wiki Article](https://en.wikipedia.org/wiki/Lexical_analysis) that explains it a little better.

The issue with the way I went around this is that I went direct from parser to program. While this probably has benefits in some cases, it is definitely not the way a learner should go. I would recommend that if attempting to write your first language, you keep to this method of doing things. It will make your life a lot easier. 

### Logs are your friend.
I cannot stress this enough, make sure you implement logs into your program. It will save you so much time. One of the biggest problems I ran into was trying to understand how my program behaved while it was running, with the lexer/parser this was trivial as I had logs. However, I never implemented logs for my interpreter, and it made it extremely difficult to debug. Learn from my mistake and **implement logs**.

### Don't let your chosen host language handle anything.
When starting off, I allowed Python to handle a LOT. This was the wrong option, as I became dependent on a bunch of Python features I should have implemented myself. This is something I'm sure is obvious to most people, but I thought I'd mention it anyway, as it might save you a headache down the road.

### Some general links that might help you out
* [Make YOUR OWN Programming Language](https://www.youtube.com/watch?v=Eythq9848Fg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD) *by CodePulse*
* [Lexical Analysis](https://en.wikipedia.org/wiki/Lexical_analysis)
* [Syntax (Programming Languages)](https://en.wikipedia.org/wiki/Syntax_(programming_languages))
