import { BoutonPartager } from "@/components/BoutonPartager"
import { useCampagne } from "@/lib/campagne"
import { t, useI18n } from "@/lib/i18n"
import { messageParents, type ContexteMessageParents } from "@/lib/messageParents"
import { cn } from "@/lib/utils"

type Props = Omit<ContexteMessageParents, "campagne"> & {
  className?: string
  variant?: "outline" | "ghost" | "secondary" | "default"
  size?: "sm" | "default" | "lg"
}

/**
 * « Montrer à mes parents » : à poser sous un mur payant. Ce sont les parents qui paient, et l'élève n'avait aucun moyen de leur
 * transmettre son envie. Le bouton partage la page des prix avec un message déjà écrit (voir lib/messageParents) : au téléphone
 * le panneau de partage (WhatsApp...), sur ordinateur WhatsApp ou la copie du lien. Le lien porte le code de parrainage de l'élève.
 */
/**
 * Le message que « Montrer à mes parents » enverra, lisible AVANT l'envoi : le bouton promet « un message tout prêt » et
 * n'ouvrait que « WhatsApp » ou « Copier le lien », sans rien montrer (audit du tunnel visiteur → abonné, 2026-11-21 :
 * deux élèves n'ont pas osé l'envoyer sans savoir ce qu'il disait). Replié : il ne prend qu'une ligne tant qu'on ne
 * l'ouvre pas. Mêmes paramètres que le bouton, pour que l'aperçu soit exactement le texte envoyé.
 */
export function ApercuMessageParents({ examen, contenu, className }: Pick<Props, "examen" | "contenu" | "className">) {
  useI18n()
  const campagne = useCampagne()
  return (
    <details className={cn("text-xs text-muted-foreground", className)}>
      <summary className="cursor-pointer font-medium underline underline-offset-4">{t("parents.voir_message")}</summary>
      <p className="mt-2 whitespace-pre-line rounded-xl border border-border bg-background/70 px-3 py-2.5 text-sm text-foreground">
        {messageParents({ examen, contenu, campagne })}
      </p>
      <p className="mt-1">{t("parents.voir_message_lien")}</p>
    </details>
  )
}

export function BoutonParents({ examen, contenu, className, variant = "outline", size = "default" }: Props) {
  useI18n()
  const campagne = useCampagne()
  return (
    <BoutonPartager
      chemin="/tarifs"
      texte={messageParents({ examen, contenu, campagne })}
      type="parents"
      variant={variant}
      size={size}
      className={className}
      libelle={t("parents.bouton")}
    />
  )
}
