"""
XCuba - Paquete de Cálculo de Costos de Infraestructura y tasas de cambio

Ejemplos
```python
from xcuba.calculadora import calcular_costo

print(calcular_costo(cpu=2, ram=4, disco=50))  # Por defecto: costo mensual
print(calcular_costo(cpu=1, ram=2, por_dia=True))  # Disco por defecto (20 GB), costo diario
```

Tasas de cambio
```python
from xcuba.cambio import tasas_json
print(tasas_json())  # Obtiene tasas de cambio en formato JSON
```
"""