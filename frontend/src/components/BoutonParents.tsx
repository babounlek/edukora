import { BoutonPartager } from "@/components/BoutonPartager"
import { useCampagne } from "@/lib/campagne"
import { t, useI18n } from "@/lib/i18n"
import { messageParents, type ContexteMessageParents } from "@/lib/messageParents"

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
