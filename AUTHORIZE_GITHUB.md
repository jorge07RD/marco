# Autorizar GitHub con Cloud Build

## 🎯 Paso Actual: Autorización OAuth

La conexión `marco-github-connection` está creada pero necesita autorización.

## 🌐 Link de Autorización

**Abre este link en tu navegador:**

```
https://accounts.google.com/AccountChooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fm%2Fgcb%2Fgithub%2Flocations%2Fsouthamerica-east1%2Foauth_v2%3Fconnection_name%3Dprojects%252F242884135694%252Flocations%252Fsouthamerica-east1%252Fconnections%252Fmarco-github-connection
```

## 📋 Pasos a Seguir

1. **Abre el link de arriba** en tu navegador
2. **Inicia sesión** con tu cuenta de Google (`jorge.beriguete.mateo@gmail.com`)
3. **Selecciona tu cuenta** de GitHub
4. **Autoriza Cloud Build** para acceder a tu cuenta de GitHub
5. **Acepta los permisos** que solicita

## ✅ Verificación

Después de autorizar, ejecuta este comando para verificar:

```bash
gcloud beta builds connections describe marco-github-connection \
  --region=southamerica-east1 \
  --project=niceproyec
```

El `installationState.stage` debe cambiar de `PENDING_USER_OAUTH` a `COMPLETE`.

## 🔗 Conectar el Repositorio

Una vez autorizado, necesitarás conectar tu repositorio específico:

```bash
# Listar repositorios disponibles
gcloud beta builds repositories list \
  --connection=marco-github-connection \
  --region=southamerica-east1 \
  --project=niceproyec
```

## 🚀 Siguiente Paso: Terraform

Una vez completada la autorización y conectado el repo, ejecuta:

```bash
terraform plan
terraform apply
```
