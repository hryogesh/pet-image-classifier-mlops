# CI/CD Notes

This repo contains two GitHub Actions workflows:

- `.github/workflows/ci.yml`: run tests, build Docker image, and push to a container registry.
- `.github/workflows/cd.yml`: on `main` branch, builds image and deploys using Docker Compose on the runner.

Secrets required for `ci.yml` (set in GitHub repository settings):

- `REGISTRY_USERNAME` and `REGISTRY_PASSWORD` (Docker Hub) or `CR_PAT` for GitHub Container Registry.
- `IMAGE_NAME` (e.g., `yourusername/catsdogs`)

CD: The provided `cd.yml` runs `docker-compose up -d --build` on the runner. For real production,
replace this with your preferred deployment target (SSH to VM, Kubernetes manifests + ArgoCD, etc.).
