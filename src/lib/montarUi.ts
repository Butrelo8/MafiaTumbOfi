// La capa de UI del ticket 03 sobre el santuario.
// D, titular que se abre: "Leer más" abre la columna en su sitio, con velo; Escape la cierra y devuelve
// el foco al botón; al dejar la sección se cierra sola. Cerrada, el bloque no scrollea (overflow hidden).
// E, una pieza a la vez: ‹ ›, ←/→ y swipe lateral (los manda montarSantuario como `santuario:paso`).
// Nada scrollea: el gesto vertical siempre es sección.

export function montarUi() {
  for (const boton of document.querySelectorAll<HTMLButtonElement>('[data-abrir]')) {
    const seccion = boton.closest<HTMLElement>('.seccion')!
    const etiqueta = boton.textContent
    const poner = (abierta: boolean) => {
      seccion.toggleAttribute('data-abierta', abierta)
      boton.setAttribute('aria-expanded', String(abierta))
      boton.textContent = abierta ? 'Cerrar' : etiqueta
    }
    boton.addEventListener('click', () => poner(!seccion.hasAttribute('data-abierta')))
    document.addEventListener('keydown', (evento) => {
      if (evento.key !== 'Escape' || !seccion.hasAttribute('data-abierta') || !seccion.classList.contains('activa')) return
      poner(false)
      boton.focus()
    })
    document.addEventListener('santuario:llega', () => {
      if (!seccion.classList.contains('activa')) poner(false)
    })
  }

  for (const seccion of document.querySelectorAll<HTMLElement>('[data-pasos]')) {
    const piezas = [...seccion.querySelectorAll<HTMLElement>('[data-pieza]')]
    let actual = 0
    const mostrar = (paso: number) => {
      actual = (actual + paso + piezas.length) % piezas.length
      piezas.forEach((pieza, indice) => (pieza.hidden = indice !== actual))
    }
    mostrar(0)
    for (const boton of seccion.querySelectorAll<HTMLButtonElement>('[data-paso]')) {
      boton.addEventListener('click', () => mostrar(Number(boton.dataset.paso)))
    }
    seccion.addEventListener('santuario:paso', (evento) => mostrar((evento as CustomEvent<number>).detail))
  }
}
