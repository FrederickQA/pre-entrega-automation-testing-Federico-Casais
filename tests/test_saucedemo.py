"""
Casos de prueba sobre saucedemo.com.

Cada test usa su propio navegador (fixtures en conftest.py), por lo que
la falla de uno no afecta a los demás.
"""
import logging

from utils import helpers

logger = logging.getLogger(__name__)


def test_login_exitoso(driver):
    """Login con credenciales válidas redirige al inventario."""
    usuario, password = helpers.cargar_credenciales("valido")
    helpers.login(driver, usuario, password)

    assert "/inventory.html" in driver.current_url, (
        f"No se redirigió al inventario. URL actual: {driver.current_url}"
    )
    assert helpers.esperar_visible(driver, helpers.TITULO_SECCION).text == "Products"
    assert helpers.esperar_visible(driver, helpers.LOGO_APP).text == "Swag Labs"


def test_catalogo_inventario(driver_logueado):
    """El inventario tiene título correcto, productos y elementos de interfaz."""
    driver = driver_logueado

    # Título de la pestaña y de la sección
    assert driver.title == "Swag Labs", f"Título inesperado: {driver.title}"
    assert helpers.esperar_visible(driver, helpers.TITULO_SECCION).text == "Products"

    # Presencia de productos
    productos = helpers.obtener_productos(driver)
    assert len(productos) > 0, "No hay productos visibles en el inventario"
    logger.info("Productos visibles: %d", len(productos))

    # Nombre y precio del primer producto
    primero = helpers.obtener_datos_producto(productos[0])
    logger.info("Primer producto: %s - %s", primero["nombre"], primero["precio"])
    print(f"\nPrimer producto: {primero['nombre']} - {primero['precio']}")
    assert primero["nombre"], "El primer producto no tiene nombre"
    assert primero["precio"].startswith("$"), f"Precio con formato inesperado: {primero['precio']}"

    # Elementos importantes de la interfaz
    assert helpers.esperar_visible(driver, helpers.BOTON_MENU).is_displayed(), "No se ve el menú"
    assert helpers.esperar_visible(driver, helpers.FILTRO_ORDEN).is_displayed(), "No se ve el filtro"
    assert helpers.esperar_visible(driver, helpers.LINK_CARRITO).is_displayed(), "No se ve el carrito"


def test_agregar_producto_al_carrito(driver_logueado):
    """Agregar el primer producto incrementa el contador y aparece en el carrito."""
    driver = driver_logueado

    contador_inicial = helpers.obtener_contador_carrito(driver)
    nombre_agregado = helpers.agregar_primer_producto(driver)

    # El contador del carrito sube en 1
    helpers.esperar_visible(driver, helpers.CONTADOR_CARRITO)
    contador_final = helpers.obtener_contador_carrito(driver)
    assert contador_final == contador_inicial + 1, (
        f"Contador esperado {contador_inicial + 1}, obtenido {contador_final}"
    )

    # El producto aparece en el carrito
    helpers.ir_al_carrito(driver)
    nombres_en_carrito = helpers.obtener_nombres_en_carrito(driver)
    assert nombre_agregado in nombres_en_carrito, (
        f"'{nombre_agregado}' no está en el carrito: {nombres_en_carrito}"
    )
