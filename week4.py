from Bio import Entrez
import pandas as pd
import time

Entrez.email = "syyue@ucsd.edu" 

query = '("Parkinson Disease"[MeSH Terms] OR "Parkinson\'s disease"[All Fields]) AND ("drug repurposing"[All Fields] OR "drug repositioning"[All Fields]) AND ("2020"[Date - Publication] : "2025"[Date - Publication]) AND "English"[Language]'

handle = Entrez.esearch(db="pubmed", term=query, retmax=20)
record = Entrez.read(handle)
ids = record["IdList"]

print(f"Found {len(ids)} articles")

abstracts = []
for pmid in ids:
    fetch_handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
    abstract_text = fetch_handle.read()
    abstracts.append({"PMID": pmid, "Abstract": abstract_text})
    fetch_handle.close()
    time.sleep(0.5)  # avoid rate-limiting

df = pd.DataFrame(abstracts)
df.to_csv("parkinsons_drug_repurposing.csv", index=False)
print(df.head())
