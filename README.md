# almacen-qr

## 🚀 Cómo ejecutar la API

### 1. Crear entorno virtual

Desde la raíz del proyecto, ejecutá el siguiente comando para crear el entorno virtual:

```bash
python -m venv venv

### 2. Estructura del proyecto
```Para activar el entorno virtual: En Windows (PowerShell): powershell
.\venv\Scripts\Activate.ps1

```En Windows (CMD): cmd
.\venv\Scripts\activate.bat

```En Linux/macOS: bash
source venv/bin/activate

pip install -r requirements.txt

### 3. Estructura del proyecto
/mi-proyecto
│
├── main.py
├── requirements.txt
├── /routers
│   └── tus_modulos.py
└── /venv

### 4. Ejecutar la aplicación
uvicorn main:app --reload

###5. Probar la API
http://127.0.0.1:8000/productos

