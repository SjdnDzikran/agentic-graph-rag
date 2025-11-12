# SEPSES KG Schema & Query Cookbook

This note extends the main paper summary with actionable details on how to navigate the SEPSES knowledge graph and reuse the published SPARQL queries.

## 1. Schema Reference and Access Links

### 1.1 Vocabulary Graph (Fig. 1)
Figure 1 in the paper shows how the domain vocabularies align. Each repository exposes a namespace under [`https://w3id.org/sepses/vocab`](https://w3id.org/sepses/vocab):
- `ref/cve#` instances link to `ref/cpe#` products, `ref/cvss#` metrics, and `ref/cwe#` weaknesses.
- `ref/cwe#` nodes further connect to `ref/capec#` attack patterns (`cwe:hasCAPEC`) and mitigation/consequence resources.
- Snort vocabularies (`vocab/rule/snort#`, `vocab/log/snort-alert#`) extend the KG so IDS alerts can point back to CVE entries.

Because the RDF model mirrors the original schemas, legacy IDs translate directly into IRIs (e.g., `https://w3id.org/sepses/resource/cve/CVE-2017-0144` or `/cpe/cpe:2.3:a:microsoft:windows_10:*`).

### 1.2 ETL and Publishing Architecture (Fig. 2)
The ETL engine (open-sourced at [`github.com/sepses/cyber-kg-converter`](https://github.com/sepses/cyber-kg-converter)) runs the following loop:
1. **Acquisition:** Poll CVE (every ~2 h), CPE (daily), CWE/CAPEC (yearly) feeds.
2. **Extraction/Lifting:** caRML executes generic RML mappings to convert CSV/XML/JSON dumps into RDF; Apache Jena reshapes them into the final ontologies.
3. **Linking & SHACL Validation:** Common identifiers (CPE IDs, CWE↔CAPEC references) are linked, and SHACL shapes ensure mandatory fields exist; dangling references are logged and temporarily materialized.
4. **Storage & Publishing:** ~36.5 M triples (July 2019) are loaded into Virtuoso and exposed via:
   - SPARQL endpoint: [`https://w3id.org/sepses/sparql`](https://w3id.org/sepses/sparql)
   - Triple Pattern Fragments: [`https://ldf-server.sepses.ifs.tuwien.ac.at`](https://ldf-server.sepses.ifs.tuwien.ac.at)
   - Linked Data pages for each `/resource/...` IRI
   - RDF dumps: [`https://w3id.org/sepses/dumps/`](https://w3id.org/sepses/dumps/)

### 1.3 Reference Tables
- **Table 1:** Schema statistics (axioms, classes, properties, individuals) per source.
- **Tables 2–4:** Sample outputs for the vulnerability-assessment and intrusion-detection use cases—handy for validating your own queries.

## 2. Ready-to-Use SPARQL Templates
General assumptions:
- Local asset/alert data are hosted in a private Virtuoso graph (e.g., `http://localhost:8890/localdata`).
- Public SEPSES data are accessed via `SERVICE <https://w3id.org/sepses/sparql>`.

### 2.1 Listing 1 – Vulnerable Assets per Host
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX asset: <http://w3id.org/sepses/vocab/bgk/assetKnowledge#>
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT DISTINCT ?hostName (STR(?ip) AS ?ip) ?product
       (GROUP_CONCAT(?cveId; separator=", ") AS ?cveIds)
FROM <http://localhost:8890/localdata2>
WHERE {
  ?s a asset:Host ;
     rdfs:label ?hostName ;
     asset:ipAddress ?ip ;
     asset:hasProduct ?p .
  SERVICE <https://w3id.org/sepses/sparql> {
    ?cve cve:hasCPE ?p ;
         cve:id ?cveId .
    ?p cpe:title ?product .
  }
}
GROUP BY ?hostName ?ip ?product
```

### 2.2 Listing 2 – High-Risk Vulnerabilities Hitting Sensitive Data
```sparql
PREFIX asset: <http://w3id.org/sepses/vocab/bgk/assetKnowledge#>
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cvss: <http://w3id.org/sepses/vocab/ref/cvss#>
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>

SELECT DISTINCT ?hostName ?dataAsset ?classification
       ?cveId ?confidentiality ?cvssScore ?consequence
FROM <http://localhost:8890/localdata>
WHERE {
  ?host a asset:Host ;
        asset:hasDataAsset ?dt ;
        asset:hasProduct ?product ;
        rdfs:label ?hostName .
  ?dt rdfs:label ?dataAsset ;
      asset:hasClassification ?class .
  ?class rdfs:label ?classification ;
         asset:dataClassificationValue ?cv .
  FILTER(?cv = 1)
  SERVICE <https://w3id.org/sepses/sparql> {
    ?cve cve:hasCPE ?product ;
         cve:id ?cveId ;
         cve:hasCVSS2BaseMetric ?metric ;
         cwe:hasCWE ?cwe .
    ?metric cvss:confidentialityImpact ?confidentiality ;
            cvss:baseScore ?cvssScore .
    FILTER(?confidentiality = \"COMPLETE\")
    ?cwe cwe:hasCommonConsequence ?cc .
    ?cc cwe:consequenceImpact ?consequence .
  }
}
```

### 2.3 Listing 3 – Loading Snort Alerts into RDF
```sparql
PREFIX snort-alert: <http://w3id.org/sepses/vocab/log/snort-alert#>

INSERT DATA {
  GRAPH <http://localhost:8890/snortalert> {
    snort-alert:Alert001 a snort-alert:IDSSnortAlertLogEntry ;
      snort-alert:signatureId \"1807\" ;
      snort-alert:message \"WEB-MISC Chunked-Encoding transfer attempt\" ;
      snort-alert:sourceIp \"10.2.190.254\" ;
      snort-alert:destinationIp \"154.241.88.201\" .
    # repeat for other alerts
  }
}
```

### 2.4 Listing 4 – Enrich Alerts with CVE/CPE Details
```sparql
PREFIX snort: <http://w3id.org/sepses/vocab/ref/snort#>
PREFIX snort-rule: <http://w3id.org/sepses/vocab/rule/snort#>
PREFIX snort-alert: <http://w3id.org/sepses/vocab/log/snort-alert#>
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT DISTINCT ?alert ?message ?sid ?sourceIp ?destinationIp ?cveId ?cpeId
FROM <http://localhost:8890/snortalert>
WHERE {
  ?alert a snort-alert:IDSSnortAlertLogEntry ;
         snort:signatureId ?sid ;
         snort:message ?message ;
         snort:sourceIp ?sourceIp ;
         snort:destinationIp ?destinationIp .
  SERVICE <https://w3id.org/sepses/sparql> {
    ?rule a snort-rule:SnortRule ;
          snort-rule:hasRuleOption ?opt .
    ?opt snort:signatureId ?sid ;
         snort-rule:hasCveReference ?cve .
    ?cve cve:id ?cveId ;
         cve:hasCPE ?cpe .
    ?cpe cpe:id ?cpeId .
  }
}
```

Use these templates as drop-in building blocks for your Agentic RAG pipelines. The column sets should match Tables 2–4 from the SEPSES paper if your local graphs are modeled equivalently.
