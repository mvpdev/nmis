VERSION=1.4.0
DATE=$(shell DATE)
CSS_OUTPUT_FILE = ./css/styles.css
CSS_MIN = ./css/styles.min.css
CSS_TEMPFILE = ./lesscss/styles.less
LESS_COMPRESSOR ?= `which lessc`
#UGLIFY_JS ?= `which uglifyjs`
#WATCHR ?= `which watchr`

build:
	@@if test ! -z ${LESS_COMPRESSOR}; then \
		sed -e 's/@VERSION/'"v${VERSION}"'/' -e 's/@DATE/'"${DATE}"'/' <${CSS_TEMPFILE} >${CSS_TEMPFILE}.tmp; \
		lessc ${CSS_TEMPFILE}.tmp > ${CSS_OUTPUT_FILE}; \
		lessc ${CSS_TEMPFILE}.tmp > ${CSS_MIN} --compress; \
		rm -f ${CSS_TEMPFILE}.tmp; \
		echo "Bootstrap successfully built! - `date`"; \
	else \
		echo "You must have the LESS compiler installed in order to build Bootstrap."; \
		echo "You can install it by running: npm install less"; \
		echo "And make sure npms bin directory is in the PATH"; \
	fi
