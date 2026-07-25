import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { CheckCircle2, GraduationCap, Lock, Search, Unlock } from "lucide-react"

import { listCours, listCursus, listSubjects } from "@/api/endpoints"
import type { Cours, Cursus, Subject } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { useCountry } from "@/context/CountryContext"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function CoursCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardContent className="flex flex-col gap-2 p-4">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <div className="flex gap-1.5">
          <Skeleton className="h-5 w-16 rounded-md" />
          <Skeleton className="h-5 w-14 rounded-md" />
        </div>
      </CardContent>
    </Card>
  )
}

export function CoursListPage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label

  useSeo({
    title: "Cours de révision",
    description: countryLabel
      ? `${countryLabel} : cours structurés (méthode, exemple résolu, erreurs classiques, exercices) pour le BEPC, le Probatoire et le BAC.`
      : undefined,
  })

  const [coursList, setCoursList] = useState<Cours[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [subjectFilter, setSubjectFilter] = useState("")
  const [cursusFilter, setCursusFilter] = useState("")
  const [search, setSearch] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    listSubjects(country).then(setSubjects).catch(() => {})
    listCursus(country).then(setCursusList).catch(() => {})
    // Une matière/un cursus sélectionné dans un autre pays n'existe plus dans les
    // nouvelles listes.
    setSubjectFilter("")
    setCursusFilter("")
  }, [country])

  useEffect(() => {
    setIsLoading(true)
    const timeout = setTimeout(() => {
      listCours({
        subject: subjectFilter || undefined,
        cursus: cursusFilter ? Number(cursusFilter) : undefined,
        country,
        search: search || undefined,
      })
        .then((data) => setCoursList(data.results))
        .finally(() => setIsLoading(false))
    }, 300)
    return () => clearTimeout(timeout)
  }, [subjectFilter, cursusFilter, search, country])

  return (
    <div>
      <section className="relative overflow-hidden border-b border-border">
        <div
          className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />
        <div className="relative mx-auto max-w-5xl px-4 py-14 sm:px-6">
          <p className="mb-2 font-display text-sm italic text-primary">
            Cours{countryLabel ? ` — ${countryLabel}` : ""}
          </p>
          <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
            Maîtrise la <span className="text-primary">méthode</span>, pas juste l'exercice du jour.
          </h1>
          <p className="mt-4 max-w-lg text-muted-foreground">
            Des cours complets sur chaque notion clé, avec exemple résolu, erreurs
            classiques et exercices gradués.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="mb-8 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Rechercher un cours..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={subjectFilter || "all"} onValueChange={(v) => setSubjectFilter(v === "all" ? "" : v)}>
            <SelectTrigger className="sm:w-56">
              <SelectValue placeholder="Toutes les matières" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes les matières</SelectItem>
              {subjects.map((s) => (
                <SelectItem key={s.id} value={s.code}>
                  {s.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={cursusFilter || "all"} onValueChange={(v) => setCursusFilter(v === "all" ? "" : v)}>
            <SelectTrigger className="sm:w-56">
              <SelectValue placeholder="Tous les cursus" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les cursus</SelectItem>
              {cursusList.map((c) => (
                <SelectItem key={c.id} value={String(c.id)}>
                  {c.examen_display}
                  {c.series ? ` - Série ${c.series.code}` : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <CoursCardSkeleton key={i} />
            ))}
          </div>
        ) : coursList.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-20 text-center text-muted-foreground">
            <GraduationCap className="size-8" />
            <p>Aucun cours ne correspond à ces critères.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {coursList.map((cours, index) => (
              <Link
                key={cours.id}
                to={cours.has_access ? `/cours/${cours.id}/lire` : `/cours/${cours.id}`}
                className="animate-fade-up"
                style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
              >
                <Card className="group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
                  <CardContent className="flex flex-col gap-2 p-4">
                    <h2 className="line-clamp-2 font-display font-medium leading-snug">
                      {cours.titre}
                    </h2>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <Badge variant="secondary">{cours.subject.label}</Badge>
                      {cours.cursus.length > 0 ? (
                        formatCursusGroups(cours.cursus).map((group) => (
                          <Badge key={group.key} variant="outline">{group.label}</Badge>
                        ))
                      ) : (
                        <Badge variant="outline">Toutes séries</Badge>
                      )}
                      {cours.duree_estimee_min && <Badge variant="outline">{cours.duree_estimee_min} min</Badge>}
                    </div>
                    <div className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                      {cours.has_access ? (
                        <>
                          <Unlock className="size-3.5 text-success" />
                          Accès inclus dans ton abonnement
                        </>
                      ) : (
                        <>
                          <Lock className="size-3.5" />
                          Abonnement requis
                        </>
                      )}
                      {cours.is_read && (
                        <>
                          <span aria-hidden="true">·</span>
                          <CheckCircle2 className="size-3.5 text-success" />
                          Lu
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
