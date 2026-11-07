import { useState } from "react"
import { useLocation } from "react-router-dom"
import { Check, Copy, MessageCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useCodeAssistance } from "@/lib/aide/hooks"
import { lienContactAide } from "@/lib/aide/contact"
import { trackEvent } from "@/lib/analytics"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * « Tu n'as pas trouvé ta réponse ? » : le bouton WhatsApp du support, avec un message déjà commencé (code d'assistance,
 * article lu, page, appareil) et, pour un compte connecté, le code d'assistance lisible et copiable.
 * `source` dit d'où l'on écrit (centre, article, panneau) pour savoir quels articles n'ont pas suffi.
 */
export function ContactAide({
  source, article, titre = true, className,
}: { source: "centre" | "article" | "panneau"; article?: { slug: string; titre: string }; titre?: boolean; className?: string }) {
  useI18n()
  const { pathname } = useLocation()
  const code = useCodeAssistance()
  const [copie, setCopie] = useState(false)

  async function copier() {
    if (!code) return
    try {
      await navigator.clipboard.writeText(code)
      setCopie(true)
      window.setTimeout(() => setCopie(false), 2000)
    } catch {
      // Presse-papiers indisponible (navigateur ancien, page non sécurisée) : le code reste affiché et sélectionnable.
    }
  }

  return (
    <section aria-labelledby="aide-contact-titre" className={cn("rounded-2xl border border-border bg-card p-5", className)}>
      {titre && (
        <h2 id="aide-contact-titre" className="font-display text-lg font-semibold">
          {t("aide.contact.titre")}
        </h2>
      )}
      <p className={cn("text-sm text-muted-foreground", titre && "mt-1")}>{t("aide.contact.texte")}</p>
      <Button asChild className="mt-4 min-h-11 w-full sm:w-auto">
        <a
          href={lienContactAide({ code, article: article?.titre, page: pathname })}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => trackEvent("aide_contact_clic", { source, ...(article ? { slug: article.slug } : {}) })}
        >
          <MessageCircle className="size-4" aria-hidden="true" />
          {t("aide.contact.bouton")}
        </a>
      </Button>
      {code && (
        <div className="mt-4 border-t border-border pt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{t("aide.contact.code")}</p>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <code className="rounded-md bg-muted px-2.5 py-1.5 font-mono text-base font-semibold tracking-wider select-all">{code}</code>
            <Button type="button" variant="outline" size="sm" className="min-h-9" onClick={copier}>
              {copie ? <Check className="size-4" aria-hidden="true" /> : <Copy className="size-4" aria-hidden="true" />}
              {copie ? t("aide.contact.copie") : t("aide.contact.copier")}
            </Button>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">{t("aide.contact.code_aide")}</p>
        </div>
      )}
    </section>
  )
}
