#Cleaning_Data

#libraries
import pandas as pd

#load data into df
renters=pd.read_csv('data/burden.csv')

#drop micropolitan areas
renters=renters[renters['NAME'].str.contains('Metro Area', na=False)].copy()

#clean labels
renters['metro']=renters['NAME'].str.replace(' Metro Area', '', regex=False)
renters['metro']=renters['metro'].str.replace(' Metropolitan Statistical Area',
                                              '', regex=False)

#rename geo 
renters=renters.rename(columns={
    'metropolitan statistical area/micropolitan statistical area': 'msa_code'
    })

#extract state
renters['state']=renters['NAME'].str.split(',').str[-1].str.strip()
renters['state']=renters['state'].str.replace(' Metro Area', '', 
                                              regex=False).str.strip()

#multi state metros
renters['state']=renters['state'].str.split('-').str[0].str.strip()

#drop non states
valid_states=[
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
    'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
    'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
    'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
    'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'
]

renters=renters[renters['state'].isin(valid_states)].copy()

#print a check
print(f"Metro areas after removing non-states: {len(renters)}")

#drop 0 or NA
renters=renters[renters['total_renter_households'] > 0].copy()

#round percentages to hundreths
pct_cols=['pct_cost_burden', 'pct_severely_burdened']
renters[pct_cols]=renters[pct_cols].round(2)

#create burden labels
def burden_category(pct):
    if pct >=50:
        return 'Very High (50%+)'
    elif pct >= 40:
      return 'High (40-49%)'
    elif pct >= 30:
      return 'Moderate (30-39%)'
    else:
      return 'Low (<30%)'

#apply to renters
renters['burden_category']=renters['pct_cost_burden'].apply(burden_category)

#merge with hud
fmr=pd.read_csv('data/hud_fmr.csv')

renters['msa_code']=pd.to_numeric(renters['msa_code'], errors='coerce')
fmr['cbsa_num']=pd.to_numeric(fmr['cbsa_num'], errors='coerce')

renters=renters.merge(
    fmr[['cbsa_num','fmr_2br']],
    left_on='msa_code',
    right_on='cbsa_num',
    how='left'
)

#save as csv
renters.to_csv('data/burden_clean.csv')

#good info to know
print(f"Metro areas after cleaning: {len(renters)}")
print(f"\nBurden category breakdown:")
print(renters['burden_category'].value_counts())
print(f"\nTop 10 most burdened metros:")
print(renters[['metro','state','pct_cost_burden','pct_severely_burdened']]
      .sort_values('pct_cost_burden', ascending=False)
      .head(10).to_string(index=False))
print(f"\nBottom 10 least burdened metros:")
print(renters[['metro','state','pct_cost_burden','pct_severely_burdened']]
      .sort_values('pct_cost_burden', ascending=True)
      .head(10).to_string(index=False))
