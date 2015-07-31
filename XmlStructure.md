# Basic Server Definition, server.xml #

The file `server.xml` describes the basic structure of the server and provides for modification to various options.

## Example ##

```
<server>
  <option name="bind_port" value="4000" />
  <option name="default_start" value="ravren:beginning" />

  <area name="ravren" file="areas/ravren.xml" />

  <handlers file="handlers-map.xml" />
</server>
```

## Features ##

Use `<option />` elements to override options otherwise set to defaults at run-time.  The full dictionary object of available options (and defaults) is contained in `options` within `common.py`.  The only two available arguments are `name` and `value`.

`<area />` elements allow the importing of area description files.  As is the case with all file references in `server.xml`, the file path is specified relative to the current file.

Similarly, `<handlers />` elements allow importing one or more mapping files for handler modules contained within the source tree.

# Handlers Mapping Files #



## Example ##

```
<handlers>

  <special type="apostrophe" rewrite="say" />
  <special type="comma" rewrite="emote" />

  <handler command="east" function="go" />
  <handler command="emote" function="emote" />
  <handler command="enter" function="go" />
  <handler command="exit" function="quit" />
  
  <handler command="go" function="go" />

  <handler command="look" function="look" />
  <handler command="laugh" function="emote" />
  <handler command="leave" function="go" />
  <handler command="logoff" function="quit" />

  <handler command="north" function="go" />
  <handler command="ne" function="go" />
  <handler command="northeast" function="go" />
  <handler command="northwest" function="go" />
  <handler command="nw" function="go" />

  <handler command="quit" function="quit" />

  <handler command="south" function="go" />
  <handler command="say" function="say" />
  <handler command="save" function="save" />
  <handler command="se" function="go" />
  <handler command="shutdown" function="quit" />
  <handler command="slap" function="emote" />
  <handler command="southeast" function="go" />
  <handler command="southwest" function="go" />
  <handler command="sw" function="go" />

  <handler command="west" function="go" />
  <handler command="wave" function="emote" />
  <handler command="wink" function="emote" />

</handlers>
```

## Features ##

Handler mapping files provide a convenient means of matching user-inputted commands with functions.  When a mapping file is parsed by sigma-mud, the original order is noted by the program.  Therefore, if a partial command ("s" for example) is typed, the first-ordered entry that begins with the typed command is selected for execution.

The provision for multiple handler mapping files was made in anticipation of a potential desire to separate commands by starting letter or starting letter range.

Functions specified within handler mappings are mapped to modules at run-time through the module importing process.