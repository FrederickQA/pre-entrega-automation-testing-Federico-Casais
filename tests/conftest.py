"""
Configuración compartida de pytest.

- Fixture `driver`: abre un navegador NUEVO para cada test y lo cierra al
  terminar, así los tests son independientes entre sí.
- Fixture `driver_logueado`: igual que `driver`, pero ya con sesión iniciada.
- Hook de captura: si un test falla, guarda una captura de pantalla en
  reports/screenshots/ y la adjunta al reporte HTML.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Permite importar el paquete utils/ desde la raíz del proyecto
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROYECTO))

from utils import helpers  # noqa: E402

CARPETA_CAPTURAS = RAIZ_PROYECTO / "reports" / "screenshots"


@pytest.fixture
def driver():
    """Navegador limpio por test. HEADLESS=1 lo corre sin ventana."""
    headless = os.getenv("HEADLESS", "0") == "1"
    navegador = helpers.crear_driver(headless=headless)
    yield navegador
    navegador.quit()


@pytest.fixture
def driver_logueado(driver):
    """Navegador con el login ya hecho con el usuario válido."""
    usuario, password = helpers.cargar_credenciales("valido")
    helpers.login(driver, usuario, password)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Saca una captura si el test falla y la suma al reporte HTML."""
    resultado = yield
    reporte = resultado.get_result()

    if reporte.when != "call" or not reporte.failed:
        return

    navegador = item.funcargs.get("driver") or item.funcargs.get("driver_logueado")
    if navegador is None:
        return

    CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = CARPETA_CAPTURAS / f"{item.name}_{marca}.png"
    navegador.save_screenshot(str(ruta))

    # Adjunta la imagen al reporte de pytest-html (si está instalado)
    plugin_html = item.config.pluginmanager.getplugin("html")
    if plugin_html is not None:
        extras = getattr(reporte, "extras", [])
        extras.append(plugin_html.extras.image(navegador.get_screenshot_as_base64()))
        reporte.extras = extras
