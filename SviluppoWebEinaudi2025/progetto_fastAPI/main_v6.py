from typing import Dict
from fastapi import Form,FastAPI, Response, HTTPException, status, Request
from fastapi import Depends, Query
from schema import User, UserCreate
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login import LoginManager
from datetime import timedelta
import os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import database_py
from datetime import datetime
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from fastapi import APIRouter



router = APIRouter()

class Prenotazione(BaseModel):
    id_libro: int

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") 
templates = Jinja2Templates(directory="templates")
SECRET = os.urandom(24).hex()
manager = LoginManager(SECRET, '/login', use_cookie=True, default_expiry = timedelta(minutes=20))
manager.cookie_name = "access-token"

@app.exception_handler(StarletteHTTPException)
async def custom_unauthorized_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=303)  # 303 per cambiare metodo a GET
    return HTMLResponse(f"<h1>Errore {exc.status_code}</h1><p>{exc.detail}</p>", status_code=exc.status_code)

@manager.user_loader()
def load_user(user: str):
    return database_py.db_get_utenti(user)

@app.get("/")
def root_redirect():
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    utente = database_py.db_get_utenti(username)
    if utente:
        credenziali = utente[7]
        if credenziali == password:
            print("credenziali corrette")
            response = RedirectResponse(url="/dashboard", status_code=303)
            access_token = manager.create_access_token(
                data=dict(sub=username)
            )
            manager.set_cookie(response, access_token)
            return response
        
        else:
            print("password errata")
            return templates.TemplateResponse("login.html", {"request": request, "error": "Credenziali errate!"})
            
    else:
        print("username errato")
        return templates.TemplateResponse("login.html", {"request": request, "message": "Credenziali errate!"})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(
    nome: str = Form(...),
    cognome: str = Form(...),
    data_nascita: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    nome_utente: str = Form(...),
    passwd: str = Form(...)
):
    dati = (nome, cognome, data_nascita, email, telefono, nome_utente, passwd)
    database_py.inserisci_utente(dati)
    return RedirectResponse(url="/", status_code=303)



@app.get("/dashboard")
def dashboard(request: Request, user = Depends(manager)):
    # Recupera tutti i libri
    tutti_libri = database_py.db_get_products({})
    
    # Recupera i prestiti dell'utente
    id_utente = database_py.db_get_utenti(user[6])[0]
    prestiti = database_py.get_prestiti_utente(id_utente)
    
    # Prepara i dati per la dashboard
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "products": tutti_libri,
        "prestiti": prestiti,
        "permessi": user[8],
        "nome_utente": f"{user[1]} {user[2]}",  # Nome + Cognome
        "num_prestiti": len(prestiti),
        "libri_totali": len(tutti_libri),
        "ultimi_arrivi": sorted(tutti_libri, key=lambda x: x['id_libro'], reverse=True)[:4]
    })



@app.get("/add_book", response_class=HTMLResponse)
def book_form(request: Request, user=Depends(manager)):
    return templates.TemplateResponse("add_book.html", {"request": request})

@app.post("/add_book")
def add_book(
    request: Request,
    titolo: str = Form(...),
    autore: str = Form(...),
    anno_pubblicazione: int = Form(...),
    editore: str = Form(...),
    isbn: str = Form(...),
    disponibilita: int = Form(...),
    user=Depends(manager)  # Aggiungi questa dipendenza
):
    dati = (titolo, autore, anno_pubblicazione, editore, isbn, disponibilita)
    database_py.inserisci_libro(dati)
    return RedirectResponse(url="/dashboard", status_code=303)


'''
@app.post("/prenota")
def prenota_libro(request: Request, id_libro: int = Form(...), user=Depends(manager)):
    utente = database_py.db_get_utenti(user[6])
    id_utente = utente[0]
    user=Depends(manager)
    # Decrementa la disponibilità
    database_py.decrementa_disponibilita(id_libro)

    # Aggiunge prestito
    data_prestito = datetime.now().date()
    database_py.aggiungi_prestito(id_libro, id_utente, data_prestito)

    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/prenota")
def prenota_libro(request: Request, id_libro: int = Form(...), user=Depends(manager)):
    user=Depends(manager)
    print("Prenotazione ricevuta per ID libro:", id_libro)
'''
@app.post("/prenota")
async def prenota_libro(request: Request,prenotazione: Prenotazione,user=Depends(manager) ):
    id_libro = prenotazione.id_libro
    print("prenota")
    # Verifica se l'utente esiste nel database
    utente = database_py.db_get_utenti(user[6])
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    id_utente = utente[0]  # Supponendo che l'ID sia il primo campo

    # Debug: stampa l'ID libro (opzionale)
    print("Prenotazione ricevuta per ID libro:", id_libro)

    # Decrementa disponibilità e aggiunge prestito
    database_py.decrementa_disponibilita(id_libro)
    database_py.aggiungi_prestito(
        id_libro=id_libro,
        id_utente=id_utente,
        data_prestito=datetime.now().date()
    )

    return {"success": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_token")  # Cancella il cookie di sessione
    return {"message": "Logout effettuato"}

@app.get("/home_search")
async def search_page(request: Request): #user = Depends(manager))
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/search")
def search(
    title: str = Query(None),
    min_quantity: int = Query(None),
    max_price: float = Query(None),
    in_stock: bool = Query(None)
):
    # Chiamata alla funzione del database per ottenere i risultati
    results = database_py.search_products(title, min_quantity, max_price, in_stock)
    return results
