import { Link } from "react-router-dom"

import { messageLimiteAtteinte, messageRestants } from "@/lib/quotaPdf"
import { useQuotaPdf } from "@/lib/useQuotaPdf"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * « Il te reste 2 téléchargements PDF aujourd'hui. » - à poser près de tout bouton qui télécharge un PDF.
 *
 * Le chiffre vient du serveur (access.quota), le même pour un visiteur, un connecté et un abonné. `doc` : le document
 * du bouton (`cours:<slug>`, `lesson:<id>`, ...) ; s'il est déjà téléchargé aujourd'hui, on le dit - le reprendre ne
 * coûte rien. Tant que le compteur n'est pas là (chargement, réseau coupé) ou si les quotas sont suspendus, rien
 * n'est affiché : le bouton reste utilisable et le serveur décide.
 *
 * Une invitation à se connecter ou à s'abonner n'apparaît que quand le quota est épuisé, et jamais à un abonné.
 */
export function QuotaPdfInfo({ doc, className }: { doc?: string; className?: string }) {
  useI18n()
  const quota = useQuotaPdf(doc)
  if (!quota) return null

  const dejaPris = Boolean(doc) && quota.gratuits.includes(doc as string)
  const epuise = quota.restant <= 0 && !dejaPris

  return (
    <div role="status" aria-live="polite" className={cn("text-sm text-muted-foreground", className)}>
      {dejaPris ? (
        <>
          <p>{t("qpdf.deja")}</p>
          <p>{messageRestants(quota.restant)}</p>
        </>
      ) : epuise ? (
        <>
          <p>{messageLimiteAtteinte(quota)}</p>
          {quota.profil === "visiteur" && (
            <p>
              <Link to="/connexion" className="underline underline-offset-2">{t("qpdf.connecte_toi")}</Link>
            </p>
          )}
          {quota.profil === "connecte" && (
            <p>
              {t("qpdf.abonnement_plus")}{" "}
              <Link to="/tarifs" className="underline underline-offset-2">{t("qpdf.voir_offres")}</Link>
            </p>
          )}
        </>
      ) : (
        <p>{messageRestants(quota.restant)}</p>
      )}
    </div>
  )
}
