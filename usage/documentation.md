# Documentation

The documentation is generated using the [sphinx] tool, plus some extensions to allow use of:

* [Markdown] rather than [reStructuredText]
* [Google-style] python docstrings
* Python [type hints]

I've used python 3.6 to develop the code but it's known to work with python 3.8.

[sphinx]: https://www.sphinx-doc.org
[markdown]: https://python-markdown.github.io
[reStructuredText]: https://docutils.sourceforge.io/rst.html
[Google-style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[type hints]: https://docs.python.org/3.6/library/typing.html

## Installation

The easiest way to see how to install the tools locally is to look at the [broadbandforum/sphinx] DockerHub repository's [Dockerfile]. You can then perform the same steps on your development system.

Alternatively, you can run the tools in the above Docker image (see the next section).

Here's the current Dockerfile with some comments. My initial attempt to upstream my various fixes and extensions didn't go very well. I'll try again later.

```
# Dockerfile for sphinx
ARG FROM=ubuntu:latest
FROM $FROM

# install OS packages and create directories
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get --yes install \
        git \
        make \
        pandoc \
        python3 \
        python3-pip \
 && apt-get clean \
 && mkdir -p \
          /opt \
          /opt/sphinx
```

This is a modified version of the standard python markdown parser. The modification is to relax the "fenced code" language pattern so that the sphinx-markdown-parser (below) will work properly.

```
# install markdown parser
RUN git -C /opt/sphinx \
        clone https://github.com/BroadbandForum/markdown.git \
 && git -C /opt/sphinx/markdown \
        checkout feature/relax-fenced-code-lang-pattern \
 && pip3 install --upgrade /opt/sphinx/markdown
```

This is sphinx itself, with a minor bug fix.

```
# install sphinx and extensions
# XXX sphinx-markdown-parser doesn't pull in the core markdown support
RUN git -C /opt/sphinx \
        clone https://github.com/BroadbandForum/sphinx.git \
 && git -C /opt/sphinx/sphinx \
        checkout feature/fix-tab-width-bug \
 && pip3 install --upgrade /opt/sphinx/sphinx
```

This is a sphinx extension for using python type hints. I had to fix a bug.

```
RUN git -C /opt/sphinx \
        clone https://github.com/BroadbandForum/sphinx-autodoc-typehints.git \
 && git -C /opt/sphinx/sphinx-autodoc-typehints \
        checkout feature/investigate-crash \
 && pip3 install --upgrade /opt/sphinx/sphinx-autodoc-typehints
```

This is a sphinx extension for pulling documentation from usages of the python `argparse` (argument parser) module. I had to fix a problem.

```
RUN git -C /opt/sphinx \
        clone https://github.com/BroadbandForum/sphinx-argparse \
 && git -C /opt/sphinx/sphinx-argparse \
        checkout feature/ensure-unique-ids \
 && pip3 install --upgrade /opt/sphinx/sphinx-argparse
```

And finally, this is a sphinx extension that supports using markdown rather than reStructuredText. I made various improvements.

```
RUN git -C /opt/sphinx \
        clone https://github.com/BroadbandForum/sphinx-markdown-parser.git \
 && git -C /opt/sphinx/sphinx-markdown-parser \
        checkout feature/misc-improvements \
 && pip3 install --upgrade /opt/sphinx/sphinx-markdown-parser
```

[broadbandforum/sphinx]: https://hub.docker.com/repository/docker/broadbandforum/sphinx
[Dockerfile]: https://code.broadband-forum.org/projects/SOFTWARE/repos/tools/browse/sphinx/Dockerfile

## Invocation

### Locally

The top-level `makefile` supports the various [sphinx-build] targets, and the default `html` target will generate HTML documentation in the `docs/html` directory. There's also a `clean` target.

[sphinx-build]: https://www.sphinx-doc.org/en/master/man/sphinx-build.html

Here's an example. In this only one file has been modified (this one).

```
% make
Running Sphinx v3.1.0+
loading pickled environment... done
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 1 source files that are out of date
updating environment: 0 added, 1 changed, 0 removed
reading sources... [100%] usage/documentation                                                                                                                                  
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [100%] usage/documentation                                                                                                                                   
generating indices...  genindex py-modindexdone
writing additional pages...  searchdone
copying static files... ... done
copying extra files... done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.

The HTML pages are in docs/html.
```

### In docker

You can use the [broadbandforum/sphinx] DockerHub image. For example:

```
% docker container run -it --name sphinx --rm \
    -v $MYROOT:$MYROOT -w $PWD -e PYTHONPATH broadbandforum/sphinx make
```

This assumes that you've:

* Set the `MYROOT` environment variable to point to a location in your local filesystem that should be mounted in the Docker image (the `-v` option handles this; the `-w` option sets the working directory)
* Defined the `PYTHONPATH` variable appropriately (the `-e` option passes it to Docker)

Here's a clean build in Docker:

```
% docker container run -it --name sphinx --rm -v $MYROOT:$MYROOT -w $PWD -e PYTHONPATH broadbandforum/sphinx make clean html
Removing everything under 'docs'...
Running Sphinx v3.1.0+
making output directory... done
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 6 source files that are out of date
updating environment: [new config] 6 added, 0 changed, 0 removed
annotation typing.IO[str] module 'typing' class_name <property object at 0x7f3a3b766220> <class 'property'>                                                                    
annotation typing.IO[str] module 'typing' class_name <property object at 0x7f3a3b766220> <class 'property'>
annotation typing.IO[str] module 'typing' class_name <property object at 0x7f3a3b766220> <class 'property'>
reading sources... [100%] usage/introduction                                                                                                                                   
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [100%] usage/introduction                                                                                                                                    
generating indices...  genindex py-modindexdone
writing additional pages...  searchdone
copying static files... ... done
copying extra files... done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.

The HTML pages are in docs/html.
```

The three `annotation` warnings are because Docker is using python 3.8, which exposes some debug output from a temporary crash-avoidance fix that I had to add.

## Adding documentation

New documentation will either be hand-written markdown (like this file) or else will be code documentation.

### Overview

To add new files to the documentation, edit the top-level `index.md`. Stick to the current conventions, even if they might look a bit strange. This section specifies the "toctree" (documentation content):

```
* [](usage/introduction)
* [](usage/extensions)
* [](bin/index)
* [](obbaa_onusim/index)
* [](usage/documentation)
```

In order to add this file, I added the last line (the files in the `usage` directory are hand-written markdown).

The third and fourth lines bring in the code documentation. For example, `bin/index.md` is shown below. It's basically markdown, but is interspersed with reStructuredText directives courtesy of [AutoStructify], e.g., `automodule:: bin.onusim` inserts the automatically-generated documentation for the `bin.onusim` python modiule.


``````
# Scripts

## ONU simulation server

``` automodule:: bin.onusim
```

**Usage**

``` argparse::
    :ref: bin.onusim.argparser
    :prog: onusim
    :nodescription:
    :nodefault:
```

## ONU test client

``` automodule:: bin.onucli
```

**Usage**

``` argparse::
    :ref: bin.onucli.argparser
    :prog: onucli
    :nodescription:
    :nodefault:
```
``````

[AutoStructify]: https://recommonmark.readthedocs.io/en/latest/auto_structify.html

### Python docstrings

The basic rule is to use [Google-style] docstrings, but to understand that you can also use some magic reStructuredText directives. You'll see examples of all this in the existing code. Here are some examples.

A section name followed by a colon will be formatted specially (I don't even know whether they have to be known names or whether it's the colon that's special).

```
Examples:

    These examples assume that an ONU simulator instance is listening on the
    default address and port. If not, commands will time out after 10 seconds.

```

A section name followed by two colons will cause its body to be formatted verbatim:

```
    Get (using all defaults)::

        % ./onucli.py get
```

Single back-quotes are cross-references. You can reference module names, class names etc., and it usually "just works". If a reference isn't found, you'll get a sphinx warning. See the [sphinx roles] documentation for details.

```
This will currently only really work on the server side, but it makes sense
also to have a client-side database, populated via `get <get_action>` and
`MIB upload <mib_upload_action>` actions.
```

Two back-quotes indicate a fixed-width font.

```
    The returned attribute mask is ``0xf600``, indicating that the
    response includes ONU-G attributes 1-4, 6 and 7
```

[sphinx roles]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-any
