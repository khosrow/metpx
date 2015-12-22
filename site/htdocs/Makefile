.SUFFIXES: .1.rst .5 .7 .dia .png .pdf .html

VERSION = $(shell grep __version__ ../../sarracenia/sarra/__init__.py | sed -e 's/"//g' | cut -c14-)
DATE = $(shell date "+%B %Y")

SOURCES = $(wildcard ../../sarracenia/doc/*.rst)
TARGETS = $(patsubst ../../sarracenia/doc/%.rst,%.html,$(SOURCES))

default: $(TARGETS) 

all: css $(TARGETS) 

#.dia.png:
#    dia -t png $*.dia

#.rst.html:
#    rst2html $*.rst >$*.html

# Build all the html pages from the rst file
# Also applies special modifications to make the site template work 
%.html: ../../sarracenia/doc/%.rst    
	rst2html --link-stylesheet --stylesheet=./dist/css/bootstrap.min.css,./dist/css/justified-nav.css --template=../template-en.txt $< $@ 
	sed -i 's/&\#64;Date&\#64;/$(DATE)/' $@
	sed -i 's/&\#64;Version&\#64;/$(VERSION)/' $@
	python template.py $@

css:
	cp -ap ../dist .  

#deploy:
#	rsync -avP -e ssh khosrowe,metpx@web.sourceforge.net:htdocs/ --exclude htdocs/Makefile --exclude htdocs/template.py

clean: 
	rm -f $(TARGETS) 
	rm -rf dist
