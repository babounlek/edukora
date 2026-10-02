import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Loader2, UserCircle } from "lucide-react"

import { listProfils } from "@/api/endpoints"
import { activerProfilProtege } from "@/lib/changerProfilActif"
import type { Profil } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Card, CardContent } from "@/components/ui/card"
import { useSeo } from "@/lib/seo"
import { catalogueHomePath } from "@/lib/countryPath"
import { useCountry } from "@/context/CountryContext"

/**
 * "Qui étudie ?" - affiché une seule fois, juste après la connexion, pour un compte
 * qui a déjà déclaré au moins deux enfants (voir les deux appels à `login()` dans
 * LoginPage.tsx, seuls points d'entrée vers cette page). Jamais montré au fil des
 * pages suivantes : le choix, une fois fait, vit dans la claim `profil_id` du token
 * (voir users.profils.profil_actif) et survit aux rechargements via le cookie de
 * refresh - jamais besoin de le redemander avant la prochaine connexion.
 */
export function QuiEtudiePage() {
  useSeo({ title: "Qui étudie ?" })

  const { isAuthenticated, isLoading, login } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const location = useLocation()
  const redirectTo = (location.state as { from?: string } | null)?.from ?? catalogueHomePath(country)

  const [profils, setProfils] = useState<Profil[] | null>(null)
  const [activatingId, setActivatingId] = useState<number | null>(null)

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
      navigate(redirectTo, { replace: true })
    } catch {
      setActivatingId(null)
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
        <h1 className="font-display text-2xl font-semibold tracking-tight">Qui étudie ?</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">
          Choisis le profil avec lequel continuer - tu pourras en changer à tout moment depuis le menu du compte.
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
                  {profil.prenom || "Profil sans nom"}
                </span>
                {activatingId === profil.id && <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />}
              </button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
