import { useEffect, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { Loader2, ShieldAlert, UserCircle } from "lucide-react"

import { listProfils } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { activerProfilProtege } from "@/lib/changerProfilActif"
import { PinAnnule } from "@/lib/pinPrompts"
import type { Profil } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useSeo } from "@/lib/seo"
import { destinationApresConnexion, ouvrirDestination } from "@/lib/apresConnexion"
import { catalogueHomePath } from "@/lib/countryPath"
import { useCountry } from "@/context/CountryContext"
import { langueCourante, t, urlAnglaiseExplicite, useI18n } from "@/lib/i18n"

const CLE_RAPPEL = "qe-rappel-code-parent-masque"

function rappelDejaMasque(): boolean {
  try {
    return localStorage.getItem(CLE_RAPPEL) === "1"
  } catch {
    return false
  }
}

/**
 * "Qui étudie ?" - affiché une seule fois, juste après la connexion, pour un compte
 * qui a déjà déclaré au moins deux enfants (voir les deux appels à `login()` dans
 * LoginPage.tsx, seuls points d'entrée vers cette page). Jamais montré au fil des
 * pages suivantes : le choix, une fois fait, vit dans la claim `profil_id` du token
 * (voir users.profils.profil_actif) et survit aux rechargements via le cookie de
 * refresh - jamais besoin de le redemander avant la prochaine connexion.
 */
export function QuiEtudiePage() {
  useI18n()
  useSeo({ title: t("qe.seo") })

  const { isAuthenticated, isLoading, login, user } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const location = useLocation()
  const demandee = (location.state as { from?: string } | null)?.from
  const redirectTo = demandee ?? catalogueHomePath(country)

  const [profils, setProfils] = useState<Profil[] | null>(null)
  const [activatingId, setActivatingId] = useState<number | null>(null)
  const [rappelMasque, setRappelMasque] = useState(rappelDejaMasque)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { replace: true })
      return
    }
    listProfils()
      .then((data) => {
        // Arrivée directe sur l'URL (lien partagé, retour arrière...) sur un compte à
        // un seul profil : rien à choisir, on ne bloque jamais l'accès pour ça.
        if (data.length <= 1) {
          navigate(redirectTo, { replace: true })
          return
        }
        setProfils(data)
      })
      .catch(() => navigate(redirectTo, { replace: true }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoading, isAuthenticated])

  async function choisir(profil: Profil) {
    setActivatingId(profil.id)
    try {
      const response = await activerProfilProtege(profil.id, profil.prenom)
      login(response.access, response.user)
      // Le pays et la langue sont ceux du profil choisi ; la page demandée à l'origine est conservée.
      ouvrirDestination(
        destinationApresConnexion({
          user: response.user,
          demandee,
          paysNavigation: country,
          courante: langueCourante(),
          urlExplicite: urlAnglaiseExplicite(),
          changement: true,
        }),
        navigate,
      )
    } catch (err) {
      setActivatingId(null)
      // Annuler la saisie du code PIN est un choix de l'élève, pas une panne : pas de message.
      if (err instanceof PinAnnule) return
      toast.error(err instanceof ApiError ? err.message : t("qe.erreur"))
    }
  }

  // Même constat que l'avertissement de « Mes accès » : ni code parent ni code d'enfant, donc chacun voit les
  // abonnements des autres. C'est ici, au moment de choisir qui étudie, que ce constat a le plus de sens.
  const rappel = !rappelMasque && !!profils && !user?.pin_parent_actif && profils.every((p) => !p.pin_actif)

  function masquerRappel() {
    setRappelMasque(true)
    try {
      localStorage.setItem(CLE_RAPPEL, "1")
    } catch {
      // Stockage indisponible : le rappel reste masqué pour cette visite seulement.
    }
  }

  if (isLoading || profils === null) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-sm flex-col justify-center px-4 py-12">
      <div className="mb-6 text-center">
        <h1 className="font-display text-2xl font-semibold tracking-tight">{t("qe.seo")}</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">
          {t("qe.texte")}
        </p>
      </div>
      <div className="flex flex-col gap-2.5">
        {profils.map((profil) => (
          <Card key={profil.id} className="overflow-hidden">
            <CardContent className="p-0">
              <button
                type="button"
                onClick={() => choisir(profil)}
                disabled={activatingId !== null}
                className="flex w-full items-center gap-3 px-4 py-3.5 text-left transition-colors hover:bg-accent disabled:opacity-60"
              >
                <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <UserCircle className="size-5" />
                </span>
                <span className="flex-1 font-display text-base font-medium">
                  {profil.prenom || t("compte.profil_sans_nom")}
                </span>
                {activatingId === profil.id && <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />}
              </button>
            </CardContent>
          </Card>
        ))}
      </div>
      {rappel && (
        <div className="mt-5 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
          <p className="flex items-start gap-2 text-xs text-muted-foreground">
            <ShieldAlert className="mt-0.5 size-4 shrink-0 text-amber-600" aria-hidden="true" />
            {t("sp.rappel")}
          </p>
          <div className="flex gap-2">
            <Button asChild size="sm" className="h-11 sm:h-8">
              <Link to="/mes-acces#securite">{t("sp.rappel_lien")}</Link>
            </Button>
            <Button type="button" variant="ghost" size="sm" className="h-11 sm:h-8" onClick={masquerRappel}>
              {t("sp.rappel_plus_tard")}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
