#hud_data

#libraries
import requests
import pandas as pd
import time

#hud api
with open('hudapitext.txt') as f:
    hudkey = f.readline().strip()

headers={'Authorization': f'Bearer {hudkey}'}
url='https://www.huduser.gov/hudapi/public/fmr/listMetroAreas'
r=requests.get(url, headers=headers)
metros=pd.DataFrame(r.json())

#extract cbsa
metros['cbsa_num']=metros['cbsa_code'].str.extract(r'METRO(\d+)M').astype(float)
metros=metros.dropna(subset=['cbsa_num'])
metros=metros[~metros['area_name'].str.contains('PR|Guam|Virgin', na=False)]

#drop pr and non matches
metros=metros.dropna(subset=['cbsa_num'])
metros=metros[~metros['area_name'].str.contains('PR|Guam|Virgin', na=False)]

#pull fmr from metro
results=[]

for i, row in metros.iterrows():
    url_fmr=f"https://www.huduser.gov/hudapi/public/fmr/data/{row['cbsa_code']}?year=2022"

    for attempt in range(5):
        resp=requests.get(url_fmr, headers=headers)
        if resp.status_code==200:
            break
        elif resp.status_code==429:
            wait=2 ** attempt 
            print(f"Rate limited on {row['area_name']}, waiting {wait}s...")
            time.sleep(wait)
        else:
            print(f"Failed {row['area_name']}: {resp.status_code}")
            break

    if resp.status_code==200:
        try:
            basic=resp.json()['data']['basicdata']
            if isinstance(basic, list):
                basic=basic[0]
            results.append({
                'cbsa_num':  row['cbsa_num'],
                'area_name': row['area_name'],
                'fmr_0br':   basic.get('Efficiency'),
                'fmr_1br':   basic.get('One-Bedroom'),
                'fmr_2br':   basic.get('Two-Bedroom'),
                'fmr_3br':   basic.get('Three-Bedroom'),
                'fmr_4br':   basic.get('Four-Bedroom'),
            })
        except Exception as e:
            print(f"Parse error for {row['area_name']}: {e}")
            print(f"Raw response: {resp.text[:200]}")

    time.sleep(0.5)

    if len(results) % 50==0 and len(results)>0:
        print(f"Progress: {len(results)} saved so far...")
        
#save csv
fmr_df=pd.DataFrame(results)
fmr_df.to_csv('data/hud_fmr.csv', index=False)