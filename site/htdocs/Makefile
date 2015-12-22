.SUFFIXES: .1.rst .5 .7 .dia .png .pdf .html


#Guide.rtf:   Guide.latex
#   latex2rtf </dev/null Guide.latex >Guide.rtf

VERSION = $(shell grep __version__ ../../sarracenia/sarra/__init__.py | sed -e 's/"//g' | cut -c14-)
DATE = $(shell date "+%B %Y")

SOURCES = $(wildcard ../../sarracenia/doc/*.rst)
TARGETS = $(patsubst ../../sarracenia/doc/%.rst,%.html,$(SOURCES))

default: $(TARGETS) 

#.dia.png:
#    dia -t png $*.dia

#.rst.html:
#    rst2html $*.rst >$*.html

# Build all the html pages from the rst file
# Also applies special modifications to make the site template work 
%.html: ../../sarracenia/doc/%.rst    
	rst2html --link-stylesheet --stylesheet=./dist/css/bootstrap.min.css,./dist/css/justified-nav.css --template=../template.txt $< $@ 
	sed -i 's/&\#64;Date&\#64;/$(DATE)/' $@
	sed -i 's/&\#64;Version&\#64;/$(VERSION)/' $@
	sed -i "s/<h1 class=\"title\">\(.*\)<\/h1>/<h3 class=\"text-muted\">\1<\/h3>/" $@ 
	sed -i "s/<h1>\(.*\)<\/h1>/<h1 class=\"section-header\">\1<\/h1>/" $@


clean: 
	rm -f $(TARGETS) 
