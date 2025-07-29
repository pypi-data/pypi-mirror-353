# ChimeraStack CLI

> 🐉 **One command to launch a production-ready development stack.**
>
> Skip the boilerplate, focus on code.

[![PyPI](https://img.shields.io/pypi/v/chimera-stack-cli)](https://pypi.org/project/chimera-stack-cli)
[![CI](https://github.com/Amirofcodes/ChimeraStack_CLI/actions/workflows/ci.yml/badge.svg)](https://github.com/Amirofcodes/ChimeraStack_CLI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)](#project-status)

---

## 📚 Table of Contents

1. [Why ChimeraStack?](#-why-chimerastack)
2. [TL;DR Quick Demo](#-tldr-quick-demo)
3. [Key Features](#-key-features)
4. [Installation](#-installation)
5. [Creating Your First Project](#-creating-your-first-project)
6. [Template Gallery](#-template-gallery)
7. [How It Works](#-how-it-works)
8. [Authoring Custom Templates](#-authoring-custom-templates)
9. [Roadmap](#-roadmap)
10. [Contributing](#-contributing)
11. [License](#-license)

---

## 🛈 Project Status

## ❓ Why ChimeraStack?

| Persona                 | Pain Points                                                         | How ChimeraStack Helps                                                                          |
| ----------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Beginners**           | Confusing Docker setup, port clashes, missing environment variables | `chimera create blog -t fullstack/react-php` → ready-to-run project with sensible defaults      |
| **Students / Teachers** | Need consistent environments on many machines                       | Project templates ensure everyone runs identical containers and ports                           |
| **Senior Devs**         | Tiring to maintain many local micro-services                        | Dynamic port allocator + compose fragments = run multiple stacks side-by-side without conflicts |

---

## ⚡ TL;DR Quick Demo

```bash
# Install (isolated) – requires Python 3.8+
pipx install chimera-stack-cli

# Spin up a React + PHP + MySQL stack in <10 s
chimera create my-app -t fullstack/react-php -d mysql   # choose db variant
cd my-app

docker compose up -d  # 🚀 Boom – services are live!
```

Open http://localhost:8xxx (ports are auto-assigned) and start coding.

## 📽 Interactive Demo

[![asciicast](https://asciinema.org/a/CjY2cVEPWHlExixA4cJJE9iOd.svg)](https://asciinema.org/a/CjY2cVEPWHlExixA4cJJE9iOd)

---

## ✨ Key Features

- 🔌 **Template Catalogue** – ready-made stacks for frontend, backend & databases
- 🔄 **Smart Port Allocation** – avoid `address already in use` forever
- 🗜️ **Zero-Config** – works with a single CLI command, no manual Docker files
- 🧩 **Composable** – mix components or add plugins (coming v0.3)
- 🧑‍🎓 **Learning-Friendly** – minimal jargon, helpful errors & docs

---

## 📦 Installation

| Method               | Command                                                     |
| -------------------- | ----------------------------------------------------------- |
| `pipx` (recommended) | `pipx install chimera-stack-cli`                            |
| `pip`                | `pip install chimera-stack-cli`                             |
| Homebrew             | `brew install chimerastack/tap/cli` _(soon)_                |
| Binary               | Grab the latest release from **Releases** page & `chmod +x` |

> _Requires Python 3.10+ and Docker 20.10+ with Docker Compose plugin._

---

## 🛠️ Creating Your First Project

```bash
# Interactive wizard
chimera create my-blog

# Non-interactive: choose stack + variant up-front
chimera create my-api -t backend/php-web -d postgresql
```

Once finished:

```bash
cd my-api
docker compose up -d
```

Your containers are accessible on dynamically allocated ports printed by the CLI.

---

## 🎨 Template Gallery _(v0.2.5)_

| Category      | Templates                                                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**  | `frontend/react-static` (Vite + Tailwind; Vite dev server on <code>3000-3999</code>), `frontend/vue` _(soon)_                           |
| **Backend**   | `backend/php-web` (MySQL, PostgreSQL, MariaDB), `backend/node-express` _(roadmap)_                                                      |
| **Databases** | `database/mysql`, `database/postgresql`, `database/mariadb`                                                                             |
| **Fullstack** | `fullstack/react-php` (React + PHP; dev server on dynamic port, Nginx on <code>8000-8999</code>; DB variants: MySQL/MariaDB/PostgreSQL) |

Run `chimera list` to explore the full list and search by tag.

---

## 🔍 How It Works

1. **Selects** stack + components based on CLI flags.
2. **Renders** all files through a Jinja2 pipeline (variable substitution).
3. **Allocates** free ports via `PortAllocator` (ranges defined in `config/ports.yaml`).
4. **Executes** optional `post_copy` tasks for final clean-up.
5. **Outputs** a ready project you can commit to Git or deploy.

_No global state, no magic network shims – just Docker Compose done right._

---

## 🧑‍🎨 Authoring Custom Templates

Want to add **Django + Redis**? Check out the dedicated guide:

➡️ [`docs/authoring-templates.md`](docs/authoring-templates.md)

It covers directory layout, `template.yaml` schema, Jinja2 helpers, testing & publishing.

---

## 🔮 Roadmap

| Version | Highlights                                                          |
| ------- | ------------------------------------------------------------------- |
| `v0.3`  | Plugin system (`chimera add redis`, monitoring…)                    |
| `v0.4`  | Mix-&-Match wizard (`chimera init --frontend react --backend node`) |
| `v0.5`  | `chimera deploy` to Coolify or bare VPS                             |
| `v1.0`  | Stable API, web/CLI sync, template marketplace                      |

See [`ROADMAP.md`](ROADMAP.md) for the full list.

---

## 🤝 Contributing

1. Fork → create feature branch → commit (semantic) → PR.
2. Run `pre-commit` & `pytest` locally – CI must stay green.
3. Need help? Open an issue or start a discussion.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for environment setup, commit policy & test guide.

---

## 📄 License

MIT © Amirofcodes & contributors
