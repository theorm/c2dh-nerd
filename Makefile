run:
	python -m c2dh_nerd

build:
	docker build -t theorm/c2dh_nerd .

docker-run:
	docker run \
		--rm -it \
		-p 8002:8002 \
		--name c2dh_nerd \
		-v $(PWD)/cache:/c2dh-nerd/cache \
		theorm/c2dh_nerd
