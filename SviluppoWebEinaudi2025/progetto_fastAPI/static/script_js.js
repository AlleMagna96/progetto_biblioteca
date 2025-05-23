document.addEventListener('DOMContentLoaded', () => {
    const homeLink = document.getElementById('home');
    const statsLink = document.getElementById('stats');
    const settingsLink = document.getElementById('settings');
    
    const homeContent = document.getElementById('home-content');
    const statsContent = document.getElementById('stats-content');
    const settingsContent = document.getElementById('settings-content');
    
    homeLink.addEventListener('click', () => {
        homeContent.classList.remove('hidden');
        statsContent.classList.add('hidden');
        settingsContent.classList.add('hidden');
    });

    statsLink.addEventListener('click', () => {
        homeContent.classList.add('hidden');
        statsContent.classList.remove('hidden');
        settingsContent.classList.add('hidden');
    });

    settingsLink.addEventListener('click', () => {
        homeContent.classList.add('hidden');
        statsContent.classList.add('hidden');
        settingsContent.classList.remove('hidden');
    });
    
    // Mostra il contenuto Home di default
    homeContent.classList.remove('hidden');


     
});
