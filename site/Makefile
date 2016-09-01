.SUFFIXES: .1.rst .5 .7 .dia .png .pdf .html

MAKE = make
# VERSION = $(shell grep __version__ ../sarracenia/sarra/__init__.py | sed -e 's/"//g' | cut -c14-)
# DATE = $(shell date "+%B %Y")

# SOURCES = $(wildcard ../sarracenia/doc/*.rst)
# TARGETS = $(patsubst ../sarracenia/doc/%.rst,htdocs/%.html,$(SOURCES))

# default: $(TARGETS) 

# all: bootstrap anchorjs svg img index $(TARGETS)
all: bootstrap anchorjs index sarra sundew

html: $(TARGETS)

sarra:
	$(MAKE) TEMPLATE=--template=../../../site/template-en.txt -C ../sarracenia/doc/html
	cp ../sarracenia/doc/html/*.html htdocs
	cp ../sarracenia/doc/html/*.svg htdocs
	cp ../sarracenia/doc/*.gif htdocs
	cp ../sarracenia/doc/html/*.jpg htdocs

sundew:
	$(MAKE) TEMPLATE=--template=../../../site/template-en.txt -C ../sundew/doc/user
	$(MAKE) TEMPLATE=--template=../../../site/template-en.txt -C ../sundew/doc/dev
	$(MAKE) -C ../sundew/doc/html
	cp ../sundew/doc/html/*.html htdocs
	cp ../sundew/doc/html/*.png htdocs
	cp ../sundew/doc/html/WMO-386.pdf htdocs

index:
	cp index-e.html htdocs
	cp index-f.html htdocs
	-ln -s index-e.html htdocs/index.html

#.rst.html:
#    rst2html $*.rst >$*.html

# Build all the html pages from the rst file
# Also applies special modifications to make the site template work 
# htdocs/%.html: ../sarracenia/doc/%.rst    
# 	rst2html --link-stylesheet --stylesheet=css/bootstrap.min.css,css/metpx-sidebar.css --template=template-en.txt $< $@ 
# 	sed -i 's/&\#64;Date&\#64;/$(DATE)/' $@
# 	sed -i 's/&\#64;Version&\#64;/$(VERSION)/' $@
# 	sed -i 's/<a class="toc-backref" .*">\(.*\)<\/a>/\1/' $@
# 	python template.py $@

# svg:
# 	cd htdocs && dia -t svg ../../sarracenia/doc/*.dia

# img:
# 	cp ../sarracenia/doc/html/*.jpg htdocs
# 	cp ../sarracenia/doc/*.gif htdocs

# Get twitter bootstrap 3.3.6
bootstrap:
	wget -q https://github.com/twbs/bootstrap/releases/download/v3.3.6/bootstrap-3.3.6-dist.zip
	unzip -q bootstrap-3.3.6-dist.zip
	-mv bootstrap-3.3.6-dist/js htdocs/js
	-mv bootstrap-3.3.6-dist/css htdocs/css
	-mv bootstrap-3.3.6-dist/fonts htdocs/fonts
	rm -rf bootstrap-3.3.6-dist
	rm bootstrap-3.3.6-dist.zip
	cp -ap css/* htdocs/css

# Get anchor.js 2.0.0
anchorjs:	
	wget -q https://github.com/bryanbraun/anchorjs/archive/3.2.1.tar.gz
	tar -zxvf 3.2.1.tar.gz anchorjs-3.2.1/anchor.js
	-mv anchorjs-3.2.1/anchor.js htdocs/js
	rm -rf anchorjs-3.2.1
	rm 3.2.1.tar.gz 

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
	$(MAKE) -C ../sarracenia/doc/html clean
	$(MAKE) -C ../sundew/doc/html clean
	$(MAKE) -C ../sundew/doc/user clean
	$(MAKE) -C ../sundew/doc/dev clean
