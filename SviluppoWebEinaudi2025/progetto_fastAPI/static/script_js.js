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

// Navigazione tra le schede
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(e) {
        if (this.getAttribute('href') && this.getAttribute('href').startsWith('/')) {
            return;
        }
        
        e.preventDefault();
        
        document.querySelectorAll('nav a').forEach(navLink => {
            navLink.classList.remove('nav-active');
        });
        this.classList.add('nav-active');
        
        const target = this.id + '-content';
        document.querySelectorAll('.card').forEach(card => {
            card.classList.remove('active');
            card.classList.add('hidden');
        });
        document.getElementById(target).classList.remove('hidden');
        document.getElementById(target).classList.add('active');
    });
});

// Variabile globale per memorizzare i risultati originali
let originalBooks = [];
let originalLoans = [];

// Funzione di ricerca migliorata
function searchBooks() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
    const resultsContainer = document.getElementById('search-results-content');
    
    // Se il campo di ricerca è vuoto, resetta tutto
    if (!searchTerm) {
        document.getElementById('search-results').classList.add('hidden');
        document.getElementById('full-table').classList.remove('hidden');
        resultsContainer.innerHTML = '';
        return;
    }
    
    // Mostra i risultati e nascondi la tabella completa
    document.getElementById('search-results').classList.remove('hidden');
    document.getElementById('full-table').classList.add('hidden');
    
    // Filtra i libri disponibili
    const availableBooks = originalBooks.filter(book => 
        book.titolo.toLowerCase().includes(searchTerm) || 
        book.autore.toLowerCase().includes(searchTerm) ||
        book.disponibilita.toLowerCase().includes(searchTerm)
    );
    
    // Filtra i libri in prestito
    const loanedBooks = originalLoans.filter(book => 
        book.titolo.toLowerCase().includes(searchTerm) || 
        book.autore.toLowerCase().includes(searchTerm) ||
        book.isbn.toLowerCase().includes(searchTerm)
    );
    
    // Aggiorna i risultati della ricerca
    updateSearchResults(availableBooks, loanedBooks);
}

// Aggiorna i risultati della ricerca (senza duplicati)
function updateSearchResults(availableBooks, loanedBooks) {
    const resultsContainer = document.getElementById('search-results-content');
    const activeTab = document.querySelector('.search-tab.active').textContent;
    
    // Crea un set per evitare duplicati
    const uniqueBookIds = new Set();
    
    if (activeTab.includes('Tutti')) {
        if (availableBooks.length === 0 && loanedBooks.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">Nessun risultato trovato</div>';
            return;
        }
        
        let html = '<h4>Libri disponibili</h4>';
        if (availableBooks.length > 0) {
            html += '<table class="book-table"><tbody>';
            availableBooks.forEach(book => {
                if (!uniqueBookIds.has(book.id)) {
                    html += book.element;
                    uniqueBookIds.add(book.id);
                }
            });
            html += '</tbody></table>';
        } else {
            html += '<p>Nessun libro disponibile corrisponde alla ricerca</p>';
        }
        
        html += '<h4 style="margin-top: 20px;">Libri in prestito</h4>';
        if (loanedBooks.length > 0) {
            html += '<table class="book-table"><tbody>';
            loanedBooks.forEach(book => {
                if (!uniqueBookIds.has(book.id)) {
                    html += book.element;
                    uniqueBookIds.add(book.id);
                }
            });
            html += '</tbody></table>';
        } else {
            html += '<p>Nessun prestito corrisponde alla ricerca</p>';
        }
        
        resultsContainer.innerHTML = html;
    } 
    else if (activeTab.includes('Disponibili')) {
        if (availableBooks.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">Nessun libro disponibile corrisponde alla ricerca</div>';
            return;
        }
        
        let html = '<table class="book-table"><tbody>';
        availableBooks.forEach(book => {
            if (!uniqueBookIds.has(book.id)) {
                html += book.element;
                uniqueBookIds.add(book.id);
            }
        });
        html += '</tbody></table>';
        resultsContainer.innerHTML = html;
    } 
    else if (activeTab.includes('prestiti')) {
        if (loanedBooks.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">Nessun prestito corrisponde alla ricerca</div>';
            return;
        }
        
        let html = '<table class="book-table"><tbody>';
        loanedBooks.forEach(book => {
            if (!uniqueBookIds.has(book.id)) {
                html += book.element;
                uniqueBookIds.add(book.id);
            }
        });
        html += '</tbody></table>';
        resultsContainer.innerHTML = html;
    }
}

// Inizializzazione della ricerca al caricamento della pagina
document.addEventListener('DOMContentLoaded', function() {
    // Salva i libri originali per la ricerca
    originalBooks = Array.from(document.querySelectorAll('.book-table tbody tr')).map(row => {
        return {
            id: row.getAttribute('data-id'),
            titolo: row.cells[0].textContent,
            autore: row.cells[1].textContent,
            anno: row.cells[2].textContent,
            disponibilita: row.cells[3].textContent,
            azioni: row.cells[4].innerHTML,
            element: row.outerHTML
        };
    });
    
    // Salva i prestiti originali per la ricerca
    originalLoans = Array.from(document.querySelectorAll('#prenotazioni-body tr')).map(row => {
        return {
            id: row.cells[2].textContent, // Usa ISBN come ID unico
            titolo: row.cells[0].textContent,
            autore: row.cells[1].textContent,
            isbn: row.cells[2].textContent,
            data: row.cells[3].textContent,
            stato: row.cells[4].innerHTML,
            element: row.outerHTML
        };
    });
    
    // Ricerca al pressione del tasto Invio
    document.getElementById('search-input').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchBooks();
        }
        
        // Reset se il campo è vuoto
        if (this.value.trim() === '') {
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('full-table').classList.remove('hidden');
        }
    });
    
    // Reset al click su "X" nel campo di ricerca (per browser che la supportano)
    document.getElementById('search-input').addEventListener('search', function() {
        if (this.value.trim() === '') {
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('full-table').classList.remove('hidden');
        }
    });
});


// Cambia tab nella ricerca
function switchSearchTab(tab) {
    document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
    
    if (tab === 'all') {
        document.querySelector('.search-tab:nth-child(1)').classList.add('active');
    } else if (tab === 'available') {
        document.querySelector('.search-tab:nth-child(2)').classList.add('active');
    } else if (tab === 'loans') {
        document.querySelector('.search-tab:nth-child(3)').classList.add('active');
    }
    
    // Riesegui la ricerca per aggiornare i risultati
    searchBooks();
}

// Ricerca al pressione del tasto Invio
document.getElementById('search-input').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') {
        searchBooks();
    }
});

// Prenotazione libro con AJAX
async function prenotaLibro(idLibro, titolo, autore, isbn) {
    const disponibilitaElement = document.getElementById(`dispo-${idLibro}`);
    const currentDisponibilita = parseInt(disponibilitaElement.textContent);
    const button = document.querySelector(`button[onclick*="${idLibro}"]`);
    
    try {
        const response = await fetch('/prenota', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_libro: idLibro })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const newDisponibilita = currentDisponibilita - 1;
            disponibilitaElement.innerHTML = newDisponibilita > 0 ? 
                `<span class="available">${newDisponibilita} disponibili</span>` : 
                `<span class="unavailable">Esaurito</span>`;
            
            if (newDisponibilita === 0) {
                button.innerHTML = '<i class="fas fa-times-circle"></i> Esaurito';
                button.classList.add('disabled');
                button.onclick = null;
            }
            
            aggiungiPrenotazione(titolo, autore, isbn);
            showNotification('Prenotazione effettuata con successo!', 'success');
        } else {
            showNotification('Errore: ' + (data.message || 'Prenotazione fallita'), 'error');
        }
    } catch (error) {
        console.error('Errore:', error);
        showNotification('Errore di connessione', 'error');
        disponibilitaElement.textContent = currentDisponibilita;
    }
}

// Aggiungi una nuova prenotazione alla tabella
function aggiungiPrenotazione(titolo, autore, isbn) {
    const tbody = document.querySelector("#prenotazioni-body");
    const now = new Date();
    const formattedDate = `${now.getDate()}/${now.getMonth()+1}/${now.getFullYear()}`;
    
    const newRow = document.createElement("tr");
    newRow.innerHTML = `
        <td>${titolo}</td>
        <td>${autore}</td>
        <td>${isbn}</td>
        <td>${formattedDate}</td>
        <td><span class="status active">In corso</span></td>
    `;
    
    tbody.prepend(newRow);
}

// Mostra notifiche temporanee
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

