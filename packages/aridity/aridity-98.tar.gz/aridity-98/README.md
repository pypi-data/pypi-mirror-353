# aridity
DRY config and template system, easily extensible with Python.

This README is auto-generated, see [project wiki](https://wikiwheel.net/s/foyono/w/aridity) for details.

## Commands

### arid-config
Print given config (with optional path in config) as shell snippet.

### aridity
Interactive REPL.

### processtemplate
Process the given template to stdout using config from stdin.

## API

<a id="aridity.config"></a>

### aridity.config

<a id="aridity.config.ConfigCtrl"></a>

#### ConfigCtrl Objects

```python
class ConfigCtrl(Forkable)
```

High level scope API.

<a id="aridity.config.ConfigCtrl.r"></a>

###### r

```python
@property
def r()
```

Get config object for reading, i.e. missing scopes will error.

<a id="aridity.config.ConfigCtrl.w"></a>

###### w

```python
@property
def w()
```

Get config object for writing, i.e. missing scopes will be created.

<a id="aridity.config.ConfigCtrl.loadappconfig"></a>

###### loadappconfig

```python
def loadappconfig(mainfunction,
                  moduleresource,
                  encoding='ascii',
                  settingsoptional=False)
```

Using app name as prefix load config from the given resource, apply user settings, and return config object for app. Context module for loading resource and the app name are deduced from `mainfunction`, or these can be provided as a tuple. Set `settingsoptional` to suppress the usual error if ~/.settings.arid does not exist.

<a id="aridity.config.ConfigCtrl.load"></a>

###### load

```python
def load(pathorstream)
```

Execute config from the given path or stream.

<a id="aridity.config.ConfigCtrl.execute"></a>

###### execute

```python
def execute(text)
```

Execute given config text.

<a id="aridity.config.ConfigCtrl.__iter__"></a>

###### \_\_iter\_\_

```python
def __iter__()
```

Yield keys and values.

<a id="aridity.config.ConfigCtrl.processtemplate"></a>

###### processtemplate

```python
def processtemplate(frompathorstream, topathorstream)
```

Evaluate expression from path/stream and write result to path/stream.

<a id="aridity.config.RConfig"></a>

#### RConfig Objects

```python
class RConfig(Parabject)
```

<a id="aridity.config.RConfig.__iter__"></a>

###### \_\_iter\_\_

```python
def __iter__()
```

Yield values only. Iterate over `-self` for keys and values.

<a id="aridity.directives"></a>

### aridity.directives

<a id="aridity.directives.colon"></a>

###### colon

```python
def colon(prefix, suffix, scope)
```

Ignore rest of logical line.

<a id="aridity.directives.source"></a>

###### source

```python
@prime
def source(prefix, suffix, scope)
```

Include path or resource at prefix.

<a id="aridity.directives.sourceifexists"></a>

###### sourceifexists

```python
@prime
def sourceifexists(prefix, suffix, scope)
```

Like `.` but allow the resource to be absent.

<a id="aridity.directives.equals"></a>

###### equals

```python
@prime
def equals(prefix, suffix, scope)
```

Assign expression to path.

<a id="aridity.directives.colonequals"></a>

###### colonequals

```python
@prime
def colonequals(prefix, suffix, scope)
```

Evaluate expression and assign result to path.

<a id="aridity.directives.plusequals"></a>

###### plusequals

```python
@prime
def plusequals(prefix, suffix, scope)
```

Assign expression to prefix plus an opaque key, i.e. add to list.

<a id="aridity.directives.commaequals"></a>

###### commaequals

```python
@prime
def commaequals(prefix, suffix, scope)
```

Split expression on whitespace and make a list out of the parts.

<a id="aridity.functions"></a>

### aridity.functions

<a id="aridity.functions.screenstr"></a>

###### screenstr

```python
def screenstr(scope, resolvable)
```

GNU Screen string literal.

<a id="aridity.functions.scstr"></a>

###### scstr

```python
def scstr(scope, resolvable)
```

SuperCollider string literal.

<a id="aridity.functions.hclstr"></a>

###### hclstr

```python
def hclstr(scope, resolvable)
```

HashiCorp configuration language string literal.

<a id="aridity.functions.groovystr"></a>

###### groovystr

```python
def groovystr(scope, resolvable)
```

Groovy string literal.

<a id="aridity.functions.pystr"></a>

###### pystr

```python
def pystr(scope, resolvable)
```

Python literal.

<a id="aridity.functions.shstr"></a>

###### shstr

```python
def shstr(scope, resolvable)
```

Shell string literal.

<a id="aridity.functions.jsonquote"></a>

###### jsonquote

```python
def jsonquote(scope, resolvable)
```

JSON literal, also suitable for YAML.

<a id="aridity.functions.xmlattr"></a>

###### xmlattr

```python
def xmlattr(scope, resolvable)
```

XML attribute literal (including quotes).

<a id="aridity.functions.xmltext"></a>

###### xmltext

```python
def xmltext(scope, resolvable)
```

XML content, suggest assigning this to & with xmlattr assigned to " as is convention.

<a id="aridity.functions.tomlquote"></a>

###### tomlquote

```python
def tomlquote(scope, resolvable)
```

TOML string literal.

<a id="aridity.functions.urlquote"></a>

###### urlquote

```python
def urlquote(scope, resolvable)
```

Percent-encode all reserved characters.

<a id="aridity.functions.map_"></a>

###### map\_

```python
def map_(scope, objsresolvable, *args)
```

If given 1 arg, evaluate it against every scope in `objsresolvable` and return that list.
If given 2 args, the first is a variable name to which each scope is temporarily assigned.
If given 3 args, the first two are variable names for scope key and scope respectively.

<a id="aridity.functions.join"></a>

###### join

```python
def join(scope, partsresolvable, sepresolvable=None)
```

Concatenate the given list, using optional separator. Frequently used with `map`.

<a id="aridity.functions.str_"></a>

###### str\_

```python
def str_(scope, resolvable)
```

Coerce to string.

<a id="aridity.functions.list_"></a>

###### list\_

```python
def list_(scope, *resolvables)
```

Create a list.

<a id="aridity.functions.try_"></a>

###### try\_

```python
def try_(scope, *resolvables)
```

Attempt to evaluate each resolvable, returning the first that succeeds.

<a id="aridity.functions.hereslash"></a>

###### hereslash

```python
def hereslash(scope, *resolvables)
```

Join the given path components with the directory of the current resource.

<a id="aridity.functions.readfile"></a>

###### readfile

```python
def readfile(scope, resolvable)
```

Include the content of the given path.

<a id="aridity.functions.processtemplate"></a>

###### processtemplate

```python
def processtemplate(scope, resolvable)
```

Evaluate the content of the given path as an expression.

<a id="aridity.functions.pyref"></a>

###### pyref

```python
def pyref(scope, moduleresolvable, qualnameresolvable)
```

Python object in given module with given qualified name. Module may be relative to current resource, in which case assignment with `:=` is normally necessary. Typically used to import functions.

<a id="aridity.functions.pyres"></a>

###### pyres

```python
def pyres(scope, packageresolvable, nameresolvable, encoding=Text('ascii'))
```

Python resource for inclusion with `.` directive.

<a id="aridity.grammar"></a>

### aridity.grammar

<a id="aridity.keyring"></a>

### aridity.keyring

<a id="aridity.keyring.gpg"></a>

###### gpg

```python
def gpg(scope, resolvable)
```

Use gpg to decrypt the given base64-encoded blob.

<a id="aridity.model"></a>

### aridity.model

<a id="aridity.model.Resolvable"></a>

#### Resolvable Objects

```python
class Resolvable(Struct)
```

<a id="aridity.model.Resolvable.resolve"></a>

###### resolve

```python
def resolve(scope)
```

Evaluate this expression against the given scope.

<a id="aridity.model.wrap"></a>

###### wrap

```python
def wrap(value)
```

Attempt to wrap the given value in a model object of the most specific type.

<a id="aridity.scope"></a>

### aridity.scope

<a id="aridity.scope.Scope"></a>

#### Scope Objects

```python
class Scope(Resolvable)
```

<a id="aridity.scope.Scope.resolved"></a>

###### resolved

```python
def resolved(*path)
```

Follow the given path to get an expression, evaluate it (resolving any paths it requires, recursively), and return the resulting model object.

<a id="aridity.scope.Slash"></a>

#### Slash Objects

```python
class Slash(Text, Function)
```

As text, the platform slash. As function, join args using that slash, starting with the last absolute path (or using all args if all relative).

<a id="aridity.util"></a>

### aridity.util

