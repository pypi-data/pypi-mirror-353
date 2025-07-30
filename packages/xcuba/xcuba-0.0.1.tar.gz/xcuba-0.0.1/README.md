# XCuba

Utilitario para desarrolladores cubanos que facilita el cálculo de costos de infraestructura y tasas de cambio.

## Instalación

```bash
pip install xcuba
```

## Características

- Cálculo de costos de servidores VPS basado en recursos (CPU, RAM, Disco)
- Obtención de tasas de cambio actualizadas desde eltoque.com
- Formato JSON para tasas de cambio

## Uso

### Cálculo de Costos de VPS

```python
from xcuba.vps_costo import calcular_costo

# Calcular costo mensual (30 días)
costo_mensual = calcular_costo(cpu=2, ram=4, disco=50)
print(f"Costo mensual: {costo_mensual} CUP")

# Calcular costo diario
costo_diario = calcular_costo(cpu=1, ram=2, por_dia=True)
print(f"Costo diario: {costo_diario} CUP")
```

### Tasas de Cambio

```python
from xcuba.tasa_cambio import tasas_json

# Obtener tasas de cambio en formato JSON
tasas = tasas_json()
print(tasas)
```

## Límites y Validaciones

### VPS
- CPU: 1 a 8 vCores
- RAM: 1 a 16 GB
- Disco: 20 a 500 GB

## Dependencias

- requests
- beautifulsoup4 (bs4)

## Autor

KeimaSenpai (KeimaSenpai@proton.me)

## Enlaces

- [Telegram Community](https://t.me/KeimaSenpai)
- [GitHub](https://github.com/KeimaSenpai)

## Licencia

Este proyecto está bajo la licencia **Creative Commons BY-NC 4.0**  
No se permite el uso comercial sin autorización del autor.  
Debe dar crédito a [Tu Nombre o Usuario] en cualquier uso o derivado.

[Ver licencia completa](https://creativecommons.org/licenses/by-nc/4.0/)
