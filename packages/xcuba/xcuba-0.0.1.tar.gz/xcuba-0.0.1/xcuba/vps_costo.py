# mi_paquete/calculadora.py

def calcular_costo(cpu: int, ram: int, disco: int = 20, por_dia: bool = False) -> float:
    """
    Calcula el costo del servidor en base a CPU, RAM y disco.

    Parámetros:
    - cpu: núcleos de CPU (1 a 8)
    - ram: GB de RAM (1 a 16)
    - disco: GB de almacenamiento SSD (20 a 500), por defecto 20 GB
    - por_dia: si True, devuelve el costo diario; si False, el costo por 30 días.

    Retorna:
    - Costo total en CUP como float (redondeado a 2 decimales)
    """

    # Validaciones
    if not (1 <= cpu <= 8):
        raise ValueError("CPU debe estar entre 1 y 8 vCores")
    if not (1 <= ram <= 16):
        raise ValueError("RAM debe estar entre 1 y 16 GB")
    if not (20 <= disco <= 500):
        raise ValueError("Disco debe estar entre 20 y 500 GB")

    # Tarifas por hora
    tarifa_cpu = 0.04     # CUP/h
    tarifa_ram = 0.05     # CUP/h
    tarifa_disco = 0.01   # CUP/h

    costo_por_hora = (cpu * tarifa_cpu) + (ram * tarifa_ram) + (disco * tarifa_disco)
    horas_por_dia = 24

    if por_dia:
        return round(costo_por_hora * horas_por_dia, 2)
    else:
        return round(costo_por_hora * horas_por_dia * 30, 2)
