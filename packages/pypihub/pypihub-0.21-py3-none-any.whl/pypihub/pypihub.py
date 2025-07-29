#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyPihub - Local PyPI Server
Copyright (C) 2025 Hadi Cahyadi <cumulus13@gmail.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

For commercial licensing options, contact: cumulus13@gmail.com
"""

import os
import sys
import logging
try:
    from . import logger as Logger
except:
    import logger as Logger

# logging.basicConfig(level=logging.CRITICAL)

logger = Logger.setup_logging()
# logger.setLevel(Logger.EMERGENCY_LEVEL)

# logger = logging.getLogger(__name__)

import requests
from flask import Flask, send_from_directory, request, render_template_string, abort, Response, jsonify, session, redirect, url_for
from bs4 import BeautifulSoup
from pydebugger.debug import debug
from configset import configset
from pathlib import Path
from functools import wraps
from getpass import getpass

if (Path(__file__).parent / 'settings.py').is_file():
    try:
        from . import settings as local_settings
    except:
        import settings as local_settings
else:
    local_settings = None

if (Path(__file__).parent / 'database.py').is_file():
    try:
        from . import database
    except:
        import database
else:
    database = None

from rich.console import Console
from rich_argparse import RichHelpFormatter, _lazy_rich as rr
from typing import ClassVar
console = Console()

class CustomRichHelpFormatter(RichHelpFormatter):
    """A custom RichHelpFormatter with modified styles."""

    styles: ClassVar[dict[str, rr.StyleType]] = {
        "argparse.args": "bold #FFFF00",
        "argparse.groups": "#AA55FF",
        "argparse.help": "bold #00FFFF",
        "argparse.metavar": "bold #FF00FF",
        "argparse.syntax": "underline",
        "argparse.text": "white",
        "argparse.prog": "bold #00AAFF italic",
        "argparse.default": "bold",
    }

import argparse
from pathlib import Path

class settings:
    #make this possbile/available like 'settings.var' then return value from 'var = value' in settings.py
    def __getattr__(self, item):
        if local_settings is None:
            return None
        if hasattr(local_settings, item):
            return getattr(local_settings, item)
        # raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")
        return None

settings = settings()

app = Flask(__name__)

CONFIGFILE = (
    os.getenv('CONFIGFILE')
    or (settings.CONFIGFILE if getattr(settings, 'CONFIGFILE', None) and Path(settings.CONFIGFILE).is_file() else None)
    or str(Path(__file__).parent / (Path(__file__).stem + '.ini'))
)
debug(CONFIGFILE=CONFIGFILE)
logger.info(f"CONFIGFILE: {CONFIGFILE}")
CONFIG = configset(CONFIGFILE)

BASE_DIR = (
    Path(os.getenv('BASE_DIR'))
    if os.getenv('BASE_DIR') and Path(os.getenv('BASE_DIR')).is_dir()
    else Path(settings.BASE_DIR)
    if getattr(settings, 'BASE_DIR', None)
    else Path(__file__).parent
)
debug(BASE_DIR=str(BASE_DIR))
logger.info(f"BASE_DIR: {BASE_DIR}")

logger.info(f"os.getenv('LOCAL_PKG_DIR'): {os.getenv('LOCAL_PKG_DIR')}, is_dir: {Path(os.getenv('LOCAL_PKG_DIR')).is_dir() if os.getenv('LOCAL_PKG_DIR') else None}")
logger.info(f"CONFIG.get_config('dirs', 'local_pkg'): {CONFIG.get_config('dirs', 'local_pkg')}, is_dir: {Path(CONFIG.get_config('dirs', 'local_pkg')).is_dir() if CONFIG.get_config('dirs', 'local_pkg') else None}")
logger.info(f"settings.LOCAL_PKG_DIR: {getattr(settings, 'LOCAL_PKG_DIR', None)}, is_dir: {Path(getattr(settings, 'LOCAL_PKG_DIR', '')) .is_dir() if getattr(settings, 'LOCAL_PKG_DIR', None) else None}")
LOCAL_PKG_DIR = (
    Path(os.getenv('LOCAL_PKG_DIR'))
    if os.getenv('LOCAL_PKG_DIR') and Path(os.getenv('LOCAL_PKG_DIR')).is_dir()
    else Path(CONFIG.get_config('dirs', 'local_pkg'))
    if CONFIG.get_config('dirs', 'local_pkg') and Path(CONFIG.get_config('dirs', 'local_pkg')).is_dir()
    else Path(getattr(settings, 'LOCAL_PKG_DIR', ''))
    if getattr(settings, 'LOCAL_PKG_DIR', None)
    else BASE_DIR / "packages"
)
debug(LOCAL_PKG_DIR=str(LOCAL_PKG_DIR))
logger.info(f"LOCAL_PKG_DIR: {LOCAL_PKG_DIR}")

logger.info(f"os.getenv('CACHE_DIR'): {os.getenv('CACHE_DIR')}, is_dir: {Path(os.getenv('CACHE_DIR')).is_dir() if os.getenv('CACHE_DIR') else None}")
logger.info(f"CONFIG.get_config('dirs', 'cache'): {CONFIG.get_config('dirs', 'cache')}, is_dir: {Path(CONFIG.get_config('dirs', 'cache')).is_dir() if CONFIG.get_config('dirs', 'cache') else None}")
logger.info(f"settings.CACHE_DIR: {getattr(settings, 'CACHE_DIR', None)}, is_dir: {Path(getattr(settings, 'CACHE_DIR', '')) .is_dir() if getattr(settings, 'CACHE_DIR', None) else None}")
CACHE_DIR = (
    Path(os.getenv('CACHE_DIR'))
    if os.getenv('CACHE_DIR') and Path(os.getenv('CACHE_DIR')).is_dir()
    else Path(CONFIG.get_config('dirs', 'cache'))
    if CONFIG.get_config('dirs', 'cache') and Path(CONFIG.get_config('dirs', 'cache')).is_dir()
    else Path(getattr(settings, 'CACHE_DIR', ''))
    if getattr(settings, 'CACHE_DIR', None)
    else BASE_DIR / "cache"
)
debug(CACHE_DIR=str(CACHE_DIR))
logger.info(f"CACHE_DIR: {CACHE_DIR}")

PYPI_SIMPLE_URL = (
    os.getenv('PYPI_SIMPLE_URL')
    or getattr(settings, 'PYPI_SIMPLE_URL', None)
    or CONFIG.get_config('urls', 'pypi_simple')
    or "https://pypi.org/simple"
)
debug(PYPI_SIMPLE_URL=PYPI_SIMPLE_URL)
logger.info(f"PYPI_SIMPLE_URL: {PYPI_SIMPLE_URL}")

HOST = (
    os.getenv('HOST')
    or getattr(settings, 'HOST', None)
    or CONFIG.get_config('server', 'host')
    or '0.0.0.0'
)
debug(HOST=HOST)
logger.info(f"HOST: {HOST}")

PORT = int(
    os.getenv('PORT')
    or getattr(settings, 'PORT', None)
    or CONFIG.get_config('server', 'port')
    or 5000
)
debug(PORT=PORT)
logger.info(f"PORT: {PORT}")

print("\n")

os.makedirs(LOCAL_PKG_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

if database:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import SQLAlchemyError

    User = database.User
    Package = database.Package

    def get_db_url():
        # Take config from Settings.co, Settings.ini, App.config, or ENV
        db_type = (
            getattr(settings, 'DB_TYPE', None)
            or CONFIG.get_config('database', 'type')
            or app.config.get('DB_TYPE')
            or os.getenv('DB_TYPE')
            or 'sqlite'
        ).lower()

        db_path = (
            getattr(settings, 'DB_PATH', None)
            or CONFIG.get_config('database', 'path')
            or app.config.get('DB_PATH')
            or os.getenv('DB_PATH')
            or f"{BASE_DIR}/pypihub.db"
        )

        db_name = (
            getattr(settings, 'DB_NAME', None)
            or CONFIG.get_config('database', 'name')
            or app.config.get('DB_NAME')
            or os.getenv('DB_NAME')
            or 'pypihub'
        )

        db_user = (
            getattr(settings, 'DB_USERNAME', None)
            or CONFIG.get_config('database', 'username')
            or app.config.get('DB_USERNAME')
            or os.getenv('DB_USERNAME')
            or ''
        )

        db_pass = (
            getattr(settings, 'DB_PASSWORD', None)
            or CONFIG.get_config('database', 'password')
            or app.config.get('DB_PASSWORD')
            or os.getenv('DB_PASSWORD')
            or ''
        )

        db_host = (
            getattr(settings, 'DB_HOST', None)
            or CONFIG.get_config('database', 'host')
            or app.config.get('DB_HOST')
            or os.getenv('DB_HOST')
            or 'localhost'
        )

        db_port = (
            getattr(settings, 'DB_PORT', None)
            or CONFIG.get_config('database', 'port')
            or app.config.get('DB_PORT')
            or os.getenv('DB_PORT')
        )

        # Default port per type
        if not db_port:
            if db_type == 'postgres':
                db_port = 5432
            elif db_type == 'mysql':
                db_port = 3306
            else:
                db_port = ''

        # Compose SQLAlchemy URL
        if db_type == 'sqlite':
            db_url = f"sqlite:///{db_path}"
        elif db_type == 'postgres':
            db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        elif db_type == 'mysql':
            db_url = f"mysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        else:
            # return jsonify({"error": f"Unsupported DB_TYPE: {db_type}"}), 401
            raise ValueError(f"Unsupported DB_TYPE: {db_type}")

        return db_url

    engine = create_engine(get_db_url(), echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine)
    database.Base.metadata.create_all(engine)

    import bcrypt

    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(password, hashed):
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            logger.error(f"Password check error: {e}")
            return False

def index_usage():
    return f"""
    <h1>PyPihub - Local PyPI Server</h1>
    <p>Upload packages to your local PyPI server.</p>
    <h2>Usage</h2>
    <ul>
        <li>Upload a package: <code>POST /upload/&lt;package&gt;/</code> with file in form-data under 'file'</li>
        <li><i>twine</i> supported</li>
        <li>Access local packages: <code>/</code></li>
        <li>Access package files: <code>/packages/&lt;package&gt;/&lt;filename&gt;</code></li>
        <li>Access cached files: <code>/cache/&lt;package&gt;/&lt;filename&gt;</code></li>
        <li>Simple index for a package: <code>/simple/&lt;package&gt;/</code></li>
    </ul>
    """

@app.route('/')
def index():
    packages = os.listdir(LOCAL_PKG_DIR)
    debug(len_packages = len(packages))
    logger.notice(f"len(packages): {len(packages)}")
    return render_template_string(index_usage() + '<br/><br/>' + '<h1>Local Packages</h1><ul>{% for p in pkgs %}<li><a href="/simple/{{p}}/">{{p}}</a></li>{% endfor %}</ul>', pkgs=packages)

def check_auth(username, password):
    if not username or not password:
        logger.warning("Username or password is empty")
        return False
    if database:
        try:
            with SessionLocal() as db:
                user = db.query(User).filter_by(username=username).first()
                if user and check_password(password, user.password):
                    return True
                logger.warning("Invalid username or password (DB)")
                return False
        except SQLAlchemyError as e:
            logger.error(f"Database error during authentication: {e}")
            return False
    logger.emergency("run auth without use database")
    # Settings.auths must be a list of tuple/list: [("user", "pass"), ...]
    auths = getattr(settings, 'AUTHS', None) or CONFIG.get_config_as_list('auths', 'users')
    if not auths or not isinstance(auths, (list, tuple)) or not auths:
        # Default: [('pypihub', 'pypihub')]
        auths = [('pypihub', 'pypihub')]
    return (username, password) in auths

def authenticate():
    # Return json so that twine can display a clear error message
    # resp = jsonify({"error": "Invalid username or password"})
    resp = Response("Invalid username or password", status=400, content_type="text/plain")
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
    logger.debug(f"resp: {resp}")
    return resp

def requires_auth(f):
    debug("requires_auth")
    logger.notice("run requires_auth")
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        debug(auth = auth)
        logger.debug(f"auth: {auth}")
        try:
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/upload/<package>/', methods=['POST'])
@requires_auth
def upload_package(package):
    file = request.files['file']
    debug(file = file)
    logger.debug(f"file: {file}")
    save_path = os.path.join(LOCAL_PKG_DIR, package)
    debug(save_path = save_path, is_dir = os.path.isdir(save_path))
    logger.debug(f"save_path: {save_path}, is_dir: {os.path.isdir(save_path)}")
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, file.filename)
    debug(file_path = file_path)
    logger.debug(f"file_path: {file_path}")
    file.save(file_path)
    logger.info(f"Uploaded {file.filename} to {file_path}")
    user_id = session.get('user_id')
    if database:
        if not user_id and request.authorization and database:
            with SessionLocal() as db2:
                user = db2.query(User).filter_by(username=request.authorization.username).first()
                if user: user_id = user.id
        with SessionLocal() as db:
            db.add(Package(name=package, source='upload', user_id=user_id))
            db.commit()
    return 'Uploaded', 200

@app.route('/upload/', methods=['POST'])
@app.route('/', methods=['POST'])
@requires_auth
def twine_upload():
    # Try to take files from several possible fields
    file = (
        request.files.get('file') or
        request.files.get('content') or
        request.files.get('distribution')
    )
    debug(file = file)
    logger.warning(f"file: {file}")
    if not file:
        # Try to take from the first field if any
        if request.files:
            file = next(iter(request.files.values()))
            debug(file = file)
            logger.notice(f"file: {file}")
        else:
            debug(error = "No file part in request [400]")
            logger.error("No file part in request [400]")
            # return "No file part", 400
            return jsonify({"error": "No file part"}), 400

    filename = file.filename
    debug(filename = filename)
    # Extract the name package (simple, can be better)
    pkg_name = filename.split('-')[0].lower()
    debug(pkg_name = pkg_name)
    logger.info(f"pkg_name: {pkg_name}")
    save_path = os.path.join(LOCAL_PKG_DIR, pkg_name)
    debug(save_path = save_path)
    logger.info(f"save_path: {save_path}")
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, filename)
    debug(file_path = file_path)
    logger.info(f"file_path: {file_path}")
    if os.path.isfile(file_path):
        debug(error = f"File {filename} already exists in {save_path} [409]")
        logger.error(f"File {filename} already exists in {save_path} [409]")
        # return jsonify({"error": f"File {filename} already exists"}), 409
        return Response("File already exists", status=400, content_type="text/plain")
    file.save(file_path)
    logger.info(f"Uploaded {file.filename} to {file_path} (via twine)")
    return 'OK', 200

@app.route('/packages/<package>/<filename>')
def serve_package(package, filename):
    local_path = os.path.join(LOCAL_PKG_DIR, package)
    debug(local_path = local_path)
    logger.debug(f"local_path: {local_path}")
    return send_from_directory(local_path, filename)

@app.route('/cache/<package>/<filename>')
def serve_cached(package, filename):
    cache_path = os.path.join(CACHE_DIR, package)
    debug(cache_path = cache_path)
    logger.notice(f"cache_path: {cache_path}")
    os.makedirs(cache_path, exist_ok=True)
    file_path = os.path.join(cache_path, filename)
    debug(file_path = file_path, is_file = os.path.isfile(file_path))
    logger.info(f"file_path: {file_path}, is_file: {os.path.isfile(file_path)}")

    if os.path.exists(file_path):
        # Sudah ada di cache, langsung serve
        return send_from_directory(cache_path, filename)

    # Find the URL File in Pypi Simple Index
    r = requests.get(f"{PYPI_SIMPLE_URL}/{package}/")
    debug(requests_status_code = r.status_code)
    logger.notice(f"requests.get status_code: {r.status_code}")
    if r.status_code != 200:
        debug(error = "Package not found on PyPI [404]")
        logger.error("Package not found on PyPI [404]")
        abort(404, description="Package not found on PyPI")
    soup = BeautifulSoup(r.text, 'html.parser')
    file_url = None
    for a in soup.find_all('a'):
        href = a.get('href')
        if href and href.split('/')[-1].split('#')[0] == filename:
            # Gunakan href langsung jika sudah absolut, jika relatif tambahkan domain
            if href.startswith('http'):
                file_url = href
            else:
                file_url = f"https://files.pythonhosted.org{href}"
            break
    debug(file_url = file_url)
    logger.debug(f"file_url: {file_url}")
    if not file_url:
        debug(error = "File not found on PyPI [404]")
        logger.error("File not found on PyPI [404]")
        abort(404, description="File not found on PyPI")

    # Stream Download from Pypi to Client and Disk in parallel
    def generate():
        with requests.get(file_url, stream=True) as resp:
            if resp.status_code != 200:
                debug(error = "Failed to download from PyPI [404]")
                logger.error("Failed to download from PyPI [404]")
                abort(404, description="Failed to download from PyPI")
            with open(file_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        yield chunk
                        
        if database:
            with SessionLocal() as db:
                db.add(Package(name=package, source='pypi', user_id=None))
                db.commit()

    response = app.response_class(generate(), mimetype='application/octet-stream')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@app.route('/simple/<package>/')
def simple_index(package):
    local_path = os.path.join(LOCAL_PKG_DIR, package)
    debug(local_path = local_path)
    logger.debug(f"local_path: {local_path}")
    cached_path = os.path.join(CACHE_DIR, package)
    debug(cached_path = cached_path)
    logger.debug(f"cached_path: {cached_path}")
    os.makedirs(cached_path, exist_ok=True)
    links = []
    found = False

    # Local files
    if os.path.exists(local_path):
        for f in os.listdir(local_path):
            links.append(f'<a href="/packages/{package}/{f}">{f}</a>')
            found = True

    # Cached files
    if os.path.exists(cached_path):
        for f in os.listdir(cached_path):
            links.append(f'<a href="/cache/{package}/{f}">{f}</a>')
            found = True

    # Fetch from PyPI (hanya generate link, TIDAK download)
    r = requests.get(f"{PYPI_SIMPLE_URL}/{package}/")
    debug(requests_status_code = r.status_code)
    logger.notice(f"requests.get status_code: {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a'):
            href = a.get('href')
            if not href:
                continue
            filename = href.split('/')[-1].split('#')[0]
            # Ambil hash jika ada
            hash_fragment = ''
            if '#' in href:
                hash_fragment = href[href.index('#'):]
            # If not in local/cache, add link to/cache/with hash
            if not os.path.exists(os.path.join(local_path, filename)) and not os.path.exists(os.path.join(cached_path, filename)):
                links.append(f'<a href="/cache/{package}/{filename}{hash_fragment}">{filename}</a>')
                found = True
    else:
        if not found:
            debug(error = "Package not found [404]")
            logger.error("Package not found [404]")
            abort(404, description="Package not found")

    html = f"<html><body>{''.join(links)}</body></html>"
    return html

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if database:
            with SessionLocal() as db:
                user = db.query(User).filter_by(username=username).first()
                if user and check_password(password, user.password):
                    session['user_id'] = user.id
                    return jsonify({"message": "Sign in successful"})
        return jsonify({"error": "Invalid username or password. Singin can be used with database."}), 401
    # Simple HTML form for sign in
    return '''
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Sign In">
        </form>
    '''

@app.route('/signout')
def signout():
    session.pop('user_id', None)
    return jsonify({"message": "Signed out"})

def create_user_cli(username = None, password = None):
    username = username or input("Username: ")
    password = password or getpass("Password: ")
    if database:
        with SessionLocal() as db:
            if db.query(User).filter_by(username=username).first():
                print("User already exists.")
                return
            hashed_pw = hash_password(password)
            user = User(username=username, password=hashed_pw)
            db.add(user)
            db.commit()
            print("User created.")
    else:
        print("Database not enabled.")
        
def list_user():
    if database:
        with SessionLocal() as db:
            users = db.query(User).all()
            if users:
                console.print("[bold green]Users:[/]")
                for user in users:
                    console.print(f"- {user.username}")
            else:
                console.print("[white on red]No users found.[/]")
    else:
        console.print("[bold red]Database not enabled, cannot list users.[/]")
    return

def version():
    # __version__.py must contain 'version = "x.y.z"' or 'version = 'x.y.z'' or 'version = x.y.z'
    for path in [Path(__file__).parent, Path(__file__).parent.parent]:
        version_file = path / '__version__.py'
        if version_file.is_file():
            import importlib.util
            spec = importlib.util.spec_from_file_location("version", str(version_file))
            version_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version_module)
            if hasattr(version_module, 'version'):
                return f"[black on #00FFFF]{str(version_module.version)}[/]"
            break  # break here is not necessary, as return already exits the function
    return f"[white on blue]UNKNOWN VERSION[/]"

def usage():
    parser = argparse.ArgumentParser(
        description="PyPihub - A simple local PyPI server with caching and upload capabilities.",
        formatter_class=CustomRichHelpFormatter
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=CONFIGFILE,
        help='Path to the configuration file (default: %(default)s)'
    )
    parser.add_argument(
        '-b', '--base-dir',
        type=str,
        default=BASE_DIR,
        help='Base directory for the server (default: %(default)s)'
    )
    parser.add_argument(
        '-l', '--local-pkg-dir',
        type=str,
        default=LOCAL_PKG_DIR,
        help='Directory for local packages (default: %(default)s)'
    )
    parser.add_argument(
        '-C', '--cache-dir',
        type=str,
        default=CACHE_DIR,
        help='Directory for cached packages (default: %(default)s)'
    )
    parser.add_argument(
        '-i', '--pypi-simple-url',
        type=str,
        default=PYPI_SIMPLE_URL,
        help='PyPI simple index URL (default: %(default)s)'
    )
    parser.add_argument(
        '-H', '--host',
        type=str,
        default=HOST,
        help='Host to run the server on (default: %(default)s)'
    )
    parser.add_argument(
        '-P', '--port',
        type=int,
        # default=int(
        #     next(
        #         (
        #             v for v in [
        #                 os.getenv('PORT'),
        #                 CONFIG.get_config('server', 'port'),
        #                 getattr(settings, 'PORT', None) if hasattr(settings, 'PORT') else None
        #             ]
        #             if v not in (None, '')
        #         ),
        #         5000
        #     )
        # ),
        default = PORT,
        help='Port to run the server on (default: %(default)s)'
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'PyPihub {version()}',
        help='Show the version of PyPihub'
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    parser.add_argument(
        'command',
        help='Command to run: serve (default), user (manage users)',
        nargs='?',
        default='serve',
        choices=['serve', 'user']
    )
    
    parser.add_argument(
        '-u', '--username',
        type=str,
        help='Username for user management (required for user command)'
    )
    
    parser.add_argument(
        '-p', '--password',
        type=str,
        help='Password for user management (required for user command)',
        default=None
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all users (only works with user command)'
    )
    
    parser.add_argument(
        '-a', '--add',
        action='store_true',
        help='Add a new user (only works with user command, requires username and password)'
    )

    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    debug(args = args)
    logger.info(f"Arguments: {args}")
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        console.log("[bold green]Verbose mode enabled[/]")

    # Set environment variables or configuration based on args
    os.environ['CONFIGFILE'] = args.config if args.config else str(CONFIGFILE)
    os.environ['BASE_DIR'] = str(args.base_dir) if args.base_dir else str(BASE_DIR)
    os.environ['LOCAL_PKG_DIR'] = str(args.local_pkg_dir) if args.local_pkg_dir else str(LOCAL_PKG_DIR)
    os.environ['CACHE_DIR'] = str(args.cache_dir) if args.cache_dir else str(CACHE_DIR)
    os.environ['PYPI_SIMPLE_URL'] = args.pypi_simple_url if args.pypi_simple_url else str(PYPI_SIMPLE_URL)
    os.environ['HOST'] = args.host if args.host else str(HOST)
    os.environ['PORT'] = str(args.port) if args.port else str(PORT)

    debug(os_env_CONFIGFILE = os.environ['CONFIGFILE'])
    logger.info(f"os.environ['CONFIGFILE']: {os.environ['CONFIGFILE']}")
    debug(os_env_BASE_DIR = os.environ['BASE_DIR'])
    logger.info(f"os.environ['BASE_DIR']: {os.environ['BASE_DIR']}")
    debug(os_env_LOCAL_PKG_DIR = os.environ['LOCAL_PKG_DIR'])
    logger.info(f"os.environ['LOCAL_PKG_DIR']: {os.environ['LOCAL_PKG_DIR']}")
    debug(os_env_CACHE_DIR = os.environ['CACHE_DIR'])
    logger.info(f"os.environ['CACHE_DIR']: {os.environ['CACHE_DIR']}")
    debug(os_env_PYPI_SIMPLE_URL = os.environ['PYPI_SIMPLE_URL'])
    logger.info(f"os.environ['PYPI_SIMPLE_URL']: {os.environ['PYPI_SIMPLE_URL']}")
    debug(os_env_HOST = os.environ['HOST'])
    logger.info(f"os.environ['HOST']: {os.environ['HOST']}")
    debug(os_env_PORT = os.environ['PORT'])
    logger.info(f"os.environ['PORT']: {os.environ['PORT']}")
    
    if args.command == 'serve':
        
        # Start the Flask server
        app.config['BASE_DIR'] = BASE_DIR
        app.config['LOCAL_PKG_DIR'] = LOCAL_PKG_DIR
        app.config['CACHE_DIR'] = CACHE_DIR
        app.config['PYPI_SIMPLE_URL'] = PYPI_SIMPLE_URL
        app.config['HOST'] = args.host
        app.config['PORT'] = args.port or int(PORT) if PORT else 5000
        
        logger.info("Starting PyPihub server...")
        debug(app_config = app.config)
        logger.debug(f"app.config: {app.config}")
        console.print(f"[bold green]Starting PyPihub server on {HOST}:{PORT} ...[/]")
        console.print(f"[bold blue]Base Directory: {BASE_DIR}[/]")
        console.print(f"[bold blue]Local Package Directory: {LOCAL_PKG_DIR}[/]")
        console.print(f"[bold blue]Cache Directory: {CACHE_DIR}[/]")
        console.print(f"[bold blue]PyPI Simple URL: {PYPI_SIMPLE_URL}[/]")
        console.print(f"[bold blue]Configuration File: {CONFIGFILE}[/]")
        console.print(f"[bold blue]Host: {args.host}[/]")
        console.print(f"[bold blue]Port: {args.port}[/]")
        app.config['DEBUG'] = True
        app.config['ENV'] = 'development'
        app.config['TESTING'] = False
        app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for session management
        debug(f"start server on {app.config['HOST']}:{app.config['PORT']}")    
        logger.notice(f"start server on {app.config['HOST']}:{app.config['PORT']}")

        app.run(
            host=args.host,
            port=args.port,
            debug=True if args.verbose else False,
            use_reloader=False  # Disable reloader to avoid multiple instances
        )
    elif args.command == 'user':
        if args.list:
            return list_user()
        elif args.add:
            if not args.username or not args.password:
                console.print("[bold red]Username and password are required to add a user.[/]")
                return
            create_user_cli(
                username=args.username,
                password=args.password
            )
            return
        elif args.username:
            if not args.password: 
                console.print("[black on #FFFF00]Password:[/] ", end = '')
                args.password = getpass()
            if args.username and not args.password:
                console.print("[bold red]Password is required to create a user.[/]")
                return
            create_user_cli(
                username=args.username,
                password=args.password
            )
            return
        else:
            console.print("[black on #FFFF00    ]No command specified. Use --list to list users or --add to add a new user.[/]")
            return

if __name__ == '__main__':    
    usage()
