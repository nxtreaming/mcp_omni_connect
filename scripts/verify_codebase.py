
import importlib
import pkgutil
import sys
import os
from pathlib import Path

def verify_imports():
    package_name = "omnicoreagent.community"
    package_path = Path("/home/abiorh/ai/omnirexflora-labs_dir/omnicoreagent/src/omnicoreagent/community")
    
    if not package_path.exists():
        package_path = Path("src/omnicoreagent/community")
        if not package_path.exists():
             print(f"Package path {package_path} not found")
             return

    # Add src to sys.path properly
    sys.path.insert(0, str(Path(package_path).parent.parent))

    print(f"Verifying imports for package: {package_name}")
    print(f"Path: {package_path}")

    failures = []
    successes = []

    for item in package_path.iterdir():
        if item.is_file() and item.name.endswith(".py") and item.name != "__init__.py":
            module_name = f"{package_name}.{item.stem}"
            try:
                importlib.import_module(module_name)
                successes.append(module_name)
                print(f"✅ Imported {module_name}")
            except Exception as e:
                failures.append((module_name, str(e)))
                print(f"❌ Failed to import {module_name}: {e}")

    print("\n" + "="*50)
    print(f"Total Modules: {len(successes) + len(failures)}")
    print(f"Successful: {len(successes)}")
    print(f"Failed: {len(failures)}")
    
    if failures:
        print("\nFailures:")
        for name, error in failures:
            print(f"- {name}: {error}")
        sys.exit(1)
    else:
        print("\n🎉 All community modules imported successfully!")

if __name__ == "__main__":
    verify_imports()
