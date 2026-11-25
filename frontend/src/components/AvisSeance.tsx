import { useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"

import { getAvisSeance } from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import { t, useI18n } from "@/lib/i18n"

const AVIS = ["oui", "un_peu", "non"] as const
// Liste fermée, la même que côté serveur (analytics.semaine.MOTIFS) : jamais de texte libre.
const MOTIFS = ["trop_facile", "trop_difficile", "pas_mon_programme", "trop_long", "autre"] as const

const CLE = "edukora:avis-seance"

function dejaRepondu(): boolean {
  try {
    return localStorage.getItem(CLE) === "1"
  } catch {
    return false
  }
}

function retenir() {
  try {
    localStorage.setItem(CLE, "1")
  } catch {
    // Stockage refusé : le serveur ne reposera pas la question à qui a répondu.
  }
}

/**
 * « Cette séance t'a aidé ? » : un toucher, et un motif quand la réponse n'est pas « oui ». La satisfaction des élèves
 * n'était mesurée nulle part (audit du 2026-11-25). C'est le serveur qui dit quand demander : une seule fois, à partir de
 * la troisième séance terminée. La réponse « oui » part tout de suite ; les autres partent avec leur motif, ou sans.
 */
export function AvisSeance({ subjectId, themeId }: { subjectId?: number | null; themeId?: number | null }) {
  useI18n()
  const queryClient = useQueryClient()
  const [ecarte, setEcarte] = useState(dejaRepondu)
  const [avis, setAvis] = useState<(typeof AVIS)[number] | null>(null)
  const [merci, setMerci] = useState(false)
  const { data } = useQuery({
    queryKey: ["avis-seance"],
    queryFn: ({ signal }) => getAvisSeance(signal),
    enabled: !ecarte,
    retry: false,
  })

  if (merci) return <p role="status" className="mt-4 text-sm text-muted-foreground">{t("avs.merci")}</p>
  if (ecarte || !data?.demander) return null

  function envoyer(reponse: (typeof AVIS)[number], motif?: (typeof MOTIFS)[number]) {
    trackEvent("seance_avis", {
      avis: reponse,
      ...(motif ? { motif } : {}),
      ...(subjectId ? { subject_id: subjectId } : {}),
      ...(themeId ? { theme_id: themeId } : {}),
    })
    retenir()
    setMerci(true)
    setEcarte(true)
    queryClient.removeQueries({ queryKey: ["avis-seance"] })
  }

  const bouton = "min-h-11 rounded-full border border-border bg-card px-4 text-sm font-medium hover:border-primary hover:text-primary"
  return (
    <section aria-label={t("avs.question")} className="mt-4 rounded-2xl border border-primary/30 bg-primary/5 p-4">
      <p className="text-sm font-semibold">{avis === null ? t("avs.question") : t("avs.pourquoi")}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {avis === null
          ? AVIS.map((a) => (
              <button key={a} type="button" className={bouton} onClick={() => (a === "oui" ? envoyer(a) : setAvis(a))}>
                {t(`avs.${a}`)}
              </button>
            ))
          : MOTIFS.map((m) => (
              <button key={m} type="button" className={bouton} onClick={() => envoyer(avis, m)}>
                {t(`avs.motif_${m}`)}
              </button>
            ))}
      </div>
      {avis !== null && (
        <button type="button" className="mt-2 min-h-11 text-xs text-muted-foreground underline underline-offset-4" onClick={() => envoyer(avis)}>
          {t("avs.sans_motif")}
        </button>
      )}
    </section>
  )
}
