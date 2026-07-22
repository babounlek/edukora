import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { CheckCircle2, Copy, Gift, MessageCircle } from "lucide-react"

import { getMyProgression, listMySubscriptions } from "@/api/endpoints"
import type { Progression, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"

export function AccountPage() {
  useSeo({ title: "Mon compte" })

  const { user, logout, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [progression, setProgression] = useState<Progression | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/compte" } })
      return
    }
    listMySubscriptions().then(setSubscriptions)
    getMyProgression().then(setProgression)
  }, [isLoading, isAuthenticated, navigate])

  function handleLogout() {
    logout()
    navigate("/")
  }

  if (isLoading || !user) return null

  const totalRead = (progression?.lessons.length ?? 0) + (progression?.cours.length ?? 0)
  const referralLink = `${window.location.origin}/?ref=${user.referral_code}`
  const whatsappMessage = `Salut ! Je révise sur ${SITE_NAME} (corrigés BEPC/Probatoire/BAC) - inscris-toi avec mon lien, ça nous donne 7 jours gratuits à tous les deux : ${referralLink}`

  function handleCopyLink() {
    navigator.clipboard.writeText(referralLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="mx-auto max-w-2xl animate-fade-up px-4 py-10">
      <h1 className="mb-6 font-display text-3xl font-semibold">Mon compte</h1>

      <Card className="mb-6">
        <CardContent className="flex items-center justify-between pt-6">
          <div>
            <p className="font-medium">{user.full_name || user.phone_number}</p>
            <p className="text-sm text-muted-foreground">{user.phone_number}</p>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            Déconnexion
          </Button>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-display text-lg">
            <Gift className="size-4.5 text-primary" />
            Parraine tes amis
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground">
            Ton ami s'inscrit avec ton lien et souscrit un abonnement : vous recevez chacun 7 jours d'accès gratuit.
            {user.filleuls_count > 0 && (
              <> Tu as déjà parrainé {user.filleuls_count} personne{user.filleuls_count > 1 ? "s" : ""}.</>
            )}
          </p>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Button variant="outline" onClick={handleCopyLink} className="flex-1">
              <Copy className="size-4" />
              {copied ? "Lien copié !" : "Copier le lien"}
            </Button>
            <Button asChild className="flex-1">
              <a
                href={`https://wa.me/?text=${encodeURIComponent(whatsappMessage)}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <MessageCircle className="size-4" />
                Partager sur WhatsApp
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="font-display text-lg">Mes abonnements</CardTitle>
        </CardHeader>
        <CardContent>
          {subscriptions.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucun abonnement pour le moment.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {subscriptions.map((sub) => (
                <li
                  key={sub.id}
                  className="flex items-center justify-between rounded-md border border-border px-3 py-2.5 transition-colors hover:bg-accent/40"
                >
                  <span className="text-sm">
                    {sub.cursus.examen_display}
                    {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">
                      Expire le {new Date(sub.expires_at).toLocaleDateString("fr-FR")}
                    </span>
                    <Badge variant={sub.is_active ? "success" : "outline"}>
                      {sub.is_active ? "Actif" : "Expiré"}
                    </Badge>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-display text-lg">Ma progression</CardTitle>
        </CardHeader>
        <CardContent>
          {!progression || totalRead === 0 ? (
            <p className="text-sm text-muted-foreground">
              Rien de lu pour l'instant - ouvre une leçon ou un cours pour commencer.
            </p>
          ) : (
            <div className="flex flex-col gap-4">
              <p className="text-sm text-muted-foreground">
                {totalRead} contenu{totalRead > 1 ? "s" : ""} lu{totalRead > 1 ? "s" : ""} au total.
              </p>

              {progression.lessons.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Leçons</p>
                  <ul className="flex flex-col gap-2">
                    {progression.lessons.map((lesson) => (
                      <li key={lesson.id}>
                        <Link
                          to={`/lecons/${lesson.id}/lire`}
                          className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm transition-colors hover:bg-accent/40"
                        >
                          <CheckCircle2 className="size-4 shrink-0 text-success" />
                          {lesson.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {progression.cours.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Cours</p>
                  <ul className="flex flex-col gap-2">
                    {progression.cours.map((cours) => (
                      <li key={cours.id}>
                        <Link
                          to={`/cours/${cours.id}/lire`}
                          className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm transition-colors hover:bg-accent/40"
                        >
                          <CheckCircle2 className="size-4 shrink-0 text-success" />
                          {cours.titre}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
