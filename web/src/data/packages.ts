/**
 * Homepage booking packages (placeholder tiers). Edit features and names before production.
 */
export type PackageTier = {
  id: string
  name: string
  description: string
  features: string[]
  cta: { label: string; href: string }
  /** Middle tier highlighted in UI */
  featured?: boolean
}

export const packageTiers: PackageTier[] = [
  {
    id: 'basico',
    name: 'Básico',
    description: 'Show compacto para espacios chicos o horarios cortos.',
    features: [
      'Set de ~90 minutos (setlist preseleccionada)',
      'Formación estándar del grupo',
      'Coordinación previa por correo o WhatsApp',
    ],
    cta: { label: 'Solicitar este paquete', href: '/contratacion' },
  },
  {
    id: 'completo',
    name: 'Completo',
    description: 'La opción más pedida para fiestas y eventos medianos.',
    features: [
      'Set extendido + cambios de ambiente (setlist + 3 elecciones de tu agrado)',
      'Equipo de sonido propio incluido',
      'Asesoría de repertorio según tipo de público',
    ],
    cta: { label: 'Solicitar este paquete', href: '/contratacion' },
    featured: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    description: 'Producción más cuidada para fechas especiales o foráneas con setlist a elección.',
    features: [
      'Logística prioritaria y tiempos flexibles (placeholder)',
      'Opciones de formato / ensamble ampliado bajo cotización',
      'Soporte cercano en día del evento',
    ],
    cta: { label: 'Solicitar este paquete', href: '/contratacion' },
  },
]
