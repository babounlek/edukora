import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, BookOpen, CheckCircle2, Clock, Eye, FileText, Sparkles, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { epreuveDetailPath, epreuveInediteDetailPath } from "@/lib/countryPath"
import { useIsTruncated } from "@/lib/useIsTruncated"
import { actionInedite, libelleAction, libelleFaite } from "@/lib/statutInedite"
import { t, tn, useI18n } from "@/lib/i18n"
import { useAbonneActif } from "@/lib/abonneActif"
import { formatDureeMinutes } from "@/lib/duration"
import { libelleDuree, libelleOrigine, libelleType } from "@/lib/libellesEpreuve"
import { cn } from "@/lib/utils"
import { BadgeInedite } from "@/components/BadgeInedite"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface EpreuveCardProps {
  epreuve: Epreuve
  className?: string
  style?: CSSProperties
  /**
   * Masque le badge de type, pour un contexte qui l'annonce déjà (le rail "Épreuves
   * Inédites", dont les douze cartes le répétaient à l'identique). Jamais dans la
   * grille fusionnée du catalogue, où ce badge est le seul moyen de repérer une
   * inédite parmi trois cent quarante-deux épreuves.
   */
  masquerTypeBadge?: boolean
  // Niveau du titre de la carte : 2 quand la page enchaîne les cartes directement sous son h1
  // (listes filtrables), 3 (défaut) quand elles sont rangées sous un titre de section.
  // Un h3 sans h2 au-dessus saute un niveau, ce que les lecteurs d'écran annoncent comme une rupture.
  niveauTitre?: 2 | 3
}

/** "3 h" pour un classique (texte saisi à la transcription), "90 min" pour une inédite
 * (Blueprint.duree_minutes) - jamais les deux, jamais une durée inventée. */
function dureeAffichee(epreuve: Epreuve): string | null {
  if (epreuve.duree_epreuve) return libelleDuree(epreuve.duree_epreuve)
  if (epreuve.duree_minutes) return formatDureeMinutes(epreuve.duree_minutes)
  return null
}

export function EpreuveCard({ epreuve, className, style, masquerTypeBadge, niveauTitre = 3 }: EpreuveCardProps) {
  useI18n()
  // « Gratuit » et « Lecture libre » n'informent pas un abonné, pour qui tout est ouvert (test élève Gogo).
  const abonne = useAbonneActif()
  const Titre = niveauTitre === 2 ? "h2" : "h3"
  const [titleRef, isTitleTruncated] = useIsTruncated<HTMLHeadingElement>()
  const country = epreuve.subject.country.code.toLowerCase()
  const inedite = epreuve.kind === "inedite"
  // Toujours la fiche détail, jamais le lecteur en direct - qu'il y ait accès ou non. Un clic
  // qui saute la fiche pour un abonné le privait de "Passer en conditions d'examen", proposé
  // UNIQUEMENT là, à côté de "Lire le corrigé" : il ne découvrait jamais ce mode (voir l'audit
  // UX du 2026-09-27). Une inédite n'a de toute façon jamais de lecteur direct (composer crée
  // une tentative, jamais un simple GET) - même destination dans les deux cas désormais.
  const to = inedite
    ? epreuveInediteDetailPath(country, epreuve.slug ?? epreuve.id)
    : epreuveDetailPath(country, epreuve.slug as string)

  const Icone = subjectIcon(epreuve.subject.code)
  const couleur = couleurMatiere(epreuve.subject.code)
  const duree = dureeAffichee(epreuve)
  // Une inédite se REFAIT et se REPREND : « Lu » ne dit rien d'une copie, sa note si.
  const faite = inedite ? libelleFaite(epreuve.mes_tentatives) : null

  /**
   * Métadonnées secondaires. L'année n'y figure que si le titre ne la porte pas déjà, ou
   * s'il la porte mais que le `line-clamp-2` l'a coupée avant qu'elle soit lisible : les
   * titres sont composés côté serveur et finissent presque toujours par l'année, la
   * réafficher quand elle est déjà visible se voyait comme un bégaiement (d'où la mesure
   * de troncature réelle, isTitleTruncated, plutôt qu'un test textuel seul).
   */
  const faits: { icone: typeof Clock; texte: string }[] = []
  if (epreuve.year && (isTitleTruncated || !epreuve.title.includes(String(epreuve.year)))) {
    faits.push({ icone: Clock, texte: t("ep.session", { year: epreuve.year }) })
  }
  // Même règle pour le paper GCE : il termine le titre (« ... GCE A Level 2018 - Paper 1 »), donc
  // c'est la première chose que le line-clamp coupe sur les matières à long intitulé. Sans lui,
  // Paper 1 et Paper 2 d'une même session sont indiscernables dans la grille.
  if (
    epreuve.numero_paper &&
    (isTitleTruncated || !new RegExp(`paper\\s*${epreuve.numero_paper}\\b`, "i").test(epreuve.title))
  ) {
    faits.push({ icone: BookOpen, texte: t("ep.paper", { n: epreuve.numero_paper }) })
  }
  // Et pour « Sujet 1 / Sujet 2 » (SVT, versions alternatives d'un même examen) : même coupe, même remède.
  const sujet = epreuve.variante_sujet_display
  if (sujet && (isTitleTruncated || !epreuve.title.toLowerCase().includes(sujet.toLowerCase()))) {
    faits.push({ icone: BookOpen, texte: sujet })
  }
  if (epreuve.exercises_count > 0) {
    faits.push({
      icone: FileText,
      texte: tn("ep.exercices", epreuve.exercises_count),
    })
  }
  if (duree) faits.push({ icone: Clock, texte: duree })
  if (/^\d+([.,]\d+)?$/.test(epreuve.coefficient.trim())) {
    faits.push({ icone: Sparkles, texte: t("ep.coef", { coef: epreuve.coefficient.trim() }) })
  }

  // origine_display vaut aussi "Épreuve inédite" pour une inédite - déjà porté par le
  // badge couronne, jamais les deux à la fois.
  const provenance =
    !inedite && epreuve.origine !== "OFFICIEL"
      ? epreuve.etablissement
        ? `${libelleOrigine(epreuve.origine, epreuve.origine_display)} - ${epreuve.etablissement}`
        : libelleOrigine(epreuve.origine, epreuve.origine_display)
      : null

  return (
    <Link to={to} className={cn("group block h-full rounded-xl focus-visible:outline-none", className)} style={style}>
      <Card
        className={cn(
          "relative h-full overflow-hidden transition-all duration-300 group-hover:-translate-y-1 group-hover:border-primary/50 group-hover:shadow-lg group-hover:shadow-primary/[0.07] group-focus-visible:ring-2 group-focus-visible:ring-ring",
          // Porte le signal "premium" de la bannière promo jusque dans le catalogue
          // fusionné - sans ça, seul le petit badge Couronne distingue une inédite
          // d'un corrigé classique dans une grille dense.
          inedite && "border-gold/40 group-hover:border-gold/70 group-hover:shadow-gold/10",
        )}
      >
        {/* Filet de matière : repère de couleur d'un coup d'œil dans une grille de 24
            cartes, avant même de lire un titre. Or pour une inédite (signal premium). */}
        <div aria-hidden className={cn("h-1 w-full", inedite ? "bg-gradient-to-r from-gold to-gold/40" : couleur.barre)} />
        <CardContent className="flex h-[calc(100%-0.25rem)] flex-col gap-3 p-4">
          <div className="flex items-start gap-3">
            <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", couleur.puce)}>
              <Icone className="size-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium uppercase tracking-wide text-muted-foreground">
                {epreuve.subject.label}
              </p>
              {/* h3 et non h2 : une carte est un élément DANS une section, pas une section
                  (45 titres de même niveau que les vraies sections rendraient le plan du
                  document inexploitable pour un lecteur d'écran comme pour un moteur de
                  recherche). Seul sur sa ligne : partager avec un badge le ferait tronquer
                  plus tôt et pourrait couper l'année avant qu'elle soit lisible. */}
              <Titre ref={titleRef} className="mt-0.5 line-clamp-2 font-display text-base font-medium leading-snug">
                {epreuve.title}
              </Titre>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {!masquerTypeBadge &&
              (inedite ? (
                <BadgeInedite mini={epreuve.est_mini} />
              ) : (
                <Badge variant={epreuve.lesson_type === "SUJET" ? "gold" : "outline"}>
                  {libelleType(epreuve.lesson_type, epreuve.lesson_type_display)}
                </Badge>
              ))}
            {epreuve.est_vitrine && !abonne && (
              <Badge variant="success" className="gap-1">
                <Sparkles className="size-3" />
                {t("ep.gratuit")}
              </Badge>
            )}
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="secondary">{group.label}</Badge>
            ))}
          </div>

          {(faits.length > 0 || provenance) && (
            <div className="flex flex-col gap-1 text-sm text-muted-foreground">
              {faits.length > 0 && (
                <p className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  {faits.map(({ icone: IconeFait, texte }) => (
                    <span key={texte} className="inline-flex items-center gap-1">
                      <IconeFait className="size-3.5 shrink-0" aria-hidden="true" />
                      {texte}
                    </span>
                  ))}
                </p>
              )}
              {provenance && <p className="truncate" title={provenance}>{provenance}</p>}
            </div>
          )}

          {/* Le pied dit CE QUE LE CLIC FAIT, pas ce qu'on n'a pas : "Abonnement requis"
              écartait avant même d'avoir vu, alors qu'un aperçu gratuit existe. mt-auto :
              l'action s'aligne d'une carte à l'autre quelle que soit la hauteur du contenu. */}
          <div className="mt-auto flex items-center justify-between gap-2 border-t border-border/70 pt-3 text-sm">
            <span className="flex min-w-0 items-center gap-1.5">
              {epreuve.est_vitrine || epreuve.has_access ? (
                <>
                  <Unlock className="size-4 shrink-0 text-success" aria-hidden="true" />
                  <span className="truncate font-medium text-foreground">
                    {inedite
                      ? epreuve.has_access
                        ? libelleAction(actionInedite(epreuve.mes_tentatives))
                        : t("qd.essayer_gratuit")
                      : epreuve.est_vitrine && !abonne ? t("ep.lire_libre") : t("ep.lire_corrige")}
                  </span>
                </>
              ) : (
                <>
                  <Eye className="size-4 shrink-0 text-primary" aria-hidden="true" />
                  <span className="truncate font-medium text-foreground">{t("ep.voir_apercu")}</span>
                </>
              )}
              {(inedite ? faite : epreuve.is_read) && (
                <span className="inline-flex shrink-0 items-center gap-1 text-success">
                  <CheckCircle2 className="size-3.5" aria-hidden="true" />
                  {inedite ? faite : t("ep.lu")}
                </span>
              )}
            </span>
            <ArrowRight
              className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-1"
              aria-hidden="true"
            />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
