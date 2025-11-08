import pandas as pd
import re
from collections import Counter

df = pd.read_csv("~/Desktop/parkinsons_drug_repurposing.csv")

print(f"Total abstracts: {len(df)}")
print("\n" + "="*80)

print("\nMETHOD 1: KEYWORD-BASED EXTRACTION")
print("="*80)

drug_keywords = {
    'Levodopa': ['levodopa', 'l-dopa', 'ldopa'],
    'Dopamine agonists': ['dopamine agonist', 'pramipexole', 'ropinirole', 'bromocriptine'],
    'MAO inhibitors': ['monoamine oxidase', 'selegiline', 'rasagiline'],
    'COMT inhibitors': ['catechol-o-methyltransferase', 'entacapone', 'tolcapone'],
    'Anticholinergics': ['anticholinergic', 'benztropine', 'trihexyphenidyl'],
    'Amantadine': ['amantadine'],
    'Codeine': ['codeine'],
    'Opioids': ['opioid', 'morphine', 'tramadol'],
    'NSAIDs': ['nsaid', 'ibuprofen', 'naproxen'],
    'Statins': ['statin', 'simvastatin', 'atorvastatin'],
    'Antihistamines': ['antihistamine', 'diphenhydramine'],
    'Beta-blockers': ['beta-blocker', 'propranolol', 'metoprolol'],
}

found_drugs = {}

for idx, row in df.iterrows():
    abstract = str(row['Abstract']).lower()
    pmid = row['PMID']
    
    for drug_class, keywords in drug_keywords.items():
        for keyword in keywords:
            if keyword in abstract:
                if drug_class not in found_drugs:
                    found_drugs[drug_class] = []
                found_drugs[drug_class].append(pmid)
                break  # Don't count the same drug class twice per abstract

print("\nDrugs/Drug Classes Found:")
print("-" * 80)
for drug_class, pmids in sorted(found_drugs.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n{drug_class}: {len(set(pmids))} abstracts")
    print(f"  PMIDs: {set(pmids)}")

print("\n\n" + "="*80)
print("METHOD 2: DRUG REPURPOSING CANDIDATES BY TITLE")
print("="*80)

candidates = []

for idx, row in df.iterrows():
    abstract = str(row['Abstract'])
    pmid = row['PMID']
    
    # Extract title (usually first line with "as a" or "potential" or "against")
    lines = abstract.split('\n')
    title_match = None
    
    for line in lines:
        if ('potential' in line.lower() or 'drug' in line.lower() or 
            'against' in line.lower() or 'treatment' in line.lower()):
            if len(line) > 20 and len(line) < 200:
                title_match = line.strip()
                break
    
    if title_match:
        # Extract drug names (capitalized words likely to be drug names)
        drug_names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', title_match)
        candidates.append({
            'PMID': pmid,
            'Title': title_match[:100],  # First 100 chars
            'Potential_Drugs': ', '.join(set(drug_names))
        })

if candidates:
    candidates_df = pd.DataFrame(candidates)
    print("\nTop Repurposing Candidates:")
    print("-" * 80)
    print(candidates_df.head(10).to_string(index=False))
    
    # Save for reference
    candidates_df.to_csv("drug_candidates.csv", index=False)
    print(f"\n✓ Saved {len(candidates_df)} candidates to drug_candidates.csv")

print("\n\n" + "="*80)
print("METHOD 3: COMMON MECHANISMS MENTIONED")
print("="*80)

mechanisms = {
    'dopamine': 0,
    'neurotransmitter': 0,
    'neuroprotection': 0,
    'inflammation': 0,
    'oxidative stress': 0,
    'mitochondrial': 0,
    'apoptosis': 0,
    'tau': 0,
    'alpha-synuclein': 0,
    'motor': 0,
    'cognitive': 0,
}

for idx, row in df.iterrows():
    abstract = str(row['Abstract']).lower()
    for mechanism in mechanisms.keys():
        if mechanism in abstract:
            mechanisms[mechanism] += 1

print("\nMechanisms of Action Frequency:")
print("-" * 80)
for mechanism, count in sorted(mechanisms.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        percentage = (count / len(df)) * 100
        print(f"{mechanism:20s}: {count:3d} ({percentage:5.1f}%)")

print("\n\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal Abstracts Analyzed: {len(df)}")
print(f"Drug Classes Found: {len(found_drugs)}")
print(f"Potential Repurposing Candidates Identified: {len(candidates)}")
print(f"\nMost Mentioned Drug Class: {max(found_drugs.items(), key=lambda x: len(x[1]))[0]}")

summary_report = f"""
PARKINSON'S DISEASE DRUG REPURPOSING ANALYSIS
{'='*80}

SEARCH CRITERIA:
- Disease: Parkinson's Disease
- Focus: Drug Repurposing/Repositioning
- Date Range: 2020-2025
- Language: English
- Total Articles Found: {len(df)}

KEY FINDINGS:

1. Drug Classes Identified: {len(found_drugs)}
   {chr(10).join([f'   - {drug}: {len(set(pmids))} articles' for drug, pmids in sorted(found_drugs.items(), key=lambda x: len(x[1]), reverse=True)[:5]])}

2. Top Mechanisms:
   {chr(10).join([f'   - {mech}: {cnt} ({(cnt/len(df)*100):.1f}%)' for mech, cnt in sorted(mechanisms.items(), key=lambda x: x[1], reverse=True)[:5] if cnt > 0])}

3. Repurposing Candidates: {len(candidates)}
   Examples: {chr(10).join([f'   - {c["Title"]}' for c in candidates[:3]])}

CONCLUSION:
The analysis identified {len(found_drugs)} different drug classes with potential for 
Parkinson's disease treatment, with {len(candidates)} specific drug candidates mentioned 
in the literature.
"""

with open("analysis_summary.txt", "w") as f:
    f.write(summary_report)
