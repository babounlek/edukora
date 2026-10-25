const CONFETTI_COULEURS = ["bg-gold", "bg-primary", "bg-success", "bg-info", "bg-warning"]

/**
 * Pluie de confettis pour un beau score - décorative, coupée si mouvement réduit (voir index.css).
 * Des `span` colorés animés en CSS : aucune image, aucune bibliothèque, rien de plus à télécharger.
 */
export function Confettis() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-0 overflow-visible">
      {Array.from({ length: 28 }).map((_, i) => (
        <span
          key={i}
          className={"quiz-confetti-piece " + CONFETTI_COULEURS[i % CONFETTI_COULEURS.length]}
          style={
            {
              left: (i * 37) % 100 + "%",
              animationDelay: (i % 7) * 0.12 + "s",
              "--dx": ((i % 5) - 2) * 26 + "px",
              "--rot": 360 + (i % 4) * 180 + "deg",
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  )
}
