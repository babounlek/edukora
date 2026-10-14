import { Languages } from "lucide-react"

import { useAuth } from "@/context/AuthContext"
import { ouvrirDansLangue, useI18n } from "@/lib/i18n"
import { langueImposee } from "@/lib/langueProfil"
import { Button } from "@/components/ui/button"

/**
 * Un élève dont le cursus est français qui ouvre un lien `/en/...` (un camarade du GCE lui envoie un
 * corrigé) lit la page en anglais : un lien explicite est respecté, jamais bloqué. Ce bandeau le lui dit
 * et propose la version française de la même page. Le cas inverse (cursus anglais, page française) n'existe
 * pas : la page est alors renvoyée d'office vers sa version `/en` (voir useSynchroLangueCompte).
 */
export function BandeauLangueCursus() {
  const { t, langue } = useI18n()
  const { user } = useAuth()
  if (langue !== "en" || langueImposee(user) !== "fr") return null

  return (
    <div role="region" aria-label={t("bandeau_langue.aria")} className="border-b border-border bg-muted/50">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2 text-sm sm:px-6">
        <Languages className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
        <p className="flex-1 text-muted-foreground">{t("bandeau_langue.texte")}</p>
        <Button type="button" size="sm" variant="outline" lang="fr" onClick={() => ouvrirDansLangue("fr")}>
          {t("bandeau_langue.bouton")}
        </Button>
      </div>
    </div>
  )
}
