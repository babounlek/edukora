import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { BookOpen, Check } from "lucide-react"
import { toast } from "sonner"

import { definirMatieres, getMatieres } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { estGce } from "@/lib/cursus"
import { useI18n } from "@/lib/i18n"
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

  const inchange = brouillon === null
  return (
    <div className="flex flex-col gap-3">
      <p className="text-sm text-muted-foreground">{t("matieres.aide")}</p>
      <div className="flex flex-wrap gap-2" role="group" aria-label={t("matieres.titre")}>
        {data.disponibles.map((matiere) => {
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
              )}
            >
              {actif && <Check className="size-3.5" aria-hidden="true" />}
              {matiere.label}
            </button>
          )
        })}
      </div>
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

  if (!actif || !data || data.choisies.length > 0 || data.disponibles.length < 2) return null

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
