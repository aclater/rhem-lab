# Lab guide web server. Run from anywhere: make -C ~/edgelab/guide <target>
#   make serve     start the guide in the background and print its address (port 8765, or the next free one)
#   make stop      stop it
#   make status    say whether it is running
# To check your work in the lab, use the lab command in the working folder: ./lab status
PORT ?= 8765
serve:
	@python3 serve.py start $(PORT)
stop:
	@python3 serve.py stop
status:
	@python3 serve.py status
.PHONY: serve stop status
