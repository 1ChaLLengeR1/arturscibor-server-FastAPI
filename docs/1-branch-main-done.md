# 1 — Branch `master` → `main`

## Kontekst

Projekt startuje refaktor "od zera" architektonicznie, więc porządkujemy też
nazewnictwo domyślnego brancha na `main` (zgodnie ze standardem używanym w
projekcie referencyjnym WhereIsWheely).

## Kroki

- [x] `git branch -m master main` (lokalnie)
- [x] `git push -u origin main`
- [x] **[TY]** GitHub → Settings → Branches → General → zmień default branch na `main`
- [x] Potwierdzenie, że default branch zmieniony → wtedy usuwamy stary branch
- [x] `git push origin --delete master`
- [x] Sprawdzić, czy nic (branch protection rules, CI triggery, README badge) nie odwołuje się jawnie do `master` —
      jedyne trafienie to link w `README.md` do innego repozytorium
      (`arturscibor-website-vue.js/blob/master/...`), nie dotyczy tego projektu

## Status

Ukończone — `origin/master` usunięty, `main` jest default branch.

## Uwagi

- GitHub nie pozwala usunąć brancha ustawionego jako default — kolejność
  kroków jest istotna.
- Nie mamy `gh` CLI zainstalowanego w środowisku — zmiana default branch
  robiona ręcznie w UI GitHuba.
