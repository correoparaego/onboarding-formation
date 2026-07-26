"""
Script para probar la importación de empleados y ver el error exacto.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mvp_project.settings")
django.setup()

import io
import pandas as pd
from django.test import Client
from django.contrib.auth.models import User

def test_import():
    """Prueba el endpoint de importación con el archivo de ejemplo."""
    
    # Obtener o crear usuario admin
    admin = User.objects.filter(is_staff=True).first()
    if not admin:
        print("[ERROR] No hay usuario admin en la base de datos")
        return
    
    print(f"[OK] Usando usuario admin: {admin.username}")
    
    # Leer el archivo Excel
    with open("empleados_ejemplo.xlsx", "rb") as f:
        file_content = f.read()
    
    # Crear cliente de prueba
    client = Client()
    client.force_login(admin)
    
    # Hacer la petición
    print("\n[INFO] Enviando archivo al endpoint /api/import...")
    response = client.post(
        "/api/import",
        {"file": io.BytesIO(file_content)},
        format="multipart"
    )
    
    print(f"\n[RESPONSE] Status: {response.status_code}")
    print(f"[RESPONSE] Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n[OK] Importación exitosa:")
        print(f"  - Creados: {data.get('created')}")
        print(f"  - Duplicados: {data.get('duplicates')}")
        print(f"  - Errores: {data.get('errors')}")
        print(f"  - Matrículas creadas: {data.get('enrollments_created')}")
        
        if data.get('report'):
            print(f"\n[REPORTE] Detalle por fila:")
            for row in data['report']:
                status = row.get('status')
                dni = row.get('dni', 'N/A')
                reasons = row.get('reasons', [])
                print(f"  Fila {row.get('row')}: {status} - DNI: {dni}")
                if reasons:
                    print(f"    Razones: {', '.join(reasons)}")
    else:
        print(f"\n[ERROR] Respuesta del servidor:")
        print(response.content.decode('utf-8'))

if __name__ == "__main__":
    print("\n=== Probando importación de empleados ===\n")
    test_import()
    print("\n=== Fin de la prueba ===")
