# Pre-entrega · Automation Testing con Selenium y Python

## Propósito

Automatizar flujos básicos de navegación sobre [saucedemo.com](https://www.saucedemo.com), una tienda demo pensada para practicar testing:

| Test | Qué valida |
|---|---|
| `test_login_exitoso` | Login con `standard_user` / `secret_sauce`, espera explícita y redirección a `/inventory.html`, textos "Products" y "Swag Labs". |
| `test_catalogo_inventario` | Título de la página, que haya productos visibles, nombre y precio del primero, y que estén el menú, el filtro y el carrito. |
| `test_agregar_producto_al_carrito` | Agrega el primer producto, verifica que el contador del carrito suba en 1 y que el producto aparezca en el carrito. |

Cada test abre su propio navegador, así que son independientes: si uno falla, los demás siguen corriendo normalmente.

## Tecnologías

- Python 3.10+
- Selenium WebDriver 4 (descarga el chromedriver solo, vía Selenium Manager)
- Pytest + pytest-html
- Google Chrome
- Git y GitHub

## Estructura

```
├── datos/
│   └── usuarios.json        # credenciales de prueba
├── reports/
│   ├── reporte.html         # reporte generado por pytest-html
│   ├── ejecucion.log        # log de la ejecución
│   └── screenshots/         # capturas automáticas cuando un test falla
├── tests/
│   ├── conftest.py          # fixtures (navegador, login) y captura en fallos
│   └── test_saucedemo.py    # casos de prueba
├── utils/
│   └── helpers.py           # localizadores y funciones auxiliares
├── pytest.ini
└── requirements.txt
```

## Instalación

```bash
git clone https://github.com/FrederickQA/pre-entrega-automation-testing-Federico-Casais.git
cd pre-entrega-automation-testing-nombre-apellido

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

py -m pip install -r requirements.txt
```

Necesitás tener Google Chrome instalado.

## Ejecución

```bash
py -m pytest -v --html=reports/reporte.html --self-contained-html
```

Para correr sin abrir la ventana del navegador:

```bash
# Windows (PowerShell)
$env:HEADLESS="1"; pytest -v --html=reports/reporte.html --self-contained-html
# macOS / Linux
HEADLESS=1 pytest -v --html=reports/reporte.html --self-contained-html
```

## Evidencias

- **Reporte HTML:** `reports/reporte.html`
- **Logs:** se muestran en consola y quedan en `reports/ejecucion.log`
- **Capturas:** si un test falla, se guarda una captura en `reports/screenshots/` y además se adjunta dentro del reporte HTML
