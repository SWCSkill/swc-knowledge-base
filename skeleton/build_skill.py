#!/usr/bin/env python3
"""
build_skill.py - собирает .skill-файл из содержимого репозитория.

Универсальный скрипт для всех скиллов SWC. Работает с любым репо,
устроенным по архитектуре SWC-скиллов.

Алгоритм:
1. Читает VERSION для текущей версии скилла.
2. Рендерит SKILL.md из шаблона skill-template/SKILL.md.template
   (подставляет {{VERSION}} и {{BUILD_DATE}}).
3. Копирует skill-references/* в references/ внутри пакета.
4. Пакует в ZIP с расширением .skill, корневая папка пакета берётся
   из поля `name` YAML frontmatter в SKILL.md.
5. Валидирует YAML frontmatter.

Использование:
    python scripts/build_skill.py --output dist/<skill-name>.skill
    python scripts/build_skill.py --version 1.3.0  # переопределить версию
"""

import argparse
import datetime
import re
import shutil
import sys
import zipfile
from pathlib import Path


def render_skill_md(repo_root: Path, version: str, build_date: str) -> str:
    """Рендерит итоговый SKILL.md из шаблона, подставляя переменные."""
    template_path = repo_root / "skill-template" / "SKILL.md.template"
    if not template_path.exists():
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    return (template
            .replace("{{VERSION}}", version)
            .replace("{{BUILD_DATE}}", build_date))


def extract_skill_name(skill_md: str) -> str:
    """Достаёт значение поля `name` из YAML frontmatter в SKILL.md."""
    if not skill_md.startswith("---\n"):
        raise ValueError("SKILL.md не начинается с YAML-frontmatter")
    parts = skill_md.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("YAML-frontmatter не закрыт (---)")
    frontmatter = parts[1]
    match = re.search(r"^name:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
    if not match:
        raise ValueError("В YAML-frontmatter не найдено поле name")
    return match.group(1)


def build_skill_dir(repo_root: Path, version: str, build_date: str, skill_name: str) -> Path:
    """Собирает папку <skill-name>/ со всем содержимым."""
    build_dir = repo_root / "build" / skill_name

    # Чистим прошлую сборку
    if build_dir.parent.exists():
        shutil.rmtree(build_dir.parent)
    build_dir.mkdir(parents=True)

    # 1. Рендерим SKILL.md из шаблона
    skill_md = render_skill_md(repo_root, version, build_date)
    (build_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    print(f"✓ SKILL.md (версия {version}, дата сборки {build_date})")

    # 2. Копируем skill-references/* в references/
    refs_src = repo_root / "skill-references"
    refs_dst = build_dir / "references"
    refs_dst.mkdir()

    if not refs_src.exists():
        raise FileNotFoundError(f"Папка skill-references/ не найдена: {refs_src}")

    for src_file in sorted(refs_src.glob("*.md")):
        dst_file = refs_dst / src_file.name
        shutil.copy2(src_file, dst_file)
        print(f"✓ references/{src_file.name}")

    return build_dir


def pack_skill(build_dir: Path, output_path: Path) -> None:
    """Пакует папку в .skill (ZIP-архив)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(build_dir.rglob("*")):
            if file_path.is_file():
                # Архивируем относительно родителя build_dir, чтобы папка
                # <skill-name>/ была корнем внутри архива
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
    parser.add_argument("--output", default=None,
                        help="Output .skill path (по умолчанию: dist/<skill-name>.skill)")
    parser.add_argument("--version", default=None,
                        help="Version override (default: read from VERSION file)")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()

    # Определяем версию
    if args.version:
        version = args.version
    else:
        version_file = repo_root / "VERSION"
        if not version_file.exists():
            print(f"❌ Файл VERSION не найден: {version_file}", file=sys.stderr)
            return 1
        version = version_file.read_text(encoding="utf-8").strip()

    build_date = datetime.date.today().isoformat()

    # Достаём имя скилла из YAML, чтобы не хардкодить
    template_path = repo_root / "skill-template" / "SKILL.md.template"
    if not template_path.exists():
        print(f"❌ Шаблон не найден: {template_path}", file=sys.stderr)
        return 1
    template_content = template_path.read_text(encoding="utf-8")
    try:
        skill_name = extract_skill_name(template_content)
    except ValueError as e:
        print(f"❌ Не удалось определить имя скилла из YAML: {e}", file=sys.stderr)
        return 1

    # Output path - если не задан, формируем по имени скилла
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = (repo_root / "dist" / f"{skill_name}.skill").resolve()

    print(f"🔨 Сборка {skill_name} v{version} (build date: {build_date})")
    print(f"   Репозиторий: {repo_root}")
    print(f"   Выход: {output_path}\n")

    try:
        build_dir = build_skill_dir(repo_root, version, build_date, skill_name)
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
