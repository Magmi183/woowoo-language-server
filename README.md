# WooWoo LSP

TODO description

## Features

Please keep in mind that the LSP is in a very early stage of development.
Even features that are working now (marked as done ✅) will very likely be subjected to major changes in the near future, due to refactoring and algorithmic improvements.

**Legend**:
- ✅ feature is done
- 🚧 feature is in progress or in very early stage (working but needs major improvements)
- 🔲 feature is yet to be done, work not even started


### Hover

1. **Template specific keywords** 🚧
   - hints for `Chapter`, `Section`, `Subsection` etc.

### Code Linting

1. **Invalid syntax detection** 🚧
2. Checking if file used in the `.include` statement exists 🔲
3. More TBD

### Auto-completion

1. **`.include` statement** ✅
   - auto-complete the `.include` statement
   - suggest files to include (all `.woo` files in the current workspace)
2. **Template specific keywords** 🔲
   - `Chapter`, `Section`, `Subsection` etc.
3. **Environment** types 🔲

### (Semantic) Highlighting ✅

Currently, the server is using the _Semantic Tokens_ feature to do **all** highlighting.
That means that no highlighting logic has to be present on the client (like TextMate grammars).
Note that this may change in the future.

All highlighting logic is done using the [Tree-Sitter queries](https://tree-sitter.github.io/tree-sitter/using-parsers#pattern-matching-with-queries).
See `queries/highlights.scm` (WooWoo without metablocks) and `queries/yaml-highlights.scm` (for the yaml meta-blocks).



### Code Folding

1. `Document part` folding 🔲
2. `Object` folding 🔲
3. `Block` folding 🔲
4. `Outer environment` folding 🔲

### Find References

1. Find references of an `Object`, `Document part` or `Outer environment` (or any _labelable_ type) 🔲 
   - based on `label` meta information

### Go to definition

1. Go to file used in the `.include` statement ✅
2. Go to definition of `Object`, `Document part` or `Outer environment` 🔲
   - based on `label` meta information
