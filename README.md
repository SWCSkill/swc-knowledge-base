# swc-skill-toolkit

Инструментарий для создания и поддержки корпоративных скиллов SWC.

## Хочу установить скилл

Постоянная ссылка на актуальную версию:

**https://github.com/SWCSkill/swc-skill-toolkit/releases/latest/download/swc-skill-toolkit.skill**

Подробная инструкция: [INSTALL.md](./INSTALL.md).

## Что делает

Помогает сотрудникам SWC:
- **Создавать новые корпоративные скиллы** по единой архитектуре
- **Администрировать существующие** скиллы (обновлять контент и поведение)
- **Находить архитектурные отклонения** и исправлять их вместе с автором скилла

Toolkit работает в Claude.ai. Ведёт сотрудника по сценарию через серию коротких диалогов, в конце отдаёт zip-архив с готовыми файлами для заливки на GitHub.

## Что внутри репо

```
swc-skill-toolkit/
├── skeleton/                        ← заготовки нового скилла
│   ├── SKILL.md.template.example
│   ├── build_skill.py
│   ├── build-skill.yml
│   ├── README.md.example
│   ├── INSTALL.md.example
│   ├── CHANGELOG.md.example
│   └── VERSION.example
│
├── skill-template/
│   └── SKILL.md.template            ← поведение toolkit'а
├── skill-references/
│   ├── INDEX.md                     ← карта референсов
│   ├── architecture.md              ← принципы архитектуры скиллов
│   ├── conventions.md               ← конкретные правила
│   ├── workflow_create.md           ← гид CREATE
│   ├── workflow_update.md           ← гид UPDATE
│   ├── changelog_style.md           ← правила CHANGELOG
│   └── checklists.md                ← чек-листы валидации
│
├── scripts/
│   └── build_skill.py               ← сборка .skill (универсальный)
├── .github/workflows/
│   └── build-skill.yml              ← автосборка релиза
│
├── VERSION
├── CHANGELOG.md
├── INSTALL.md
└── README.md
```

## Карта экосистемы

| Скилл | Зона | Репо | Стадия |
| :--- | :--- | :--- | :--- |
| swc-assistant | Продукты, бренд, партнёрка SWC | https://github.com/SWCSkill/swc-knowledge-base | Готов |
| swc-manajet-expert | Работа в системе ManaJet | https://github.com/SWCSkill/manajet-knowledge-base | Готов (архитектурный эталон) |
| swc-orgpolicies-guru | Орг.политика и регламенты SWC | https://github.com/SWCSkill/swc-orgpolicies-guru | В разработке |
| manajet-api-helper | Интеграции с ManaJet через API | https://github.com/SWCSkill/manajet-api-helper | В разработке |
| **swc-skill-toolkit** | **Инструментарий для разработки** | **этот репо** | **Готов** |

## Кому это полезно

Сотрудники SWC, которые:
- Хотят создать корпоративный скилл, помогающий их отделу или команде
- Администрируют существующий скилл и нужно его обновить
- Только начинают разбираться с тем, как устроены скиллы SWC
- Хотят понять «почему именно так устроено» и «как у нас правильно»

## Принцип работы

Сотрудник в Claude.ai активирует toolkit, описывает свою задачу. Toolkit задаёт уточняющие вопросы, помогает спроектировать архитектуру скилла или внести изменение, в конце генерирует zip-архив. Сотрудник руками заливает архив в свой репо на GitHub - дальше Action делает остальное (собирает release, обновляет постоянную ссылку).

Toolkit **не имеет прямого доступа к GitHub** - он только читает публичные файлы через curl. Все правки через сотрудника.

## Архитектурные принципы

См. [skill-references/architecture.md](./skill-references/architecture.md).

Краткие тезисы:
1. Контент в репо, поведение в скилле
2. Один источник правды по каждому факту
3. Слой меты для навигации
4. Слоты под рост заранее
5. Гарантированный канал распространения через постоянную ссылку
6. Переадресация, не подмена

## Конвенции

См. [skill-references/conventions.md](./skill-references/conventions.md).

## Источник архитектуры

Все архитектурные решения отлажены на скилле `swc-manajet-expert` (https://github.com/SWCSkill/manajet-knowledge-base). Этот скилл - эталон, на который следует ориентироваться при сомнениях.

## Лицензия

Внутренний инструмент SWC. Использование за пределами SWCSkill не предполагается.
