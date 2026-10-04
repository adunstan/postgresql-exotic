Task 1: complete (tooling in results/nls-demo, 10 tests pass; done during planning)
Task 2: complete (worktree nls-demo @ master, pots 6217/1528/411, cassert build ok; no commits)
Task 3: complete (commit 01b745b4470 amended from 31295288fa1; review clean after fix round 1: option-arg protection, relative pot refs, smoke.sh multiarch libdir)
Task 4: complete (user approved glossary + prompt 2026-10-04)
Task 5 notes:
- translate-prompt.md amended after wave 1: severity/field labels (ERROR, DETAIL:, LINE %d: ...) ARE translated. Fix up already-done eo chunks (libpq chunk-001 kept NOTICE/WARNING/DETAIL: etc. in English; psql chunk-000 translated STATEMENT).
- glossary extended after wave 1 (17 terms). Wave-1 chunks may use variant terms: collation kunordigo/kolacio, access method atingo-metodo/atingmetodo, backend dorsa procezo/backend/servila procezo, hash haŝo/haketaĵo. Normalise after merge.
- eo postgres chunk-021 translated SQL type names (smallint/bigint/real/double precision) in error messages; restore originals in normalisation pass. Add rule to prompt before tlh: SQL type names stay.
Task 5: complete (commit caf4f9e1d17, eo 6217/1528/411 all translated; normalisation 65 changes; smoke.sh now sets LC_CTYPE=en_US.utf8; review clean)
Task 6: in progress — tlh pilot libpq/chunk-000 done; wave 1 (libpq-001, psql 000-006, postgres 000-001) dispatched
- tlh: normalise after merge — transaction "ta'" in postgres chunk-001 vs glossary "ta' mIr"; WARNING prefix lines in libpq left English (fine); check other variants.
Task 6: complete (commit 3f1e40b0083 after amend; tlh 6217/1528/411; normalisation 139 changes + 1 review fix; review clean)
Task 7: msgfmt -c all 9 clean; meson test cassert 368 ok / 0 fail / 53 skipped; smoke all 3 langs OK. Final whole-branch review pending.
Final review: Ready with minor follow-ups. Fixed M1/M2 (tlh psql quoted text) -> Klingon commit amended. Open optional: M3 tlh type names, M4 3 rewraps, M6 commit wording.
