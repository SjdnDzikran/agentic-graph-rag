## SEPSES Cybersecurity Knowledge Graph

- **Endpoint:** <https://sepses.ifs.tuwien.ac.at/sparql>
- **Default dataset:** leave blank in the query form
- **Status:** all queries verified with current property names

---

### Query 1: Get 20 Recent CVE Vulnerabilities with Descriptions

Retrieves the latest CVEs with descriptions and timestamps.

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?cveId ?description ?issued ?modified
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?description ;
         dcterms:issued ?issued ;
         dcterms:modified ?modified .
  }
}
ORDER BY DESC(?issued)
LIMIT 20
```

---

### Query 2: Find High Severity Vulnerabilities (CVSS v2 Score >= 9.0)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cvss: <http://w3id.org/sepses/vocab/ref/cvss#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?cveId ?score ?description
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?description ;
         cve:hasCVSS2BaseMetric ?cvss2 .
  }
  GRAPH ?g2 {
    ?cvss2 cvss:baseScore ?score .
  }
  FILTER(?score >= 9.0)
}
ORDER BY DESC(?score)
LIMIT 30
```

---

### Query 3: Find High Severity Vulnerabilities (CVSS v3 Score >= 9.0)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cvss: <http://w3id.org/sepses/vocab/ref/cvss#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?cveId ?score ?description
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?description ;
         cve:hasCVSS3BaseMetric ?cvss3 .
  }
  GRAPH ?g2 {
    ?cvss3 cvss:baseScore ?score .
  }
  FILTER(?score >= 9.0)
}
ORDER BY DESC(?score)
LIMIT 30
```

---

### Query 4: Find CVEs Related to Specific Weaknesses (CWE)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?cveId ?cweId ?cweName ?cveDescription
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?cveDescription ;
         cve:hasCWE ?cweResource .
  }
  GRAPH ?g2 {
    ?cweResource cwe:id ?cweId ;
                 cwe:name ?cweName .
  }
}
LIMIT 30
```

---

### Query 5: Find CVEs Affecting Specific Products (e.g., Apache)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT DISTINCT ?cveId ?productTitle ?vendor
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:hasCPE ?cpeResource .
  }
  GRAPH ?g2 {
    ?cpeResource cpe:title ?productTitle ;
                 cpe:hasVendor ?vendorObj .
    ?vendorObj cpe:vendorName ?vendor .
  }
  FILTER(CONTAINS(LCASE(?vendor), "apache"))
}
LIMIT 50
```

---

### Query 6: Find CVEs Affecting Windows Products

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?cveId ?productTitle ?description
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?description ;
         cve:hasCPE ?cpeResource .
  }
  GRAPH ?g2 {
    ?cpeResource cpe:title ?productTitle .
  }
  FILTER(CONTAINS(LCASE(?productTitle), "windows"))
}
LIMIT 30
```

---

### Query 7: Get Complete CVE Details for Specific CVE (e.g., Heartbleed)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>

SELECT ?property ?value
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         cve:id "CVE-2014-0160" ;
         ?property ?value .
  }
}
```

---

### Query 8: Count Vulnerabilities by Year (Published Date)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (YEAR(?issued) AS ?year) (COUNT(DISTINCT ?cve) AS ?count)
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         dcterms:issued ?issued .
  }
}
GROUP BY (YEAR(?issued))
ORDER BY DESC(?year)
```

---

### Query 9: Find Recent CVEs (Last 30 days from 2019 - adjust date as needed)

Adjust the literal to shift the time window.

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?cveId ?description ?issued
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?description ;
         dcterms:issued ?issued .
  }
  FILTER(?issued >= "2019-06-01T00:00:00"^^xsd:dateTime)
}
ORDER BY DESC(?issued)
LIMIT 50
```

---

### Query 10: Find CVEs with CVSS v2 Impact Metrics

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cvss: <http://w3id.org/sepses/vocab/ref/cvss#>

SELECT DISTINCT ?cveId ?score ?confImpact ?integrityImpact ?availImpact
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:hasCVSS2BaseMetric ?cvss2 .
  }
  GRAPH ?g2 {
    ?cvss2 cvss:baseScore ?score ;
           cvss:confidentialityImpact ?confImpact ;
           cvss:integrityImpact ?integrityImpact ;
           cvss:availabilityImpact ?availImpact .
  }
}
ORDER BY DESC(?score)
LIMIT 30
```

---

### Query 11: Find Critical CVEs with Complete Confidentiality Impact

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cvss: <http://w3id.org/sepses/vocab/ref/cvss#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?cveId ?score ?description
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         dcterms:description ?description ;
         cve:hasCVSS2BaseMetric ?cvss2 .
  }
  GRAPH ?g2 {
    ?cvss2 cvss:baseScore ?score ;
           cvss:confidentialityImpact ?confImpact .
  }
  FILTER(?confImpact = "COMPLETE")
  FILTER(?score >= 7.0)
}
ORDER BY DESC(?score)
LIMIT 30
```

---

### Query 12: Explore CWE Weaknesses with Mitigations

```sparql
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>

SELECT DISTINCT ?cweId ?cweName ?mitigationDesc
WHERE {
  GRAPH ?g {
    ?cwe a cwe:CWE ;
         cwe:id ?cweId ;
         cwe:name ?cweName ;
         cwe:hasPotentialMitigation ?mitigation .
    ?mitigation cwe:mitigationDescription ?mitigationDesc .
  }
}
LIMIT 20
```

---

### Query 13: Get CAPEC Attack Patterns

```sparql
PREFIX capec: <http://w3id.org/sepses/vocab/ref/capec#>

SELECT DISTINCT ?capecId ?capecName ?likelihood ?description
WHERE {
  GRAPH ?g {
    ?capec a capec:CAPEC ;
           capec:id ?capecId ;
           capec:name ?capecName .
    OPTIONAL { ?capec capec:likelihoodOfAttack ?likelihood . }
    OPTIONAL { ?capec capec:description ?description . }
  }
}
LIMIT 20
```

---

### Query 14: Link CVE -> CWE -> CAPEC (Vulnerability Chain)

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>
PREFIX capec: <http://w3id.org/sepses/vocab/ref/capec#>

SELECT DISTINCT ?cveId ?cweId ?cweName ?capecId ?attackPattern
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:hasCWE ?cweResource .
  }
  GRAPH ?g2 {
    ?cweResource cwe:id ?cweId ;
                 cwe:name ?cweName ;
                 cwe:hasCAPEC ?capecResource .
  }
  GRAPH ?g3 {
    ?capecResource capec:id ?capecId ;
                   capec:name ?attackPattern .
  }
}
LIMIT 20
```

---

### Query 15: Count Products by Vendor

```sparql
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT ?vendor (COUNT(DISTINCT ?cpe) AS ?productCount)
WHERE {
  GRAPH ?g {
    ?cpe a cpe:CPE ;
         cpe:hasVendor ?vendorObj .
    ?vendorObj cpe:vendorName ?vendor .
  }
}
GROUP BY ?vendor
ORDER BY DESC(?productCount)
LIMIT 30
```

---

### Query 16: Dataset Statistics

```sparql
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>
PREFIX capec: <http://w3id.org/sepses/vocab/ref/capec#>
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT 
  (COUNT(DISTINCT ?cve) AS ?totalCVEs)
  (COUNT(DISTINCT ?cwe) AS ?totalCWEs)
  (COUNT(DISTINCT ?capec) AS ?totalCAPECs)
  (COUNT(DISTINCT ?cpe) AS ?totalCPEs)
WHERE {
  {
    GRAPH ?g1 { ?cve a cve:CVE . }
  }
  UNION
  {
    GRAPH ?g2 { ?cwe a cwe:CWE . }
  }
  UNION
  {
    GRAPH ?g3 { ?capec a capec:CAPEC . }
  }
  UNION
  {
    GRAPH ?g4 { ?cpe a cpe:CPE . }
  }
}
```

---

## Key Property Mappings

- **CVE ID:** `cve:id` (not `cve:cveId`)
- **Description:** `dcterms:description` (not `cve:description`)
- **Published:** `dcterms:issued`
- **Modified:** `dcterms:modified`
- **Identifier:** `dcterms:identifier`

**Relationships**

- `cve:hasCWE` → linked weakness  
- `cve:hasCPE` → affected product  
- `cve:hasCVSS2BaseMetric` / `cve:hasCVSS3BaseMetric` → scoring metrics  
- `cve:hasReference` → outbound references  
- `cve:hasVulnerableConfiguration` → configuration objects
