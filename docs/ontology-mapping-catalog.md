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

The canonical node set consists of HPO, every source in
`ontology_network/source_registry.json`, and the distinct governed source
families in `research_validation/supplementary_source_access_reviews.json`.
This currently gives 28 canonical nodes: HPO, 18 registry sources, and 9
supplementary sources that are not already represented by a registry source.
Auxiliary nodes, such as a routing hub that is not governed as a source family,
may mediate a route but are not silently promoted into the canonical set.
Namespace aliases are explicit so that, for example, SNOMED CT identifiers are
not confused with a national edition or an unrelated label for the same
product.

The generated pairwise catalogue contains one directed outcome for every
ordered canonical-source pair, including identity outcomes. The current 28-node
inventory therefore produces 784 outcomes. The validator derives the expected
count from the governed input rather than relying on either number as a fixed
constant. The generated JSON is the authoritative complete matrix; this page
explains how to interpret it. A reverse outcome is evaluated independently
because many maps are directional.

Each outcome has one of these route classes:

- `identity`: the source and target are the same canonical node.
- `direct`: one declared edge connects the source to the target.
- `mediated`: two or more declared crosswalk edges form a permitted path.
- `compositional`: the path uses anatomy, quality, cell, or other components
  and therefore cannot claim lexical or class equivalence.
- `unavailable`: no governed path satisfies the catalogue rules. The outcome
  records a reason rather than inventing a relationship.

The current generated matrix has 28 identity outcomes, 40 direct outcomes,
one mediated outcome, one compositional outcome, and 714 explicitly unavailable
outcomes. This deliberately sparse result reflects the direction and semantics
of the evidence actually catalogued. It is not appropriate to fill the matrix
by assuming that a cross-reference can be reversed or that two namespaces in
one aggregate artifact are mutually mapped.

## Source-to-HPO view

This compact view answers the most common query. The complete, machine-readable
28 by 28 directed matrix is `research_validation/mapping_route_catalog.json`.

| Source family | Route to HPO | Present use | Evidence or reason |
| --- | --- | --- | --- |
| HPO | identity | metadata only | identity |
| Mondo | direct | metadata only | source xref and lexical assertions remain distinct; the source xref is preferred over the lexical candidate |
| MP | direct | metadata only | reverse candidate declared by the HP-MP manual collection |
| NCIt | direct | blocked | lexical candidate; rights review required |
| LDDB, DeCS, PRO-CTCAE, WHO ICF, RadLex | unavailable | none | no governed mapping artifact |
| All other governed source families | unavailable | none | no declared directed path to HPO under current domain and composition rules |

An unavailable source-to-HPO route does not mean the source has no mappings at
all. For example, Mondo has directed assertions to several disease sources,
and Orphadata has directed assertions from Orphanet to multiple disease
classifications. It means that the declared directions cannot currently be
composed into an HPO route without inventing reversal or semantic equivalence.

Route class and present admissibility are independent. A technically plausible
route can remain `metadata_only`, `candidate_only`, or `blocked` because of
permissions, integrity, version, predicate, or semantic-loss constraints. Only
an explicitly authorized path can be labelled `authorized`, and the route
cannot be more permissive than its least permissive edge.

## Reading a route

A route records its source and target, ordered edge identifiers, path nodes,
admissibility, semantic-loss class, and the evidence records used. Consecutive
edges must meet at the same declared node. Artifact identifiers resolve to the
mapping expansion catalogue, and source records resolve to their governed
catalogues. Versions, lineage groups, retrieval gates, and licence gates remain
attached to the edge rather than being erased during traversal.

The route builder chooses deterministically among eligible paths. It prefers
the governed route ordering defined by the catalogue and uses stable
identifiers as a final tie-break. Regenerating from unchanged inputs must
therefore produce the same ordered outcomes byte for byte.

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
