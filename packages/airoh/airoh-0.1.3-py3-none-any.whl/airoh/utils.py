# src/airoh/utils.py
import os
import shutil
from pathlib import Path
from invoke import task

@task
def setup_env_python(c, reqs="requirements.txt"):
    """
    Set up Python environment by installing from a requirements file.
    """
    if not os.path.exists(reqs):
        raise FileNotFoundError(f"⚠️ Requirements file not found: {reqs}")

    print(f"🐍 Installing Python requirements from {reqs}...")
    c.run(f"pip install -r {reqs}")

@task
def ensure_submodule(c, path):
    """
    Ensure a git submodule is present and up to date.

        Parameters:
            path (str): Path to the submodule directory 
    """
    if not os.path.exists(path) or not os.path.exists(os.path.join(path, ".git")):
        print(f"📦 Initializing submodule at {path}...")
        c.run(f"git submodule update --init --recursive {path}")
    else:
        print(f"🔄 Updating submodule at {path}...")
        c.run(f"git submodule update --remote {path}")

@task
def install_local(c, path):
    """
    Install a local Python package in editable mode using pip.

    Parameters:
        path (str): Path to the package directory
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Package path not found: {path}")

    print(f"🔧 Installing package from {path} in editable mode...")
    c.run(f"pip install -e {path}")
    print("✅ Editable install complete.")

@task
def ensure_dir_exist(c, name):
    """
    Ensure the output_data_dir exists, create it if not.
    """
    output_dir = c.config.get(name)
    if not isinstance(output_dir, str):
        raise ValueError("❌ 'output_data_dir' not found or not a string in invoke.yaml")

    output_path = Path(output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True)
        print(f"📁 Created output directory: {output_path}")
    else:
        print(f"✅ Output directory already exists: {output_path}")

@task
def clean_folder(c, name):
    """
    Remove a directory specified in invoke.yaml using a key.

    Parameters:
        name (str): Key in invoke.yaml whose value is the directory path.
        label (str, optional): Custom label for verbose output.
    """
    dir_name = c.config.get(name)
    if not isinstance(dir_name, str):
        raise ValueError(f"❌ Could not resolve a path from invoke config for key: '{name}'")

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
        print(f"💥 Removed {name} at {dir_name}")
    else:
        print(f"🫧 Nothing to clean: {name}")

@task
def run_figures(c, notebooks_path=None, figures_base=None):
    """
    Run figure notebooks, skipping any that already have output folders.
    Notebooks directory and output location pulled from invoke.yaml.
    """
    import pathlib as lib

    notebooks_path = Path(notebooks_path or c.config.get("notebooks_dir", "code/figures"))
    figures_base = Path(figures_base or c.config.get("figures_dir", "output_data/Figures"))

    if not notebooks_path.exists():
        print(f"⚠️ Notebooks directory not found: {notebooks_path}")
        return

    notebooks = sorted(notebooks_path.glob("*.ipynb"))

    if not notebooks:
        print(f"⚠️ No notebooks found in {notebooks_path}/")
        return

    for nb in notebooks:
        fig_name = nb.stem
        fig_output_dir = figures_base / fig_name

        if fig_output_dir.exists():
            print(f"✅ Skipping {nb.name} (output exists at {fig_output_dir})")
            continue

        print(f"📈 Running {nb.name}...")
        c.run(f"jupyter nbconvert --to notebook --execute --inplace {nb}")

    print("🎉 All figure notebooks processed.")
