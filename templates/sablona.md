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

WooWoo dokumenty se však používají pro generování různého obsahu. Generátor pracuje s konkrétní šablonou, která definuje možné názvy struktur.
Použití jiných názvů by nevedlo k syntax erroru při parsování, ale problém by nastal až ve chvíli použití generátoru.


Každá šablona tedy musí definovat výčet možných typů pro:
1. document_part (document_part_type)
2. object (object_type)
3. outer_environments (outer_environment_type)
    - výčet možných typů pro křehké vnější prostředí
    - výčet možných typů pro klasické vnější prosředí
4. inner_environments
   - klasické (verbose_inner_environment_type)
   - krátké (short_inner_environment_type)


### Popis typů

Každý typ může mít popis. Tento popis je dobrý pro uživatele šablony, generování obsahu nijak neovlivňuje.
Také slouží pro LSP jako zdroj pro funkci `hover`.

## Obsah meta bloků

Některé WooWoo struktury mohou být následovány tzv. meta blokem (`meta_block`), což je kus kódu ve formátu `yaml`, který obsahuje meta informace danné struktury. Tyto informace pak většinou ovlivňují výstup generátorů obsahu.

Pro **všechny typy struktur** šablona definuje seznam **povinných** a seznam **volitelných** atributů v meta bloku.


### Reference

Některé struktury mohou odkazovat na jiné struktury, např. krátké vnitřní prostředí
`.eqref` odkazuje na nějaké vnější prostředí typy `equation`. 
Konkrétní struktura se pak rozpozná podle meta bloku, u šablony FIT-Math je to klíč `label`.

Na co konkrétně struktura odkazuje se dá parametrizovat pomocí `reference`, která je definovaná třemi prvky:
  1. structure_type (např. outer_environment) 
  2. structure_name (např. equation)
  3. meta_key (např. label)

Ve výše uvedeném příkladu by struktura s touto referencí odkazovala na vnější prostředí typu equation pomocí meta klíče `label`.

    
## Implicitní vnější prostředí

V každé šabloné je právě jedno vnější prostředí označené jako implicitní. Každá šablona proto musí definovat, které to je.
Např. u matematické šablony to může být `equation`, u programátorské pak zase `code`.



## Vnitřní prostředí

TODO

- význam operátorů # a @, např. # je reference, takže je tam možné udělat nějaké napovídání
- výčet názvů...



# Nápady


## Povinný obsah

TODO: ve fázi nápadu

např. objekt Question by mohl povinně obsahovat vnější prostředí .solution
objekt Table by mohl povinně obsahovat křehké prostředí !tabular

s tím souvisí i povinnost meta-bloku u některých vnitřních prostředí
u vnitřních prostředí informaci, jeslti je povolen/vyžadován metablok, a pokud je vyžadován tak následná kontrola souvisejícíh věcí (např. jestli textový blok obsahuje upřesňující informace)


## Povolený obsah

TBD

u krátkých vnitřních prostředí by šablona mohla definovat jaký má být jejich obsah
např. u cite je to klíč z bibliografie