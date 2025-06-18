#!/usr/bin/env python3
"""
Comprehensive integration script for ManzAI Studio.

This script consolidates duplicate implementations:
1. Models: src/models/ -> src/backend/app/models/
2. Utils: src/utils/ -> src/backend/app/utils/
3. Templates: src/backend/app/templates/ -> src/backend/app/templates/

It also creates backward compatibility modules to prevent import errors.
"""

import filecmp
import logging
import os
import re
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("integration")

# Project directories
PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"

# Directories to integrate
DIRS_TO_INTEGRATE = [
    {
        "src": SRC_DIR / "models",
        "dst": SRC_DIR / "backend" / "app" / "models",
        "import_pattern": r"from src.backend.app.models.",
        "new_import": r"from src.backend.app.models.",
    },
    {
        "src": SRC_DIR / "utils",
        "dst": SRC_DIR / "backend" / "app" / "utils",
        "import_pattern": r"from src.backend.app.utils.",
        "new_import": r"from src.backend.app.utils.",
    },
    {
        "src": SRC_DIR / "templates",
        "dst": SRC_DIR / "backend" / "app" / "templates",
        "path_pattern": "src/backend/app/templates/",
        "new_path": "src/backend/app/templates/",
    },
]


def check_files_identical(file1, file2):
    """Check if two files are identical"""
    if not file1.exists() or not file2.exists():
        return False

    return filecmp.cmp(file1, file2)


def find_references(directory, pattern):
    """Find all references to a specific pattern in the codebase"""
    references = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if isinstance(pattern, str) and pattern in content:
                            references.append(file_path)
                        elif isinstance(pattern, re.Pattern) and pattern.search(content):
                            references.append(file_path)
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")

    return references


def update_references(file_path, old_pattern, new_pattern) -> bool | None:
    """Update references in a file from old pattern to new pattern"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update references
        if isinstance(old_pattern, str) and isinstance(new_pattern, str):
            updated_content = content.replace(old_pattern, new_pattern)
        else:
            updated_content = re.sub(old_pattern, new_pattern, content)

        if content != updated_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return True

        return False
    except Exception as e:
        logger.error(f"Error updating references in {file_path}: {e}")
        return False


def create_backward_compatibility_module(src_dir, dst_dir) -> None:
    """Create a backward compatibility module that imports from the new location"""
    # Create __init__.py with imports
    init_content = (
        '"""Backward compatibility module. Imports maintain compatibility with old imports."""\n\n'
    )

    # Get all Python modules in the destination directory
    dst_modules = [f.stem for f in dst_dir.glob("*.py") if f.name != "__init__.py"]

    for module in dst_modules:
        init_content += f"from src.backend.app.{dst_dir.name}.{module} import *\n"

    # Write the init file
    init_path = src_dir / "__init__.py"
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(init_content)

    logger.info(f"Created backward compatibility module in {init_path}")


def integrate_directory(src_dir, dst_dir) -> None:
    """Integrate files from src_dir into dst_dir"""
    if not src_dir.exists():
        logger.warning(f"Source directory {src_dir} does not exist. Skipping.")
        return

    # Create destination directory if it doesn't exist
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Get all files in source directory
    src_files = list(src_dir.glob("**/*"))
    logger.info(f"Found {len(src_files)} files in {src_dir}")

    for src_file in src_files:
        if src_file.is_file():
            # Determine the relative path from src_dir
            rel_path = src_file.relative_to(src_dir)
            dst_file = dst_dir / rel_path

            # Create parent directories if they don't exist
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # If the file already exists in the dest dir, check if it's identical
            if dst_file.exists():
                if check_files_identical(src_file, dst_file):
                    logger.info(f"Files {rel_path} are identical in both locations")
                else:
                    logger.warning(
                        f"Files {rel_path} differ between locations. Manual review needed."
                    )
            else:
                logger.info(f"Copying {rel_path} to {dst_file}")
                shutil.copy2(src_file, dst_file)


def main() -> None:
    """Main integration process"""
    # Process each directory to integrate
    for dir_info in DIRS_TO_INTEGRATE:
        src_dir = dir_info["src"]
        dst_dir = dir_info["dst"]

        logger.info(f"Integrating {src_dir} into {dst_dir}")

        # 1. Integrate files
        integrate_directory(src_dir, dst_dir)

        # 2. Find and update references
        if "import_pattern" in dir_info and "new_import" in dir_info:
            old_pattern = dir_info["import_pattern"]
            new_pattern = dir_info["new_import"]

            references = find_references(PROJECT_ROOT, old_pattern)
            logger.info(f"Found {len(references)} files with references to {old_pattern}")

            update_count = 0
            for ref in references:
                if update_references(ref, old_pattern, new_pattern):
                    update_count += 1
                    logger.info(f"Updated references in {ref}")

            logger.info(f"Updated references in {update_count} files")

        elif "path_pattern" in dir_info and "new_path" in dir_info:
            old_pattern = dir_info["path_pattern"]
            new_pattern = dir_info["new_path"]

            references = find_references(PROJECT_ROOT, old_pattern)
            logger.info(f"Found {len(references)} files with references to {old_pattern}")

            update_count = 0
            for ref in references:
                if update_references(ref, old_pattern, new_pattern):
                    update_count += 1
                    logger.info(f"Updated references in {ref}")

            logger.info(f"Updated references in {update_count} files")

        # 3. Create backward compatibility
        if src_dir.name in ["models", "utils"]:
            create_backward_compatibility_module(src_dir, dst_dir)

    logger.info("Integration complete")


if __name__ == "__main__":
    main()
