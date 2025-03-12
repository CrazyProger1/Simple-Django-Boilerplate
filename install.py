import argparse
import pathlib
import shutil
import subprocess
import sys

SRC_DIR = pathlib.Path("src")
CONFIG_DIR = SRC_DIR / "config"
WEB_CONFIG_DIR = CONFIG_DIR / "web"
SETTINGS_DIR = CONFIG_DIR / "settings"
APPS_DIR = SRC_DIR / "apps"
ACCOUNTS_APP_DIR = APPS_DIR / "accounts"
DOCS_APP_DIR = APPS_DIR / "docs"

DOTENV_SAMPLE_FILE = ".env.sample"

SETTINGS_FILES = {
    "rest": SETTINGS_DIR / "rest.py",
    "docs": SETTINGS_DIR / "docs.py",
    "unfold": SETTINGS_DIR / "unfold.py",
    "cors": SETTINGS_DIR / "cors.py",
    "base": SETTINGS_DIR / "base.py",
}

URLS_FILE_CONTENT = """
from django.urls import path, include

urlpatterns = [
    path('', include('src.apps.accounts.urls')),
    path('', include('src.apps.docs.urls')),
]
"""

BASE_SETTINGS_FILE_CONTENT = """
from pathlib import Path
from decouple import config, Csv

APPLICATION = "Simple Django Boilerplate"
DESCRIPTION = "Boilerplate for Django projects"
VERSION = "0.0.1"

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BASE_URL = config("BASE_URL", cast=str, default="http://localhost:8000")
SECRET_KEY = config("SECRET_KEY", cast=str)
DEBUG = config("DEBUG", cast=bool, default=False)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=["*"])

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    'src.apps.docs',
    'src.apps.accounts',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "src.config.web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "src.config.web.wsgi.application"
ASGI_APPLICATION = "src.config.web.asgi.application"
STATIC_URL = config("STATIC_URL", default="static/")
STATIC_ROOT = config("STATIC_ROOT", default="static/")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Simple Django Boilerplate", description="Boilerplate for Django projects"
    )
    parser.add_argument(
        "destination",
        type=str,
        help="Specify the output folder for the boilerplate to install",
    )
    parser.add_argument(
        "--docs",
        action="store_true",
        help="Include spectacular documentation",
    )
    parser.add_argument(
        "--cors",
        action="store_true",
        help="Include CORS headers",
    )
    parser.add_argument(
        "--rest",
        action="store_true",
        help="Include REST framework",
    )
    parser.add_argument(
        "--unfold",
        action="store_true",
        help="Include Unfold admin",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include all features",
    )
    return parser.parse_args()


def run_command(command: list, cwd: pathlib.Path = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def check_poetry_installed() -> bool:
    return (
            subprocess.run(
                ["poetry", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).returncode
            == 0
    )


def install_poetry() -> None:
    if not check_poetry_installed():
        print("[+] Installing Poetry...")
        run_command([sys.executable, "-m", "pip", "install", "poetry"])
        print("[+] Poetry installed successfully")
    else:
        print("[+] Poetry is already installed")


def copy_file(src: pathlib.Path, dest: pathlib.Path) -> None:
    shutil.copy(src, dest)


def copy_boilerplate(dest: pathlib.Path) -> None:
    shutil.copytree(".", dest, dirs_exist_ok=True)


def create_file(file: pathlib.Path, content: str) -> None:
    file.write_text(content, encoding="utf-8")


def delete_files(files: list[pathlib.Path]) -> None:
    for file in files:
        try:
            if file.exists():
                if file.is_file():
                    file.unlink()
                else:
                    shutil.rmtree(file)
        except Exception as e:
            raise RuntimeError(f"[-] Failed to delete {file}: {e}")


def install(arguments: argparse.Namespace) -> None:
    destination = pathlib.Path(arguments.destination)
    print(f"[+] Installing boilerplate into {destination}...")

    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise RuntimeError("Destination folder is not empty")

    include_all = arguments.all
    include_docs = include_all or arguments.docs
    include_cors = include_all or arguments.cors
    include_rest = include_all or arguments.rest
    include_unfold = include_all or arguments.unfold

    copy_boilerplate(destination)
    install_poetry()
    run_command([sys.executable, "-m", "venv", ".venv"], cwd=destination)
    run_command(["poetry", "install"], cwd=destination)

    copy_file(destination / DOTENV_SAMPLE_FILE, destination / ".env")

    print("[+] Cleaning up...")
    unused_files = [
        destination / ".git",
        destination / "install.py",
    ]
    urls_file_content = URLS_FILE_CONTENT
    base_settings_file_content = BASE_SETTINGS_FILE_CONTENT

    if not include_cors:
        unused_files.append(destination / SETTINGS_FILES["cors"])
    if not include_docs:
        unused_files.extend(
            [destination / SETTINGS_FILES["docs"], destination / DOCS_APP_DIR]
        )
        urls_file_content = urls_file_content.replace(
            "path('', include('src.apps.docs.urls')),", ""
        )
        base_settings_file_content = base_settings_file_content.replace(
            "'src.apps.docs',", ""
        )
    if not include_rest:
        unused_files.append(destination / SETTINGS_FILES["rest"])
    if not include_unfold:
        unused_files.extend(
            [destination / SETTINGS_FILES["unfold"], destination / ACCOUNTS_APP_DIR]
        )
        urls_file_content = urls_file_content.replace(
            "path('', include('src.apps.accounts.urls')),", ""
        )
        base_settings_file_content = base_settings_file_content.replace(
            "'src.apps.accounts',", ""
        )

    create_file(destination / SETTINGS_FILES["base"], base_settings_file_content)
    create_file(destination / WEB_CONFIG_DIR / "urls.py", urls_file_content)
    delete_files(unused_files)
    run_command(["poetry", "run", "black", "."], cwd=destination)

    print("[+] Installation complete!")

    print("[+] Running...")
    run_command(["poetry", "run", "python", "manage.py", "runserver"], cwd=destination)


if __name__ == "__main__":
    install(parse_args())
