"""
Funciones auxiliares para automatizar saucedemo.com con Selenium WebDriver.

Acá se centralizan:
- la creación del navegador,
- los localizadores de los elementos de la página,
- las acciones reutilizables (login, agregar al carrito, etc.).

Así los tests quedan cortos y enfocados en las validaciones.
"""
import json
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
URL_BASE = "https://www.saucedemo.com/"
TIEMPO_ESPERA = 10  # segundos máximos para las esperas explícitas
RUTA_USUARIOS = Path(__file__).resolve().parent.parent / "datos" / "usuarios.json"

# ---------------------------------------------------------------------------
# Localizadores (tuplas By + valor)
# ---------------------------------------------------------------------------
# Login
CAMPO_USUARIO = (By.ID, "user-name")
CAMPO_PASSWORD = (By.ID, "password")
BOTON_LOGIN = (By.ID, "login-button")

# Inventario
TITULO_SECCION = (By.CLASS_NAME, "title")          # texto "Products"
LOGO_APP = (By.CLASS_NAME, "app_logo")             # texto "Swag Labs"
ITEMS_INVENTARIO = (By.CLASS_NAME, "inventory_item")
NOMBRE_ITEM = (By.CLASS_NAME, "inventory_item_name")
PRECIO_ITEM = (By.CLASS_NAME, "inventory_item_price")
BOTON_AGREGAR = (By.CSS_SELECTOR, "button.btn_inventory")
BOTON_MENU = (By.ID, "react-burger-menu-btn")
FILTRO_ORDEN = (By.CLASS_NAME, "product_sort_container")

# Carrito
CONTADOR_CARRITO = (By.CLASS_NAME, "shopping_cart_badge")
LINK_CARRITO = (By.CLASS_NAME, "shopping_cart_link")
ITEMS_CARRITO = (By.CLASS_NAME, "cart_item")


# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------
def cargar_credenciales(tipo="valido"):
    """Lee usuario y contraseña desde datos/usuarios.json."""
    with open(RUTA_USUARIOS, encoding="utf-8") as archivo:
        datos = json.load(archivo)
    credenciales = datos[tipo]
    return credenciales["usuario"], credenciales["password"]


# ---------------------------------------------------------------------------
# Navegador
# ---------------------------------------------------------------------------
def crear_driver(headless=False):
    """
    Crea una instancia de Chrome lista para usar.

    Selenium 4.6+ descarga el chromedriver correcto automáticamente
    (Selenium Manager), así que no hace falta instalarlo a mano.
    """
    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--window-size=1366,900")
    # Evita el popup de Chrome "cambiá tu contraseña" que bloquea los clics
    opciones.add_argument("--incognito")
    opciones.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    if headless:
        opciones.add_argument("--headless=new")

    logger.info("Iniciando Chrome (headless=%s)", headless)
    return webdriver.Chrome(options=opciones)


def esperar_visible(driver, localizador):
    """Espera explícita hasta que el elemento sea visible y lo devuelve."""
    return WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.visibility_of_element_located(localizador)
    )


def esperar_clickeable(driver, localizador):
    """Espera explícita hasta que el elemento se pueda clickear y lo devuelve."""
    return WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.element_to_be_clickable(localizador)
    )


# ---------------------------------------------------------------------------
# Acciones de negocio
# ---------------------------------------------------------------------------
def login(driver, usuario, password):
    """Abre la página de login, ingresa credenciales y espera el inventario."""
    logger.info("Navegando a %s", URL_BASE)
    driver.get(URL_BASE)

    esperar_visible(driver, CAMPO_USUARIO).send_keys(usuario)
    driver.find_element(*CAMPO_PASSWORD).send_keys(password)
    logger.info("Ingresando con el usuario '%s'", usuario)
    esperar_clickeable(driver, BOTON_LOGIN).click()

    # Espera explícita de la redirección al inventario
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.url_contains("/inventory.html"))
    logger.info("Login completado, URL actual: %s", driver.current_url)


def obtener_productos(driver):
    """Devuelve la lista de productos visibles en el inventario."""
    WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.visibility_of_all_elements_located(ITEMS_INVENTARIO)
    )
    return driver.find_elements(*ITEMS_INVENTARIO)


def obtener_datos_producto(producto):
    """Extrae nombre y precio de un elemento de producto."""
    return {
        "nombre": producto.find_element(*NOMBRE_ITEM).text,
        "precio": producto.find_element(*PRECIO_ITEM).text,
    }


def agregar_primer_producto(driver):
    """Agrega al carrito el primer producto del inventario y devuelve su nombre."""
    primer_producto = obtener_productos(driver)[0]
    nombre = primer_producto.find_element(*NOMBRE_ITEM).text
    primer_producto.find_element(*BOTON_AGREGAR).click()
    logger.info("Producto agregado al carrito: %s", nombre)
    return nombre


def obtener_contador_carrito(driver):
    """Devuelve el número del badge del carrito (0 si no se muestra)."""
    badges = driver.find_elements(*CONTADOR_CARRITO)
    return int(badges[0].text) if badges else 0


def ir_al_carrito(driver):
    """Hace clic en el ícono del carrito y espera la página del carrito."""
    esperar_clickeable(driver, LINK_CARRITO).click()
    WebDriverWait(driver, TIEMPO_ESPERA).until(EC.url_contains("/cart.html"))
    logger.info("Navegó al carrito: %s", driver.current_url)


def obtener_nombres_en_carrito(driver):
    """Devuelve los nombres de los productos que hay en el carrito."""
    items = WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.visibility_of_all_elements_located(ITEMS_CARRITO)
    )
    return [item.find_element(*NOMBRE_ITEM).text for item in items]
