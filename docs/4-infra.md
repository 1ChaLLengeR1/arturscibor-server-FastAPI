# 4 — Infra: `ansible/` `dockerfiles/` `scripts/`

## Kontekst

Wzorzec: `docs/ARCHITEKTURA.md` sekcja 12. Do dopracowania w skali
odpowiedniej dla portfolio (prawdopodobnie bez Docker Swarm multi-node,
Traefik, Prometheus/Grafana — to nadmiar dla jednoosobowego portfolio, chyba
że chcesz to celowo pokazać jako element portfolio DevOps).

## Kroki (szkic — do rozwinięcia bliżej realizacji)

- [ ] `infra/dockerfiles/` — `production.dockerfile`, ewentualnie
      `test.dockerfile`
- [ ] `infra/scripts/` — skrypt migracji DB, `docker_entrypoint.sh`
- [ ] `infra/ansible/` lub prostszy deploy (do ustalenia — Ansible może być
      przerostem formy nad treścią dla jednego serwera portfolio)
- [ ] `compose/` — lokalny `docker-compose.yaml` (Postgres + backend)

## Do ustalenia z Tobą przed startem

- Docelowy hosting (VPS własny? Coś managed?) — wpływa mocno na to, czy
  Ansible + Swarm ma sens, czy wystarczy prostszy `docker compose up -d` +
  webhook deploy.

## Status

- [ ] Zablokowane do czasu ukończenia pkt. 3
