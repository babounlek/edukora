import { useState } from "react"
import { toast } from "sonner"

import { marquerExerciceFait } from "@/api/endpoints"
import { formatPoints } from "@/lib/notation"
import { cn } from "@/lib/utils"
import { t, useI18n, type CleI18n } from "@/lib/i18n"

/** Les quatre réponses, en % de l'exercice (voir access.ExerciceFait.PARTS_REUSSIES côté serveur). */
const PARTS: { valeur: number; libelle: CleI18n }[] = [
  { valeur: 0, libelle: "note.part_0" },
  { valeur: 50, libelle: "note.part_50" },
  { valeur: 75, libelle: "note.part_75" },
  { valeur: 100, libelle: "note.part_100" },
]

/** « 5 », « 3.5 », « 2,25 pts » : le barème de l'exercice en nombre, ou null s'il n'est pas lisible. */
function bareme(points: string | null | undefined): number | null {
  if (!points) return null
  const valeur = Number.parseFloat(points.replace(",", "."))
  return Number.isFinite(valeur) && valeur > 0 ? valeur : null
}

/**
 * « Qu'as-tu réussi ? » : après « Exercice validé », l'élève dit ce qu'il a réussi de l'exercice - rien, la
 * moitié, presque tout, tout. Quand le barème est connu, la réponse se traduit en points (« environ 3,75 sur 5 ») :
 * c'est le chiffre qu'il aurait eu à l'examen, pas une note que nous inventons.
 *
 * Avant ce bloc, un exercice d'annale ne connaissait que « fait » : le barème, renseigné sur la plupart des
 * exercices, s'affichait sans jamais servir (audit produit du 2026-11-13). Facultatif : ne pas répondre laisse
 * l'exercice simplement « fait ». Se corrige à volonté ; la déclaration « fait » et ses points restent ceux du
 * bouton « Je l'ai fait » (ValiderResolution, FinExercice), que ce bloc ne remplace pas.
 */
export function PartReussie({
  exerciseId, points, initiale, className,
}: { exerciseId: number; points?: string | null; initiale?: number | null; className?: string }) {
  useI18n()
  const [part, setPart] = useState<number | null>(initiale ?? null)
  const [enCours, setEnCours] = useState(false)
  const total = bareme(points)

  async function choisir(valeur: number) {
    if (enCours || valeur === part) return
    const avant = part
    setPart(valeur)
    setEnCours(true)
    try {
      await marquerExerciceFait(exerciseId, true, valeur)
    } catch {
      // Revenir en arrière sans rien dire laisserait croire que la réponse est enregistrée.
      setPart(avant)
      toast.error(t("note.erreur"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <p className="text-sm font-medium">{t("note.question")}</p>
      <div className="flex flex-wrap gap-2" role="group" aria-label={t("note.question")}>
        {PARTS.map(({ valeur, libelle }) => (
          <button
            key={valeur}
            type="button"
            aria-pressed={part === valeur}
            disabled={enCours}
            onClick={() => choisir(valeur)}
            className={cn(
              "inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-medium transition-colors disabled:opacity-60",
              part === valeur
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:border-primary/50 hover:text-foreground",
            )}
          >
            {t(libelle)}
          </button>
        ))}
      </div>
      {part !== null && total !== null && (
        <p role="status" className="text-sm text-muted-foreground">
          {t("note.points", { obtenus: formatPoints((total * part) / 100), total: formatPoints(total) })}
        </p>
      )}
    </div>
  )
}
