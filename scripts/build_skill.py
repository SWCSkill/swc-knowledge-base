#!/usr/bin/env python3
“””
build_skill.py - Собирает .skill-файл из содержимого репозитория.

Алгоритм:

1. Читает VERSION для текущей версии навыка
1. Копирует файлы из core/ в references/ (с префиксами для сохранения порядка)
1. Рендерит SKILL.md из шаблона skill-template/SKILL.md.template
1. Пакует всё в ZIP с расширением .skill
1. Валидирует результат

Использование (локально):
python scripts/build_skill.py –output dist/swc-assistant.skill

В GitHub Actions - вызывается из workflow.
“””

import argparse
import datetime
import shutil
import sys
import zipfile
from pathlib import Path

# Маппинг файлов из core/ репозитория в references/ навыка

# Нумерация сохраняет логический порядок как в v1 навыка

CORE_TO_REFERENCES = {
“ecosystem.md”: “01-ecosystem.md”,
“swc-pass.md”: “02-swc-pass.md”,
“swc-field.md”: “03-swc-field.md”,
“road-to-1m.md”: “04-road-to-1m.md”,
“partner-program.md”: “07-partner-program.md”,
“brand-voice.md”: “08-brand-voice.md”,
“visual-style.md”: “09-visual-style.md”,
“legal-disclaimers.md”: “11-legal-disclaimers.md”,
}

# Проекты витрины из projects/ - собираем в один файл 05-06

PROJECT_FILES = [“atlas.md”, “smart.md”, “cryptadium.md”]

# FAQ из faq/ - собираем в единый 10-master-faq.md

FAQ_FILES = [“general.md”, “swc-pass.md”, “swc-field.md”, “road-to-1m.md”, “atlas.md”]

def read_file(path: Path) -> str:
“”“Читает файл, возвращает пустую строку если файл отсутствует.”””
if not path.exists():
print(f”⚠️  Файл не найден: {path}”, file=sys.stderr)
return “”
return path.read_text(encoding=“utf-8”)

def clean_artifacts(content: str) -> str:
“””
Удаляет артефакты, характерные для файлов из репозитория, но бесполезные
(или мешающие) в собранном .skill. Сохраняет полезный контент нетронутым.

```
Что удаляется:
1. Внутренние ссылки вида `core/<n>.md`, `faq/<n>.md`, `projects/<n>.md` -
   заменяются на просто `<n>.md` или убираются целиком
2. Служебные хвосты в конце файла: блоки со "Статус:", "Последнее обновление:"
   которые идут после финального --- разделителя
"""
import re

# 1. Убираем ссылки на внутренние пути репо
# "Подробнее в `core/09-visual-style.md`." - убираем целиком фразы типа этого
content = re.sub(
    r"\.\s*Подробнее в `(core|faq|projects|updates)/[^`]+`\.",
    ".",
    content,
)
# Мягче: если где-то остались ссылки типа `core/X.md` сами по себе,
# превращаем в просто `X.md` (как он лежит в навыке)
content = re.sub(r"`(core|faq|projects|updates)/([^`]+\.md)`", r"`\2`", content)

# 2. Режем хвосты метаданных в самом конце файла
# Ищем последний блок, начинающийся с --- и содержащий "Последнее обновление"
# или "Статус:" - и обрезаем его
lines = content.rstrip().split("\n")

# Идём с конца: если последняя не-пустая строка с метаданными -
# срезаем до ближайшего --- перед ней
footer_markers = ("**Последнее обновление:**", "**Статус:**", "Последнее обновление:", "Статус:")

# Найти позицию последнего --- разделителя
last_hr_idx = -1
for i in range(len(lines) - 1, -1, -1):
    if lines[i].strip() == "---":
        last_hr_idx = i
        break

if last_hr_idx >= 0:
    # Проверяем, что после --- идут только метаданные
    after_hr = "\n".join(lines[last_hr_idx + 1:]).strip()
    is_metadata_only = after_hr and all(
        not line.strip() or any(marker in line for marker in footer_markers)
        for line in after_hr.split("\n")
    )
    if is_metadata_only:
        # Отрезаем --- и всё после него
        lines = lines[:last_hr_idx]

# Убираем лишние пустые строки в конце
while lines and not lines[-1].strip():
    lines.pop()

return "\n".join(lines) + "\n"
```

def render_skill_md(repo_root: Path, version: str, build_date: str) -> str:
“”“Рендерит итоговый SKILL.md из шаблона, подставляя переменные.”””
template_path = repo_root / “skill-template” / “SKILL.md.template”
template = read_file(template_path)
return (template
.replace(”{{VERSION}}”, version)
.replace(”{{BUILD_DATE}}”, build_date))

def build_references(repo_root: Path, output_dir: Path) -> None:
“”“Собирает папку references/ из core/, projects/, faq/ репозитория.”””
refs = output_dir / “references”
refs.mkdir(parents=True, exist_ok=True)

```
# 1. Copy core files (с очисткой артефактов)
for src_name, dst_name in CORE_TO_REFERENCES.items():
    src = repo_root / "core" / src_name
    dst = refs / dst_name
    if src.exists():
        content = clean_artifacts(read_file(src))
        dst.write_text(content, encoding="utf-8")
        print(f"  ✓ core/{src_name} → references/{dst_name}")
    else:
        print(f"  ⚠️  Пропущено: core/{src_name} не найден")

# 2. Build 05-atlas.md (full project) and 06-smart-cryptadium.md (joined)
atlas_content = clean_artifacts(read_file(repo_root / "projects" / "atlas.md"))
if atlas_content.strip():
    (refs / "05-atlas.md").write_text(atlas_content, encoding="utf-8")
    print(f"  ✓ projects/atlas.md → references/05-atlas.md")

smart_content = clean_artifacts(read_file(repo_root / "projects" / "smart.md"))
crypt_content = clean_artifacts(read_file(repo_root / "projects" / "cryptadium.md"))
if smart_content.strip() or crypt_content.strip():
    combined = "# SMART и Cryptadium\n\n"
    if smart_content.strip():
        combined += "## SMART\n\n" + smart_content + "\n\n"
    if crypt_content.strip():
        combined += "## Cryptadium\n\n" + crypt_content + "\n"
    (refs / "06-smart-cryptadium.md").write_text(combined, encoding="utf-8")
    print(f"  ✓ projects/{{smart,cryptadium}}.md → references/06-smart-cryptadium.md")

# 3. Build 10-master-faq.md from all faq/ files
faq_combined = "# Master FAQ SWC\n\n"
faq_combined += "Ответы на типовые вопросы партнёров.\n\n"
for faq_name in FAQ_FILES:
    content = clean_artifacts(read_file(repo_root / "faq" / faq_name))
    if content.strip():
        # Remove top-level heading if present - we add our own structure
        lines = content.split("\n")
        if lines and lines[0].startswith("# "):
            content = "\n".join(lines[1:]).strip()
        faq_combined += f"\n---\n\n{content}\n\n"
(refs / "10-master-faq.md").write_text(faq_combined, encoding="utf-8")
print(f"  ✓ faq/*.md → references/10-master-faq.md")
```

def build_skill_dir(repo_root: Path, version: str, build_date: str) -> Path:
“”“Собирает папку swc-assistant/ со всем содержимым.”””
build_dir = repo_root / “build” / “swc-assistant”

```
# Clean previous build
if build_dir.parent.exists():
    shutil.rmtree(build_dir.parent)
build_dir.mkdir(parents=True)

# 1. Render SKILL.md
skill_md = render_skill_md(repo_root, version, build_date)
(build_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
print(f"✓ Создан SKILL.md (версия {version})")

# 2. Build references/
print("✓ Собираю references/:")
build_references(repo_root, build_dir)

# 3. Empty assets/ for future use
(build_dir / "assets").mkdir(exist_ok=True)

return build_dir
```

def pack_skill(build_dir: Path, output_path: Path) -> None:
“”“Пакует папку в .skill (zip-архив).”””
output_path.parent.mkdir(parents=True, exist_ok=True)
if output_path.exists():
output_path.unlink()

```
with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for file_path in sorted(build_dir.rglob("*")):
        if file_path.is_file():
            arcname = file_path.relative_to(build_dir.parent)
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

size_kb = output_path.stat().st_size / 1024
print(f"\n✅ Готово: {output_path} ({size_kb:.1f} KB)")
```

def validate_yaml(build_dir: Path) -> bool:
“”“Быстрая проверка YAML-frontmatter в SKILL.md.”””
skill_md = (build_dir / “SKILL.md”).read_text(encoding=“utf-8”)
if not skill_md.startswith(”—\n”):
print(“❌ SKILL.md не начинается с YAML-frontmatter”, file=sys.stderr)
return False
parts = skill_md.split(”—\n”, 2)
if len(parts) < 3:
print(“❌ YAML-frontmatter не закрыт”, file=sys.stderr)
return False
try:
import yaml  # type: ignore
frontmatter = yaml.safe_load(parts[1])
if not isinstance(frontmatter, dict) or “name” not in frontmatter or “description” not in frontmatter:
print(“❌ YAML не содержит обязательных полей name/description”, file=sys.stderr)
return False
print(f”✓ YAML валидный, name=’{frontmatter[‘name’]}’”)
except ImportError:
print(“ℹ️  PyYAML не установлен - пропускаю строгую валидацию YAML”)
except Exception as e:
print(f”❌ Ошибка парсинга YAML: {e}”, file=sys.stderr)
return False
return True

def main() -> int:
parser = argparse.ArgumentParser(description=“Build .skill file from repository content”)
parser.add_argument(”–repo”, default=”.”, help=“Path to repository root”)
parser.add_argument(”–output”, default=“dist/swc-assistant.skill”, help=“Output .skill path”)
parser.add_argument(”–version”, default=None, help=“Version override (default: read from VERSION file)”)
args = parser.parse_args()

```
repo_root = Path(args.repo).resolve()
output_path = Path(args.output).resolve()

# Determine version
if args.version:
    version = args.version
else:
    version_file = repo_root / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "0.0.0"

build_date = datetime.date.today().isoformat()

print(f"🔨 Сборка swc-assistant v{version} (build date: {build_date})")
print(f"   Репозиторий: {repo_root}")
print(f"   Выход: {output_path}\n")

try:
    build_dir = build_skill_dir(repo_root, version, build_date)
    if not validate_yaml(build_dir):
        return 1
    pack_skill(build_dir, output_path)
    return 0
except Exception as e:
    print(f"\n❌ Ошибка сборки: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    return 1
```

if **name** == “**main**”:
sys.exit(main())
