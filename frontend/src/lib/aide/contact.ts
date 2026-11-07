import { CONTACT_WHATSAPP_URL, SITE_NAME } from "@/lib/site"
import { t } from "@/lib/i18n"

export interface ContexteContact {
  /** Le code d'assistance du compte connecté (jamais un numéro ni une adresse e-mail : ils ne vont pas dans une URL). */
  code?: string | null
  /** Titre de l'article d'où l'on écrit. */
  article?: string
  /** Chemin de la page où l'on se trouve. */
  page?: string
}

function appareil(): string {
  if (typeof navigator === "undefined") return ""
  return /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent) ? "mobile" : "ordinateur"
}

/**
 * Le lien WhatsApp du support avec un message déjà commencé. Il porte ce qui évite les allers-retours (code d'assistance,
 * article lu, page, type d'appareil) et rien de personnel au-delà : ni téléphone, ni e-mail, ni nom.
 */
export function lienContactAide(contexte: ContexteContact = {}): string {
  const lignes = [t("aide.contact.message_intro", { site: SITE_NAME })]
  if (contexte.code) lignes.push(t("aide.contact.message_code", { code: contexte.code }))
  if (contexte.article) lignes.push(t("aide.contact.message_article", { article: contexte.article }))
  if (contexte.page) lignes.push(t("aide.contact.message_page", { page: contexte.page }))
  const type = appareil()
  if (type) lignes.push(t("aide.contact.message_appareil", { appareil: type }))
  lignes.push("", t("aide.contact.message_question"))
  return `${CONTACT_WHATSAPP_URL}?text=${encodeURIComponent(lignes.join("\n"))}`
}
