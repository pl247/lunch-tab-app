# LunchTab
Shared office lunch-order tracker: one person collects orders, tracks payments, sees who still owes.

## Prerequisites
Ubuntu with Docker Engine and the Compose plugin pre-installed.

## Quick start
```bash
chmod +x deploy/*.sh
./deploy/deploy.sh
```
This prints http://localhost:8723 when ready.

## Manual run alternatives
- Compose: `docker compose up -d --build`
- Plain Docker: 
  ```bash
  docker build -t lunchtab .
  docker run -d -p 8723:8723 -v lunchtab-data:/app/data lunchtab
  ```

## Pull from GHCR
```bash
docker pull ghcr.io/<owner>/lunch-tab-app:latest
```
Note: The package must be made public in repo settings (Packages → visibility) for unauthenticated pulls.

## Local development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Teardown
```bash
./deploy/cleanup.sh   # stops containers
./deploy/cleanup.sh -v   # also removes the stored data volume
```

## Note
Data persists in the named volume `lunchtab-data` across container restarts. Demo data is seeded only when the database is empty, ensuring a fresh container shows a populated UI.
