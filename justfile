set dotenv-load := true
set shell := ["bash", "-cu"]

venv_dir := "venv"
python := venv_dir + "/bin/python"
pip := venv_dir + "/bin/pip"
python_admin := "../" + venv_dir + "/bin/python"

default:
	@just --list

venv:
	@test -d "{{venv_dir}}" || python3 -m venv "{{venv_dir}}"
	@{{python}} -V

install: venv
	@{{pip}} install -U pip
	@{{pip}} install -r sqlite_to_postgres/requirements.txt
	@{{pip}} install -r movies_admin/requirements.txt

migrate: install
	@{{python}} sqlite_to_postgres/load_data.py

admin-migrate: install
	@cd movies_admin && {{python_admin}} manage.py migrate

superuser: install
	@cd movies_admin && {{python_admin}} manage.py createsuperuser

run: install
	@cd movies_admin && {{python_admin}} manage.py runserver

reset-venv:
	@rm -rf "{{venv_dir}}"
