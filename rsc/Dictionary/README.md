# Processing

Original source file was concatened form of files with empty lines inbetween
each of the entries.  The entries have the form 
  <Word> (<TypeOfSpeech>) <Definition>

Not the easiest files to deal with in an automated way.  

### Get rid of all empty lines
:%g/^$/d

### Get rid of all quoted lines.  Not sure why some of them have quotes.
```
:%s/^"\(.*\)"$/\1
```

### Get rid of all 1 letter words.

```
:%g/^. /d  
```

### Get rid of all 2 letter words.
```
:%g/^.. /d
```

### Get rid of all multi-word words.
```
:%g/^[^ ]* [A-Za-z]* (/d 
```

### For some reason some definitions have a ' , ' in them.
:%s/ , /, /g

### Odd misspelling Convict1ible
:%s/Convict1ible/Convictable/

### Remove any word with '-' in it.  

There are a few words in the source which have a random '-' in it - like
Aardvark - which I am removing with this rule but oh well.

```
:%g/^[A-Za-z]*-[A-Za-z]/d 
:%g/^[A-Za-z]*- /d 
```
### Weird pattern with '; -- '

Instead of just using a ';' to connect statements in the definitions there is
sometimes, but not always, a '; -- ' construct.  

```
:%s/; -- /;/g
```

### Transform the parts into tab delimited form

I doubt that I will use the part of speech at all but might as well keep it
for now.

```
%s/^\([^ ]*\) (\([^)]*\)) \(.*\)$/\1^I\2^I\3/ 
```

Afterwards anything that didn't match that should be removed.
```
:%g!/.*^I.*^I.*$/d  
```

### Sort all lines.

After I sorted all lines I saw that there was some stupid characters at the
front that I just manually deleted.

### Remove any line which didn't match our parsing.

/^[^\t]*[^A-Za-z\t][^\t]*  


