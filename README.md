# Editura Shambala — Traduceri Prestashop 9 (ro-RO)

Acest repository conține fișierele de traducere în limba română (format XLIFF / `.xlf`) pentru site-ul **editurashambala.ro**, bazat pe **Prestashop 9** cu tema **LeoBookifa**.

## Structura repository-ului

```
├── ro-RO/                    # 167 fișiere .xlf cu traduceri în română
│   ├── AdminActions.ro-RO.xlf
│   ├── AdminGlobal.ro-RO.xlf
│   ├── ShopThemeCheckout.ro-RO.xlf
│   └── ...
├── fix_diacritics.py         # Script Python pentru adăugarea diacriticelor
├── README.md                 # Acest fișier
└── ...
```

---

## Script: `fix_diacritics.py`

### Ce face?

Scriptul adaugă **diacritice românești corecte** (ă, â, î, ș, ț) în fișierele `.xlf` de traducere. Modifică **doar** textul din interiorul elementelor `<target state="final">`, lăsând neatins restul structurii XML (sursa în engleză, notele, atributele etc.).

### Cerințe

- **Python 3.6+** (nu necesită biblioteci externe)

### Cum se folosește

#### 1. Utilizare de bază (directorul `ro-RO` implicit)

Deschide terminalul în directorul repository-ului și rulează:

```bash
python3 fix_diacritics.py
```

Scriptul va procesa automat toate fișierele `.xlf` din directorul `ro-RO/`.

#### 2. Specificarea unui alt director

Dacă fișierele `.xlf` se află într-un alt director:

```bash
python3 fix_diacritics.py /cale/spre/directorul/cu/fisiere
```

### Ce afișează

Scriptul afișează progresul în timp real:

```
  Modificat: AdminActions.ro-RO.xlf
  Modificat: AdminGlobal.ro-RO.xlf
  Fără modificări: AdminCatalogAttribute.ro-RO.xlf
  ...

Total fișiere: 167, Modificate: 151
```

### Exemplu de transformare

**Înainte:**
```xml
<target state="final">Comanda ta din %s este finalizata.</target>
```

**După:**
```xml
<target state="final">Comanda ta din %s este finalizată.</target>
```

### Ce diacritice adaugă?

| Literă fără diacritice | Literă cu diacritice | Exemplu |
|------------------------|----------------------|---------|
| a | ă | finalizat**a** → finalizat**ă** |
| a | â | c**a**mp → c**â**mp |
| i | î | **i**n → **î**n |
| s | ș | **s**terge → **ș**terge |
| t | ț | informa**t**ii → informa**ț**ii |

### Detalii tehnice

- Conține un dicționar cu **~1100 cuvinte** mapate de la forma fără diacritice la forma corectă
- Păstrează **majusculele** (ex: `Platiti` → `Plătiți`, `INFORMATII` → `INFORMAȚII`)
- **Nu modifică** textele sursă în engleză (elementele `<source>`)
- **Nu modifică** notele sau atributele XML
- Corectează automat **formele de infinitiv** după particulele `a`, `va`, `putea` (ex: „a valida" rămâne cu `-a`, nu devine „a validă")
- Păstrează **formele definite** ale substantivelor feminine (ex: „comanda ta" rămâne „comanda ta", nu devine „comandă ta")

### Cum să adaugi cuvinte noi

Dacă găsești cuvinte care nu au fost corectate, le poți adăuga în dicționarul `DIACRITICS_MAP` din script:

```python
DIACRITICS_MAP = {
    # ... cuvintele existente ...
    "cuvantul_fara_diacritice": "cuvântul_cu_diacritice",
}
```

**Atenție:** Adaugă doar forma **lowercase** — scriptul aplică automat majusculele.

### Sfaturi de utilizare

1. **Fă un backup** înainte de a rula scriptul (sau folosește `git` pentru a putea reveni)
2. **Verifică diferențele** după rulare cu `git diff` pentru a te asigura că modificările sunt corecte
3. Scriptul poate fi rulat **de mai multe ori** fără probleme — dacă diacriticele sunt deja adăugate, fișierul nu va fi modificat din nou

---

## Despre fișierele XLF

Fișierele `.xlf` (XLIFF 1.2) sunt folosite de Prestashop pentru traduceri. Fiecare fișier conține perechi de texte sursă (engleză) și țintă (română):

```xml
<trans-unit id="..." approved="yes">
    <source>Your order on %s is complete.</source>
    <target state="final">Comanda ta din %s este finalizată.</target>
    <note>File: modules/ps_checkpayment/... [Line: 26]</note>
</trans-unit>
```

Scriptul modifică **doar** conținutul din `<target state="final">`.
