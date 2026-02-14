# GTM MX — Go-To-Market Strategy

## Resumen
Estrategia de lanzamiento para el mercado mexicano con **divorcio incausado** como wedge.

---

## Modelos de Negocio

### 1. B2B SaaS — Despachos
| Aspecto | Detalle |
|---|---|
| **Oferta** | Dashboard de pipeline, completeness engine, aprobaciones, recordatorios WhatsApp |
| **Pricing** | Freemium → $3,000-8,000 MXN/mes según volumen |
| **Target** | Despachos de 1-10 abogados en derecho familiar |
| **Canal de venta** | Cold outreach LinkedIn, Google Ads "software despacho abogados", referidos |
| **Métrica clave** | MRR (Monthly Recurring Revenue) |

### 2. B2C Prep Kit — Clientes Finales
| Aspecto | Detalle |
|---|---|
| **Oferta** | Prep Kit gratuito: checklist documentos + preguntas para abogado |
| **Monetización** | Lead generation para despachos B2B (el despacho paga por leads calificados) |
| **Target** | Personas buscando divorcio incausado en Google/WhatsApp |
| **Canal** | SEO, Google Ads, Facebook/Instagram, WhatsApp viral |
| **Métrica clave** | Leads generados por semana, costo por lead |

### 3. B2B2C Partner Routing
| Aspecto | Detalle |
|---|---|
| **Oferta** | Leads B2C auto-ruteados a despachos partner por vertical + región |
| **Monetización** | Incluido en suscripción B2B (upsell: leads premium) |
| **Target** | Despachos que quieren recibir clientes sin hacer marketing |
| **Canal** | Automático vía plataforma |
| **Métrica clave** | Leads ruteados → convertidos por despacho |

---

## Fases de Lanzamiento

### Fase 0: Pre-Piloto (Semana -2 a 0)
- Identificar 10 despachos candidatos en CDMX y Jalisco
- Cold outreach vía LinkedIn + WhatsApp
- Filtrar a 3-5 despachos piloto (ver ICP.md)
- Setup técnico: deploy frontend (Vercel), backend (Render/Fly)

### Fase 1: Piloto (Semanas 1-2)
- Ejecutar PilotPlan.md con 3-5 despachos
- Campañas Google Ads: "divorcio incausado CDMX", "cómo divorciarse en México"
- Facebook Ads: audiencia mujeres 28-45, intereses legales
- Medir todos los KPIs del piloto
- Entrevistar despachos (InterviewScript.md)

### Fase 2: Expansión Regional (Semanas 3-6)
- Escalar a 10-20 despachos en CDMX, Jalisco, Nuevo León
- Agregar verticales: mx_consumer (PROFECO), mx_labor
- Optimizar funnel B2C basado en datos del piloto
- Implementar pricing tier (freemium → paid)

### Fase 3: Escala Nacional (Meses 2-4)
- Expandir a 5+ estados
- SEO content marketing: guías de divorcio por estado
- Partnerships con colegios de abogados
- Implementar WhatsApp Business API real (reemplazar simulación)

---

## Canales de Adquisición

### B2C (Clientes → Prep Kit → Lead)

| Canal | Costo Est. | Volume Est. | CPL Est. |
|---|---|---|---|
| Google Ads "divorcio incausado" | $5,000 MXN/sem | 50-100 clicks | $50-100 MXN |
| Facebook/Instagram Ads | $3,000 MXN/sem | 30-60 clicks | $50-100 MXN |
| SEO (orgánico, medio plazo) | $0 (contenido) | 20-50/sem (mes 3+) | $0 |
| WhatsApp viral / referidos | $0 | 10-20/sem | $0 |

### B2B (Despachos → Suscripción)

| Canal | Costo Est. | Conversión Est. |
|---|---|---|
| Cold LinkedIn outreach | $0 (tiempo) | 5-10% respuesta |
| Google Ads "software abogados" | $2,000 MXN/sem | 2-5% conversión |
| Referidos de despachos piloto | $0 | 20-30% conversión |
| Colegios de abogados | $0 (partnerships) | Variable |

---

## ROI para el Despacho

### Cálculo Base (Divorcio Incausado)

```
Honorarios promedio por divorcio:     $15,000 MXN
Casos nuevos por mes (sin plataforma):     8
Casos nuevos por mes (con plataforma):    12  (+50% por leads B2C)
Incremento en ingresos:               $60,000 MXN/mes

Ahorro en tiempo de coordinación:
  - Antes: 3 horas/caso × 8 casos = 24 horas/mes
  - Después: 1 hora/caso × 12 casos = 12 horas/mes
  - Ahorro: 12 horas/mes × $500/hora = $6,000 MXN/mes

ROI total vs. suscripción de $5,000 MXN/mes:
  - Incremento ingresos: $60,000
  - Ahorro tiempo: $6,000
  - Costo plataforma: -$5,000
  - ROI neto: $61,000 MXN/mes
  - ROI %: 1,220%
```

### Escenario Conservador

```
Incremento casos: +2/mes (en vez de +4)
Ahorro tiempo: 6 horas/mes
ROI neto: $30,000 + $3,000 - $5,000 = $28,000 MXN/mes
ROI %: 560%
```

---

## Métricas de Éxito por Fase

| Fase | Métrica | Target |
|---|---|---|
| Piloto | Despachos activos | 3-5 |
| Piloto | Expedientes aprobados/semana | 5+ |
| Piloto | NPS abogados | > 7 |
| Expansión | MRR | $15,000+ MXN |
| Expansión | Leads B2C/semana | 50+ |
| Expansión | Costo por lead | < $80 MXN |
| Escala | MRR | $100,000+ MXN |
| Escala | Despachos pagando | 20+ |
| Escala | Tasa retención mensual | > 90% |

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Abogados no adoptan dashboard | Alto | Simplificar UX, WhatsApp-first, capacitación 1:1 |
| Clientes no completan Prep Kit | Alto | Reducir pasos, mobile-first, recordatorios |
| Competencia (otros SaaS legales MX) | Medio | Enfoque vertical (divorcio), velocidad de ejecución |
| Regulación UPL (práctica no autorizada) | Alto | Disclaimers claros, aprobaciones obligatorias, no generar documentos legales |
| WhatsApp Business API costosa | Bajo | Empezar con simulación, migrar cuando haya MRR |
