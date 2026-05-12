# MCP Server Integration

Price Tracker expone un servidor MCP (Model Context Protocol) que permite a herramientas como Claude Code interactuar directamente con tu base de datos de productos.

## Endpoint

`POST /api/mcp/tools/call`

Requiere autenticación JWT via header `Authorization: Bearer <token>`.

## Tools Disponibles

### `get_product_price`

Obtiene el precio actual y metadata de un producto por su ID.

**Parametros:**
- `product_id` (int, requerido)

**Ejemplo:**
```json
{
  "tool": "get_product_price",
  "parameters": {"product_id": 42}
}
```

### `add_product`

Agrega un nuevo producto al tracker.

**Parametros:**
- `url` (string, requerido) - URL del producto
- `nombre` (string, opcional) - Nombre personalizado
- `precio_objetivo` (number, opcional)

**Ejemplo:**
```json
{
  "tool": "add_product",
  "parameters": {
    "url": "https://ejemplo.com/producto",
    "precio_objetivo": 199.99
  }
}
```

### `get_alerts`

Lista todos los productos que han alcanzado su precio objetivo.

**Parametros:** ninguno

### `update_prices`

Fuerza la actualizacion de precios de todos los productos.

**Parametros:** ninguno

### `get_products_list`

Lista todos los productos del usuario autenticado.

**Parametros:** ninguno

### `get_price_history`

Obtiene el historial de precios de un producto.

**Parametros:**
- `product_id` (int, requerido)

## Uso con Claude Code

Configura el MCP server en tu IDE:

```json
{
  "mcpServers": {
    "price-tracker": {
      "url": "https://tu-api.com/api/mcp/tools/call",
      "headers": {
        "Authorization": "Bearer tu-jwt-token"
      }
    }
  }
}
```

## Seguridad

- Todas las herramientas requieren autenticación JWT valida
- Los endpoints respetan las reglas de autorizacion del usuario
- No se exponen datos de otros usuarios

## Respuesta

Todas las herramientas devuelven:

```json
{
  "success": true,
  "data": { ... },
  "message": "string"
}
```

En caso de error:

```json
{
  "success": false,
  "error": "descripcion del error",
  "message": "string"
}
```
