(async () => {
    const destination = document.querySelector('link[rel="canonical"]').getAttribute('href');
    const fragment = decodeURIComponent(window.location.hash.slice(1));
    let target = destination + window.location.hash;
    if (fragment) {
        try {
            const response = await fetch('/plexosdb/api-fragments.json');
            if (!response.ok) throw new Error(`API fragment map: HTTP ${response.status}`);
            const members = await response.json();
            target = members[fragment] ?? target;
        } catch (error) {
            console.warn('Could not resolve the API member bookmark', error);
        }
    }
    window.location.replace(target);
})();
