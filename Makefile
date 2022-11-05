DIST ?= dist/
BUILD_DIR ?= build/
PIP ?= pip
PYTHON ?= python
PYTHON_VERSION ?= python3.8
VENV ?= .venv
VENV_BIN ?= $(VENV)/bin
SRC_DIR ?= django_nats_nkeys
TEST_DIR ?= tests


clean-venv:
	rm -rf $(VENV)
clean-dist: ## remove dist artifacts
	rm -rf $(DIST)

clean-build:
	rm -rf $(BUILD_DIR)

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean: clean-dist clean-pyc clean-build

clean-operator:
	sudo chown -R $(USER) .
	rm -rf .nats/config
	rm -rf .nats/stores
	rm -rf .nats/keys
	rm .nats/DjangoOperator.conf
	docker-compose -f docker/local.yml stop
	docker-compose -f docker/local.yml rm
	docker volume prune


sdist: ## builds source package
	$(PYTHON) setup.py sdist && ls -l dist

bdist_wheel: ## builds wheel package
	$(PYTHON) setup.py bdist_wheel && ls -l dist

dist: clean-dist sdist bdist_wheel

release: dist
	twine upload dist/*

pip-sync:
	$(VENV_BIN)/pip-sync

dev-install:
	$(PIP) install pip-tools
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt

.venv:
	$(PYTHON_VERSION) -m venv $(VENV)

venv: .venv dev-install

requirements.txt: setup.py
	$(VENV_BIN)/pip-compile --generate-hashes

dev-requirements.txt: dev-requirements.in
	$(VENV_BIN)/pip-compile --generate-hashes dev-requirements.in --output-file dev-requirements.txt

lint:
	black $(SRC_DIR) $(TEST_DIR)

tests/fixtures/testsqldbsetup.json: tests/fixtures/testsqldbsetup.sql
	cat tests/fixtures/testsqldbsetup.sql | docker-compose -f docker/local.yml run django manage.py dbshell
	docker-compose -f docker/local.yml run django manage.py dbshell
	docker-compose -f docker/local.yml run django manage.py dumpdata > tests/fixtures/testsqldbsetup.json

images:
	docker-compose -f docker/local.yml build

pytest:
	docker-compose -f docker/local.yml run --rm django pytest

tox:
	docker-compose -f docker/local.yml exec django tox

dev:
	docker-compose -f docker/local.yml up

superuser:
	docker-compose -f docker/local.yml exec django python manage.py createsuperuser

migrations:
	docker-compose -f docker/local.yml run --rm django python manage.py makemigrations

migrate:
	docker-compose -f docker/local.yml run --rm django python manage.py migrate

nsc-init:
	docker-compose -f docker/local.yml exec django python manage.py nsc_init
	docker-compose -f docker/local.yml restart nats
	docker-compose -f docker/local.yml exec django python manage.py nsc_push

nsc-env:
	docker-compose -f docker/local.yml exec django python manage.py nsc_env

docker-up-d:
	docker-compose -f docker/local.yml up -d

docker-up:
	docker-compose -f docker/local.yml up
