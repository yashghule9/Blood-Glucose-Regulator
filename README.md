# Blood-Glucose-Regulator – AP Dashboard

This repository contains a Flask-based dashboard to visualize results from an Artificial Pancreas simulation.

## Local development

Prerequisites: Python 3.11, pip, or Docker.

1) Install dependencies and run locally:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r ap_dashboard/requirements.txt
python ap_dashboard/app.py
```

Open http://localhost:5000

2) Build and run with Docker:

```bash
docker build -t ap-dashboard:latest -f ap_dashboard/Dockerfile .
docker run --rm -p 5000:5000 ap-dashboard:latest
```

Or with docker-compose:

```bash
docker compose up --build
```

## Container Registry (GitHub Container Registry)

This repo includes a GitHub Actions workflow at `.github/workflows/docker-build-push.yml` that builds the Docker image from `ap_dashboard` and pushes it to GitHub Container Registry (GHCR) as `ghcr.io/<owner>/<repo>:latest` on pushes to main.

If you want to use the image in a cloud service (Render, Fly.io, Azure Web Apps for Containers, Heroku with container registry, etc.), configure the target platform to pull the image `ghcr.io/<owner>/<repo>:latest` (or the tag you push) and supply the appropriate credentials or a public image.

### Push to GitHub Container Registry manually

1. Authenticate with GitHub Container Registry (GHCR):

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u <github-username> --password-stdin
```

2. Build and push image (from repo root):

```bash
docker build -t ghcr.io/<owner>/<repo>:latest -f ap_dashboard/Dockerfile .
docker push ghcr.io/<owner>/<repo>:latest
```

### Push to Docker Hub (manual example)

Authenticate and push:

```bash
docker login --username=<your-dockerhub-username>
docker tag ghcr.io/<owner>/<repo>:latest <your-dockerhub-username>/ap-dashboard:latest
docker push <your-dockerhub-username>/ap-dashboard:latest
```

> Tip: If you want the GitHub Action to push to Docker Hub, create the repo secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.

### Heroku (container-based deploy)

1. Login to Heroku registry and push the image:

```bash
heroku container:login
heroku create <app-name>
docker build -t registry.heroku.com/<app-name>/web -f ap_dashboard/Dockerfile .
docker push registry.heroku.com/<app-name>/web
heroku container:release web -a <app-name>
```

Replace <app-name> with your Heroku app name.

## Heroku (optional)

A `Procfile` is included to start Gunicorn. To deploy to Heroku Container Registry (or normal Heroku), follow Heroku doc to push the container or a source-based deployment.

## Notes

- The application reads `ap_dashboard/latest_results.mat`. Replace it with your data or feed updates into that file.
- The GitHub action uses `GITHUB_TOKEN` to authenticate with GHCR. If you prefer Docker Hub, add a step to log into Docker Hub using secrets.

If you'd like, I can also add a deployment GitHub Action for a specific provider (Render/Azure/Heroku/Fly.io) — tell me which platform you prefer and I can implement it.
