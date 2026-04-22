# Обновление README репозитория

Добавь в конец существующего файла `README.md` в твоём репо следующий раздел:

---

## Автоматическая сборка `.skill`

При каждом коммите в ветку `main` (затрагивающем `core/`, `projects/`, `faq/`, `updates/`, `skill-template/`, `VERSION` или сами скрипты сборки) GitHub Actions автоматически:

1. Собирает свежий `.skill`-файл из содержимого репозитория
2. Публикует его в [Releases](https://github.com/SWCSkill/swc-knowledge-base/releases)

### Ссылки для скачивания

- **Последняя версия (всегда актуальная):**
  `https://github.com/SWCSkill/swc-knowledge-base/releases/latest/download/swc-assistant.skill`

- **Конкретная версия:**
  `https://github.com/SWCSkill/swc-knowledge-base/releases/download/v2.2.0/swc-assistant.skill`

- **Страница всех релизов:** [github.com/SWCSkill/swc-knowledge-base/releases](https://github.com/SWCSkill/swc-knowledge-base/releases)

### Как выпустить новую версию

1. Внеси правки в контент (`core/`, `projects/`, `faq/`, `updates/`) через PR или прямой коммит
2. Если правки затрагивают ядро - обнови файл `VERSION` (например, `2.2.0` → `2.2.1`)
3. Закоммить изменения в `main`
4. GitHub Actions автоматически соберёт и опубликует новый релиз

### Ручной запуск сборки

Если нужно пересобрать без коммита:

1. Зайди в репо → вкладка **Actions** → workflow **Build and Release SWC Assistant Skill**
2. Нажми **Run workflow** (кнопка справа)
3. Можно указать кастомный тег релиза или оставить пустым - возьмётся версия из `VERSION`

### Локальная сборка (для проверки)

```bash
pip install PyYAML
python scripts/build_skill.py --output dist/swc-assistant.skill
```

## Правила версионирования

Версии в файле `VERSION` следуют [semver](https://semver.org/lang/ru/):

- **Major (`X.0.0`)** - значительные изменения, несовместимые с предыдущими версиями (переделка бренд-гайда, смена архитектуры)
- **Minor (`2.X.0`)** - новые разделы, новые проекты на витрине, новые темы FAQ
- **Patch (`2.2.X`)** - уточнения формулировок, исправления опечаток, мелкие правки контента

После обновления `VERSION` закоммить изменение в `main` - релиз создастся автоматически.
