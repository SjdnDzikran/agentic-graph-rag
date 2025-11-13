# ============================================
# SEPSES Cybersecurity Knowledge Graph
# UPDATED SPARQL Queries for Named Graphs
# Endpoint: https://sepses.ifs.tuwien.ac.at/sparql
# Graph IRI: Leave BLANK or use "FROM <...>" clauses
# ============================================

# --------------------------------------------
# Query 1: Get CVE Count (Quick Test)
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>

SELECT (COUNT(DISTINCT ?cve) AS ?totalCVEs)
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE .
  }
}


# --------------------------------------------
# Query 2: Get 10 CVE Vulnerabilities (Any from named graphs)
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>

SELECT DISTINCT ?cveId ?description
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:description ?description .
  }
}
LIMIT 10


# --------------------------------------------
# Query 3: Find High Severity Vulnerabilities (CVSS >= 9.0)
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cvss: <http://w3id.org/sepses/vocab/ref/cvss#>

SELECT DISTINCT ?cveId ?score ?description
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:description ?description ;
         cve:hasCVSS2BaseMetric ?cvssMetric .
  }
  GRAPH ?g2 {
    ?cvssMetric cvss:baseScore ?score .
  }
  FILTER(?score >= 9.0)
}
ORDER BY DESC(?score)
LIMIT 20


# --------------------------------------------
# Query 4: Explore CVE with Related CWE Weaknesses
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>

SELECT DISTINCT ?cveId ?cweId ?cweName
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:hasCWE ?cweResource .
  }
  GRAPH ?g2 {
    ?cweResource cwe:id ?cweId ;
                 cwe:name ?cweName .
  }
}
LIMIT 20


# --------------------------------------------
# Query 5: Find Products by Vendor (e.g., Apache)
# --------------------------------------------
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT DISTINCT ?productTitle ?vendor
WHERE {
  GRAPH ?g {
    ?cpe a cpe:CPE ;
         cpe:title ?productTitle ;
         cpe:hasVendor ?vendorObj .
    ?vendorObj cpe:vendorName ?vendor .
    FILTER(CONTAINS(LCASE(?vendor), "apache"))
  }
}
LIMIT 50


# --------------------------------------------
# Query 6: Count CPEs by Vendor
# --------------------------------------------
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
LIMIT 20


# --------------------------------------------
# Query 7: Get All CWE Weaknesses
# --------------------------------------------
PREFIX cwe: <http://w3id.org/sepses/vocab/ref/cwe#>

SELECT DISTINCT ?cweId ?cweName ?description
WHERE {
  GRAPH ?g {
    ?cwe a cwe:CWE ;
         cwe:id ?cweId ;
         cwe:name ?cweName ;
         cwe:description ?description .
  }
}
LIMIT 20


# --------------------------------------------
# Query 8: Get CAPEC Attack Patterns
# --------------------------------------------
PREFIX capec: <http://w3id.org/sepses/vocab/ref/capec#>

SELECT DISTINCT ?capecId ?capecName ?likelihood
WHERE {
  GRAPH ?g {
    ?capec a capec:CAPEC ;
           capec:id ?capecId ;
           capec:name ?capecName ;
           capec:likelihoodOfAttack ?likelihood .
  }
}
LIMIT 20


# --------------------------------------------
# Query 9: Find CVEs for Specific Product (e.g., Windows)
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
PREFIX cpe: <http://w3id.org/sepses/vocab/ref/cpe#>

SELECT DISTINCT ?cveId ?productTitle
WHERE {
  GRAPH ?g1 {
    ?cve a cve:CVE ;
         cve:id ?cveId ;
         cve:hasCPE ?cpeResource .
  }
  GRAPH ?g2 {
    ?cpeResource cpe:title ?productTitle .
    FILTER(CONTAINS(LCASE(?productTitle), "windows"))
  }
}
LIMIT 30


# --------------------------------------------
# Query 10: Explore Weakness Mitigations
# --------------------------------------------
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


# --------------------------------------------
# Query 11: Dataset Statistics - Count Everything
# --------------------------------------------
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


# --------------------------------------------
# Query 12: Simple Exploration - See What Properties CVEs Have
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>

SELECT DISTINCT ?property (COUNT(?value) AS ?count)
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         ?property ?value .
  }
}
GROUP BY ?property
ORDER BY DESC(?count)


# --------------------------------------------
# Query 13: Get One Complete CVE Example
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>

SELECT DISTINCT ?cve ?property ?value
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE .
    ?cve ?property ?value .
  }
}
LIMIT 50


# ============================================
# ALTERNATIVE: If you know a specific CVE ID
# ============================================
# Query 14: Get Specific CVE by ID (e.g., CVE-2014-0160 - Heartbleed)
# --------------------------------------------
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>

SELECT DISTINCT ?cve ?property ?value
WHERE {
  GRAPH ?g {
    ?cve a cve:CVE ;
         cve:id "CVE-2014-0160" ;
         ?property ?value .
  }
}


# ============================================
# TIPS FOR NAMED GRAPH QUERIES:
# ============================================
# 1. Always use "GRAPH ?g { ... }" to search across all graphs
# 2. Use different graph variables (?g1, ?g2) when joining data
# 3. Use DISTINCT to avoid duplicate results
# 4. Start with COUNT queries to verify data exists
# 5. Leave the "Default Data Set Name" field BLANK in the interface
# ============================================