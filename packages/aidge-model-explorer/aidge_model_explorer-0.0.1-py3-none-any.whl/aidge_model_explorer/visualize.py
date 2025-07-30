import os
import threading
import time
import requests
import socket
import sys
import portpicker
import aidge_core
from model_explorer import visualize_from_config
from IPython.display import display, HTML
from IPython import get_ipython
from .config import config
from .consts import (
    DEFAULT_PORT,
    DEFAULT_HOST,
)


def _is_port_in_use(host: str, port: int) -> bool:
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      return s.connect_ex((host, port)) == 0
  except socket.gaierror:
    print(
        f'"{host}" cannot be resolved. Try using IP address directly:'
        ' model-explorer --host=127.0.0.1'
    )
    sys.exit(1)

def visualize(graphview, name, host=DEFAULT_HOST, port=DEFAULT_PORT, no_open_in_browser=False, embed=False) -> None:
    if get_ipython():
        show_in_notebook(
            graphview,
            name,
            host=host,
            port=port,
            embed=embed
        )
    else:
        show_ext_server(
            graphview,
            name,
            host=host,
            port=port,
            no_open_in_browser=no_open_in_browser
        )

def show_ext_server(graphview, name, host=DEFAULT_HOST, port=DEFAULT_PORT, no_open_in_browser=False) -> None:
    conf = config()
    conf.add_graphview(graphview, name)
    visualize_from_config(
        config = conf,
        host= host,
        port=port,
        no_open_in_browser=no_open_in_browser
    )

def show_in_notebook(graphview, name, host=DEFAULT_HOST, port=DEFAULT_PORT, embed=True) -> None:
    if get_ipython() is None:
        raise RuntimeError("This function should only be used inside of a Notebook.")
    conf = config()
    conf.add_graphview(graphview, name)


    if _is_port_in_use(host, port):
        aidge_core.Log.notice(f"{host}::{port} is already taken, finding another port")
        found_port = False
        for i in range(0, 20):
            port = port + i
            if not _is_port_in_use(host, port):
                found_port = True
                break
        if not found_port:
            port = portpicker.pick_unused_port()
        aidge_core.Log.notice(f"New port used: {host}::{port}")

    app_thread = threading.Thread(target=lambda: visualize_from_config(
        config = conf,
        host= host,
        port=port,
        no_open_in_browser=False
    ))

    app_thread.daemon = True
    aidge_core.Log.debug("Starting server ...")
    app_thread.start()
    starting_time = time.time()
    while True:
        try:
            response = requests.get(f'http://{host}:{port}/')
        except:
            continue

        if response.status_code == 200:
            aidge_core.Log.debug("Server found!")
            break
        elif time.time() - starting_time > 10:
            raise RuntimeError(f"Trying to detect app for 10s failed, http error {response.status_code}")
    
    # Determine if the notebook is running in Binder
    is_binder = 'JUPYTERHUB_API_URL' in os.environ

    if is_binder:
        # Get base URL from JupyterHub environment (should always start with /user/...)
        base_url = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
        # Build full link to the proxied Flask app on {port} 
        url = f"{base_url}proxy/{port}/?data={conf.to_url_param_value()}"

    else:
        url = f"http://{host}:{port}/?data={conf.to_url_param_value()}"

    # Print the URL for debugging
    aidge_core.Log.debug(f"Generated URL: {url}")

    if embed:
        display(HTML(f'''
        <iframe src="{url}" width="100%" height="600"
            style="border: 2px solid #444; border-radius: 8px; margin-top:10px;">
        </iframe>
        '''))
    else:
        display(HTML(f'<a href="{url}" target="_blank">🔗 Open Model Explorer server.</a>'))