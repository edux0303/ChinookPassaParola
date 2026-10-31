import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    # ---------- PUNTO 1 ----------

    def fillDDGeneri(self):
        self._view._ddGenere.options.clear()
        for idG, nome in self._model.getGeneri():
            self._view._ddGenere.options.append(ft.dropdown.Option(key=str(idG), text=nome))
        self._view.update_page()

    def handleCreaGrafo(self, e):
        self._view._txt_result.controls.clear()

        # 1. genere
        if self._view._ddGenere.value is None:
            self._errore("Seleziona un genere!")
            return
        idGenere = int(self._view._ddGenere.value)

        # 2. soglia S
        try:
            soglia = int(self._view._txtInS.value)
        except (ValueError, TypeError):
            self._errore("S deve essere un numero intero!")
            return
        if soglia < 1:
            self._errore("S deve essere almeno 1!")
            return

        # 3. grafo
        self._model.buildGraph(idGenere, soglia)

        if self._model.getNumNodi() == 0:
            self._errore("Nessun cliente ha acquistato brani di questo genere.")
            return

        # 4. stampo
        self._view._txt_result.controls.append(ft.Text("Grafo creato correttamente!", color="green"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di nodi: {self._model.getNumNodi()}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumArchi()}"))

        # 5. dropdown clienti
        self.fillDDClienti()

        self._view.update_page()

    def fillDDClienti(self):
        self._view._ddClienteA.options.clear()
        self._view._ddClienteB.options.clear()
        self._view._ddClienteA.value = None
        self._view._ddClienteB.value = None
        for c in self._model.getNodiOrdinati():
            testo = f"{c.cognome} {c.nome} ({c.paese})"
            self._view._ddClienteA.options.append(ft.dropdown.Option(key=str(c.id), text=testo))
            self._view._ddClienteB.options.append(ft.dropdown.Option(key=str(c.id), text=testo))

    def handleStampaInfo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodi() == 0:
            self._errore("Crea prima il grafo!")
            return

        res = self._view._txt_result.controls

        # a) spesa maggiore
        cliente, spesa = self._model.getSpesaMaggiore()
        res.append(ft.Text(f"a) Cliente con spesa maggiore: {cliente} ({spesa:.2f} $)"))

        # b) più artisti
        lista, n = self._model.getPiuArtisti()
        res.append(ft.Text(f"b) Cliente con più artisti diversi ({n}): {', '.join(str(c) for c in lista)}"))

        # c) grado maggiore
        lista, grado = self._model.getGradoMaggiore()
        res.append(ft.Text(f"c) Cliente con grado maggiore ({grado}): {', '.join(str(c) for c in lista)}"))

        # d) top 5 archi
        res.append(ft.Text("d) I 5 archi di peso maggiore:"))
        for n1, n2, peso in self._model.getTop5Archi():
            res.append(ft.Text(f"     {n1} – {n2}: {peso}"))

        # e) componenti
        nComp, dimMax, isolati = self._model.getInfoComponenti()
        res.append(ft.Text(f"e) Componenti connesse: {nComp}"))
        res.append(ft.Text(f"     Dimensione della più grande: {dimMax}"))
        res.append(ft.Text(f"     Clienti isolati: {isolati}"))

        # f) paesi
        nPaesi, paesi, nClienti = self._model.getInfoPaesi()
        res.append(ft.Text(f"f) Paesi diversi: {nPaesi}"))
        res.append(ft.Text(f"     Paese con più clienti ({nClienti}): {', '.join(paesi)}"))

        # g) dipendenti
        res.append(ft.Text("g) Dipendenti di supporto:"))
        for nome, nClienti, spesa in self._model.getInfoDipendenti():
            res.append(ft.Text(f"     {nome}: {nClienti} clienti, spesa totale {spesa:.2f} $"))

        # h) archi stesso paese
        nArchi, arco = self._model.getArchiStessoPaese()
        res.append(ft.Text(f"h) Archi tra clienti dello stesso paese: {nArchi}"))
        if arco is not None:
            res.append(ft.Text(f"     Peso maggiore: {arco[0]} – {arco[1]}: {arco[2]} ({arco[3]})"))

        self._view.update_page()

    # ---------- PUNTO 2 ----------

    def handlePassaParola(self, e):
        self._view._txt_result.controls.clear()

        # 1. grafo creato?
        if self._model.getNumNodi() == 0:
            self._errore("Crea prima il grafo!")
            return

        # 2. clienti A e B
        if self._view._ddClienteA.value is None or self._view._ddClienteB.value is None:
            self._errore("Seleziona il cliente di partenza e quello di arrivo!")
            return
        A = self._model.getCliente(int(self._view._ddClienteA.value))
        B = self._model.getCliente(int(self._view._ddClienteB.value))
        if A is None or B is None:
            self._errore("Cliente non presente nel grafo!")
            return
        if A == B:
            self._errore("Partenza e arrivo devono essere clienti diversi!")
            return
        if A.paese == B.paese:
            self._errore(f"{A} e {B} sono dello stesso paese ({A.paese})!")
            return

        # 3. K
        try:
            K = int(self._view._txtInK.value)
        except (ValueError, TypeError):
            self._errore("K deve essere un numero intero!")
            return
        if K < 1:
            self._errore("K deve essere almeno 1!")
            return

        # 4. ricorsione
        cammino, peso = self._model.getPassaParola(A, B, K)

        if len(cammino) == 0:
            self._errore(f"Nessun cammino da {A} a {B} con al massimo {K} archi.")
            return

        # 5. stampo
        res = self._view._txt_result.controls
        res.append(ft.Text(f"Passaparola da {A} a {B}:", color="green"))
        res.append(ft.Text(f"     {cammino[0]} ({cammino[0].paese})"))
        for i in range(1, len(cammino)):
            p = self._model.getPesoArco(cammino[i - 1], cammino[i])
            res.append(ft.Text(f"     → {cammino[i]} ({cammino[i].paese}) [peso {p}]"))
        res.append(ft.Text(f"Numero di archi: {len(cammino) - 1}"))
        res.append(ft.Text(f"Peso totale: {peso}"))

        self._view.update_page()

    # ---------- UTILITY ----------

    def _errore(self, messaggio):
        self._view._txt_result.controls.append(ft.Text(messaggio, color="red"))
        self._view.update_page()