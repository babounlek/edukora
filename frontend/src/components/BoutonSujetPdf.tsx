import { useState } from "react"
import { toast } from "sonner"
import { FileDown, Loader2 } from "lucide-react"

import { ouvrirSujetClassique } from "@/api/endpoints"
import { NetworkError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { PastilleQuotaPdf, QuotaPdfComplement, useQuotaPdfBouton } from "@/components/QuotaPdfPastille"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * « Télécharger le sujet » d'une épreuve classique. Le sujet est public mais il est servi par l'API, qui compte le
 * téléchargement dans le quota quotidien : on ne pointe donc plus vers le fichier (un lien direct n'enverrait ni
 * jeton ni cookie, et passerait à côté du compteur).
 *
 * Le compteur tient dans une pastille à l'intérieur du bouton (« 2 restants », « Déjà téléchargé ») : il ne casse plus
 * la rangée d'actions avec une note de deux lignes. La phrase complète reste en infobulle et pour les lecteurs d'écran.
 * Seul un quota épuisé a de quoi dire (heure de remise à zéro, invitation à se connecter) : cela prend alors toute la
 * largeur, sous la rangée.
 */
export function BoutonSujetPdf({ epreuveId, url, grand = false }: { epreuveId: number; url: string; grand?: boolean }) {
  useI18n()
  const [enCours, setEnCours] = useState(false)
  const doc = `lesson:${epreuveId}`
  const etat = useQuotaPdfBouton(doc)

  async function telecharger() {
    if (enCours) return
    setEnCours(true)
    try {
      await ouvrirSujetClassique(url)
    } catch (err) {
      toast.error(err instanceof NetworkError ? err.message : t("gl.pdf_sujet"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className={cn("flex flex-col items-start gap-2", etat.epuise && "basis-full")}>
      <Button
        variant="outline"
        size={grand ? "lg" : "sm"}
        className={cn("rounded-full", grand && "h-12")}
        disabled={enCours}
        onClick={telecharger}
        title={etat.phrase}
      >
        {enCours ? <Loader2 className="animate-spin" /> : <FileDown />}
        {t("ed.telecharger")}
        <PastilleQuotaPdf etat={etat} />
      </Button>
      <QuotaPdfComplement doc={doc} etat={etat} />
    </div>
  )
}
