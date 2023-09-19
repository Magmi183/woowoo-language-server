# tree-sitter-woowoo

WooWoo grammar for [tree-sitter](https://github.com/tree-sitter/tree-sitter).


## Usage

To use `tree-sitter-woowoo`, you'll need to have Tree-sitter installed on your machine. You can follow the official Tree-sitter documentation to [install Tree-sitter](https://tree-sitter.github.io/tree-sitter/).

Once you have Tree-sitter installed, clone the repository and use Tree-sitter to generate the parser:

```commandline
git clone <repository>
cd tree-sitter-woowoo
tree-sitter generate
```


After generating the parser, you can use it as follows:

```commandline
tree-sitter parse <your-file.woowoo>
```


## Corpus

The `corpus` directory contains examples of different parts of WooWoo.

### Test
The corpus also serves for testing - the entire corpus can be tested by running

```commandline
tree-sitter test
```

This command verifies that the parser correctly parses each of the samples.

## Highlighting

TODO: Guide to highlighting + explain what it does.

`tree-sitter highlight --html ../woowoo_files/textbook-dml/chap-04-dukazy-indukce.woo > output.html`

https://tree-sitter.github.io/tree-sitter/syntax-highlighting

## Compiling

If you want to compile the code to a shared object, do:

```
g++ -o parser.so -shared src/parser.c src/scanner.cc -I./src
```

## Debugging

On Mac using `lldb`:

```
lldb -- tree-sitter
(lldb) run parse ...
(lldb) bt
```