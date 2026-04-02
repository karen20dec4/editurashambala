#!/usr/bin/env python3
"""
Script pentru adăugarea diacriticelor românești în fișierele XLF de traducere Prestashop.

Modifică doar elementele <target state="final"> din fișierele .xlf,
adăugând diacriticele corecte (ă, â, î, ș, ț) în textele românești.
Structura XML și textele sursă (engleză) rămân neschimbate.

Utilizare:
    python3 fix_diacritics.py                     # procesează directorul ro-RO implicit
    python3 fix_diacritics.py /cale/spre/director  # procesează alt director
"""

import os
import re
import sys

# =============================================================================
# DICȚIONAR CUPRINZĂTOR: cuvânt_fără_diacritice -> cuvânt_cu_diacritice
# Doar forme lowercase – majusculele se aplică automat
# =============================================================================
DIACRITICS_MAP = {
    # =========================================================================
    # CUVINTE FUNCȚIONALE (prepoziții, conjuncții, particule)
    # =========================================================================
    "in": "în", "sa": "să", "si": "și", "daca": "dacă", "dupa": "după",
    "fara": "fără", "catre": "către", "cand": "când", "iti": "îți",
    "inainte": "înainte", "inaintea": "înaintea", "inapoi": "înapoi",
    "insa": "însă", "intre": "între", "pana": "până", "cat": "cât",
    "inca": "încă", "impotriva": "împotriva", "decat": "decât",
    "caci": "căci", "asadar": "așadar", "oricand": "oricând",
    "oricat": "oricât", "oricate": "oricâte", "oricind": "oricând",
    "nicicand": "nicicând", "niciodata": "niciodată",
    "intotdeauna": "întotdeauna", "totusi": "totuși",
    "datorita": "datorită", "asa": "așa", "acasa": "acasă",
    "catva": "câtva", "cate": "câte", "cati": "câți",
    "cativa": "câțiva", "cateva": "câteva", "indata": "îndată",
    "incotro": "încotro", "inapoiezi": "înapoiezi",
    "inainteaza": "înaintează",

    # =========================================================================
    # PRONUME ȘI POSESIVE
    # =========================================================================
    "aceasta": "această", "aceeasi": "aceeași", "aceaasta": "această",
    "aceiasi": "aceiași", "aceluiasi": "aceluiași",
    "tau": "tău", "tai": "tăi",
    "dumneavoastra": "dumneavoastră", "dumeavoastra": "dumneavoastră",
    "noastra": "noastră", "voastra": "voastră",

    # =========================================================================
    # VERBE CU TERMINAȚIA -EAZĂ (persoana a 3-a / imperativ)
    # =========================================================================
    "activeaza": "activează", "actualizeaza": "actualizează",
    "actualizeazati": "actualizează-ți", "actioneaza": "acționează",
    "afiseaza": "afișează", "ajusteaza": "ajustează",
    "analizeaza": "analizează", "anuleaza": "anulează",
    "asteapta": "așteaptă", "ataseaza": "atașează",
    "cauta": "caută", "clicheaza": "clichează",
    "copiaza": "copiază", "configureaza": "configurează",
    "configureazati": "configurează-ți",
    "contacteaza": "contactează", "contacteazane": "contactează-ne",
    "contacteazati": "contactează-ți",
    "controleaza": "controlează",
    "creeaza": "creează", "creeazati": "creează-ți",
    "comuta": "comută", "debifeaza": "debifează",
    "decupleaza": "decuplează",
    "deselecteaza": "deselectează", "deselecteazale": "deselectează-le",
    "dezactiveaza": "dezactivează",
    "evidentiaza": "evidențiază", "evidentiazai": "evidențiază-i",
    "estimeaza": "estimează", "evalueaza": "evaluează",
    "faciliteaza": "facilitează", "filtreaza": "filtrează",
    "finalizeaza": "finalizează", "genereaza": "generează",
    "gestioneaza": "gestionează", "gestioneazati": "gestionează-ți",
    "ilustreaza": "ilustrează", "limiteaza": "limitează",
    "listeaza": "listează", "memorizeaza": "memorează",
    "ordoneaza": "ordonează",
    "personalizeaza": "personalizează",
    "personalizeazati": "personalizează-ți",
    "proceseaza": "procesează", "recomanda": "recomandă",
    "redirectioneaza": "redirecționează",
    "regenereaza": "regenerează",
    "reinitializeaza": "reinițializează",
    "selecteaza": "selectează", "selecteazal": "selectează-l",
    "selecteazale": "selectează-le", "selecteazati": "selectează-ți",
    "sorteaza": "sortează", "tasteaza": "tastează",
    "valideaza": "validează", "viziteaza": "vizitează",
    "vizualizeaza": "vizualizează",
    "abandoneaza": "abandonează", "acceseaza": "accesează",
    "afecteaza": "afectează", "aplica": "aplică",
    "asociaza": "asociază", "bifeaza": "bifează",
    "colecteaza": "colectează", "compileaza": "compilează",
    "completeaza": "completează", "concentreazate": "concentrează-te",
    "corecteaza": "corectează", "creaza": "creează",
    "editeaza": "editează", "exploreaza": "explorează",
    "forteaza": "forțează", "furnizeaza": "furnizează",
    "improspateaza": "împrospătează", "incurajeaza": "încurajează",
    "indexeaza": "indexează", "jurnalizeaza": "jurnalizează",
    "lanseaza": "lansează", "marcheaza": "marchează",
    "reactiveaza": "reactivează", "realimenteaza": "realimentează",
    "realizeaza": "realizează", "rearanjeaza": "rearanjează",
    "recompileaza": "recompilează", "reinstaleaza": "reinstalează",
    "reseteaza": "resetează", "restaureaza": "restaurează",
    "sugereaza": "sugerează", "usureaza": "ușurează",
    "usureazale": "ușurează-le", "usureazati": "ușurează-ți",
    "reconforteazati": "reconfortează-ți",
    "imbogatesteti": "îmbogățește-ți",
    "administreaza": "administrează",
    "administreazati": "administrează-ți",
    "previzualizeaza": "previzualizează",
    "vizualieaza": "vizualizează",
    "printeaza": "printează",
    "stocheaza": "stochează",
    "navigheaza": "navighează",
    "salveaza": "salvează",
    "insoteasca": "însoțească",
    "completeazati": "completează-ți",
    "aboneazate": "abonează-te",

    # =========================================================================
    # VERBE CU TERMINAȚIA -EȘTE (persoana a 3-a)
    # =========================================================================
    "foloseste": "folosește", "defineste": "definește",
    "stabileste": "stabilește", "construieste": "construiește",
    "economiseste": "economisește", "goleste": "golește",
    "imbogateste": "îmbogățește", "incetineste": "încetinește",
    "indeplineste": "îndeplinește", "inlocuieste": "înlocuiește",
    "intareste": "întărește", "mareste": "mărește",
    "maresteti": "mărește-ți", "opreste": "oprește",
    "paraseste": "părăsește", "potriveste": "potrivește",
    "primeste": "primește", "reconstruieste": "reconstruiește",
    "redenumeste": "redenumește", "tipareste": "tipărește",
    "citeste": "citește", "fololeste": "folosește",
    "depaseste": "depășește", "descopera": "descoperă",

    # =========================================================================
    # VERBE CU TERMINAȚIA -EȘTI (persoana a 2-a singular)
    # =========================================================================
    "doresti": "dorești", "poti": "poți", "esti": "ești",
    "folosesti": "folosești", "definesti": "definești",
    "construiesti": "construiești", "citesti": "citești",
    "economisesti": "economisești", "golesti": "golești",
    "impartasesti": "împărtășești", "indeplinesti": "îndeplinești",
    "opresti": "oprești", "parasesti": "părăsești",
    "stabilesti": "stabilești", "tiparesti": "tipărești",
    "banuiesti": "bănuiești", "gandestete": "gândește-te",
    "pregatesteti": "pregătește-ți", "tintesteti": "țintește-ți",
    "urmaresteti": "urmărește-ți",
    "platesti": "plătești",
    "intalnesti": "întâlnești",

    # =========================================================================
    # VERBE CU TERMINAȚIA -Ă (persoana a 3-a / imperativ)
    # =========================================================================
    "adauga": "adaugă", "arata": "arată",
    "aratale": "arată-le", "contina": "conțină",
    "determina": "determină", "exista": "există",
    "incearca": "încearcă", "incarca": "încarcă",
    "inceapa": "înceapă", "incepe": "începe",
    "inchide": "închide", "inseamna": "înseamnă",
    "inregistreaza": "înregistrează",
    "instaleaza": "instalează",
    "dezinstaleaza": "dezinstalează",
    "verifica": "verifică", "astepta": "așteaptă",
    "confirma": "confirmă", "asigura": "asigură",
    "indica": "indică", "reincarca": "reîncarcă",
    "reincearca": "reîncearcă", "apartine": "aparține",
    "contine": "conține", "solicita": "solicită",
    "elimina": "elimină", "ajuta": "ajută",
    "necesita": "necesită", "consulta": "consultă",
    "notifica": "notifică", "identifica": "identifică",
    "comunica": "comunică", "specifica": "specifică",
    "modifica": "modifică", "afla": "află",
    "cumpara": "cumpără", "descarca": "descarcă",
    "informa": "informă",

    # =========================================================================
    # VERBE PERSOANA I PLURAL (-ĂM)
    # =========================================================================
    "rugam": "rugăm", "asiguram": "asigurăm",
    "recomandam": "recomandăm", "sugeram": "sugerăm",
    "informam": "informăm", "actualizam": "actualizăm",
    "sfatuim": "sfătuim", "verificam": "verificăm",

    # =========================================================================
    # VERBE PERSOANA A 2-A PLURAL (-AȚI / -EȚI)
    # =========================================================================
    "acceptati": "acceptați", "activati": "activați",
    "ajutati": "ajutați", "alegeti": "alegeți",
    "completati": "completați", "configurati": "configurați",
    "contactati": "contactați", "dezactivati": "dezactivați",
    "identificati": "identificați", "selectati": "selectați",
    "verificati": "verificați", "editati": "editați",
    "distribuiti": "distribuiți", "adunati": "adunați",
    "aveti": "aveți", "cereti": "cereți",
    "primiti": "primiți", "retrimiti": "retrimiți",
    "scrieti": "scrieți", "doriti": "doriți",
    "fiti": "fiți", "sunteti": "sunteți",
    "sinteti": "sunteți", "introduceti": "introduceți",
    "stergeti": "ștergeți", "incantati": "încântați",
    "ridicati": "ridicați",

    # =========================================================================
    # FAMILIA ȘTERGE
    # =========================================================================
    "sterge": "șterge", "stergere": "ștergere",
    "stergerea": "ștergerea", "stergerii": "ștergerii",
    "stergi": "ștergi", "sterg": "șterg",
    "sters": "șters", "stearsa": "ștearsă",
    "sterse": "șterse", "stersi": "șterși",

    # =========================================================================
    # FAMILIA ȘTI
    # =========================================================================
    "stie": "știe", "stii": "știi", "stiu": "știu",
    "stiri": "știri", "stirii": "știrii",

    # =========================================================================
    # SUBSTANTIVE CU Ș
    # =========================================================================
    # FIȘIER
    "fisier": "fișier", "fisiere": "fișiere",
    "fisierele": "fișierele", "fisierelor": "fișierelor",
    "fisierul": "fișierul", "fisierulde": "fișierulde",
    "fisierului": "fișierului", "fisieruui": "fișierului",
    # COȘ
    "cos": "coș", "cosul": "coșul", "cosului": "coșului",
    "cosuri": "coșuri", "cosurile": "coșurile",
    # CĂSUȚĂ
    "casuta": "căsuță", "casutele": "căsuțele",
    # GREȘEALĂ
    "greseala": "greșeală", "gresit": "greșit", "gresita": "greșită",
    "greseli": "greșeli",
    # UȘOR
    "usor": "ușor", "usoara": "ușoară", "usori": "ușori",
    "usurinta": "ușurință", "usura": "ușura",
    # ȘABLON
    "sabloane": "șabloane", "sabloanele": "șabloanele",
    "sabloanelor": "șabloanelor", "sablon": "șablon",
    "sablonul": "șablonul", "sablonului": "șablonului",
    # MAȘINĂ
    "masina": "mașină",
    # CUNOAȘTE
    "cunoaste": "cunoaște", "cunostinta": "cunoștință",
    # CENUȘIU
    "cenusiu": "cenușiu",
    # CROȘET
    "croset": "croșet",
    # CURIOȘILOR
    "curiosilor": "curioșilor",
    # DESFĂȘURARE
    "desfasurare": "desfășurare",
    # MIȘCARE
    "miscarea": "mișcarea", "miscari": "mișcări",
    "miscarii": "mișcării", "miscarile": "mișcările",
    # OBIȘNUIT
    "obisnuit": "obișnuit",

    # =========================================================================
    # SUBSTANTIVE CU Ț
    # =========================================================================
    # INFORMAȚII
    "informatii": "informații", "informatiile": "informațiile",
    "informatiilor": "informațiilor", "informatie": "informație",
    "informatia": "informația",
    "metainformatii": "metainformații",
    # PREȚ
    "pret": "preț", "pretul": "prețul", "pretului": "prețului",
    "preturi": "prețuri", "preturile": "prețurile",
    "preturilor": "prețurilor",
    # OPȚIUNE
    "optiune": "opțiune", "optiunea": "opțiunea",
    "optiuni": "opțiuni", "optiunii": "opțiunii",
    "optiunile": "opțiunile",
    # ACȚIUNE
    "actiune": "acțiune", "actiunea": "acțiunea",
    "actiuni": "acțiuni", "actiunile": "acțiunile",
    # SECȚIUNE
    "sectiune": "secțiune", "sectiunea": "secțiunea",
    "sectiuni": "secțiuni",
    # CONDIȚIE
    "conditie": "condiție", "conditia": "condiția",
    "conditii": "condiții", "conditiile": "condițiile",
    "conditiilor": "condițiilor",
    # FUNCȚIE
    "functie": "funcție", "functia": "funcția",
    "functiei": "funcției", "functii": "funcții",
    "functiile": "funcțiile", "functional": "funcțional",
    "functionala": "funcțională",
    "functionalitate": "funcționalitate",
    "functionalitatea": "funcționalitatea",
    "functionalitati": "funcționalități",
    "functionalitatile": "funcționalitățile",
    "functioneaza": "funcționează",
    "functioneze": "funcționeze",
    # RELAȚIE
    "relatii": "relații",
    # COMBINAȚIE
    "combinatii": "combinații", "combinatiile": "combinațiile",
    "combinatiilor": "combinațiilor", "combinatie": "combinație",
    "combinatia": "combinația", "combinatiei": "combinației",
    # OPERAȚIE
    "operatie": "operație", "operatia": "operația",
    "operationale": "operaționale", "operatiune": "operațiune",
    "operatiunea": "operațiunea", "operatiuni": "operațiuni",
    # TRANZACȚIE
    "tranzactie": "tranzacție", "tranzactiei": "tranzacției",
    "tranzitiei": "tranziției",
    # ACHIZIȚIE
    "achizitie": "achiziție", "achizitii": "achiziții",
    "achizitiile": "achizițiile", "achizitionat": "achiziționat",
    "achizitionate": "achiziționate",
    # POZIȚIE
    "pozitie": "poziție", "pozitia": "poziția",
    "pozitiei": "poziției", "pozitii": "poziții",
    "pozitionat": "poziționat",
    # EXPEDIȚIE
    "expeditie": "expediție", "expeditia": "expediția",
    # EXECUȚIE
    "executie": "execuție", "executia": "execuția",
    # EDIȚIE
    "editie": "ediție", "editii": "ediții",
    # PROTECȚIE
    "protectie": "protecție",
    # PRODUCȚIE
    "productie": "producție",
    # DISTRIBUȚIE
    "distributie": "distribuție", "distributia": "distribuția",
    # PROMOȚIE
    "promotii": "promoții", "promotiile": "promoțiile",
    "promotional": "promoțional", "promotionale": "promoționale",
    # RESTRICȚIE
    "restrictie": "restricție", "restrictii": "restricții",
    "restrictiilor": "restricțiilor", "restrictia": "restricția",
    "restrictionarea": "restricționarea",
    "restrictionat": "restricționat",
    "restrictionate": "restricționate",
    "restictii": "restricții",
    # SELECȚIE
    "selectie": "selecție", "selectia": "selecția",
    "selectiei": "selecției", "selectii": "selecții",
    # DESTINAȚIE
    "destinatie": "destinație",
    # OBLIGAȚIE
    "obligatie": "obligație", "obligatia": "obligația",
    "obligatii": "obligații", "obligatiuni": "obligațiuni",
    # AUTORIZAȚIE
    "autorizatie": "autorizație",
    # NOTIFICĂRI
    "notificari": "notificări", "notificarii": "notificării",
    "notificarile": "notificările",
    # REDIRECȚIONARE
    "redirectionare": "redirecționare",
    "redirectionarea": "redirecționarea",
    "redirectionarii": "redirecționării",
    "redirectionat": "redirecționat",
    "redirectionate": "redirecționate",
    "redirectionati": "redirecționați",
    "redirectioneze": "redirecționeze",
    "redirectionezi": "redirecționezi",
    # APROXIMAȚII
    "aproximatii": "aproximații",
    # PUȚIN
    "putin": "puțin", "putina": "puțină",
    # ATENȚIE
    "atentie": "atenție", "atentia": "atenția",
    # DISCUȚIE
    "discutie": "discuție", "discutiei": "discuției",
    "discutii": "discuții", "discutiilor": "discuțiilor",
    # SITUAȚIE
    "situatia": "situația", "situatii": "situații",
    # PROPORȚIA
    "proportia": "proporția",
    # CONVERSAȚIE
    "conversatia": "conversația", "conversatii": "conversații",
    # EXPLICAȚIE
    "explicatia": "explicația", "explicatii": "explicații",
    "explicatie": "explicație",
    # EXCEPȚIE
    "exceptia": "excepția", "exceptii": "excepții",
    "exceptiile": "excepțiile",
    # DISPOZIȚIE
    "dispozitia": "dispoziția",
    # CONFIGURAȚIE
    "configuratia": "configurația", "configuratiei": "configurației",
    "configuratii": "configurații", "configuratie": "configurație",
    # COMPARAȚIE
    "comparatie": "comparație", "reclamatia": "reclamația",
    # CONSECINȚĂ
    "consecinta": "consecință", "consecinte": "consecințe",
    # REFERINȚĂ
    "referinta": "referință", "referinte": "referințe",
    "referintele": "referințele",
    # CERINȚĂ
    "cerinta": "cerință", "cerinte": "cerințe",
    "cerintele": "cerințele",
    # CONȚINUT
    "continut": "conținut", "continute": "conținute",
    "continutul": "conținutul", "continutului": "conținutului",
    "contin": "conțin", "contina": "conțină",
    "contine": "conține", "continand": "conținând",
    # REȚINE / MENȚINE / OBȚINE
    "retine": "reține", "retinut": "reținut",
    "intretinere": "întreținere",
    "mentine": "menține", "mentinel": "menține-l",
    "mentinerea": "menținerea",
    "obtine": "obține", "obtinerea": "obținerea",
    # DICȚIONAR
    "dictionar": "dicționar",
    # COMERȚ
    "comert": "comerț", "comertului": "comerțului",
    # RECEPȚIE
    "receptia": "recepția",
    "receptionat": "recepționat",
    # DOCUMENTAȚIE
    "documentatia": "documentația", "documentatie": "documentație",
    # LEGISLAȚIE
    "legislatia": "legislația",
    # EVOLUȚIE
    "evolutia": "evoluția", "evolutiei": "evoluției",
    # CONSIMȚĂMÂNT
    "consimtamantul": "consimțământul",
    # INJECȚIE
    "injectie": "injecție",
    # VARIAȚII
    "variatii": "variații",
    # OBSERVAȚII
    "observatii": "observații",
    # DORINȚE
    "dorinte": "dorințe", "dorintelor": "dorințelor",
    # NOUTĂȚI
    "noutati": "noutăți",
    # FRUMUSEȚE
    "frumusete": "frumusețe",
    # INSTANȚĂ
    "instanta": "instanță",

    # =========================================================================
    # SUBSTANTIVE / ADJECTIVE CU Â
    # =========================================================================
    # CÂMP
    "campul": "câmpul", "campului": "câmpului",
    "campuri": "câmpuri", "campurile": "câmpurile",
    "campurilor": "câmpurilor", "camp": "câmp",
    # NUMĂR
    "numar": "număr", "numarul": "numărul",
    "numarului": "numărului",
    # ADÂNCIME
    "adancime": "adâncime", "adancimea": "adâncimea",
    # CUVÂNT
    "cuvant": "cuvânt", "cuvantcheie": "cuvântcheie",
    "cuvantul": "cuvântul", "cuvantulcheie": "cuvântulcheie",
    "cuvantului": "cuvântului",
    # VÂRSTĂ
    "varsta": "vârstă",
    # TÂRZIU
    "tarziu": "târziu",
    # ÎNTÂI
    "intai": "întâi",
    # GÂTUITURILOR
    "gatuiturilor": "gâtuiturilor",

    # =========================================================================
    # CUVINTE CU PREFIXUL ÎM- / ÎN-
    # =========================================================================
    # ÎMBUNĂTĂȚI
    "imbunatati": "îmbunătăți", "imbunatateste": "îmbunătățește",
    "imbunatateasca": "îmbunătățească",
    "imbunatatirea": "îmbunătățirea",
    "imbricata": "îmbricată",
    "imbogateste": "îmbogățește",
    "imbogatesteti": "îmbogățește-ți",
    "imbogati": "îmbogăți",
    # ÎMPACHETARE
    "impachetare": "împachetare", "impachetarea": "împachetarea",
    "impartasesti": "împărtășești",
    "impartirea": "împărțirea", "impartite": "împărțite",
    "impiedica": "împiedică",
    "improspata": "împrospăta", "improspatarea": "împrospătarea",
    "improspateaza": "împrospătează",
    # ÎNĂLȚIME
    "inaltime": "înălțime", "inaltimea": "înălțimea",
    # ÎNCĂLȚĂMINTE
    "incaltaminte": "încălțăminte",
    # ÎNCARCĂ
    "incarca": "încarcă", "incarcabile": "încărcabile",
    "incarcare": "încărcare", "incarcarea": "încărcarea",
    "incarcarii": "încărcării", "incarcat": "încărcat",
    "incarcata": "încărcată", "incarcate": "încărcate",
    "incarce": "încarce", "incarci": "încarci",
    # ÎNCÂT
    "incat": "încât",
    # ÎNCEAPĂ / ÎNCEPE
    "inceapa": "înceapă", "incearca": "încearcă",
    "incepand": "începând", "incepe": "începe",
    "incepem": "începem", "inceperii": "începerii",
    "incepi": "începi", "inceput": "început",
    "inceputa": "începută", "inceputul": "începutul",
    # ÎNCERCARE
    "incerca": "încearcă", "incercare": "încercare",
    "incercarea": "încercarea", "incercari": "încercări",
    "incerci": "încerci",
    # ÎNCETINEȘTE
    "incetineste": "încetinește",
    # ÎNCHEIE
    "incheiat": "încheiat", "incheie": "încheie",
    "incheierea": "încheierea",
    # ÎNCHIDE
    "inchide": "închide", "inchiderea": "închiderea",
    "inchis": "închis", "inchisa": "închisă",
    "inchise": "închise",
    # INCLUDE
    "includa": "includă", "inclusa": "inclusă",
    "incluzand": "incluzând",
    # INCOMPLETĂ / INCORECTĂ
    "incompleta": "incompletă",
    "incorecta": "incorectă",
    # ÎNCREDERE
    "increderea": "încrederea",
    # ÎNCRUCIȘATE
    "incrucisate": "încrucișate",
    # ÎNDEPĂRTEAZĂ
    "indeparta": "îndepărtă", "indeparteaza": "îndepărtează",
    "indeplinesc": "îndeplinesc", "indeplineste": "îndeplinește",
    "indeplinesti": "îndeplinești", "indeplinite": "îndeplinite",
    # INDICĂ
    "indica": "indică",
    # INDISPONIBILĂ
    "indisponibila": "indisponibilă",
    # ÎNLĂTURAT
    "inlaturat": "înlăturat",
    # ÎNLOCUI
    "inlocui": "înlocui", "inlocuieste": "înlocuiește",
    "inlocuit": "înlocuit", "inlocuita": "înlocuită",
    "inlocuite": "înlocuite",
    # ÎNREGISTRA
    "inregistra": "înregistra", "inregistrand": "înregistrând",
    "inregistrare": "înregistrare", "inregistrarea": "înregistrarea",
    "inregistrari": "înregistrări", "inregistrarii": "înregistrării",
    "inregistrarilor": "înregistrărilor",
    "inregistrat": "înregistrat", "inregistrata": "înregistrată",
    "inregistrate": "înregistrate", "inregistrati": "înregistrați",
    "inregistreaza": "înregistrează",
    "inregistreze": "înregistreze", "inregistrezi": "înregistrezi",
    # ÎNRUDITE
    "inrudite": "înrudite",
    # ÎNSCRIE
    "inscrie": "înscrie", "inscriete": "înscrie-te",
    "inscris": "înscris",
    # ÎNSEAMNĂ
    "inseamna": "înseamnă",
    # INSTABILĂ / INSTALARE
    "instabila": "instabilă",
    "instalarii": "instalării", "instalata": "instalată",
    "instaleaza": "instalează",
    "dezinstalarii": "dezinstalării",
    "dezinstaleaza": "dezinstalează",
    # ÎNTÂMPINĂ
    "intampina": "întâmpină", "intampla": "întâmplă",
    "intamplat": "întâmplat",
    # ÎNTĂREȘTE / ÎNTÂRZIERE
    "intareste": "întărește",
    "intarziere": "întârziere", "intarzierea": "întârzierea",
    # ÎNȚELEG
    "inteleaga": "înțeleagă", "inteleg": "înțeleg",
    "intelegi": "înțelegi",
    # INTERFAȚĂ
    "interfata": "interfață",
    # INTERNĂ / INTERNAȚIONAL
    "interna": "internă",
    "international": "internațional",
    "internationala": "internațională",
    # INTERZISĂ
    "interzisa": "interzisă",
    # ÎNTINDERE
    "intinderea": "întinderea",
    # ÎNTOARCE
    "intoarce": "întoarce",
    # INTRĂ
    "intra": "intră",
    # ÎNTREBARE
    "intrebare": "întrebare", "intrebari": "întrebări",
    # ÎNTREG
    "intreg": "întreg", "intregi": "întregi",
    "intregului": "întregului",
    # ÎNTRERUPTĂ
    "intrerupta": "întreruptă",
    # INTRODUCE
    "introducand": "introducând",
    "introduceo": "introduce-o",
    # ÎNTRUCÂT
    "intrucat": "întrucât", "intrucit": "întrucât",
    # ÎNVAȚĂ
    "invata": "învață",
    # ÎNGUSTĂ
    "ingusta": "îngustă",
    # ÎNTREAGĂ
    "intreaga": "întreagă",
    # ÎNTREȚINERE
    "intretinere": "întreținere",

    # =========================================================================
    # SUBSTANTIVE – ȚARĂ
    # =========================================================================
    "tara": "țară", "tari": "țări", "tarii": "țării",
    "tarile": "țările", "tarilele": "țările",
    "tarilor": "țărilor",

    # =========================================================================
    # CĂUTARE
    # =========================================================================
    "cautare": "căutare", "cautarea": "căutarea",
    "cautari": "căutări", "cautarii": "căutării",
    "cautat": "căutat", "cautata": "căutată",
    "cautate": "căutate", "cautati": "căutați",
    "cautand": "căutând",

    # =========================================================================
    # CLIENȚI / ABONAȚI / ANGAJAȚI / COMERCIANȚI
    # =========================================================================
    "clienti": "clienți", "clientii": "clienții",
    "clientilor": "clienților",
    "abonati": "abonați", "abonatii": "abonații",
    "angajati": "angajați", "angajatii": "angajații",
    "angajatilor": "angajaților",
    "comercianti": "comercianți", "comerciantii": "comercianții",
    "comerciantilor": "comercianților",

    # =========================================================================
    # CUMPĂRĂ / VÂNZARE
    # =========================================================================
    "cumpara": "cumpără", "cumparare": "cumpărare",
    "cumparat": "cumpărat", "cumparate": "cumpărate",
    "cumparatura": "cumpărătură", "cumparaturi": "cumpărături",
    "cumparaturie": "cumpărăturile",
    "cumparaturile": "cumpărăturile",
    "cumparatorii": "cumpărătorii",
    "cumparatorilor": "cumpărătorilor",
    "cumparatoarelor": "cumpărătoarelor",
    "vanzare": "vânzare", "vanzarea": "vânzarea",
    "vanzari": "vânzări", "vanzarile": "vânzările",
    "vanzarilor": "vânzărilor",
    "vandut": "vândut", "vanduta": "vândută",
    "vandute": "vândute",

    # =========================================================================
    # APĂRUT
    # =========================================================================
    "aparut": "apărut", "aparuta": "apărută",
    "aparea": "apărea", "aparitiei": "apariției",
    "aparitii": "apariții",

    # =========================================================================
    # FORME DE -ĂRI (plural substantive verbale)
    # =========================================================================
    "abonari": "abonări", "abonarii": "abonării",
    "modificari": "modificări", "modificarii": "modificării",
    "modificarile": "modificările", "modificarilor": "modificărilor",
    "configurari": "configurări", "configurarii": "configurării",
    "configurarile": "configurările",
    "actualizari": "actualizări", "actualizarii": "actualizării",
    "avertizari": "avertizări", "avertizarile": "avertizările",
    "setari": "setări", "setarii": "setării",
    "setarile": "setările", "setarilor": "setărilor",
    "verificari": "verificări", "verificarii": "verificării",
    "verificarile": "verificările",
    "returnari": "returnări", "returnarii": "returnării",
    "returnarile": "returnările", "returnarilor": "returnărilor",
    "rambursarii": "rambursării",
    "informarile": "informările",
    "comunicarile": "comunicările",
    "inserarii": "inserării",
    "expirarii": "expirării",
    "aplicarii": "aplicării",
    "comprimarii": "comprimării",
    "finalizarii": "finalizării",
    "publicarii": "publicării",
    "lucrarilor": "lucrărilor",
    "reglementarilor": "reglementărilor",
    "incercari": "încercări",
    "felicitari": "felicitări",
    "nasteri": "nașteri", "nasterii": "nașterii",

    # =========================================================================
    # PARTICIPII FEMININE (-ATĂ)
    # =========================================================================
    "finalizata": "finalizată",
    "activata": "activată",
    "dezactivata": "dezactivată",
    "actualizata": "actualizată",
    "configurata": "configurată",
    "instalata": "instalată",
    "anulata": "anulată",
    "creata": "creată",
    "confirmata": "confirmată",
    "asociata": "asociată",
    "aplicata": "aplicată",
    "modificata": "modificată",
    "selectata": "selectată",
    "acceptata": "acceptată",
    "conectata": "conectată",
    "efectuata": "efectuată",
    "verificata": "verificată",
    "detectata": "detectată",
    "descarcata": "descărcată",
    "generata": "generată",
    "exportata": "exportată",
    "importata": "importată",
    "resetata": "resetată",
    "autentificata": "autentificată",
    "copiata": "copiată",
    "personalizata": "personalizată",
    "redenumita": "redenumită",
    "returnata": "returnată",
    "restaurata": "restaurată",
    "procesata": "procesată",
    "trimisa": "trimisă",
    "blocata": "blocată",
    "expediata": "expediată",
    "livrata": "livrată",
    "ridicata": "ridicată",
    "adaptata": "adaptată",
    "informata": "informată",
    "securizata": "securizată",
    "rezolvata": "rezolvată",
    "depreciata": "depreciată",
    "facuta": "făcută", "facute": "făcute", "facut": "făcut",
    "alcatuita": "alcătuită",
    "apasata": "apăsată",
    "adaugata": "adăugată", "adaugate": "adăugate", "adaugat": "adăugat",
    "inregistrata": "înregistrată",
    "incarcata": "încărcată",
    "inceputa": "începută",
    "inlocuita": "înlocuită",
    "salvata": "salvată",
    "utilizata": "utilizată",
    "specificata": "specificată",
    "moderata": "moderată",
    "citita": "citită", "cititi": "citiți",
    "atribuita": "atribuită",
    "cheltuita": "cheltuită",
    "migrata": "migrată",
    "golita": "golită",
    "neasteptata": "neașteptată",
    "neprevazuta": "neprevăzută", "neprevazute": "neprevăzute",
    "neplatita": "neplătită",
    "evidentiata": "evidențiată",
    "micsorata": "micșorată",
    "scazuta": "scăzută",
    "satisfacut": "satisfăcut",
    "deschisa": "deschisă",
    "ascunsa": "ascunsă",
    "intalnita": "întâlnită",

    # =========================================================================
    # ADJECTIVE FEMININE (-Ă)
    # =========================================================================
    "disponibila": "disponibilă",
    "compatibila": "compatibilă",
    "aplicabila": "aplicabilă",
    "necesara": "necesară",
    "valida": "validă",
    "invalida": "invalidă",
    "corecta": "corectă",
    "directa": "directă",
    "imediata": "imediată",
    "separata": "separată",
    "completa": "completă",
    "reala": "reală",
    "diferita": "diferită",
    "actuala": "actuală",
    "generala": "generală",
    "globala": "globală",
    "originala": "originală",
    "clasica": "clasică",
    "publica": "publică",
    "simpla": "simplă",
    "stabila": "stabilă",
    "albastra": "albastră",
    "alternativa": "alternativă",
    "anterioara": "anterioară",
    "apropiata": "apropiată",
    "atractiva": "atractivă",
    "abuziva": "abuzivă",
    "centrala": "centrală",
    "clara": "clară",
    "circulara": "circulară",
    "complementara": "complementară",
    "curenta": "curentă",
    "eficienta": "eficientă",
    "electronica": "electronică",
    "fatala": "fatală",
    "fiscala": "fiscală",
    "geografica": "geografică",
    "gratuita": "gratuită",
    "implicita": "implicită",
    "importanta": "importantă",
    "larga": "largă",
    "laterala": "laterală",
    "legala": "legală",
    "maxima": "maximă",
    "minima": "minimă",
    "monetara": "monetară",
    "oficiala": "oficială",
    "permanenta": "permanentă",
    "personala": "personală",
    "principala": "principală",
    "privata": "privată",
    "profitabila": "profitabilă",
    "publicitara": "publicitară",
    "rapida": "rapidă",
    "recursiva": "recursivă",
    "relevanta": "relevantă",
    "secundara": "secundară",
    "suficienta": "suficientă",
    "insuficienta": "insuficientă",
    "suplimentara": "suplimentară",
    "temporara": "temporară",
    "verticala": "verticală",
    "virtuala": "virtuală",
    "nelimitata": "nelimitată",
    "instabila": "instabilă",
    "aferenta": "aferentă",
    "automata": "automată",
    "manuala": "manuală",
    "nationala": "națională",
    "bancara": "bancară",
    "buna": "bună",
    "scurta": "scurtă",
    "plina": "plină",
    "proasta": "proastă",
    "similara": "similară",
    "prietenoasa": "prietenoasă",
    "semnificativa": "semnificativă",
    "reprezentativa": "reprezentativă",
    "sugestiva": "sugestivă",
    "incapabila": "incapabilă",

    # =========================================================================
    # OPȚIONAL / ESENȚIAL / CONFIDENȚIAL / POTENȚIAL
    # =========================================================================
    "optionala": "opțională", "optionale": "opționale",
    "optionali": "opționali", "optional": "opțional",
    "esentiala": "esențială", "esentiale": "esențiale",
    "esentiali": "esențiali", "esentialul": "esențialul",
    "esential": "esențial",
    "confidentialitate": "confidențialitate",
    "confidentialitatea": "confidențialitatea",
    "potentiale": "potențiale", "potentialelor": "potențialelor",

    # =========================================================================
    # INIȚIAL / REINIȚIALIZARE
    # =========================================================================
    "initiala": "inițială", "initiale": "inițiale",
    "initialele": "inițialele",
    "initiata": "inițiată", "initierea": "inițierea",
    "reinitializa": "reinițializa",
    "reinitializare": "reinițializare",
    "reinitializarea": "reinițializarea",
    "reinitializeaza": "reinițializează",
    "reinitializezi": "reinițializezi",
    "aditional": "adițional", "aditionala": "adițională",
    "aditionale": "adiționale",

    # =========================================================================
    # DIVERSE -INȚĂ / -ENȚĂ / -AȚĂ / -ĂȚII
    # =========================================================================
    "diferente": "diferențe",
    "existenta": "existență",
    "toleranta": "toleranță",
    "experienta": "experiență",
    "licenta": "licență", "licentei": "licenței",
    "licentiat": "licențiat", "licentiate": "licențiate",
    "constanta": "constantă",
    "performanta": "performanță",
    "siguranta": "siguranță",
    "balanta": "balanță",
    "restanta": "restanță",
    "securitatii": "securității",
    "disponibilitatii": "disponibilității",
    "activitatii": "activității",
    "proprietati": "proprietăți",
    "proprietatii": "proprietății",
    "proprietatile": "proprietățile",
    "facilitati": "facilități",
    "facilitatile": "facilitățile",
    "cantitati": "cantități",
    "cantitatile": "cantitățile",
    "cantitatilor": "cantităților",
    "prioritatilor": "priorităților",
    "vulnerabilitatilor": "vulnerabilităților",
    "unitati": "unități", "unitatii": "unității",
    "entitati": "entități",
    "loialitatii": "loialității",
    "profitabilitatii": "profitabilității",

    # =========================================================================
    # DESCĂRCARE / PĂSTRARE / GĂSIRE / RĂMÂNE / MĂSURĂ
    # =========================================================================
    "descarcabil": "descărcabil", "descarcabile": "descărcabile",
    "descarcare": "descărcare", "descarcarea": "descărcarea",
    "descarcari": "descărcări", "descarcarii": "descărcării",
    "descarcat": "descărcat", "descarcata": "descărcată",
    "descarcate": "descărcate", "descarce": "descărce",
    "descarci": "descărci",
    "pastra": "păstra", "pastrarea": "păstrarea",
    "pastrat": "păstrat", "pastrate": "păstrate",
    "pastreaza": "păstrează", "pastreazati": "păstrează-ți",
    "pastrezi": "păstrezi",
    "gaseasca": "găsească", "gaseste": "găsește",
    "gasi": "găsi", "gasim": "găsim",
    "gasirea": "găsirea", "gasit": "găsit",
    "gasita": "găsită", "gasite": "găsite",
    "gasiti": "găsiți",
    "ramas": "rămas", "ramasa": "rămasă",
    "ramase": "rămase", "ramai": "rămâi",
    "raman": "rămân", "ramane": "rămâne",
    "ramanere": "rămânere",
    "masura": "măsură", "masuratorile": "măsurătorile",
    "masuri": "măsuri",

    # =========================================================================
    # SĂPTĂMÂNĂ / CARACTERISTICĂ / ADĂUGARE / AFIȘARE / ATAȘAMENT
    # =========================================================================
    "saptamana": "săptămână", "saptamanal": "săptămânal",
    "saptamanale": "săptămânale",
    "caracteristica": "caracteristică",
    "corespunzatoare": "corespunzătoare",
    "corespunzator": "corespunzător",
    "crescator": "crescător", "descrescator": "descrescător",
    "adaugare": "adăugare", "adaugarea": "adăugarea",
    "adaugarii": "adăugării",
    "adaugale": "adaugă-le",
    "adaugandule": "adăugându-le",
    "adaugand": "adăugând",
    "afisand": "afișând", "afisare": "afișare",
    "afisarea": "afișarea", "afisarii": "afișării",
    "afisat": "afișat", "afisata": "afișată",
    "afisate": "afișate", "afisezi": "afișezi",
    "atasament": "atașament", "atasamentului": "atașamentului",
    "atasat": "atașat", "atasate": "atașate",

    # =========================================================================
    # ALTE CUVINTE DIVERSE
    # =========================================================================
    "adevarat": "adevărat",
    "aratand": "arătând",
    "raspunde": "răspunde", "raspuns": "răspuns", "raspunsul": "răspunsul",
    "vrajitor": "vrăjitor",
    "retea": "rețea", "retele": "rețele", "retelele": "rețelele",
    "scurtatura": "scurtătură",
    "legatura": "legătură", "legaturi": "legături",
    "legaturile": "legăturile", "legaturilor": "legăturilor",
    "nelamuriri": "nelămuriri",
    "macar": "măcar",
    "marime": "mărime", "marimea": "mărimea",
    "marimi": "mărimi",
    "marita": "mărită",
    "mareasca": "mărească",
    "amanare": "amânare", "amanarea": "amânarea",
    "amanuntul": "amănuntul",
    "variabila": "variabilă",
    "conecteazate": "conectează-te",
    "deconecteazama": "deconectează-mă",
    "scoatema": "scoate-mă",
    "negasit": "negăsit", "negasita": "negăsită",
    "negasite": "negăsite",
    "neselecteaza": "neselectează",
    "iesi": "ieși",
    "castiga": "câștigă", "castigale": "câștigă-le",
    "castigarea": "câștigarea",
    "sarit": "sărit",
    "ratacit": "rătăcit",
    "sageata": "săgeată",
    "hartile": "hărțile",
    # "harta" nu se include — este ambiguu (forma definită "harta site-ului" e corectă)
    "aiba": "aibă",
    "faca": "facă",
    "permita": "permită",
    "plateasca": "plătească",
    "potriveasca": "potrivească",
    "primeasca": "primească",
    "aleaga": "aleagă",
    "creasca": "crească",
    "bucura": "bucură",
    "invitai": "invită-i",
    "invitatia": "invitația",
    "acordai": "acordă-i",
    "oferai": "oferă-i",
    "clicai": "clică-i",
    "trimitemi": "trimite-mi",
    "trimitene": "trimite-ne",
    "leai": "le-ai",
    "tiai": "ți-ai",
    "teai": "te-ai",
    "alegeo": "alege-o",
    "ofera": "oferă",
    "evidentiaza": "evidențiază",
    "evidentiere": "evidențiere",
    "evidentiat": "evidențiat",
    "reputatiei": "reputației",
    "reactionezi": "reacționezi",
    "partajeaza": "partajează",
    "transformandul": "transformându-l",
    "folosindute": "folosindu-te",
    "plati": "plăți", "platibil": "plătibil",
    "platii": "plății", "platile": "plățile",
    "platilor": "plăților", "platit": "plătit",
    "platita": "plătită", "platite": "plătite",
    "platiti": "plătiți",

    # GERUNDII (-ÂND)
    "activand": "activând", "alegand": "alegând",
    "completand": "completând", "facand": "făcând",
    "luand": "luând", "selectand": "selectând",
    "apasand": "apăsând", "furnizand": "furnizând",
    "reprezentand": "reprezentând", "mergand": "mergând",
    "tinand": "ținând", "urmand": "urmând",
    "trimiti": "trimiți",

    # PRODUCĂTOR
    "producator": "producător", "producatori": "producători",
}

# Elimină intrările unde cheia = valoarea (fără modificare)
DIACRITICS_MAP = {k: v for k, v in DIACRITICS_MAP.items() if k != v}


def apply_case(original, replacement):
    """Aplică modelul de majuscule/minuscule din original în replacement."""
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


def replace_word(match):
    """Înlocuiește un cuvânt cu varianta sa cu diacritice, păstrând majusculele."""
    word = match.group(0)
    lower = word.lower()
    if lower in DIACRITICS_MAP:
        return apply_case(word, DIACRITICS_MAP[lower])
    return word


def fix_infinitive_context(content):
    """Corectează cazurile unde verbele trebuie să rămână la infinitiv.

    În limba română, verbele rămân la infinitiv (terminația -a) după:
    - 'a' (particula infinitivului): "a valida"
    - 'va' (marker viitor): "va aplica", "se va aplica"
    - 'putea' (verb modal): "putea aplica"
    """
    infinitive_verbs = {
        "aplică": "aplica", "arată": "arata",
        "asigură": "asigura", "ajută": "ajuta",
        "caută": "cauta", "comută": "comuta",
        "confirmă": "confirma", "consultă": "consulta",
        "comunică": "comunica",
        "descarcă": "descarca", "determină": "determina",
        "elimină": "elimina", "există": "exista",
        "identifică": "identifica", "indică": "indica",
        "modifică": "modifica", "necesită": "necesita",
        "notifică": "notifica", "recomandă": "recomanda",
        "solicită": "solicita", "specifică": "specifica",
        "verifică": "verifica", "validă": "valida",
        "inseră": "insera", "informă": "informa",
        "adaugă": "adauga",
    }

    infinitive_contexts = [
        r'\ba\s+', r'\bA\s+',
        r'\bva\s+', r'\bVa\s+',
    ]

    for wrong_form, correct_inf in infinitive_verbs.items():
        for ctx_pattern in infinitive_contexts:
            pattern = ctx_pattern + re.escape(wrong_form) + r'\b'
            content = re.sub(
                pattern,
                lambda m, wf=wrong_form, ci=correct_inf:
                    m.group(0)[:len(m.group(0)) - len(wf)] + ci,
                content
            )

    # „putea [verb]"
    for wrong_form, correct_inf in infinitive_verbs.items():
        pattern = r'\bputea\s+' + re.escape(wrong_form) + r'\b'
        content = re.sub(pattern, lambda m, ci=correct_inf: 'putea ' + ci, content)

    return content


def process_target_content(content):
    """Procesează conținutul unui element target, înlocuind cuvintele cu diacritice."""
    result = re.sub(r'\b([a-zA-Z]+)\b', replace_word, content)
    result = fix_infinitive_context(result)
    return result


def process_file(filepath):
    """Procesează un singur fișier XLF, adăugând diacritice în elementele target."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_target(match):
        prefix = match.group(1)
        target_content = match.group(2)
        suffix = match.group(3)
        new_content = process_target_content(target_content)
        return prefix + new_content + suffix

    new_content = re.sub(
        r'(<target state="final">)(.*?)(</target>)',
        replace_target,
        content,
        flags=re.DOTALL
    )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else 'ro-RO'

    if not os.path.isdir(directory):
        print(f"Eroare: directorul '{directory}' nu există.")
        sys.exit(1)

    files_modified = 0
    files_total = 0

    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.xlf'):
            files_total += 1
            filepath = os.path.join(directory, filename)
            if process_file(filepath):
                files_modified += 1
                print(f"  Modificat: {filename}")
            else:
                print(f"  Fără modificări: {filename}")

    print(f"\nTotal fișiere: {files_total}, Modificate: {files_modified}")


if __name__ == '__main__':
    main()
