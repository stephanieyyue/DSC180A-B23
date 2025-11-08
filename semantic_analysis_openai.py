

import os
import pandas as pd
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("~/Desktop/parkinsons_drug_repurposing.csv")

print("="*80)
print("PARKINSON'S DRUG REPURPOSING ANALYSIS - SEMANTIC LLM APPROACH")
print("="*80)
print(f"Analyzing {len(df)} abstracts with OpenAI API...\n")


results = []

for idx, row in df.iterrows():
    pmid = row['PMID']
    abstract = row['Abstract']
    
    print(f"[{idx+1}/{len(df)}] Processing PMID: {pmid}...")
    
    try:
        user_prompt = f"""Analyze this Parkinson's disease drug repurposing abstract and extract:
{abstract[:1500]}  # Limit to first 1500 chars to save tokens

Return JSON with:
{{
    "pmid": "{pmid}",
    "drug_candidates": ["drug1", "drug2"],
    "mechanisms": ["mechanism1", "mechanism2"],
    "clinical_application": "brief description",
    "repurposing_potential": "high/medium/low",
    "key_finding": "most important insight"
}}"""
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            analysis = json.loads(json_str)
        except json.JSONDecodeError:
            analysis = {
                "pmid": pmid,
                "drug_candidates": [],
                "mechanisms": [],
                "clinical_application": response_text[:200],
                "repurposing_potential": "unknown",
                "key_finding": response_text[:100]
            }
        
        results.append(analysis)
    
        print(f"  Drugs found: {', '.join(analysis.get('drug_candidates', []))}")
        print(f"  Potential: {analysis.get('repurposing_potential', 'unknown')}\n")
        
    except Exception as e:
        print(f"  ✗ Error processing PMID {pmid}: {str(e)}\n")
        results.append({
            "pmid": pmid,
            "error": str(e)
        })


print("\n" + "="*80)
print("="*80 + "\n")

all_drugs = {}
all_mechanisms = {}
high_potential_drugs = []

for result in results:
    if "error" not in result:
        for drug in result.get('drug_candidates', []):
            if drug:
                all_drugs[drug] = all_drugs.get(drug, 0) + 1
    
        for mech in result.get('mechanisms', []):
            if mech:
                all_mechanisms[mech] = all_mechanisms.get(mech, 0) + 1
        if result.get('repurposing_potential') == 'high':
            high_potential_drugs.append({
                'pmid': result['pmid'],
                'drugs': result.get('drug_candidates', []),
                'finding': result.get('key_finding', '')
            })

top_drugs = sorted(all_drugs.items(), key=lambda x: x[1], reverse=True)
top_mechanisms = sorted(all_mechanisms.items(), key=lambda x: x[1], reverse=True)

print("Drug Repurposing")
print("-" * 80)
for i, (drug, count) in enumerate(top_drugs[:15], 1):
    print(f"{i:2d}. {drug:30s} - Found in {count} abstract(s)")

print("-" * 80)
for i, (mech, count) in enumerate(top_mechanisms[:10], 1):
    print(f"{i:2d}. {mech:40s} - Mentioned in {count} abstract(s)")

print("-" * 80)
if high_potential_drugs:
    for item in high_potential_drugs[:5]:
        print(f"\nPMID: {item['pmid']}")
        print(f"Drugs: {', '.join(item['drugs'])}")
        print(f"Finding: {item['finding'][:100]}...")
else:
    print("No high-potential candidates identified")


results_df = pd.DataFrame([r for r in results if "error" not in r])
