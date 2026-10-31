from database.DB_connect import DBConnect
from model.cliente import Cliente

"""
PUNTO 1
1. All’avvio, riempire un menu a tendina con tutti i generi.
2. L’utente sceglie un genere G e inserisce un intero S ≥ 1. Premendo “Crea Grafo”, l’applicazione costruisce un grafo semplice, non orientato e pesato: a) i nodi sono i clienti che hanno acquistato almeno un brano del genere G. Per ogni cliente si memorizzino:
    * nome, cognome e paese;
    * il dipendente di supporto (SupportRepId);
    * la spesa totale per i brani del genere G;
    * l’insieme degli artisti acquistati, sempre solo del genere G; b) due clienti sono collegati da un arco se hanno almeno S artisti in comune; c) il peso dell’arco è il numero di artisti in comune.
3. Stampare il numero di nodi e di archi. Riempire poi i due menu a tendina del punto 2 con i clienti del grafo, ordinati per cognome e nome.
4. Premendo “Stampa Info”, stampare: a) il cliente con la spesa maggiore e la spesa; b) il cliente (o i clienti, se a pari merito) con più artisti diversi e il numero; c) il cliente (o i clienti) con grado maggiore e il grado; d) i 5 archi di peso maggiore, in ordine decrescente di peso. A parità si ordina alfabeticamente per il nome del primo cliente e poi del secondo; e) il numero di componenti connesse, la dimensione della più grande e il numero di clienti isolati; f) il numero di paesi diversi presenti nel grafo e il paese (o i paesi) con più clienti; g) per ogni dipendente di supporto: nome e cognome, numero di clienti del grafo che segue e la loro spesa totale, in ordine di spesa decrescente; h) il numero di archi tra clienti dello stesso paese e l’arco di peso maggiore tra questi, con il paese.
PUNTO 2
Si vuole far girare un consiglio musicale con il passaparola da un cliente all’altro. L’utente sceglie un cliente di partenza A, un cliente di arrivo B e inserisce un intero K ≥ 1. Con un algoritmo ricorsivo, trovare il cammino da A a B che:
1. usa al massimo K archi;
2. ha tutti i clienti (A e B compresi) di paesi diversi;
3. massimizza la somma dei pesi degli archi;
4. a parità di peso, usa meno archi.
Se A e B sono dello stesso paese, oppure se non esiste nessun cammino, stampare un messaggio.
Stampare il cammino con il paese di ogni cliente e il peso di ogni arco, poi il numero di archi e il peso totale.

"""


class DAO():
    @staticmethod
    def getGeneri():
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT g.GenreId, g.Name
                FROM Genre g
                ORDER BY g.Name
                """

        cursor.execute(query)

        for row in cursor:
            results.append((row["GenreId"], row["Name"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getGetNodi(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT c.CustomerId as cId, c.FirstName as nome, c.LastName as cognome ,c.Country AS paese, e.EmployeeId AS emId, SUM(il.Quantity*il.UnitPrice) AS spesa
                FROM customer c, employee e, invoice i, invoiceline il, track t
                WHERE c.SupportRepId = e.EmployeeId AND c.CustomerId = i.CustomerId AND il.InvoiceId = i.InvoiceId AND il.TrackId = t.TrackId AND t.GenreId = %s
                GROUP BY c.CustomerId, c.FirstName, c.LastName, c.Country, e.EmployeeId
                """

        cursor.execute(query,(genere,))

        for row in cursor:
            c = Cliente(row["cId"],row["nome"],row["cognome"],row["paese"],row["emId"],float(row["spesa"]))
            results.append(c)

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCoppia(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT DISTINCT i.CustomerId AS idC, al.ArtistId AS idA
                FROM Invoice i, InvoiceLine il, Track t, Album al
                WHERE i.InvoiceId = il.InvoiceId AND il.TrackId = t.TrackId
                AND t.AlbumId = al.AlbumId AND t.GenreId = %s
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            results.append((row["idC"], row["idA"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getDipendenti():
        conn = DBConnect.get_connection()
        if conn is None:
            return {}

        results = {}

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT e.EmployeeId, e.FirstName, e.LastName
                FROM Employee e
                """

        cursor.execute(query)

        for row in cursor:
            results[row["EmployeeId"]] = f"{row['FirstName']} {row['LastName']}"

        cursor.close()
        conn.close()
        return results