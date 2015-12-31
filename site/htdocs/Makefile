.SUFFIXES: .1.rst .5 .7 .dia .png .pdf .html

VERSION = $(shell grep __version__ ../../sarracenia/sarra/__init__.py | sed -e 's/"//g' | cut -c14-)
DATE = $(shell date "+%B %Y")

SOURCES = $(wildcard ../../sarracenia/doc/*.rst)
TARGETS = $(patsubst ../../sarracenia/doc/%.rst,%.html,$(SOURCES))

default: $(TARGETS) 

#all: css $(TARGETS)
all: bootstrap anchorjs svg $(TARGETS)

html: $(TARGETS)

#.rst.html:
#    rst2html $*.rst >$*.html

# Build all the html pages from the rst file
# Also applies special modifications to make the site template work 
%.html: ../../sarracenia/doc/%.rst    
	rst2html --link-stylesheet --stylesheet=./css/bootstrap.min.css,./css/justified-nav.css --template=../template-en.txt $< $@ 
	sed -i 's/&\#64;Date&\#64;/$(DATE)/' $@
	sed -i 's/&\#64;Version&\#64;/$(VERSION)/' $@
	python template.py $@

svg:
	dia -t svg ../../sarracenia/doc/*.dia

# Get twitter bootstrap 3.3.6
bootstrap:
	wget -q https://github.com/twbs/bootstrap/releases/download/v3.3.6/bootstrap-3.3.6-dist.zip
	unzip -q bootstrap-3.3.6-dist.zip
	mv bootstrap-3.3.6-dist/js js
	mv bootstrap-3.3.6-dist/css css
	mv bootstrap-3.3.6-dist/fonts fonts
	rmdir bootstrap-3.3.6-dist
	rm bootstrap-3.3.6-dist.zip

# Get anchor.js 2.0.0
anchorjs:	
	cd js && wget -q https://raw.githubusercontent.com/bryanbraun/anchorjs/2.0.0/anchor.js

css:
	cp -ap ../dist .  

# NOTE: In order to deploy the site to sourceforge, run the following commands:
# 1. make all
# 2. make SFUSER=<username> deploy
#deploy:
#	rsync -avP -e ssh $(SFUSER),metpx@web.sourceforge.net:htdocs/ --exclude htdocs/Makefile --exclude htdocs/template.py

clean: 
	rm -f $(TARGETS) 
	rm -rf dist
	rm -rf fonts js css
	rm -f *.svg
