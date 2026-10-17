import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { BookOpen, Check } from "lucide-react"
import { toast } from "sonner"

import { definirMatieres, getMatieres } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import type { AvertissementInscription, MatiereOfficielle } from "@/api/types"
import { estGce } from "@/lib/cursus"
import { tn, useI18n } from "@/lib/i18n"
import { avertissementsInscription } from "@/lib/inscription"
import { cn } from "@/lib/utils"

/** Données qui dépendent des matières choisies : à relire après un changement. */
const CLES_A_RELIRE = [["accueil"], ["plan-du-jour"], ["parcours-resume"], ["priorites"]] as const

function useMatieres() {
  const { user } = useAuth()
  const cursusId = user?.cursus_prepare?.id
  const actif = estGce(user?.cursus_prepare)
  const requete = useQuery({
    queryKey: ["matieres", cursusId],
    queryFn: ({ signal }) => getMatieres(signal),
    enabled: actif && Boolean(cursusId),
  })
  return { actif, cursusId, ...requete }
}

/** Phrase d'un avertissement d'inscription : toujours un conseil, jamais un blocage. */
function texteAvertissement(
  a: AvertissementInscription,
  libelleDe: (code?: string) => string,
  maximum: number | null,
  t: (cle: "matieres.av_minimum" | "matieres.av_maximum" | "matieres.av_obligatoire" | "matieres.av_derniere", v?: Record<string, string | number>) => string,
): string {
  if (a.code === "minimum") return t("matieres.av_minimum", { attendu: a.attendu ?? "", actuel: a.actuel ?? "" })
  if (a.code === "maximum") return t("matieres.av_maximum", { attendu: a.attendu ?? "", actuel: a.actuel ?? "" })
  if (a.code === "obligatoire") return t("matieres.av_obligatoire", { matiere: libelleDe(a.matiere) })
  return t("matieres.av_derniere", { max: maximum ?? "", matiere: libelleDe(a.matiere) })
}

/**
 * « Mes matières » : au GCE il n'y a pas de série qui fixe le programme, l'élève passe 5 à 8
 * matières qu'il choisit. Le plan du jour, les priorités et la progression se limitent à ce choix
 * (voir quiz.matieres côté serveur) ; la bibliothèque reste ouverte à tout. Aucun choix = toutes
 * les matières, comme pour un élève du BAC.
 */
export function ChoixMatieres({ onEnregistre }: { onEnregistre?: () => void }) {
  const { t } = useI18n()
  const queryClient = useQueryClient()
  const { cursusId, data, isError } = useMatieres()
  // null = rien touché : on montre le choix enregistré.
  const [brouillon, setBrouillon] = useState<number[] | null>(null)
  const choisies = brouillon ?? data?.choisies ?? []

  const enregistrer = useMutation({
    mutationFn: (ids: number[]) => definirMatieres(ids),
    onSuccess: (reponse) => {
      queryClient.setQueryData(["matieres", cursusId], reponse)
      CLES_A_RELIRE.forEach((cle) => queryClient.invalidateQueries({ queryKey: cle }))
      setBrouillon(null)
      toast.success(t("matieres.enregistre"))
      onEnregistre?.()
    },
    onError: () => toast.error(t("matieres.erreur")),
  })

  if (isError) return <p role="alert" className="text-sm text-muted-foreground">{t("matieres.erreur")}</p>
  if (!data) return <p className="text-sm text-muted-foreground">{t("matieres.chargement")}</p>

  function basculer(id: number) {
    setBrouillon(choisies.includes(id) ? choisies.filter((i) => i !== id) : [...choisies, id])
  }

  // Au GCE (branche générale) le serveur envoie toutes les matières du Board à ce niveau et leurs règles ; sinon (ou
  // serveur plus ancien) on retombe sur la liste des matières qui ont du contenu, sans règles.
  const officielles: MatiereOfficielle[] = data.officielles ?? []
  const modeBoard = officielles.length > 0
  const liste: MatiereOfficielle[] = modeBoard
    ? officielles
    : data.disponibles.map((m) => ({ ...m, code_officiel: null, couverte: true, obligatoire: false }))
  const connues = [...liste, ...data.disponibles.filter((d) => !liste.some((m) => m.id === d.id))]
  const regles = modeBoard ? data.regles : null
  const avertissements = avertissementsInscription(
    regles,
    connues.filter((m) => choisies.includes(m.id)).map((m) => m.code),
  )
  const libelleDe = (code?: string) => connues.find((m) => m.code === code)?.label ?? code ?? ""
  const aDesNonCouvertes = liste.some((m) => !m.couverte)

  const inchange = brouillon === null
  return (
    <div className="flex flex-col gap-3">
      <p className="text-sm text-muted-foreground">{t("matieres.aide")}</p>
      {regles && choisies.length > 0 && (
        <p className="text-sm font-medium" aria-live="polite">
          {tn(regles.minimum !== null ? "matieres.compteur_plage" : "matieres.compteur_max", choisies.length, {
            min: regles.minimum ?? "",
            max: regles.maximum ?? "",
          })}
        </p>
      )}
      <div className="flex flex-wrap gap-2" role="group" aria-label={t("matieres.titre")}>
        {liste.map((matiere) => {
          const actif = choisies.includes(matiere.id)
          return (
            <button
              key={matiere.id}
              type="button"
              aria-pressed={actif}
              onClick={() => basculer(matiere.id)}
              className={cn(
                "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3 text-sm font-medium transition-colors",
                actif
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:border-primary/50 hover:text-foreground",
                !matiere.couverte && !actif && "border-dashed opacity-60",
              )}
            >
              {actif && <Check className="size-3.5" aria-hidden="true" />}
              {matiere.label}
              {matiere.obligatoire && <span className="text-xs font-normal">· {t("matieres.obligatoire")}</span>}
              {!matiere.couverte && <span className="text-xs font-normal italic">· {t("matieres.bientot")}</span>}
            </button>
          )
        })}
      </div>
      {avertissements.length > 0 && (
        <ul role="status" className="flex list-disc flex-col gap-1 pl-5 text-sm text-amber-700 dark:text-amber-400">
          {avertissements.map((a, i) => (
            <li key={`${a.code}-${a.matiere ?? i}`}>{texteAvertissement(a, libelleDe, regles?.maximum ?? null, t)}</li>
          ))}
        </ul>
      )}
      {modeBoard && (
        <div className="flex flex-col gap-1 text-xs text-muted-foreground">
          {aDesNonCouvertes && <p>{t("matieres.non_couverte_aide")}</p>}
          <p>{t("matieres.regles_note")}</p>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          size="sm"
          className="min-h-9 rounded-full"
          disabled={inchange || enregistrer.isPending}
          onClick={() => enregistrer.mutate(choisies)}
        >
          {t("matieres.enregistrer")}
        </Button>
        {choisies.length > 0 && (
          <Button
            size="sm"
            variant="ghost"
            className="min-h-9 rounded-full"
            disabled={enregistrer.isPending}
            onClick={() => setBrouillon([])}
          >
            {t("matieres.toutes")}
          </Button>
        )}
      </div>
    </div>
  )
}

/**
 * Sur l'accueil d'un élève du GCE qui n'a pas encore dit quelles matières il passe : une invitation,
 * pas un écran bloquant - son plan existe déjà, il sera simplement plus large. Disparaît dès qu'un
 * choix est enregistré, et n'apparaît jamais hors GCE ni quand il n'y a rien à choisir.
 */
export function InvitationMatieres() {
  const { t } = useI18n()
  const { actif, data } = useMatieres()
  const [ouvert, setOuvert] = useState(false)

  const nbChoix = data?.officielles?.length || data?.disponibles.length || 0
  if (!actif || !data || data.choisies.length > 0 || nbChoix < 2) return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
      <div className="rounded-2xl border border-primary/30 bg-primary/5 p-4 sm:p-5">
        <div className="flex items-start gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <BookOpen className="size-4" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold">{t("matieres.invitation_titre")}</p>
            <p className="text-sm text-muted-foreground">{t("matieres.invitation_texte")}</p>
          </div>
          {!ouvert && (
            <Button size="sm" className="shrink-0 rounded-full" onClick={() => setOuvert(true)}>
              {t("matieres.invitation_bouton")}
            </Button>
          )}
        </div>
        {ouvert && (
          <div className="mt-4 border-t border-border pt-4">
            <ChoixMatieres />
          </div>
        )}
      </div>
    </section>
  )
}

/** Dans la page du compte : la section « Mes matières », seulement pour un élève du GCE. */
export function useAfficherChoixMatieres(): boolean {
  const { user } = useAuth()
  return estGce(user?.cursus_prepare)
}
