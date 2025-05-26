import mysql.connector 
from decimal import Decimal
from typing import List, Dict
from datetime import date

conn = mysql.connector.connect(
    host="localhost", #sostituisci l'indirizzo IP del server con il DB dentro
    user="root", #nome utente
    password="",  #passw account 
    database="casarini_davide", #nome_db
    port=3306, #porta default di mySQL
    )

# a tutti passerei un dizionario cosÃ¬ che dentro abbia le informazioni per presonalizzare le query 
def db_get_utenti(user):
    cur = conn.cursor()
    print(user)
    query = f"SELECT * FROM Utenti where username = '{user}' "
    print(query)
    cur.execute(query)
    dati = cur.fetchone()
    print(dati)
    return dati

def db_get_products(diz):
    cur = conn.cursor()

    # si chiama una funzione di libreria passando i parametri di ricerca dell'utente. esempio controlla_caratteri(nome)
    query = "SELECT * FROM Libri"
    cur.execute(query)
    dati = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Converte le tuple in dizionari
    products = []
    for row in dati:
        product = {column_names[i]: (float(row[i]) if isinstance(row[i], Decimal) else row[i]) for i in range(len(row))}
        products.append(product)

    print(products)
    cur.close()
    return products

def db_set(diz): 
    if diz=="Libri":
        campi="(titolo,autore,anno_pubblicazione,editore,isbn,disponibilita)"
        values="%s, %s, %s, %s, %s, %s"
    elif diz=="Prestiti":
            campi="(id_libro,id_utente,data_prestito,data_restituzione,data_restituito)"
            values="%s, %s, %s,%s,%s"
    elif diz=="Utenti":
            campi="(nome,cognome,data_nascita,email,telefono,nome_utente,passwd)"
            values="%s,%s,%s,%s,%s,%s,%s"
    else:
        return "Tabella inesistente."
    query = f"INSERT INTO {diz}{campi} VALUES ({values})"
    

def db_update(diz):
    # query update
    if diz=="Libri":
        campi="titolo=%s,autore=%s,anno_pubblicazione=%s,editore=%s,isbn=%s,disponibilita=%s"
    elif diz=="Prestiti":
            campi="id_libro=%s,id_utente=%s,data_prestito=%s,data_restituzione=%s,data_restituito=%s"
    elif diz=="Utenti":
        campi="nome=%s,cognome=%s,data_nascita=%s,email=%s,telefono=%s,nome_utente=%s,passwd=%s"
    else:
        return "Tabella inesistente."
    
    query = f"UPDATE {diz} SET {campi} WHERE id = %s"

def db_delete(diz):
    cursor = conn.cursor()
    # query delete diz["tabella"], diz["id_libro"]
    if diz=="Libri":
        query_delete_zone="DELETE FROM Libri WHERE id_libro=%s"
        cursor.execute(query_delete_zone,("id_libro",))
    if diz=="Prestiti":
            query_delete_zone="DELETE FROM Prestiti WHERE id_prestito=%s"
            cursor.execute(query_delete_zone,("id_prestito",))
    if diz=="Utenti":
            query_delete_zone="DELETE FROM Utenti WHERE id_utente=%s"
            cursor.execute(query_delete_zone,("id_utente",))
            
    query_delete_Utenti=f"DELETE FROM {diz} WHERE id_Utenti=%s"
    query_delete_Libri=f"DELETE FROM {diz} WHERE id_Libri=%s"

def inserisci_utente(dati):
    cur = conn.cursor()
    query = """
        INSERT INTO Utenti (nome, cognome, data_nascita, email, telefono, username, passwd)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    print(query)
    cur.execute(query, dati)
    conn.commit()
    cur.close()

def inserisci_libro(dati):
    cur = conn.cursor()
    query = """
        INSERT INTO Libri (titolo, autore, anno_pubblicazione, editore, isbn, disponibilita)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, dati)
    conn.commit()
    cur.close()

def decrementa_disponibilita(id_libro):
    cur = conn.cursor()
    query = "UPDATE Libri SET disponibilita = disponibilita - 1 WHERE id_libro = %s AND disponibilita > 0"
    cur.execute(query, (id_libro,))
    conn.commit()
    cur.close()

def aggiungi_prestito(id_libro, id_utente, data_prestito):
    cur = conn.cursor()
    data_oggi=date.today()
    query = """
        INSERT INTO Prestiti (id_libro, id_utente, data_prestito)
        VALUES (%s, %s, %s)
    """
    cur.execute(query, (id_libro, id_utente, data_oggi))
    conn.commit()
    cur.close()

def get_prestiti_utente(id_utente):
    cur = conn.cursor()
    query = """
        SELECT Libri.titolo, Libri.autore, Libri.isbn, Prestiti.data_prestito
        FROM Prestiti
        JOIN Libri ON Prestiti.id_libro = Libri.id_libro
        WHERE id_utente = %s
    """
    cur.execute(query, (id_utente,))
    prestiti = cur.fetchall()
    cur.close()
    return prestiti




def search_products(
    title: str = None,
    min_quantity: int = None,
    max_price: float = None,
    in_stock: bool = None
) -> List[Dict]:

    cursor = conn.cursor()
        
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if title:
        query += " AND title LIKE %s"
        params.append(f"%{title}%")
    if min_quantity is not None:
        query += " AND quantity >= %s"
        params.append(min_quantity)
    if max_price is not None:
        query += " AND price <= %s"
        params.append(max_price)

    cursor.execute(query, tuple(params))
    print(cursor.description)
    results = cursor.fetchall()

    results = [(1, 'Smartphone', 50, Decimal('699'), 0), (4, 'Mouse Wireless', 75, Decimal('100'), 1), (11, 'ciao', 3, Decimal('10'), 11)]
    return results


if __name__ == '__main__':
    db_get_utenti({"username" : "casaro"})
