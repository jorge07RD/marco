#!/bin/bash
# Script para verificar la configuración actual de Cloud Run

echo "🔍 Verificando servicio Cloud Run..."
echo ""

gcloud run services describe marco \
  --region=southamerica-east1 \
  --format="table(
    spec.template.spec.containers[0].env[].name,
    spec.template.spec.containers[0].env[].value
  )"

echo ""
echo "🌐 Verificando si ENVIRONMENT está configurado..."
gcloud run services describe marco \
  --region=southamerica-east1 \
  --format="value(spec.template.spec.containers[0].env.filter(name:ENVIRONMENT).value)"

echo ""
echo "🔐 Verificando si SECRET_KEY está configurado..."
gcloud run services describe marco \
  --region=southamerica-east1 \
  --format="value(spec.template.spec.containers[0].env.filter(name:SECRET_KEY).value)" | head -c 20
echo "..."
