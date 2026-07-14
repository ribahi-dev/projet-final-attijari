// Service worker minimal — rend l'application INSTALLABLE (PWA) SANS jamais
// servir une version perimee.
//
// Choix volontaire : on NE met RIEN en cache. Chaque requete part au reseau
//   - les donnees bancaires (/api) sont toujours FRAICHES et authentifiees ;
//   - l'interface (HTML/JS/CSS) est toujours A JOUR -> on ne voit jamais une
//     ancienne version apres une mise a jour du projet.
// Le seul fait d'enregistrer un service worker avec un gestionnaire "fetch"
// suffit a rendre l'application installable (avec le manifeste).
//
// Historique : une version precedente mettait l'app shell en cache, ce qui
// pouvait afficher une ancienne interface. Ce SW efface donc AUSSI tous les
// anciens caches au demarrage.

self.addEventListener("install", () => {
  // Prendre la main immediatement, sans attendre la fermeture des onglets.
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      // Supprime TOUS les caches laisses par une version precedente.
      .then((keys) => Promise.all(keys.map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Gestionnaire fetch present (requis pour l'installabilite) mais volontairement
// PASSIF : on n'appelle jamais respondWith -> le navigateur gere la requete
// normalement, via le reseau. Aucun risque de contenu perime.
self.addEventListener("fetch", () => {});
