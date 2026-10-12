// Lu au build par Vite (voir docker/caddy/Dockerfile, ARG VITE_SENTRY_DSN) - jamais à
// l'exécution, contrairement à SENTRY_DSN côté backend.
const dsn = import.meta.env.VITE_SENTRY_DSN

type SentryModule = typeof import("@sentry/react")

// Import dynamique : le SDK (avec son intégration de traçage) pèse dans le bundle principal
// de chaque visiteur, y compris tant qu'aucun DSN n'est renseigné et qu'il ne sert à rien.
// Sans DSN, il n'est jamais téléchargé.
let chargement: Promise<SentryModule> | null = null
function charger(): Promise<SentryModule> {
  chargement ??= import("@sentry/react")
  return chargement
}

/**
 * Inerte tant que VITE_SENTRY_DSN n'est pas renseigné au build - aucun projet Sentry
 * créé pour ce dépôt à ce stade. Voir l'audit UX, reco 5.1 : "aucun outil de
 * supervision d'erreurs n'est installé... la seule remontée de bug possible
 * aujourd'hui est un message spontané d'un utilisateur." Appelée le plus tôt possible
 * dans main.tsx, avant le rendu de l'app.
 */
export function initSentry() {
  if (!dsn) return
  void charger().then((Sentry) =>
    Sentry.init({
      dsn,
      environment: import.meta.env.MODE,
      integrations: [Sentry.browserTracingIntegration()],
      // Échantillon prudent (pas 1.0), même raison que côté backend (voir
      // edtech_cm/settings.py SENTRY_TRACES_SAMPLE_RATE) : marge sur un plan Sentry
      // gratuit avant d'ajuster ce réglage consciemment.
      tracesSampleRate: 0.2,
      // Un chunk introuvable après déploiement est déjà géré par un rechargement
      // automatique (voir ErrorBoundary.tsx) - bruit attendu, jamais un vrai bug à
      // investiguer côté Sentry.
      ignoreErrors: [/failed to fetch dynamically imported module/i, /error loading dynamically imported module/i],
    }),
  )
}

// Même forme qu'avant l'import dynamique (`Sentry.captureException(...)`) : les appelants
// n'ont rien à changer, et sans DSN l'appel ne fait rien et ne télécharge rien.
export const Sentry = {
  captureException(erreur: unknown, contexte?: Parameters<SentryModule["captureException"]>[1]) {
    if (!dsn) return
    void charger().then((S) => S.captureException(erreur, contexte))
  },
}
