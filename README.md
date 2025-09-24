# Setup
Instruction how to run server. All commands should be run in root directory of this project.
- install python not older than 3.10

```bash
sudo apt update
```
```bash
sudo apt upgrade
```
```bash
sudo apt install python 3.10
```

- create virtual environment

```bash
python -m venv venv
```

- install requirements

```bash
pip install -r requirements.txt
```

- start your database host

- create `.env` file in root directory and fill it with actual data:
```env
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
```
# Run server

```bash
uvicorn app:app --reload
```
Use Ctrl + C to stop it

# Comments
- route GET "/invoices/get" looks not very logical to me and it's not how it should be as described in "REST API Design Rulebook" by Mark Masse. I would better make it as GET "/invoices" if it's possible to change routes at the moment of development.
