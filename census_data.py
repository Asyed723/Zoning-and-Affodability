#Census Data

#Libraries
import requests
import pandas as pd

#variables needed
variables={
    'B25070_001E': 'total_renter_households',
    'B25070_007E': '30_to_34pct',
    'B25070_008E': '35_to_39pct',
    'B25070_009E': '40_to_49pct',
    'B25070_010E': '50pct_plus',
    'B25064_001E': 'median_gross_rent',
    'B19013_001E': 'median_household_income'
    } #number of households with rentt/income ratio

#set var_list
var_list=variables.keys()

#set var_string
var_string=','.join(var_list)

#api
api='https://api.census.gov/data/2022/acs/acs5'

with open("apitext.txt") as f:
    apikey = f.readline().strip()
    
#Parameters of data
params={
        'get':f'NAME,{var_string}',
        'for':'metropolitan statistical area/micropolitan statistical area:*',
        'key':apikey
        }

#make requests
r=requests.get(api, params=params)

#create dataframe
data=r.json()
df=pd.DataFrame(data[1:], columns=data[0])

#rename cols
df=df.rename(columns=variables)

#convert numeric columns from str to num
numeric_cols=list(variables.values())
df[numeric_cols]=df[numeric_cols].apply(pd.to_numeric, errors='coerce')

#calc key measures
df['cost_burdened']=(
    df['30_to_34pct']+df['35_to_39pct']+df['40_to_49pct']+df['50pct_plus']
    )

df['severely_burdened']=df['50pct_plus']

df['pct_cost_burden']=100*df['cost_burdened']/df['total_renter_households']

df['pct_severely_burdened']=100*(
    df['severely_burdened']/df['total_renter_households']
    )

#save as csv
df.to_csv('data/burden.csv', index=False)

#some info
print(f"Saved {len(df)} metro areas")
print(df[['NAME','pct_cost_burden','pct_severely_burdened']].sort_values('pct_cost_burden', ascending=False).head(10))