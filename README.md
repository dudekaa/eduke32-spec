# EDuke32 RPM Packaging Automation

[![Copr build status](https://copr.fedorainfracloud.org/coprs/nost23/eduke32/package/eduke32/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/nost23/eduke32/package/eduke32/)

Build packages: https://copr.fedorainfracloud.org/coprs/nost23/eduke32/

This repository contains the packaging logic (Spec file, patches, and pipeline) to build **EDuke32** RPMs for Fedora via [COPR](https://copr.fedorainfracloud.org/).

It is designed as a **"Sidecar Repository"**: it does not contain the source code. Instead, it automates the retrieval of upstream source code, updates the versioning, and triggers builds on COPR.

## 🏗 Architecture

The workflow relies on **GitOps** principles. Jenkins acts as a bot that watches upstream, commits changes to this repo, and triggers external build systems.

1.  **Check:** Jenkins polls the upstream [EDuke32 GitLab](https://voidpoint.io/terminx/eduke32) for the latest commit hash.
2.  **Compare:** It compares the upstream hash against the `%global commit` defined in `eduke32.spec`.
3.  **Update:** If a new version is found:
    *   Updates the commit hash and date in `eduke32.spec` using `sed`.
    *   Bumps the Release number and adds a new `%changelog` entry using `rpmdev-bumpspec`.
    *   Commits and Pushes the changes back to **this** repository.
4.  **Build:** Jenkins triggers `copr-cli buildscm`.
5.  **Distribute:** COPR pulls the updated spec from this repo, downloads the source tarball from GitLab, and builds the RPMs.

## 🚀 Setup Guide

### 1. COPR Configuration
1.  Create a project on [COPR](https://copr.fedorainfracloud.org/) (e.g., `eduke32`).
2.  Obtain your API token from [https://copr.fedorainfracloud.org/api/](https://copr.fedorainfracloud.org/api/).
3.  Save the API config content to a file (usually `~/.config/copr`).

### 2. Jenkins Credentials
You need to configure the following credentials in Jenkins:

| ID | Type | Description |
| :--- | :--- | :--- |
| `copr-cli` | **Secret File** | Contains the content of your `~/.config/copr` file. Used to authenticate with COPR API. |
| `jenkins` | **SSH Username with private key** | The SSH key allowed to push commits to this Git repository. |
| `nexus-jenkins` | **Username with password** | (Optional) If using a private Docker registry for the builder image. |

### 3. Pipeline Environment Variables
The `Jenkinsfile` uses the following environment variables which can be adjusted at the top of the file:

*   `UPSTREAM_GIT_URL`: The URL of the official source code (used to check for updates).
*   `COPR_PROJECT`: Your COPR project slug (e.g., `username/project`).
*   `PACKAGE_NAME`: The name of the package (must match `.spec` filename).
*   `REGISTRY` / `IMAGE_NAME`: The Docker image used to run `copr-cli`.

### 4. Docker Image
The pipeline requires a Docker image with `copr-cli`, `rpmdevtools` (for version bumping), and `git` installed. A simple Dockerfile for this:

```dockerfile
FROM fedora:latest
RUN dnf install -y copr-cli rpmdevtools rpmlint rpm-build git && dnf clean all
USER 1000
```

## 📄 Repository Structure

*   **`eduke32.spec`**: The heart of the package. Defines dependencies, build steps, and versioning.
    *   *Note:* The `%global commit` and `%global date` lines are managed by Jenkins. Do not manually edit them unless you are forcing a specific version.
*   **`Jenkinsfile`**: The declarative pipeline defining the automation logic.
*   **`*.patch`**: Patches applied to the source code during the build (e.g., fixing `.desktop` files).

## 🔧 Manual usage

If you want to build a specific commit manually without waiting for Jenkins:

1.  Edit `eduke32.spec`:
    ```spec
    %global commit <FULL_COMMIT_HASH>
    %global date <YYYYMMDD>
    ```
2.  Run `rpmdev-bumpspec` to update the changelog (optional).
3.  Commit and push.
4.  Run the COPR build command manually:
    ```bash
    copr-cli buildscm eduke32 \
      --clone-url https://github.com/youruser/eduke32-packaging.git \
      --spec eduke32.spec
    ```

## 🔗 Links

*   **Upstream Source:** https://voidpoint.io/terminx/eduke32
*   **COPR Repository:** https://copr.fedorainfracloud.org/coprs/nost23/eduke32/