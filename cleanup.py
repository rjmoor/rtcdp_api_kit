# cleanup_manager.py

import os
import shutil
import subprocess
import argparse

class CleanUpManager:
    def __init__(self, root_path='.'):
        self.root_path = root_path

    def remove_pycache_dirs(self):
        print("🚀 Removing all __pycache__ directories...")
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            for dirname in dirnames:
                if dirname == "__pycache__":
                    full_path = os.path.join(dirpath, dirname)
                    shutil.rmtree(full_path)
                    print(f"🗑️ Deleted: {full_path}")

    def ensure_init_files(self):
        print("🚀 Ensuring __init__.py files exist...")
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            if any(part.startswith('.') for part in dirpath.split(os.sep)):
                continue
            if "__init__.py" not in filenames:
                init_file = os.path.join(dirpath, "__init__.py")
                open(init_file, 'a').close()
                print(f"➕ Created missing __init__.py in: {dirpath}")

    def move_or_rename_files(self, old_path, new_path):
        print(f"🚚 Moving {old_path} to {new_path}...")
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"✅ Moved {old_path} to {new_path}")
        else:
            print(f"❌ Source path not found: {old_path}")

    def slice_large_file(self, file_path, max_lines=1000):
        print(f"✂️ Slicing {file_path} to {max_lines} lines...")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
            with open(file_path, 'w') as f:
                f.writelines(lines[:max_lines])
            print(f"✅ Sliced {file_path} to {max_lines} lines")
        else:
            print(f"❌ File not found: {file_path}")

    def lint_with_black(self):
        print("🧹 Linting Python files with black...")
        try:
            subprocess.run(["black", self.root_path], check=True)
            print("✅ Linting complete!")
        except Exception as e:
            print(f"❌ Linting failed: {e}")

    def run_full_cleanup(self):
        self.remove_pycache_dirs()
        self.ensure_init_files()

def parse_arguments():
    parser = argparse.ArgumentParser(description="🧹 CleanUp Manager for rtcdp_api_kit Project")
    parser.add_argument('--root', type=str, default='rtcdp', help='Root directory to clean')
    parser.add_argument('--remove-pycache', action='store_true', help='Remove all __pycache__ directories')
    parser.add_argument('--ensure-init', action='store_true', help='Ensure __init__.py exists in all packages')
    parser.add_argument('--move', nargs=2, metavar=('OLD_PATH', 'NEW_PATH'), help='Move or rename a file or folder')
    parser.add_argument('--slice', nargs=2, metavar=('FILE_PATH', 'MAX_LINES'), help='Slice a file to max lines')
    parser.add_argument('--lint', action='store_true', help='Lint project with black')
    parser.add_argument('--full-clean', action='store_true', help='Run full cleanup (remove pycache + ensure init)')
    return parser.parse_args()

def main():
    args = parse_arguments()
    manager = CleanUpManager(root_path=args.root)

    if args.remove_pycache:
        manager.remove_pycache_dirs()
    if args.ensure_init:
        manager.ensure_init_files()
    if args.move:
        old_path, new_path = args.move
        manager.move_or_rename_files(old_path, new_path)
    if args.slice:
        file_path, max_lines = args.slice
        manager.slice_large_file(file_path, int(max_lines))
    if args.lint:
        manager.lint_with_black()
    if args.full_clean:
        manager.run_full_cleanup()

if __name__ == "__main__":
    main()
