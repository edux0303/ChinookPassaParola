import networkx as nx
from itertools import combinations
from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.Graph()
        self._idMap = {}
        self._dipendenti = {}

    # ==================== PUNTO 1 ====================

    def getGeneri(self):
        return DAO.getGeneri()

    def buildGraph(self, genere, soglia):
        self._grafo.clear()
        self._idMap = {}

        # nodi: clienti che hanno comprato il genere
        nodi = DAO.getGetNodi(genere)
        self._idMap = {c.id: c for c in nodi}
        self._grafo.add_nodes_from(nodi)

        # set degli artisti di ogni cliente
        for idC, idA in DAO.getCoppia(genere):
            if idC in self._idMap:
                self._idMap[idC].artisti.add(idA)

        # archi: almeno 'soglia' artisti in comune
        for c1, c2 in combinations(nodi, 2):
            comuni = c1.artisti & c2.artisti
            if len(comuni) >= soglia:
                self._grafo.add_edge(c1, c2, weight=len(comuni))

    def getNumNodi(self):
        return self._grafo.number_of_nodes()

    def getNumArchi(self):
        return self._grafo.number_of_edges()

    def getNodiOrdinati(self):
        return sorted(self._grafo.nodes, key=lambda c: (c.cognome, c.nome))

    def getCliente(self, idC):
        return self._idMap.get(idC)

    # a) cliente con spesa maggiore
    def getSpesaMaggiore(self):
        best = max(self._grafo.nodes, key=lambda c: c.spesa)
        return best, best.spesa

    # b) clienti con più artisti diversi
    def getPiuArtisti(self):
        maxArtisti = max(len(c.artisti) for c in self._grafo.nodes)
        migliori = [c for c in self._grafo.nodes if len(c.artisti) == maxArtisti]
        migliori.sort(key=lambda c: str(c))
        return migliori, maxArtisti

    # c) clienti con grado maggiore
    def getGradoMaggiore(self):
        maxGrado = max(self._grafo.degree(c) for c in self._grafo.nodes)
        migliori = [c for c in self._grafo.nodes if self._grafo.degree(c) == maxGrado]
        migliori.sort(key=lambda c: str(c))
        return migliori, maxGrado

    # d) 5 archi di peso maggiore
    def getTop5Archi(self):
        archi = []
        for u, v, dati in self._grafo.edges(data=True):
            nomi = sorted([str(u), str(v)])
            archi.append((nomi[0], nomi[1], dati["weight"]))
        archi.sort(key=lambda x: (-x[2], x[0], x[1]))
        return archi[:5]

    # e) componenti connesse
    def getInfoComponenti(self):
        componenti = list(nx.connected_components(self._grafo))
        piuGrande = max(componenti, key=len)
        isolati = 0
        for comp in componenti:
            if len(comp) == 1:
                isolati += 1
        return len(componenti), len(piuGrande), isolati

    # f) numero di paesi e paese con più clienti
    def getInfoPaesi(self):
        conta = {}
        for c in self._grafo.nodes:
            conta[c.paese] = conta.get(c.paese, 0) + 1
        maxClienti = max(conta.values())
        migliori = sorted([p for p in conta if conta[p] == maxClienti])
        return len(conta), migliori, maxClienti

    # g) per ogni dipendente: numero clienti e spesa totale
    def getInfoDipendenti(self):
        if len(self._dipendenti) == 0:
            self._dipendenti = DAO.getDipendenti()     # {EmployeeId: "Nome Cognome"}
        info = {}                                      # {EmployeeId: [numClienti, spesa]}
        for c in self._grafo.nodes:
            if c.supportRep not in info:
                info[c.supportRep] = [0, 0]
            info[c.supportRep][0] += 1
            info[c.supportRep][1] += c.spesa
        risultato = []
        for idE in info:
            nome = self._dipendenti.get(idE, "sconosciuto")
            risultato.append((nome, info[idE][0], info[idE][1]))
        risultato.sort(key=lambda x: -x[2])
        return risultato

    # h) archi tra clienti dello stesso paese
    def getArchiStessoPaese(self):
        archi = []
        for u, v, dati in self._grafo.edges(data=True):
            if u.paese == v.paese:
                nomi = sorted([str(u), str(v)])
                archi.append((nomi[0], nomi[1], dati["weight"], u.paese))
        if len(archi) == 0:
            return 0, None
        archi.sort(key=lambda x: (-x[2], x[0], x[1]))
        return len(archi), archi[0]


    # ==================== PUNTO 2 ====================

    def getPassaParola(self, partenza, arrivo, K):
        self._camminoBest = []
        self._pesoBest = -1
        self._arrivo = arrivo
        self._K = K
        self._ricorsione([partenza], 0, {partenza.paese})
        return self._camminoBest, self._pesoBest

    def _ricorsione(self, parziale, pesoParziale, paesiUsati):
        ultimo = parziale[-1]

        # 1. sono arrivato in B -> controllo se è il migliore
        if ultimo == self._arrivo:
            if (pesoParziale > self._pesoBest or
                    (pesoParziale == self._pesoBest and len(parziale) < len(self._camminoBest))):
                self._pesoBest = pesoParziale
                self._camminoBest = list(parziale)
            return

        # 2. ho già usato K archi -> mi fermo
        if len(parziale) - 1 == self._K:
            return

        # 3. provo ad andare in un vicino
        for vicino in self._grafo.neighbors(ultimo):
            if vicino in parziale:
                continue
            if vicino.paese in paesiUsati:
                continue
            peso = self._grafo[ultimo][vicino]["weight"]
            parziale.append(vicino)
            paesiUsati.add(vicino.paese)
            self._ricorsione(parziale, pesoParziale + peso, paesiUsati)
            parziale.pop()
            paesiUsati.remove(vicino.paese)

    def getPesoArco(self, c1, c2):
        return self._grafo[c1][c2]["weight"]