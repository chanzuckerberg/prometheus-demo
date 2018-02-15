.PHONY: install
install:
	virtualenv venv && . venv/bin/activate && pip install -r requirements.txt


.PHONY: image
image:
	docker build -t chanzuckerberg/prometheus-demo .
