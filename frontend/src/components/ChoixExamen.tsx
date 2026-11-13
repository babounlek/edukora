import type { ReactNode } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Check, ChevronDown, GraduationCap } from "lucide-react"

import type { Cursus } from "@/api/types"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { libelleCursus, trierCursus } from "@/lib/cursus"
import { useCursusPrepareDeclare } from "@/lib/cursusAccueil"
import { estDeLangue, useCursusListe } from "@/lib/cursusLangue"
import { useDeclarerCursus } from "@/lib/declarerCursus"
import { langueDeListe } from "@/lib/discipline"
import { langueCourante, useI18n } from "@/lib/i18n"
import { cibleApresChangementCursus } from "@/lib/pageApresChangementCursus"
import { cn } from "@/lib/utils"

/**
 * La liste des examens du pays, ouverte depuis n'importe quel déclencheur (`children`, rendu tel quel) : le même menu pour
 * la ligne du hero de l'accueil et pour la pastille de l'en-tête, visiteur comme compte.
 *
 * Elle propose les examens de la langue de l'interface, plus l'examen déjà choisi même s'il est de l'autre langue (voir
 * lib/cursusLangue) : on ne retire jamais à l'élève ce qu'il a déclaré.
 */
export function SelecteurExamen({ children }: { children: ReactNode }) {
  const { t } = useI18n()
  const { country } = useCountry()
  const choisi = useCursusPrepareDeclare(country)
  const { data: liste } = useCursusListe(country, { langue: langueDeListe("", false) })
  const { declarer, enCours } = useDeclarerCursus()
  const navigate = useNavigate()
  const { pathname, search } = useLocation()

  // Changer d'examen laisse l'élève sur sa page : les listes se rechargent pour le nouvel examen. Une page de détail
  // (épreuve, cours...) appartient à l'ancien : on remonte à sa liste (voir pageApresChangementCursus).
  function choisir(cursus: Cursus) {
    const cible = cibleApresChangementCursus(pathname, search, cursus.country?.code ?? country)
    // Un quiz ou une inédite en cours est enregistré (on le reprend), mais on prévient avant de quitter l'écran.
    if (cible.seanceEnCours && !window.confirm(t("choix.quitter_tentative"))) return
    declarer(cursus, () => {
      if (cible.chemin) navigate(cible.chemin, { replace: true })
    })
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>{children}</DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="max-h-80 overflow-y-auto">
        <DropdownMenuLabel>{t("choix.menu_titre")}</DropdownMenuLabel>
        {trierCursus(liste).map((cursus) => {
          const actif = cursus.id === choisi?.id
          return (
            <DropdownMenuItem
              key={cursus.id}
              disabled={enCours}
              onSelect={() => {
                if (!actif) choisir(cursus)
              }}
            >
              {actif ? <Check className="text-primary" /> : <GraduationCap />}
              {libelleCursus(cursus)}
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

/**
 * Dans le hero de l'accueil, à la place de la ligne d'accroche : ce que la personne a déclaré, et le moyen de le changer.
 * Sans cela, le choix n'avait aucun écho sur la page où on l'avait fait (le hero listait toujours « BEPC · Probatoire · BAC »).
 * Un visiteur sans examen déclaré - robots compris - garde l'accroche d'origine (voir CataloguePage).
 *
 * Quand l'examen est de l'autre langue que l'interface, les listes ne sont pas réduites à lui (voir useFiltreCursusParDefaut) :
 * on le dit, au lieu de laisser croire que le choix est ignoré.
 */
export function LigneExamenChoisi({ cursus }: { cursus: Cursus }) {
  const { t } = useI18n()
  const horsLangue = !estDeLangue(cursus, langueCourante())

  return (
    <div className="mb-2">
      <p className="flex flex-wrap items-center gap-x-2 font-display text-sm italic text-primary">
        <span>{t("choix.tu_prepares", { cursus: libelleCursus(cursus) })}</span>
        <SelecteurExamen>
          <button
            type="button"
            className="inline-flex items-center gap-0.5 rounded-sm text-sm not-italic underline underline-offset-4 transition-colors hover:text-primary/80 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            {t("choix.changer")}
            <ChevronDown className="size-3.5 opacity-70" aria-hidden="true" />
          </button>
        </SelecteurExamen>
      </p>
      {horsLangue && <p className="mt-1 text-xs not-italic text-muted-foreground">{t("choix.autre_langue")}</p>}
    </div>
  )
}

/**
 * L'examen préparé, dans l'en-tête, sur toutes les pages : pour un visiteur ou un compte sans abonnement, rien d'autre ne
 * dit où l'on en est de ce choix (le bandeau disparaît dès qu'on a cliqué). Un abonné a déjà sa pastille sur l'accueil
 * (TeteAccueil) et son abonnement dans le menu du compte : il n'en voit pas deux.
 *
 * Sans examen déclaré, rien : c'est le rôle du bandeau (BandeauCursus) de le demander. `className` s'applique à l'enveloppe,
 * pour décider où la pastille se montre (barre ou menu mobile) sans toucher à son affichage propre.
 */
export function PastilleExamen({ className }: { className?: string }) {
  const { t } = useI18n()
  const { isAuthenticated, user } = useAuth()
  const { country } = useCountry()
  const cursus = useCursusPrepareDeclare(country)

  if (!cursus) return null
  if (isAuthenticated && user?.cursus_prepare && user.a_un_abonnement_actif) return null
  const libelle = libelleCursus(cursus)

  return (
    <span className={className}>
      <SelecteurExamen>
        <button
          type="button"
          aria-label={t("choix.pastille_aria", { cursus: libelle })}
          className={cn(
            "inline-flex max-w-full items-center gap-1.5 whitespace-nowrap rounded-full border border-primary/30 bg-primary/5 px-2.5 py-1",
            "text-xs font-medium text-primary transition-colors hover:bg-primary/10",
          )}
        >
          <GraduationCap className="size-3.5 shrink-0" aria-hidden="true" />
          <span className="truncate">{libelle}</span>
          <ChevronDown className="size-3 shrink-0 opacity-60" aria-hidden="true" />
        </button>
      </SelecteurExamen>
    </span>
  )
}
