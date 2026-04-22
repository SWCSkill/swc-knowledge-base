#!/usr/bin/env python3
"""
build_skill.py - Собирает .skill-файл из содержимого репозитория.

Алгоритм:
1. Читает VERSION для текущей версии навыка
2. Копирует файлы из core/ в references/ (с префиксами для сохранения порядка)
3. Рендерит SKILL.md из шаблона skill-template/SKILL.md.template
4. Пакует всё в ZIP с расширением .skill
5. Валидирует результат

Использование (локально):
    python scripts/build_skill.py --output dist/swc-assistant.skill

В GitHub Actions - вызывается из workflow.
"""

import argparse
import datetime
import shutil
import sys
import zipfile
from pathlib import Path

# Маппинг файлов из core/ репозитория в references/ навыка
# Нумерация сохраняет логический порядок как в v1 навыка
CORE_TO_REFERENCES = {
    "ecosystem.md": "01-ecosystem.md",
    "swc-pass.md": "02-swc-pass.md",
    "swc-field.md": "03-swc-field.md",
    "road-to-1m.md": "04-road-to-1m.md",
    "partner-program.md": "07-partner-program.md",
    "brand-voice.md": "08-brand-voice.md",
    "visual-style.md": "09-visual-style.md",
    "legal-disclaimers.md": "11-legal-disclaimers.md",
}

# Проекты витрины из projects/ - собираем в один файл 05-06
PROJECT_FILES = ["atlas.md", "smart.md", "cryptadium.md"]

# FAQ из faq/ - собираем в единый 10-master-faq.md
FAQ_FILES = ["general.md", "swc-pass.md", "swc-field.md", "road-to-1m.md", "atlas.md"]


def read_file(path: Path) -> str:
    """Читает файл, возвращает пустую строку если файл отсутствует."""
    if not path.exists():
        print(f"⚠️  Файл не найден: {path}", file=sys.stderr)
        return ""
    return path.read_text(encoding="utf-8")


def render_skill_md(repo_root: Path, version: str, build_date: str) -> str:
    """Рендерит итоговый SKILL.md из шаблона, подставляя переменные."""
    template_path = repo_root / "skill-template" / "SKILL.md.template"
    template = read_file(template_path)
    return (template
            .replace("{{VERSION}}", version)
            .replace("{{BUILD_DATE}}", build_date))


def build_references(repo_root: Path, output_dir: Path) -> None:
    """Собирает папку references/ из core/, projects/, faq/ репозитория."""
    refs = output_dir / "references"
    refs.mkdir(parents=True, exist_ok=True)

    # 1. Copy core files
    for src_name, dst_name in CORE_TO_REFERENCES.items():
        src = repo_root / "core" / src_name
        dst = refs / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ core/{src_name} → references/{dst_name}")
        else:
            print(f"  ⚠️  Пропущено: core/{src_name} не найден")

    # 2. Build 05-atlas.md (full project) and 06-smart-cryptadium.md (joined)
    atlas_content = read_file(repo_root / "projects" / "atlas.md")
    if atlas_content:
        (refs / "05-atlas.md").write_text(atlas_content, encoding="utf-8")
        print(f"  ✓ projects/atlas.md → references/05-atlas.md")

    smart_content = read_file(repo_root / "projects" / "smart.md")
    crypt_content = read_file(repo_root / "projects" / "cryptadium.md")
    if smart_content or crypt_content:
        combined = "# SMART и Cryptadium\n\n"
        if smart_content:
            combined += "## SMART\n\n" + smart_content + "\n\n"
        if crypt_content:
            combined += "## Cryptadium\n\n" + crypt_content + "\n"
        (refs / "06-smart-cryptadium.md").write_text(combined, encoding="utf-8")
        print(f"  ✓ projects/{{smart,cryptadium}}.md → references/06-smart-cryptadium.md")

    # 3. Build 10-master-faq.md from all faq/ files
    faq_combined = "# Master FAQ SWC\n\n"
    faq_combined += "Ответы на типовые вопросы партнёров.\n\n"
    for faq_name in FAQ_FILES:
        content = read_file(repo_root / "faq" / faq_name)
        if content:
            # Remove top-level heading if present - we add our own structure
            lines = content.split("\n")
            if lines and lines[0].startswith("# "):
                content = "\n".join(lines[1:]).strip()
            faq_combined += f"\n---\n\n{content}\n\n"
    (refs / "10-master-faq.md").write_text(faq_combined, encoding="utf-8")
    print(f"  ✓ faq/*.md → references/10-master-faq.md")


def build_skill_dir(repo_root: Path, version: str, build_date: str) -> Path:
    """Собирает папку swc-assistant/ со всем содержимым."""
    build_dir = repo_root / "build" / "swc-assistant"

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


def pack_skill(build_dir: Path, output_path: Path) -> None:
    """Пакует папку в .skill (zip-архив)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(build_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir.parent)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    size_kb = output_path.stat().st_size / 1024
    print(f"\n✅ Готово: {output_path} ({size_kb:.1f} KB)")


def validate_yaml(build_dir: Path) -> bool:
    """Быстрая проверка YAML-frontmatter в SKILL.md."""
    skill_md = (build_dir / "SKILL.md").read_text(encoding="utf-8")
    if not skill_md.startswith("---\n"):
        print("❌ SKILL.md не начинается с YAML-frontmatter", file=sys.stderr)
        return False
    parts = skill_md.split("---\n", 2)
    if len(parts) < 3:
        print("❌ YAML-frontmatter не закрыт", file=sys.stderr)
        return False
    try:
        import yaml  # type: ignore
        frontmatter = yaml.safe_load(parts[1])
        if not isinstance(frontmatter, dict) or "name" not in frontmatter or "description" not in frontmatter:
            print("❌ YAML не содержит обязательных полей name/description", file=sys.stderr)
            return False
        print(f"✓ YAML валидный, name='{frontmatter['name']}'")
    except ImportError:
        print("ℹ️  PyYAML не установлен - пропускаю строгую валидацию YAML")
    except Exception as e:
        print(f"❌ Ошибка парсинга YAML: {e}", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build .skill file from repository content")
    parser.add_argument("--repo", default=".", help="Path to repository root")
    parser.add_argument("--output", default="dist/swc-assistant.skill", help="Output .skill path")
    parser.add_argument("--version", default=None, help="Version override (default: read from VERSION file)")
    args = parser.parse_args()

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


if __name__ == "__main__":
    sys.exit(main())
