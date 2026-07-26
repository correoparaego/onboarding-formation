"""
Script para generar DNIs españoles válidos.
Formato: 8 dígitos + letra de control
La letra se calcula: número % 23 -> índice en "TRWAGMYFPDXBNJZSQVHLCKE"
"""
import random
import pandas as pd

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

def calcular_letra_dni(numero: int) -> str:
    """Calcula la letra de control para un DNI."""
    return LETRAS_DNI[numero % 23]

def generar_dni_valido() -> str:
    """Genera un DNI español válido aleatorio."""
    numero = random.randint(10000000, 99999999)
    letra = calcular_letra_dni(numero)
    return f"{numero}{letra}"

def generar_lista_dnis(cantidad: int) -> list:
    """Genera una lista de DNIs únicos válidos."""
    dnis = set()
    while len(dnis) < cantidad:
        dnis.add(generar_dni_valido())
    return sorted(list(dnis))

if __name__ == "__main__":
    print("\n=== Generando DNIs válidos ===\n")
    
    # Generar 10 DNIs válidos
    dnis = generar_lista_dnis(10)
    
    print("DNIs generados:")
    for i, dni in enumerate(dnis, 1):
        print(f"{i}. {dni}")
    
    # Crear datos de empleados con DNIs válidos
    empleados = [
        {"dni": dnis[0], "name": "Juan Pérez", "position": "Operario", "email": "juan@empresa.com", "phone": "+34600111222"},
        {"dni": dnis[1], "name": "María García", "position": "Técnico", "email": "maria@empresa.com", "phone": "+34600333444"},
        {"dni": dnis[2], "name": "Carlos López", "position": "Operario", "email": "carlos@empresa.com", "phone": "+34600555666"},
        {"dni": dnis[3], "name": "Ana Martínez", "position": "Supervisor", "email": "ana@empresa.com", "phone": "+34600777888"},
        {"dni": dnis[4], "name": "Pedro Sánchez", "position": "Técnico", "email": "pedro@empresa.com", "phone": "+34600999000"},
        {"dni": dnis[5], "name": "Laura Fernández", "position": "Operario", "email": "laura@empresa.com", "phone": "+34600111333"},
        {"dni": dnis[6], "name": "David Rodríguez", "position": "Técnico", "email": "david@empresa.com", "phone": "+34600222444"},
        {"dni": dnis[7], "name": "Sofía González", "position": "Supervisor", "email": "sofia@empresa.com", "phone": "+34600333555"},
        {"dni": dnis[8], "name": "Javier Díaz", "position": "Operario", "email": "javier@empresa.com", "phone": "+34600444666"},
        {"dni": dnis[9], "name": "Elena Moreno", "position": "Técnico", "email": "elena@empresa.com", "phone": "+34600555777"},
    ]
    
    # Crear DataFrame y exportar a Excel
    df = pd.DataFrame(empleados)
    df.to_excel("empleados_ejemplo.xlsx", index=False)
    print(f"\n[OK] Archivo empleados_ejemplo.xlsx actualizado con DNIs válidos")
    
    # También exportar a CSV
    df.to_csv("ejemplo_empleados.csv", index=False)
    print("[OK] Archivo ejemplo_empleados.csv actualizado con DNIs válidos")
    
    print("\n=== DNIs válidos generados ===")
