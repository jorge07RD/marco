# Resumen: Configuración de Cloud Build con GitHub

## ✅ Lo Que Hemos Logrado

### 1. **Habilitación de APIs Necesarias**
- ✅ Cloud Build API
- ✅ Secret Manager API
- ✅ Compute Engine API
- ✅ Storage API

### 2. **Configuración de Permisos**
- ✅ Cuenta de servicio de Cloud Build con permisos de Secret Manager Admin
- ✅ Permisos para crear y gestionar secretos

### 3. **Conexión de GitHub**
- ✅ Conexión `marco-github-connection` creada
- ✅ Autorización OAuth completada
- ✅ Token de GitHub guardado en Secret Manager

### 4. **Archivos Creados**
- ✅ `cloudbuild.yaml` - Configuración de build
- ✅ `main.tf` - Infraestructura de Terraform
- ✅ `variables.tf` - Variables de configuración
- ✅ Commit local realizado

---

## ⏳ Pasos Pendientes

### 1. **Hacer Push al Repositorio**

Actualmente tus cambios están en commit local pero no en GitHub:

```bash
# Opción A: Si tienes SSH configurado
git push

# Opción B: Con GitHub CLI
gh auth login
git push

# Opción C: Configurar remote con token
git remote set-url origin https://YOUR_TOKEN@github.com/jorge07RD/marco.git
git push
```

### 2. **Crear el Trigger en la Consola de GCP**

El error de Terraform sugiere que es más fácil crear el trigger manualmente primero:

**URL:** https://console.cloud.google.com/cloud-build/triggers/add?project=niceproyec

**Configuración:**

| Campo | Valor |
|-------|-------|
| **Nombre** | `build-desde-dockerfile` |
| **Región** | `global` |
| **Descripción** | `Construye imagen desde Dockerfile.backend en el repo` |
| **Event** | `Push to a branch` |
| **Source - Repository** | Conecta `jorge07RD/marco` (GitHub App) |
| **Source - Branch** | `^main$` |
| **Configuration Type** | `Cloud Build configuration file (yaml or json)` |
| **Location** | `Repository` |
| **Cloud Build config file** | `/cloudbuild.yaml` |

### 3. **Importar el Trigger a Terraform (Opcional)**

Una vez creado el trigger manualmente, puedes importarlo a Terraform:

```bash
# Primero, obtén el TRIGGER_ID de la consola o con:
gcloud builds triggers list --region=global --project=niceproyec

# Luego, impórtalo:
terraform import google_cloudbuild_trigger.docker_build \
  projects/niceproyec/locations/global/triggers/[TRIGGER_ID]
```

---

## 📄 Archivos Importantes

### `cloudbuild.yaml`
```yaml
steps:
  # Paso 1: Construir la imagen del backend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/mi-app-backend:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/mi-app-backend:latest'
      - '-f'
      - 'Dockerfile.backend'
      - '.'

  # Paso 2: Push de la imagen al registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - 'gcr.io/$PROJECT_ID/mi-app-backend'

images:
  - 'gcr.io/$PROJECT_ID/mi-app-backend:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/mi-app-backend:latest'

timeout: 1200s
```

---

## 🔍 ¿Por Qué el Error de Terraform?

El error `Error 400: Request contains an invalid argument` ocurrió porque:

1. **Problema de vinculación de repositorio**: Aunque conectamos GitHub a GCP mediante OAuth, el repositorio específico necesita ser "vinculado" explícitamente durante la creación del trigger
2. **API de Cloud Build**: La API tiene algunos quirks al crear triggers mediante Terraform que se resuelven más fácilmente desde la consola web
3. **GitHub App vs GitHub OAuth**: La consola maneja mejor la vinculación inicial del repositorio con la GitHub App

---

## 🚀 Qué Pasará Después

Una vez que:
1. Hagas push de `cloudbuild.yaml` al repositorio
2. Crees el trigger en la consola

**Cada vez que hagas `git push` a la rama `main`:**

```
Push to main
     ↓
Cloud Build Trigger se activa
     ↓
Ejecuta cloudbuild.yaml
     ↓
1. Construye imagen Docker con Dockerfile.backend
     ↓
2. Etiqueta imagen con:
   - gcr.io/niceproyec/mi-app-backend:$COMMIT_SHA
   - gcr.io/niceproyec/mi-app-backend:latest
     ↓
3. Push al Container Registry
     ↓
✅ Imagen disponible para deployment
```

---

## 🎯 Verificación Post-Creación

Después de crear el trigger, verifica:

```bash
# Listar triggers
gcloud builds triggers list --region=global --project=niceproyec

# Ver detalles del trigger
gcloud builds triggers describe build-desde-dockerfile \
  --region=global \
  --project=niceproyec

# Ver historial de builds
gcloud builds list --region=global --project=niceproyec
```

---

## 📚 Recursos Creados

| Recurso | ID | Estado |
|---------|-----|--------|
| **Conexión GitHub** | `marco-github-connection` | ✅ Creado y autorizado |
| **Storage Bucket** | `242884135694-datos-bucket` | ✅ Creado |
| **VPC Network** | `terraform-network` | ✅ Creado |
| **Build Trigger** | `build-desde-dockerfile` | ⏳ Pendiente (crear manualmente) |

---

## 🛠️ Troubleshooting

### Si el build falla después de crear el trigger:

1. **Verifica que cloudbuild.yaml existe en la rama main**
   ```bash
   git ls-files | grep cloudbuild.yaml
   ```

2. **Verifica permisos de Cloud Build**
   ```bash
   gcloud projects get-iam-policy niceproyec \
     --flatten="bindings[].members" \
     --filter="bindings.members:serviceAccount:*cloudbuild*"
   ```

3. **Ve los logs del build**
   ```bash
   gcloud builds list --region=global --project=niceproyec
   gcloud builds log [BUILD_ID] --region=global
   ```

---

## 💡 Siguientes Pasos Recomendados

Después de tener el trigger funcionando:

1. **Agregar tests automáticos** en cloudbuild.yaml
2. **Configurar notificaciones** de build (Slack, email)
3. **Agregar deployment automático** a Cloud Run o GKE
4. **Implementar multi-stage builds** para optimizar la imagen

---

✨ **Estamos muy cerca de tener CI/CD completamente configurado!**
