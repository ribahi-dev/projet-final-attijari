// Service worker minimal — rend l'application INSTALLABLE et disponible
// même hors ligne pour la coquille de l'app (app shell).
//
// Choix volontaire : on NE met PAS en cache les réponses de /api.
// Une plateforme bancaire doit toujours afficher des données FRAÎCHES et
// authentifiées — un cache d'alertes périmées serait dangereux. Le SW ne
// sert donc que les fichiers statiques (JS/CSS/icônes), et laisse passer
// toute requête API vers le réseau sans interception.
const CACHE = "novabank-shell-v1";
const SHELL = ["/", "/index.html", "/manifest.webmanifest", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  // Jamais de cache pour l'API ni les requêtes non-GET : toujours le réseau.
  if (url.pathname.startsWith("/api") || event.request.method !== "GET") return;

  // App shell : réseau d'abord (pour récupérer les nouvelles versions),
  // repli sur le cache si hors ligne.
  event.respondWith(
    fetch(event.request)
      .then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(event.request, copy)).catch(() => {});
        return resp;
      })
      .catch(() => caches.match(event.request).then((r) => r || caches.match("/index.html")))
  );
});
