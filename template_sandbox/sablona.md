# Definice WooWoo šablona 

Tento dokument neformálně popisuje, co všechno by měl obsahovat soubor, který plně popisuje konkrétní WooWoo šablonu.

## Informace o šabloně

Následující položky neovlivňují interpretaci WooWoo dokumentu, ale jsou potřebné v definici šablony.

1. Jméno šablony
    - např. FIT Math
2. Popis šablony
    - slovní popis toho, k čemu se šablona používá
3. Jméno verze
    - verze šablony (spravuje autor šablony)
    - libovolný text, např. `1.0.0` či `v0.0.1-alpha`
4. Kód verze
    - začíná na 1, s každou další verzí by se měl inkrementovat o 1
    
## Klíčová slova

Názvy struktur nejsou jazykem WooWoo nijak definovány. Například název `document_part` může být libovolný regex `/[^[\n\r]]+/`.  Že se jedná o typ `document_part` je parserem rozeznáno na základě kontextu (operátory `.`, `:`, použití malých/velkých písmen...), nikdy na základě konkrétních klíčových slov.

WooWoo dokumenty se však používají pro generování různého obsahu. Generátor pracuje s konkrétní šablonou, která definuje, různé možné názvy struktur.
Použití jiných názvů by nevedlo k syntax erroru při parsování, ale problém by nastal ve chvíli použití generátoru.

Každá šablona tedy musí definovat výčet možných typů pro:
1. document_part (document_part_type)
2. object (object_type)
3. outer_environment (outer_environment_type)
    - výčet možných typů pro křehké vnější prostředí
    - výčet možných typů pro klasické vnější prosředí
4. verbose_inner_environment (verbose_inner_environment_type)
5. short_inner_environment (short_inner_environment_type)

Ke každému z těchto typů se tedy váže seznam povolených názvů. Seznam pro `outer_environment` je pak rozdělený na dvě části.

### Popis klíčových slov

Každé klíčové slovo (typ) může mít popis. Tento popis je dobrý pro uživatele šablony, generování obsahu nijak neovlivňuje.

## Obsah meta bloků

Některé WooWoo struktury mohou být následovány tzv. meta blokem (`meta_block`), což je kus kódu ve formátu `yaml`, který obsahuje meta informace danné struktury. Tyto informace pak většinou ovlivňují výstup generátorů obsahu.

Pro všechny typy následujících struktur šablona definuje seznam **povinných** a seznam **volitelných** atributů v meta bloku.

1. document_part
2. object
3. outer_environment

### Hodnoty atributů

Šablona také definuje, jakých hodnot můžou jednotlivé atributy nabývat. 
Pro každý atribut (ze sjednocení povinných a volitelných) je uvedena jedna z následujících možností:

1. Regulární výraz
2. Výčet hodnot (seznam)
3. Název jiného atributu (jedna hodnota)
    - Toto je pro případ, kdy hodnota může být jakákoliv taková, která byla někdy použita jako hodnota uvedeného atributu.
    - Např. reference vždy odkazuje na label.
    
## Implicitní vnější prostředí

V každé šabloné může být právě jedno vnější prostředí označené jako implicitní. Každá šablona proto musí definovat, které to je.
Např. u matematické šablony to může být `equation`, u programátorské pak zase `code`.

## Povinný obsah

TBD

např. objekt Question by mohl povinně obsahovat vnější prostředí .solution
objekt Table by mohl povinně obsahovat křehké prostředí !tabular

s tím souvisí i povinnost meta-bloku u některých vnitřních prostředí
u vnitřních prostředí informaci, jeslti je povolen/vyžadován metablok, a pokud je vyžadován tak následná kontrola souvisejícíh věcí (např. jestli textový blok obsahuje upřesňující informace)


## Povolený obsah

TBD

u krátkých vnitřních prostředí by šablona mohla definovat jaký má být jejich obsah
např. u cite je to klíč z bibliografie

## Vnitřní prostředí

TBD

- význam operátorů # a @, např. # je reference, takže je tam možné udělat nějaké napovídání
- výčet názvů...



## Nápady

1) U konstruktů, kde se proklikávám ke zdroji, bych mohl mít field "instance", např. reference by
měl "instance_of: label", body field může být názvem matoucí.


2) Místo "body: "label"" bych mohl psát např. body: "equation.label" a tím bych zajistil, že např. 
   "eqref" se zajímá jen o labeli, co jsou součástí equation.