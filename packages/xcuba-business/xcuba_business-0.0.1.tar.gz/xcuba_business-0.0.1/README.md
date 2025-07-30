![HD](https://github.com/user-attachments/assets/bf2c1f32-dede-4a3b-81c5-87f744cb7d9a)
# XCuba-Business 🚀

XCuba-Business es una librería async de utilidades diseñado específicamente para desarrolladores cubanos que trabajan en MYPIMES y negocios privados. Esta herramienta busca facilitar y optimizar la gestión empresarial mediante un conjunto completo de módulos integrados.

## 🌟 Características Principales

- 👥 **Gestión de Clientes**: Administración completa de la cartera de clientes
- 🏢 **Gestión Empresarial**: Herramientas para administración de empresas
- 👨‍💼 **Recursos Humanos**: Control de empleados y gestión de personal
- 💰 **Finanzas**: Gestión financiera y contable
- 📦 **Inventario**: Control de stock y productos
- 🛍️ **Productos y Servicios**: Gestión de catálogo y servicios
- 📊 **Reportes**: Generación de informes y análisis
- 📨 **Notificaciones**: Sistema de alertas y notificaciones
- 🔐 **Autenticación y Permisos**: Control de acceso y seguridad

## 📋 Requisitos

- Python 3.6 o superior
- Dependencias listadas en `pyproject.toml`

## 🚀 Instalación

```bash
pip install xcuba-business
```

## 🛠️ Uso Básico

```python
from xcuba_business import clients, inventory, sales

# Gestionar clientes
client = clients.create_client(name="Ejemplo", email="ejemplo@email.com")

# Control de inventario
inventory.add_product(name="Producto", quantity=10)

# Registrar ventas
sales.create_sale(client_id=client.id, products=[{"id": 1, "quantity": 2}])
```

## 🤝 Cómo Contribuir

¡Nos encanta recibir contribuciones! Aquí hay varias formas de participar:

### 1. Reportar Problemas
- Revisa si el problema ya ha sido reportado en la sección de Issues
- Abre un nuevo issue con una descripción clara del problema
- Incluye pasos para reproducir el error
- Menciona tu entorno (sistema operativo, versión de Python, etc.)

### 2. Proponer Mejoras
- Abre un issue describiendo tu propuesta
- Explica por qué sería beneficiosa para el proyecto
- Espera feedback de los mantenedores

### 3. Enviar Código
1. Fork del repositorio
2. Crea una nueva rama para tu feature:
   ```bash
   git checkout -b feature/nombre-caracteristica
   ```
3. Realiza tus cambios siguiendo las guías de estilo
4. Asegúrate de que los tests pasen
5. Commit de tus cambios:
   ```bash
   git commit -m "feat: añade nueva característica"
   ```
6. Push a tu fork:
   ```bash
   git push origin feature/nombre-caracteristica
   ```
7. Crea un Pull Request

### Guías de Contribución

- Sigue las convenciones de código establecidas
- Documenta el nuevo código
- Añade tests para nuevas funcionalidades
- Actualiza la documentación si es necesario

## 📝 Convenciones de Código

- Sigue PEP 8 para estilo de código Python
- Usa type hints cuando sea posible
- Documenta las funciones y clases con docstrings
- Usa nombres descriptivos en español

## 🧪 Tests

Para ejecutar los tests:

```bash
python test/test.py
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto y Soporte

- **Comunidad**: [Grupo de Telegram](https://t.me/KeimaSenpai)
- **Email**: KeimaSenpai@proton.me
- **Documentación**: [GitHub Wiki](https://github.com/KeimaSenpai)

## ✨ Agradecimientos

Gracias a todos los contribuidores que hacen de este proyecto una herramienta útil para la comunidad empresarial cubana.

---

Hecho con ❤️ por KeimaSenpai para la comunidad cubana
