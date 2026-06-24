# MXroute Manager

<p align="center">
  <a href="https://github.com/t0msh/mxroute-manager/actions/workflows/test.yml"><img src="https://github.com/t0msh/mxroute-manager/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://scanaislop.com/t0msh/mxroute-manager"><img src="https://badges.scanaislop.com/score/t0msh/mxroute-manager.svg" alt="aislop score"></a>
</p>

<p align="center">
  <img src="static/logo-emerald.svg" alt="MXroute Manager logo" width="220" />
</p>

> [!NOTE]
>
> This is a control panel for MXroute. It solves personal annoyances I had with managing many domains and mailboxes, and users that forget their passwords. Full disclosure, a lot of it was written with AI help (Cursor) and then beaten into shape with tests, security review, and real-world DNS pain.
>
> It's meant to run on **your** server. Back up the SQLite database, put it behind TLS, and read [Getting started](docs/getting-started.md) before you expose it to the internet. The test suite runs in CI without live MXroute or Cloudflare keys. Sensitive paths use CSRF, rate limits, hashed credentials, and audit logging.

A Self-hosted Flask app for managing Mxroute domains, mailboxes, forwarders, Cloudflare DNS, delegated access, API tokens, and branded password-reset portals. One UI instead of juggling panels and API docs.

## Quickstart

**Requirements:** Docker and Docker Compose, plus MXroute API credentials.

```bash
git clone https://github.com/t0msh/mxroute-manager.git
cd mxroute-manager
cp .env.example .env
# Edit .env - see docs/getting-started.md
docker compose up --build -d
```

Open [http://localhost:5000](http://localhost:5000) and sign in with `admin` (or `ADMIN_USER`) and your `ADMIN_PASSWORD`.

Production TLS, Cloudflare, SMTP, portals: [Getting started](docs/getting-started.md)

## What it does

- **Mail** - Provision mailboxes, forwarders, spam rules, CSV import/export, client setup cards
- **DNS** - Setup wizard, health checks, bulk fix, scheduled monitoring with alerts
- **Fleet view** - Dashboard table of all domains (mail, DNS, mailbox counts)
- **Access** - Delegated users, per-domain permissions, API tokens for scripting
- **Portals** - Branded mailbox password reset on your subdomain
- **Ops** - Apprise notifications (audit events, DNS health, mailbox quota/send alerts), audit logs, themes

Full detail lives in the docs below.

## Documentation

Index: [docs/README.md](docs/README.md)

| Area | Start here |
| --- | --- |
| First deploy | [Getting started](docs/getting-started.md) |
| Domains and DNS | [Adding a domain](docs/adding-a-domain.md) |
| Bulk mailboxes | [Bulk CSV import/export](docs/bulk-mailbox-csv.md) |
| Team access | [Access control](docs/access-control.md) |
| Scripting | [HTTP API](docs/api.md) |
| Alerts | [Notifications](docs/notifications.md) |
| UI tour | [App tour](docs/app-tour.md) |

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

Details: [Testing](docs/testing.md) · [Frontend scripts](docs/frontend-app-scripts.md)

## License

MIT. See [LICENSE](LICENSE).
