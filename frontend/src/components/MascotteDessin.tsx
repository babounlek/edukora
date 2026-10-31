import { cn } from "@/lib/utils"
import type { HumeurMascotte } from "@/lib/mascotte"

const ETINCELLES = [
  { x: 14, y: 30, delai: "0s" },
  { x: 106, y: 22, delai: "0.4s" },
  { x: 100, y: 62, delai: "0.8s" },
]

/** La bouche suit l'humeur : grand sourire ouvert (fête), sourire (content), petit sourire doux et sourcils levés (courage). */
function Bouche({ humeur }: { humeur: HumeurMascotte }) {
  if (humeur === "fete") {
    return (
      <g>
        <path d="M49 93Q60 112 71 93Z" fill="#7A1F2B" stroke="#12301C" strokeWidth="2" strokeLinejoin="round" />
        <path d="M54 102Q60 97 66 102Q60 107 54 102Z" fill="#F08A8A" />
      </g>
    )
  }
  if (humeur === "content") {
    return <path d="M50 95Q60 106 70 95" fill="none" stroke="#12301C" strokeWidth="2.6" strokeLinecap="round" />
  }
  return (
    <g fill="none" stroke="#12301C" strokeWidth="2.6" strokeLinecap="round">
      <path d="M52 99Q60 104 68 99" />
      <path d="M32 68Q40 63 49 68" />
      <path d="M71 68Q80 63 88 68" />
    </g>
  )
}


/**
 * Le dessin de la mascotte (voir Mascotte pour l'écran de résultat, MascotteReaction pour les réponses du quiz,
 * MascotteJour pour l'accueil) : du SVG animé en CSS, décoratif. `saut` : un compteur qui, en changeant, relance un
 * saut (toucher, nouvelle réponse) ; `parle` : la bouche bouge ; `taille` : la largeur en px.
 */
export function MascotteDessin({
  humeur, parle = false, saut = 0, taille = 84, className,
}: { humeur: HumeurMascotte; parle?: boolean; saut?: number; taille?: number; className?: string }) {
  return (
    <svg
      viewBox="0 0 120 128" width={taille} height={Math.round(taille * 90 / 84)} aria-hidden="true" focusable="false"
      className={cn("mascotte overflow-visible", `mascotte-${humeur}`, className)}
    >
      <ellipse cx="60" cy="123" rx="34" ry="4.5" fill="#000" opacity="0.1" />
      {humeur === "fete" &&
        ETINCELLES.map((e) => (
          <path
            key={e.x} className="mascotte-etincelle" style={{ animationDelay: e.delai }}
            d={`M${e.x} ${e.y - 7}L${e.x + 2.2} ${e.y - 2.2}L${e.x + 7} ${e.y}L${e.x + 2.2} ${e.y + 2.2}L${e.x} ${e.y + 7}L${e.x - 2.2} ${e.y + 2.2}L${e.x - 7} ${e.y}L${e.x - 2.2} ${e.y - 2.2}Z`}
            fill="#F5B82E"
          />
        ))}
      <g key={saut} className={cn("mascotte-corps", saut > 0 && "mascotte-hop")}>
        <g className="mascotte-respire">
          <ellipse cx="44" cy="118" rx="9" ry="5" fill="#0B6623" />
          <ellipse cx="76" cy="118" rx="9" ry="5" fill="#0B6623" />
          <g className="mascotte-bras mascotte-bras-g"><circle cx="9" cy="94" r="7" fill="#39B54A" /></g>
          <g className="mascotte-bras mascotte-bras-d"><circle cx="111" cy="94" r="7" fill="#39B54A" /></g>
          {/* le livre : couverture verte, pages crème */}
          <path fill="#006837" d="M60 64C50 54 28 52 8 58V108C28 104 50 106 60 118C70 106 92 104 112 108V58C92 52 70 54 60 64Z" />
          <path fill="#FFF8E6" d="M60 69C51 60 31 58 14 63V102C31 99 51 101 60 111C69 101 89 99 106 102V63C89 58 69 60 60 69Z" />
          <path d="M60 69V111" stroke="#E3D8B8" strokeWidth="1.5" />
          {/* visage */}
          <g className="mascotte-yeux">
            <ellipse cx="43" cy="83" rx="7" ry="9" fill="#12301C" />
            <ellipse cx="77" cy="83" rx="7" ry="9" fill="#12301C" />
            <circle cx="45.5" cy="79.5" r="2.6" fill="#fff" />
            <circle cx="79.5" cy="79.5" r="2.6" fill="#fff" />
            <circle cx="41.5" cy="86" r="1.2" fill="#fff" />
            <circle cx="75.5" cy="86" r="1.2" fill="#fff" />
          </g>
          <ellipse cx="30" cy="94" rx="6" ry="3.6" fill="#F4A3A3" opacity="0.7" />
          <ellipse cx="90" cy="94" rx="6" ry="3.6" fill="#F4A3A3" opacity="0.7" />
          <g className={cn("mascotte-bouche", parle && "mascotte-parle")}>
            <Bouche humeur={humeur} />
          </g>
          {/* la toque, légèrement penchée */}
          <g transform="rotate(-5 60 50)">
            <path fill="#0B6623" d="M38 46L60 53L82 46V58C82 63 71 66 60 66S38 63 38 58Z" />
            <path fill="#006837" d="M60 18 104 34 60 50 16 34Z" />
            <g className="mascotte-gland">
              <path fill="#F5B82E" d="M96 36.5h3V54h-3z" />
              <circle cx="97.5" cy="57" r="4" fill="#F5B82E" />
            </g>
          </g>
        </g>
      </g>
    </svg>
  )
}
