# Plan de Piloto MX — 14 Días

## Objetivo
Validar el wedge de **divorcio incausado express** con 3-5 despachos en CDMX/Jalisco.

**North Star Metric:** Expedientes listos y aprobados por semana por despacho.

---

## Semana 1: Setup + Primeros Intakes (Días 1-7)

### Día 1-2: Onboarding
- [ ] Registrar 3-5 despachos piloto (B2B onboard endpoint)
- [ ] Configurar credenciales del despacho (cédula profesional, ubicación, horarios, WhatsApp)
- [ ] Capacitar al abogado titular en el dashboard (pipeline, docs, aprobaciones)
- [ ] Verificar que el widget de intake funciona en el sitio del despacho

### Día 3-4: Primeros Leads B2C
- [ ] Lanzar 3 campañas UTM para divorcio incausado:
  - Google Ads: "divorcio incausado [ciudad]"
  - Facebook/Instagram: audiencia mujeres 28-45, CDMX
  - WhatsApp Status del despacho piloto
- [ ] Monitorear leads entrantes en `/app/leads`
- [ ] Verificar que el routing asigna leads al despacho correcto por entidad federativa

### Día 5-7: Primer Ciclo Completo
- [ ] Primer cliente completa Prep Kit en `/help`
- [ ] Despacho recibe lead + intake en pipeline
- [ ] Cliente sube documentos (acta de matrimonio, INE, CURP, domicilio)
- [ ] Completeness engine muestra progreso
- [ ] WhatsApp reminder se genera para documentos faltantes
- [ ] Abogado aprueba expediente borrador
- [ ] Medir: tiempo desde intake hasta expediente aprobado

---

## Semana 2: Iteración + Métricas (Días 8-14)

### Día 8-10: Volumen + Feedback
- [ ] Target: 10+ intakes por despacho
- [ ] Recoger feedback de abogados (InterviewScript.md)
- [ ] Recoger feedback de clientes (modal de feedback en /help)
- [ ] Ajustar checklist de documentos según feedback real
- [ ] Verificar SLA nudges (aprobaciones pendientes > 4h)

### Día 11-12: Métricas y Ajustes
- [ ] Revisar analytics dashboard:
  - Tasa de conversión: visita → prep kit → lead
  - Tasa de completeness: docs faltantes promedio
  - Tiempo promedio: intake → expediente aprobado
  - NPS de abogados y clientes
- [ ] Iterar UI según datos (¿dónde abandonan los clientes?)
- [ ] Ajustar pipeline stages si el flujo real difiere

### Día 13-14: Decisión Go/No-Go
- [ ] Compilar resultados del piloto
- [ ] Entrevistar a cada despacho piloto (ver InterviewScript.md)
- [ ] Calcular ROI por despacho (ver GTM_MX.md)
- [ ] Decisión: escalar a 10-20 despachos o pivotar vertical

---

## KPIs del Piloto

| Métrica | Target Semana 1 | Target Semana 2 |
|---|---|---|
| Despachos activos | 3 | 5 |
| Intakes totales | 15 | 50+ |
| Prep Kits generados | 10 | 30+ |
| Expedientes aprobados | 3 | 10+ |
| Tiempo intake→aprobado | < 72h | < 48h |
| Completeness promedio | 60% | 80%+ |
| NPS abogados | > 7 | > 8 |
| NPS clientes | > 6 | > 7 |

---

## Criterios Go/No-Go

### GO (escalar a 10-20 despachos)
- 3+ despachos activos con > 5 expedientes aprobados
- Tiempo intake→aprobado < 48h consistente
- NPS abogados > 7
- Al menos 1 despacho dispuesto a pagar

### NO-GO (pivotar)
- < 2 despachos activos después de 14 días
- Los abogados no usan el dashboard (vuelven a WhatsApp manual)
- Los clientes abandonan el Prep Kit antes de completar
- El checklist de documentos no es útil según los abogados

---

## Recursos Necesarios

| Recurso | Costo Estimado |
|---|---|
| Google Ads (divorcio incausado) | $3,000 MXN / semana |
| Facebook Ads | $2,000 MXN / semana |
| Vercel hosting (frontend) | Gratis (hobby tier) |
| Backend hosting (Render/Fly) | $5-10 USD/mes |
| Tiempo del equipo | 2 personas, 50% dedicación |
