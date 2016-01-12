.SUFFIXES: .1.rst .5 .7 .dia .png .pdf .html

VERSION = $(shell grep __version__ ../sarracenia/sarra/__init__.py | sed -e 's/"//g' | cut -c14-)
DATE = $(shell date "+%B %Y")

SOURCES = $(wildcard ../sarracenia/doc/*.rst)
TARGETS = $(patsubst ../sarracenia/doc/%.rst,htdocs/%.html,$(SOURCES))

default: $(TARGETS) 

#all: css $(TARGETS)
all: bootstrap anchorjs svg img index $(TARGETS)

html: $(TARGETS)

index:
	cp index-e.html htdocs
	cp index-f.html htdocs
	cd htdocs && ln -s index-e.html index.html

#.rst.html:
#    rst2html $*.rst >$*.html

# Build all the html pages from the rst file
# Also applies special modifications to make the site template work 
htdocs/%.html: ../sarracenia/doc/%.rst    
	rst2html --link-stylesheet --stylesheet=css/bootstrap.min.css,css/metpx-sidebar.css --template=template-en.txt $< $@ 
	sed -i 's/&\#64;Date&\#64;/$(DATE)/' $@
	sed -i 's/&\#64;Version&\#64;/$(VERSION)/' $@
	sed -i 's/<a class="toc-backref" .*">\(.*\)<\/a>/\1/' $@
	python template.py $@

svg:
	cd htdocs && dia -t svg ../../sarracenia/doc/*.dia

img:
	cp ../sarracenia/doc/html/*.jpg htdocs
	cp ../sarracenia/doc/*.gif htdocs

# Get twitter bootstrap 3.3.6
bootstrap:
	wget -q https://github.com/twbs/bootstrap/releases/download/v3.3.6/bootstrap-3.3.6-dist.zip
	unzip -q bootstrap-3.3.6-dist.zip
	mv bootstrap-3.3.6-dist/js htdocs/js
	mv bootstrap-3.3.6-dist/css htdocs/css
	mv bootstrap-3.3.6-dist/fonts htdocs/fonts
	rmdir bootstrap-3.3.6-dist
	rm bootstrap-3.3.6-dist.zip
	cp -ap css/* htdocs/css

# Get anchor.js 2.0.0
anchorjs:	
	cd htdocs/js && wget -q https://raw.githubusercontent.com/bryanbraun/anchorjs/2.0.0/anchor.js

css:
	mkdir -p htdocs/css
	cp -ap css/* ./htdocs/css

# NOTE: In order to deploy the site to sourceforge, run the following commands:
# 1. make all
# 2. make SFUSER=<username> deploy
deploy:
	rsync -avP htdocs/ -e ssh $(SFUSER),metpx@web.sourceforge.net:htdocs/

clean: 
	rm -f $(TARGETS) 	
	rm -rf htdocs/fonts htdocs/js htdocs/css
	rm -f htodcs/*.svg
	rm -f htdocs/*.jpg
	rm -f htdocs/*.gif
	rm -f htdocs/*.html
