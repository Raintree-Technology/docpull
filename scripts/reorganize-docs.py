#!/usr/bin/env python3
"""
Documentation Reorganization Script
Cleans up malformed directory structures and reorganizes documentation
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Tuple

class DocsReorganizer:
    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self.backup_dir = self.docs_dir.parent / 'docs_backup'
        self.changes_log = []

    def backup_docs(self):
        """Create backup before reorganization"""
        print(f"Creating backup at {self.backup_dir}...")
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        shutil.copytree(self.docs_dir, self.backup_dir)
        print("✓ Backup created")

    def find_malformed_dirs(self) -> List[Path]:
        """Find directories with URLs in their names"""
        malformed = []

        for root, dirs, files in os.walk(self.docs_dir):
            for dir_name in dirs:
                # Check for URL-like patterns
                if any(pattern in dir_name for pattern in ['http:', 'https:', 'www.', '.com', '.org']):
                    full_path = Path(root) / dir_name
                    malformed.append(full_path)

        return malformed

    def extract_logical_path(self, malformed_path: Path) -> str:
        """Extract logical path from malformed URL path"""
        path_str = str(malformed_path)

        # Remove URL components
        # Example: docs/bun/https:/bun.com/docs/runtime -> docs/bun/runtime

        # Get the part after the last domain
        if 'bun.com/docs/' in path_str:
            logical_part = path_str.split('bun.com/docs/')[-1]
            return logical_part
        elif 'plaid.com/' in path_str:
            if '/docs/' in path_str:
                logical_part = path_str.split('plaid.com/docs/')[-1]
                return logical_part
            elif '/api/' in path_str:
                logical_part = path_str.split('plaid.com/api/')[-1]
                return f"api/{logical_part}"

        # Generic: take everything after the TLD
        parts = path_str.split('/')
        clean_parts = []
        skip_next = False

        for i, part in enumerate(parts):
            if skip_next:
                skip_next = False
                continue

            # Skip URL-like parts
            if any(p in part for p in ['http:', 'https:', 'www.']):
                skip_next = True
                continue
            elif '.com' in part or '.org' in part:
                continue
            elif part and not part.startswith('.'):
                clean_parts.append(part)

        return '/'.join(clean_parts)

    def reorganize_bun_docs(self):
        """Specifically reorganize Bun documentation"""
        print("\nReorganizing Bun documentation...")

        bun_dir = self.docs_dir / 'bun'
        malformed_root = bun_dir / 'https:'

        if not malformed_root.exists():
            print("  No malformed Bun docs found")
            return

        # Find the actual docs directory
        docs_content = malformed_root / 'bun.com' / 'docs'

        if not docs_content.exists():
            print("  Bun docs structure not as expected")
            return

        # Move all subdirectories up to bun/
        for item in docs_content.iterdir():
            if item.is_dir():
                dest = bun_dir / item.name

                # If destination exists, merge contents
                if dest.exists():
                    print(f"  Merging {item.name}...")
                    for subitem in item.iterdir():
                        shutil.move(str(subitem), str(dest))
                else:
                    print(f"  Moving {item.name}...")
                    shutil.move(str(item), str(dest))

            elif item.is_file():
                # Move files directly to bun/
                dest = bun_dir / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))

        # Remove the malformed directory structure
        print("  Cleaning up malformed structure...")
        shutil.rmtree(malformed_root)

        self.changes_log.append(f"Reorganized Bun docs: removed https:/bun.com/docs structure")
        print("✓ Bun docs reorganized")

    def reorganize_plaid_docs(self):
        """Specifically reorganize Plaid documentation"""
        print("\nReorganizing Plaid documentation...")

        plaid_dir = self.docs_dir / 'plaid'

        for subdir in ['api-reference', 'guides']:
            malformed_root = plaid_dir / subdir / 'https:'

            if not malformed_root.exists():
                continue

            print(f"  Processing {subdir}...")

            # Find content
            plaid_content = malformed_root / 'plaid.com'

            if not plaid_content.exists():
                continue

            # Move all contents up
            for item in plaid_content.rglob('*'):
                if item.is_file():
                    # Calculate relative path
                    rel_path = item.relative_to(plaid_content)
                    dest = plaid_dir / subdir / rel_path

                    dest.parent.mkdir(parents=True, exist_ok=True)

                    if not dest.exists():
                        shutil.move(str(item), str(dest))

            # Remove malformed structure
            shutil.rmtree(malformed_root)

        self.changes_log.append(f"Reorganized Plaid docs: removed https: structures")
        print("✓ Plaid docs reorganized")

    def standardize_filenames(self):
        """Standardize all filenames"""
        print("\nStandardizing filenames...")

        for root, dirs, files in os.walk(self.docs_dir):
            for filename in files:
                if not filename.endswith(('.md', '.txt')):
                    continue

                old_path = Path(root) / filename

                # Clean filename
                clean_name = filename

                # Remove URL components from filename
                clean_name = re.sub(r'https?[:-]', '', clean_name)
                clean_name = re.sub(r'www\.', '', clean_name)
                clean_name = re.sub(r'\.com[-_]?', '', clean_name)
                clean_name = re.sub(r'\.org[-_]?', '', clean_name)

                # Replace multiple dashes/underscores
                clean_name = re.sub(r'[-_]+', '-', clean_name)

                # Remove leading/trailing dashes
                clean_name = clean_name.strip('-_')

                if clean_name != filename:
                    new_path = old_path.parent / clean_name

                    # Avoid conflicts
                    if new_path.exists():
                        base, ext = os.path.splitext(clean_name)
                        counter = 1
                        while new_path.exists():
                            clean_name = f"{base}-{counter}{ext}"
                            new_path = old_path.parent / clean_name
                            counter += 1

                    shutil.move(str(old_path), str(new_path))
                    self.changes_log.append(f"Renamed: {old_path.name} -> {clean_name}")

        print("✓ Filenames standardized")

    def create_directory_index(self):
        """Create an index of all documentation"""
        print("\nCreating documentation index...")

        index = {}

        for project_dir in self.docs_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name.startswith('.'):
                continue

            project_name = project_dir.name
            index[project_name] = {
                'path': str(project_dir.relative_to(self.docs_dir.parent)),
                'categories': {},
                'file_count': 0
            }

            # Count files and categorize
            for root, dirs, files in os.walk(project_dir):
                root_path = Path(root)
                category = root_path.relative_to(project_dir).parts[0] if root_path != project_dir else 'root'

                if category not in index[project_name]['categories']:
                    index[project_name]['categories'][category] = 0

                doc_files = [f for f in files if f.endswith(('.md', '.txt'))]
                index[project_name]['categories'][category] += len(doc_files)
                index[project_name]['file_count'] += len(doc_files)

        # Write index file
        index_file = self.docs_dir / 'INDEX.md'

        with open(index_file, 'w') as f:
            f.write('# Documentation Index\n\n')
            f.write(f'Last updated: {self.get_timestamp()}\n\n')

            for project, info in sorted(index.items()):
                f.write(f'## {project.title()}\n\n')
                f.write(f'- **Location:** `{info["path"]}`\n')
                f.write(f'- **Total Files:** {info["file_count"]}\n')
                f.write(f'- **Categories:**\n')

                for category, count in sorted(info['categories'].items()):
                    if count > 0:
                        f.write(f'  - {category}: {count} files\n')

                f.write('\n')

        print(f"✓ Index created at {index_file}")

    def create_structure_summary(self):
        """Create a visual summary of the documentation structure"""
        print("\nCreating structure summary...")

        summary_file = self.docs_dir / 'STRUCTURE.txt'

        with open(summary_file, 'w') as f:
            f.write('Documentation Structure\n')
            f.write('=' * 80 + '\n\n')

            for project_dir in sorted(self.docs_dir.iterdir()):
                if not project_dir.is_dir() or project_dir.name.startswith('.'):
                    continue

                f.write(f'{project_dir.name}/\n')

                # Show first 2 levels
                for item in sorted(project_dir.iterdir()):
                    if item.is_dir():
                        f.write(f'├── {item.name}/\n')

                        for subitem in sorted(item.iterdir())[:5]:
                            if subitem.is_dir():
                                f.write(f'│   ├── {subitem.name}/\n')
                            else:
                                f.write(f'│   └── {subitem.name}\n')

                        if len(list(item.iterdir())) > 5:
                            f.write(f'│   └── ... ({len(list(item.iterdir())) - 5} more)\n')

                f.write('\n')

        print(f"✓ Structure summary created at {summary_file}")

    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def save_changes_log(self):
        """Save the changes log"""
        log_file = self.docs_dir / 'REORGANIZATION_LOG.txt'

        with open(log_file, 'w') as f:
            f.write('Documentation Reorganization Log\n')
            f.write('=' * 80 + '\n\n')
            f.write(f'Timestamp: {self.get_timestamp()}\n\n')
            f.write(f'Total changes: {len(self.changes_log)}\n\n')

            for change in self.changes_log:
                f.write(f'- {change}\n')

        print(f"\n✓ Changes log saved at {log_file}")

    def run(self):
        """Execute full reorganization"""
        print("Documentation Reorganization")
        print("=" * 80)

        # Backup first
        self.backup_docs()

        # Reorganize specific projects
        self.reorganize_bun_docs()
        self.reorganize_plaid_docs()

        # Standardize all filenames
        self.standardize_filenames()

        # Create documentation
        self.create_directory_index()
        self.create_structure_summary()

        # Save log
        self.save_changes_log()

        print("\n" + "=" * 80)
        print(f"✓ REORGANIZATION COMPLETE")
        print(f"  - Backup: {self.backup_dir}")
        print(f"  - Changes: {len(self.changes_log)}")
        print(f"  - Index: {self.docs_dir / 'INDEX.md'}")
        print(f"  - Structure: {self.docs_dir / 'STRUCTURE.txt'}")
        print("=" * 80)

def main():
    docs_dir = Path(__file__).parent.parent / 'docs'

    reorganizer = DocsReorganizer(str(docs_dir))
    reorganizer.run()

if __name__ == '__main__':
    main()
