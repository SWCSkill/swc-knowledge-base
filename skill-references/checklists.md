# Чек-листы валидации

Конкретные проверки, которые ты делаешь перед тем как отдать сотруднику архив для заливки или после его заливки.

## Чек-лист: перед отдачей архива (CREATE)

После сборки скелета нового скилла - проверь:

- [ ] **YAML frontmatter** в `skill-template/SKILL.md.template` начинается с `---\n`, заканчивается `---\n`, парсится валидно.
- [ ] В YAML есть поля `name` и `description`. Имя = имя скилла в kebab-case. Description многострочный, содержит триггеры.
- [ ] Версия в шаблоне - **переменная** `{{VERSION}}`, не конкретная цифра. Иначе при сборке Action ничего не подставит.
- [ ] Файл `VERSION` существует, содержит `1.0.0\n`, без пробелов и комментариев.
- [ ] `CHANGELOG.md` существует, содержит первую запись `## [1.0.0]` с описанием первого релиза.
- [ ] `scripts/build_skill.py` присутствует.
- [ ] `.github/workflows/build-skill.yml` присутствует, в нём имя скилла подставлено корректно (поиск по `<skill-name>` в шаблоне).
- [ ] `INSTALL.md` адаптирован: правильное имя скилла, правильное имя репо в URL.
- [ ] `README.md` есть, описывает зону скилла.
- [ ] Стартовые контентные файлы (3-5 штук) есть в нужных папках.
- [ ] Архив запакован, размер разумный (<500 КБ для пустого скилла, контент может больше).

## Чек-лист: перед отдачей архива (UPDATE)

Когда апдейт затрагивает поведение:

- [ ] Тип изменения определён правильно (контент / поведение / инфраструктура).
- [ ] Если бампим версию - в архиве **есть** обновлённый VERSION.
- [ ] Если бампим версию - в архиве **есть** обновлённый CHANGELOG с новой записью.
- [ ] CHANGELOG-запись соответствует версии (если бампим до 1.4.0 - запись `## [1.4.0]`).
- [ ] Запись в CHANGELOG конкретна (не «Update», «Improvements»).
- [ ] В архиве **нет лишнего**. Только то, что меняется. Не пихай весь скилл в патч одной строки.
- [ ] Если правил `skill-template/SKILL.md.template` - YAML всё ещё валиден.
- [ ] Если правил с подстановкой переменных - `{{VERSION}}` и `{{BUILD_DATE}}` сохранены.

Когда апдейт - только контент:

- [ ] VERSION **не менялся**.
- [ ] CHANGELOG **не менялся**.
- [ ] Архив содержит только контентные файлы.

## Чек-лист: после заливки сотрудником (UPDATE с бампом версии)

Подождать ~60 секунд после коммита, потом:

```bash
# Проверка 1: новый release есть
curl -sIL "https://github.com/SWCSkill/<repo>/releases/latest/download/<skill>.skill" | head -1
# Ожидание: HTTP/2 302

# Проверка 2: VERSION в репо обновлён
curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/VERSION"
# Ожидание: новая версия

# Проверка 3: CHANGELOG обновлён
curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/CHANGELOG.md" | head -10
# Ожидание: первая запись = новая версия
```

Если что-то из этого не так - попроси сотрудника зайти в Actions tab репо и прислать тебе логи последнего workflow run.

## Чек-лист: при первом обращении к чужому скиллу (фоновая валидация)

Эти проверки запускаешь **молча**, до начала работы по задаче. Если что-то критично сломано - молча чинишь как часть текущей задачи.

```bash
# 1. SKILL.md.template читается?
curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/skill-template/SKILL.md.template" | head -5

# 2. YAML валидный?
curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/skill-template/SKILL.md.template" | python3 -c "
import sys, yaml
content = sys.stdin.read()
if not content.startswith('---\n'):
    print('NO_YAML')
    sys.exit()
parts = content.split('---\n', 2)
try:
    fm = yaml.safe_load(parts[1])
    if 'name' in fm and 'description' in fm:
        print('OK')
    else:
        print('MISSING_FIELDS')
except Exception as e:
    print(f'INVALID_YAML: {e}')
"

# 3. VERSION есть и парсится?
curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/VERSION" | tr -d '[:space:]'

# 4. Последняя запись в CHANGELOG соответствует VERSION?
ver=$(curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/VERSION" | tr -d '[:space:]')
curl -s "https://raw.githubusercontent.com/SWCSkill/<repo>/main/CHANGELOG.md" | grep "^## \[" | head -1
# В выводе должна быть [<ver>]

# 5. Workflow есть?
curl -sI "https://raw.githubusercontent.com/SWCSkill/<repo>/main/.github/workflows/build-skill.yml" | head -1
# Ожидание: HTTP/2 200

# 6. Релизы выпускались?
curl -sIL "https://github.com/SWCSkill/<repo>/releases/latest/download/<skill>.skill" | head -1
# Ожидание: HTTP/2 302 (релиз есть)
```

Если что-то возвращает не то, что ожидается - оцени критичность:

| Проблема | Критичность | Что делать |
| :--- | :--- | :--- |
| YAML невалиден | Критично | Включи починку в текущую задачу, уведоми одной строкой |
| VERSION не парсится | Критично | То же |
| VERSION ≠ последний CHANGELOG | Средне | Уведоми, спроси: «Поправить CHANGELOG?» |
| Нет workflow | Критично если скилл новый | Залей вместе с правкой |
| Нет release | Зависит | Если скилл новый - норм. Если есть VERSION но нет release - что-то с Action, нужны логи |

## Чек-лист: на финальном тесте у сотрудника (после установки)

Когда сотрудник переустановил скилл и идёт тестировать:

- [ ] Базовый сценарий - скилл активируется на ожидаемом триггере?
- [ ] Скилл проверяет доступ к репо в начале сессии (если применимо)?
- [ ] При вопросе из основной зоны - даёт корректный ответ с ссылкой на источник?
- [ ] При вопросе из чужой зоны - переадресует, не пытается ответить?
- [ ] При запросе чего-то, что должно быть в обновлённой версии - реально использует это?

Если что-то отвечает не так - вернись к шагу 4 в `workflow_update.md`.
