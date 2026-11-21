# Lab guide web server. Run from anywhere: make -C ~/edgelab/guide <target>
#   make serve     start the guide in the background and print its address (port 8765, or the next free one)
#                  make serve HOST=0.0.0.0 also lets other machines on your network open the guide
#   make stop      stop it
#   make status    say whether it is running
#   make version   print the guide's version; make version V=1.2.3 sets it in VERSION and in the sidebar
# To check your work in the lab, use the lab command in the working folder: ./lab status
PORT ?= 8765
HOST ?= 127.0.0.1
serve:
	@python3 serve.py start $(PORT) $(HOST)
stop:
	@python3 serve.py stop
status:
	@python3 serve.py status
version:
ifdef V
	@echo '$(V)' | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$$' || { echo 'V must look like 1.2.3'; exit 1; }
	@echo '$(V)' > VERSION
	@sed -i 's/^const LAB_VERSION = "[^"]*";/const LAB_VERSION = "$(V)";/' site/lab.js
endif
	@cat VERSION
.PHONY: serve stop status version
