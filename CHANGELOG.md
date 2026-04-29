# Changelog

История версий скилла swc-skill-toolkit.

## [1.0.0] - 2026-04-28

### Первый релиз
- SKILL.md с маршрутизацией по сценариям CREATE / UPDATE / CONSULT
- `references/architecture.md` - принципы архитектуры скиллов SWC (контент vs поведение, один источник правды, слои меты, слоты под рост, постоянная ссылка, переадресация vs подмена)
- `references/conventions.md` - конкретные правила: имена, структура репо, версионирование (semver), YAML frontmatter, разделы SKILL.md, GitHub Action
- `references/workflow_create.md` - 10-шаговый гид по созданию нового скилла с нуля
- `references/workflow_update.md` - гид по обновлению существующего скилла с трёхуровневой моделью вмешательства (фоновая валидация / обычная работа / архитектурный аудит)
- `references/changelog_style.md` - формат и правила CHANGELOG записей
- `references/checklists.md` - чек-листы валидации перед отдачей архива и после заливки
- Скелет нового скилла в `skeleton/`: SKILL.md.template.example, build_skill.py, build-skill.yml, README.md.example, INSTALL.md.example, CHANGELOG.md.example, VERSION.example
- Универсальный `scripts/build_skill.py` - имя скилла берётся из YAML frontmatter, не хардкодится
- Универсальный `.github/workflows/build-skill.yml` - имя скилла извлекается на лету
- Знание о четвёрке скиллов SWC: swc-assistant, swc-manajet-expert, swc-orgpolicies-guru, manajet-api-helper

### Зачем это
Корпоративные скиллы SWC должны быть устроены единообразно - чтобы их можно было поддерживать и развивать без глубокого погружения в каждый. Toolkit передаёт авторам скиллов накопленные архитектурные решения и проводит через создание/обновление по проверенному процессу. Эталон архитектуры - swc-manajet-expert v1.4.0+.
