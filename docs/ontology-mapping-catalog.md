# Ontology mapping catalogue

The ontology mapping catalogue describes how the Human Phenotype Ontology
(HPO) and the governed external sources could be connected. It is a
payload-safe planning and traceability artefact. It does not contain source
mapping rows, grant permission to retrieve a source, or establish that a
translation is correct.

## Three different claims

The repository keeps three claims separate:

| Claim | Meaning | What it does not mean |
| --- | --- | --- |
| Inventory | A source, edition, language, or mapping product has been identified. | The product has been retrieved, licensed, or inspected. |
| Assertion | An authoritative product declares a directed relationship between two namespaces. | Every identifier in either namespace has a match, or the relationship is symmetric. |
| Route | A declared sequence of assertions could connect one canonical source to another. | The route is authorized for empirical use, semantically lossless, or valid as translation evidence. |

An ontology appearing in the same multi-namespace product as another ontology
is only an inventory fact. It does not create an edge. Likewise, matching
labels never create an edge. Every edge must be declared explicitly and cite
the metadata record that supports it.

## Catalogue scope

The terminology registry and route catalogue have different scopes. The
terminology registry currently contains:

| Record kind | Count | Purpose |
| --- | ---: | --- |
| Governed source families | 28 | Governance roots from the ontology and supplementary-source catalogues |
| Identifier namespaces | 64 | Every namespace token observed in a governed mapping artifact or source-coverage declaration |
| National or international editions | 30 | Exact ICD-10 and SNOMED CT editions, kept separate from their families |
| Product releases | 9 | Versioned HPO, UMLS, LOINC, MedDRA, WHO, and Orphadata products |
| Language renditions | 184 | Product-language records kept outside the ontology-equivalence graph |

The route catalogue contains the 28 governed source families plus the exact
Canadian SNOMED CT and ICD-10-CA edition endpoints needed by the documented
national map. Its 30 nodes produce 900 directed outcomes. The remaining
namespaces, editions, products, and language renditions are explicit
`inventory_only` or parented registry records until a governed assertion names
them as exact endpoints. This is complete cataloguing without inventing graph
edges.

Aliases are typed and authority-scoped. `ICD10CA`, `ICD10CM`, and `SCTID-CA`
resolve to their own namespace or edition records, never to the international
parent family. Likewise, `fr-CA`, `fr-FR`, and `fr-BE`, or `zh-Hans` and
`zh-Hant`, remain distinct renditions. Parent, edition, and language relations
do not create mappings.

Each outcome has one of these route classes:

- `identity`: the source and target are the same canonical node.
- `direct`: one declared edge connects the source to the target.
- `mediated`: two or more declared crosswalk edges form a permitted path.
- `compositional`: the path uses anatomy, quality, cell, or other components
  and therefore cannot claim lexical or class equivalence.
- `unavailable`: no governed path satisfies the catalogue rules. The outcome
  records a reason rather than inventing a relationship.

The current generated matrix has 30 identity outcomes, 41 direct outcomes,
one mediated outcome, and 828 explicitly unavailable
outcomes. This deliberately sparse result reflects the direction and semantics
of the evidence actually catalogued. It is not appropriate to fill the matrix
by assuming that a cross-reference can be reversed or that two namespaces in
one aggregate artifact are mutually mapped.

## Source-to-HPO view

This compact view answers the most common query. The complete, machine-readable
30 by 30 directed matrix is `research_validation/mapping_route_catalog.json`.

| Source family | Route to HPO | Present use | Evidence or reason |
| --- | --- | --- | --- |
| HPO | identity | metadata only | identity |
| Mondo | direct | metadata only | source xref and lexical assertions remain distinct; the source xref is preferred over the lexical candidate |
| NCIt | direct | blocked | lexical candidate; rights review required |
| LDDB, DeCS, PRO-CTCAE, WHO ICF, RadLex | unavailable | none | no governed mapping artifact |
| All other governed source families | unavailable | none | no declared directed path to HPO under current domain and composition rules |

An unavailable source-to-HPO route does not mean the source has no mappings at
all. For example, Mondo has directed assertions to several disease sources,
and Orphadata has directed assertions from Orphanet to multiple disease
classifications. It means that the declared directions cannot currently be
composed into an HPO route without inventing reversal or semantic equivalence.

Route class and present use are independent. A technically plausible route is
`catalogue_only`, `candidate_only`, or `blocked` according to its weakest
rights, payload, integrity, version, predicate, and semantic-loss state. No
route can be labelled authorized.

## Reading a route

A route records its source and target, ordered edge identifiers, path nodes,
present use, semantic-loss class, and the evidence records used. Consecutive
edges must meet at the same declared node. Artifact identifiers resolve to the
mapping expansion catalogue, and source records resolve to their governed
catalogues. Versions, lineage groups, retrieval gates, and licence gates remain
attached to the edge rather than being erased during traversal.

The route builder enumerates every simple, policy-admissible path up to three
hops. It ranks complete paths by present use, semantic loss, weakest rights,
hop count, repeated lineage, mapping class, and stable assertion identifiers.
The preferred path and all alternatives are retained. Regenerating unchanged
inputs produces the same ordered outcomes byte for byte.

Every assertion records its predicate, mapping unit, reversal policy,
composition policy, semantic loss, artifact release, integrity, rights,
payload gate, authority, origin, derivation, lineage, and independent evidence
group. The 21 artifact dispositions exactly cover both governed mapping
catalogues, including artifacts that remain inventory-only because their
endpoint structure or rights are unresolved.

## National-edition example

The Canadian map is represented only as:

`SNOMED CT Canadian Edition` → `ICD-10-CA / CIM-10-CA v2022`

It is directed, classification-specific, access-gated, and supported by the
Canadian map-product metadata. It does not create SNOMED International → WHO
ICD-10, ICD-10-CM, or a reverse ICD-10-CA → SNOMED route. Its `en-CA` and
`fr-CA` renditions remain language metadata, not mapping evidence.

## Worked interpretations

### Direct route

An explicit HPO-to-Mouse Phenotype Ontology assertion supported by the governed
HP-MP manual mapping product can be a direct route. Its direction, release,
lineage, and current permission state still apply. The existence of that map
does not authorize committing its rows or treating mouse phenotype labels as
translations.

### Mediated route

A disease terminology may be connected to another disease terminology through
an explicitly declared Mondo edge on each side. This is a mediated route only
when both directed edges exist and their predicates permit composition. Merely
listing both namespaces in the Mondo aggregate product is insufficient.

### Compositional route

PATO, Uberon, or the Cell Ontology may help represent a phenotype through
quality, anatomy, or cell-type components. Such a route is labelled
compositional. It must not be promoted to exact class equivalence or used as
lexical translation evidence.

### Unavailable route

LDDB may be inventoried while no governed assertion connects it to another
canonical source. Its pairwise outcomes remain unavailable with an explicit
reason. This is a complete and useful result: it distinguishes a known gap from
an omitted source.

## Safety and interpretation boundaries

The catalogue is fail-closed:

- Shared labels, identifiers mentioned in prose, and artifact co-membership do
  not create routes.
- `relatedMatch`, candidate, probe, and compositional assertions cannot be
  transitively promoted to equivalence.
- Restricted, authenticated, or permission-uncertain sources cannot yield an
  authorized route.
- A national or regional edition is not interchangeable with its international
  parent unless a declared assertion says so.
- Mapping availability is not evidence of translation quality, cultural
  suitability, clinical validity, or coverage.
- No route authorizes payload retrieval, redistribution, empirical use, or
  release. Those decisions remain with the source and research governance
  gates.

The generated catalogue should be rebuilt and validated whenever the source
registry, mapping expansion catalogue, source catalogue, rights matrix, or
explicit edge declarations change. A missing pair, broken directed path,
unknown evidence reference, permission escalation, or nondeterministic output
is an admission failure.
