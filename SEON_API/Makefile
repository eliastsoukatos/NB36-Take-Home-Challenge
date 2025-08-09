.PHONY: install run docker-build docker-run

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8080

docker-build:
	docker build -t seon-mock:latest .

docker-run:
	docker run --rm -p 8080:8080 --name seon-mock \
		-e API_KEY="$(API_KEY)" \
		-e SECRET_KEY="$(SECRET_KEY)" \
		-e WEBHOOK_URL="$(WEBHOOK_URL)" \
		seon-mock:latest
