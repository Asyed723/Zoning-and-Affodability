#Models

#libraries
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

#create dfs
census=pd.read_csv('data/burden_clean.csv')
wrluri=pd.read_stata('data/wrluri.dta')

#aggregate wrluri to metro areas
wrluri_metro=(
    wrluri.dropna(subset=['cbsacode18', 'WRLURI18'])
    .groupby('cbsacode18')
    .apply(lambda x: pd.Series({
        'WRLURI18': np.average(x['WRLURI18'], 
                               weights=x['weight_cbsa'].fillna(1)),
        'num_municipalities': len(x),
        'cbsatitle': x['cbsatitle18'].iloc[0]
        }))
    .reset_index()
    )

#force msa code to numeric
census['msa_code']=pd.to_numeric(census['msa_code'], errors='coerce')
wrluri_metro['cbsacode18']=pd.to_numeric(wrluri_metro['cbsacode18'],
                                         errors='coerce')

#merge data
merged=census.merge(
    wrluri_metro[['cbsacode18', 'WRLURI18', 'num_municipalities']],
    left_on='msa_code',
    right_on='cbsacode18',
    how='inner'
    )

print(f'Metros after merge: {len(merged)}')
print(f'Metros lost (no WRLURI match): {len(census)-len(merged)}')

#welfare loss index
merged['welfare_loss_index']=(merged['pct_cost_burden']-25).clip(lower=0)
merged['welfare_loss_score']=(
    100*merged['welfare_loss_index']/merged['welfare_loss_index'].max()
    ).round(2)

print("\nMODEL 1: WELFARE LOSS")
print(merged[['metro','state','pct_cost_burden','welfare_loss_score']]
      .sort_values('welfare_loss_score', ascending=False)
      .head(10).to_string(index=False))

#zoning tax proxy
merged['zoning_tax']=(merged['median_gross_rent']-merged['fmr_2br']).round(2)
merged['zoning_tax_pct']=(100*merged['zoning_tax']/merged['fmr_2br']).round(2)

#regression

#make log var
merged['log_renters']=np.log(merged['total_renter_households'])

#df for model
model_cols=['pct_cost_burden', 'WRLURI18', 'log_renters',
              'pct_severely_burdened', 'zoning_tax_pct']
merged_model=merged.dropna(subset=model_cols).copy()

#set regression 
X=merged_model[['WRLURI18', 'log_renters',
                  'pct_severely_burdened', 'zoning_tax_pct']]
Y=merged_model['pct_cost_burden']

scaler=StandardScaler()
X_scaled=scaler.fit_transform(X)

reg=LinearRegression()
reg.fit(X_scaled, Y)

#reg info
print('\nMODEL 3: REGRESSION')
print(f'R-squared: {reg.score(X_scaled, Y):.4f}')
print('Coefficients (standardized):')
for name, coef in zip(X.columns, reg.coef_):
    print(f'  {name:30s}: {coef:+.4f}')
print(f"  {'intercept':30s}: {reg.intercept_:.4f}")

#values into df
merged_model['predicted_burden']=reg.predict(X_scaled).round(2)
merged_model['residual']=(
    merged_model['pct_cost_burden']-merged_model['predicted_burden']
).round(2)

#summary info
print("\nMetros most ABOVE predicted burden (policy red flags):")
print(merged_model[['metro', 'state', 'pct_cost_burden',
                    'predicted_burden', 'residual', 'WRLURI18']]
      .sort_values('residual', ascending=False)
      .head(10).to_string(index=False))

print("\nMetros most BELOW predicted burden (relatively affordable):")
print(merged_model[['metro', 'state', 'pct_cost_burden',
                    'predicted_burden', 'residual', 'WRLURI18']]
      .sort_values('residual', ascending=True)
      .head(10).to_string(index=False))

#save as csv
merged_model.to_csv('data/burden_model.csv', index=False)