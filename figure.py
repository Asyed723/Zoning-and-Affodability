#figures

#libraries
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

#load data
cbsa_shape=gpd.read_file('data/tl_2021_us_cbsa.zip')
states=gpd.read_file('data/tl_2021_us_state.zip')
df=pd.read_csv('data/burden_model.csv')

#merge
cbsa_shape['GEOID']=pd.to_numeric(cbsa_shape['GEOID'], errors='coerce')
df['cbsacode18']=pd.to_numeric(df['cbsacode18'], errors='coerce')

gdf=cbsa_shape.merge(
    df,
    left_on='GEOID',
    right_on='cbsacode18',
    how='inner'
)

#drop non continental US
gdf_cont=gdf[~gdf['state'].isin(['AK', 'HI', 'PR'])].copy()
states_cont=states[~states['STUSPS'].isin(['AK', 'HI', 'PR', 
                                           'VI', 'GU', 
                                           'MP', 'AS'])].copy()

#set dpi
plt.rcParams['figure.dpi']=300

#map
fig1, ax1 = plt.subplots(figsize=(16, 9))

gdf_cont.plot(
    column='pct_cost_burden',
    cmap='RdYlGn_r',
    linewidth=0.3,
    edgecolor='white',
    legend=True,
    legend_kwds={
        'label': '% of Renters Cost Burdened (30%+)',
        'orientation': 'horizontal',
        'shrink': 0.6,
        'pad': 0.02
    },
    ax=ax1,
    missing_kwds={'color': 'lightgray', 'label': 'No data'}
)
states_cont.boundary.plot(
    ax=ax1,
    linewidth=0.8,
    edgecolor='black',
    alpha=0.4
)

ax1.set_title('Rent Burden by Metro Area\n% of Renters Paying 30%+ of Income on Housing',
              fontsize=14, fontweight='bold', pad=15)
ax1.set_axis_off()
ax1.set_xlim(-125, -65)
ax1.set_ylim(24, 50)
plt.tight_layout()
plt.savefig('figures/fig1_map.png', bbox_inches='tight')
plt.close()

#WRLURI vs burdne
fig2, ax2=plt.subplots(figsize=(10, 7))

scatter = ax2.scatter(
    df['WRLURI18'],
    df['pct_cost_burden'],
    c=df['pct_severely_burdened'],
    cmap='RdYlGn_r',
    alpha=0.7,
    s=df['total_renter_households']/df['total_renter_households'].max()*300 +20,
    edgecolors='white',
    linewidths=0.5
)

z=np.polyfit(df['WRLURI18'].dropna(),
               df.loc[df['WRLURI18'].notna(), 'pct_cost_burden'], 1)
p=np.poly1d(z)
x_line=np.linspace(df['WRLURI18'].min(), df['WRLURI18'].max(), 100)
ax2.plot(x_line, p(x_line), 'steelblue', linewidth=2,
         linestyle='--', label='Trend line')

notable=df.nlargest(5, 'pct_cost_burden')
for _, row in notable.iterrows():
    ax2.annotate(row['metro'].split(',')[0],
                 (row['WRLURI18'], row['pct_cost_burden']),
                 textcoords='offset points', xytext=(6, 4),
                 fontsize=7, color='#333')

plt.colorbar(scatter, ax=ax2, label='% Severely Burdened (50%+)')
ax2.set_xlabel('Zoning Restrictiveness (WRLURI Score)\n← Less Restrictive    More Restrictive →',
               fontsize=11)
ax2.set_ylabel('% of Renters Cost Burdened (30%+)', fontsize=11)
ax2.set_title('Zoning Restrictiveness vs. Rent Burden by Metro Area',
              fontsize=13, fontweight='bold')
ax2.axvline(x=0, color='gray', linestyle=':', alpha=0.5, label='Mean restrictiveness')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figures/fig2_zoning_vs_burden.png', bbox_inches='tight')
plt.close()

#predicted vs actual
fig3, ax3=plt.subplots(figsize=(10, 7))

scatter3=ax3.scatter(
    df['predicted_burden'],
    df['pct_cost_burden'],
    c=df['WRLURI18'],
    cmap='RdBu_r',
    alpha=0.7,
    s=60,
    edgecolors='white',
    linewidths=0.5
)

min_val=min(df['predicted_burden'].min(), df['pct_cost_burden'].min())-1
max_val=max(df['predicted_burden'].max(), df['pct_cost_burden'].max())+1
ax3.plot([min_val, max_val], [min_val, max_val], 'k--',
         linewidth=1.5, alpha=0.5, label='Perfect prediction')

top_residuals=df.nlargest(5, 'residual')
bot_residuals=df.nsmallest(5, 'residual')
for _, row in pd.concat([top_residuals, bot_residuals]).iterrows():
    ax3.annotate(row['metro'].split(',')[0],
                 (row['predicted_burden'], row['pct_cost_burden']),
                 textcoords='offset points', xytext=(6, 4),
                 fontsize=7, color='#333')

plt.colorbar(scatter3, ax=ax3, label='Zoning Restrictiveness (WRLURI)')
ax3.set_xlabel('Predicted Rent Burden (%)', fontsize=11)
ax3.set_ylabel('Actual Rent Burden (%)', fontsize=11)
ax3.set_title('Predicted vs. Actual Rent Burden\n'
              '(Points above line = more burdened than model predicts)',
              fontsize=12, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figures/fig3_predicted_vs_actual.png', bbox_inches='tight')
plt.close()

#supply and demand 
#calibrate with medians
median_fmr=df['fmr_2br'].median()
median_rent=df['median_gross_rent'].median()
median_renters=df['total_renter_households'].median()
zoning_tax=median_rent-median_fmr

#build curves
q = np.linspace(0, 2*median_renters, 300)

wtp_max=median_fmr*1.8
wtp_slope=(wtp_max-median_fmr)/median_renters
demand=wtp_max-wtp_slope*q

wta_min=median_fmr*0.4
wta_slope=(median_fmr-wta_min)/median_renters
supply_free=wta_min+wta_slope*q
supply_zoning=supply_free+zoning_tax

#equilibriums
q_eq_free=(wtp_max - wta_min)/(wtp_slope+wta_slope)
p_eq_free= wtp_max - wtp_slope * q_eq_free
q_eq_zoning=(wtp_max-wta_min-zoning_tax)/(wtp_slope+wta_slope)
p_eq_zoning=wtp_max-wtp_slope*q_eq_zoning

print(f"Free market eq:  Q={q_eq_free:,.0f}, P=${p_eq_free:,.0f}/mo")
print(f"Zoning eq:       Q={q_eq_zoning:,.0f}, P=${p_eq_zoning:,.0f}/mo")
print(f"Units lost:      {q_eq_free - q_eq_zoning:,.0f}")

#make plot
q_plot=np.linspace(0, q_eq_free*1.3, 300)
demand_plot=wtp_max-wtp_slope*q_plot
supply_f_plot=wta_min+wta_slope*q_plot
supply_z_plot=supply_f_plot+zoning_tax

fig4, ax4=plt.subplots(figsize=(10, 8))

ax4.plot(q_plot, demand_plot, color='steelblue', linewidth=2.5,
         label='Demand (Willingness to Pay)')
ax4.plot(q_plot, supply_f_plot, color='green', linewidth=2.5,
         label='Supply — Free Market')
ax4.plot(q_plot, supply_z_plot, color='red', linewidth=2.5,
         linestyle='--', label='Supply — Zoning Restricted')

ax4.plot(q_eq_free,   p_eq_free,   'go', markersize=10, zorder=5)
ax4.plot(q_eq_zoning, p_eq_zoning, 'ro', markersize=10, zorder=5)

ax4.plot([q_eq_free, q_eq_free], [0, p_eq_free], 'g--', linewidth=1, alpha=0.5)
ax4.plot([0, q_eq_free], [p_eq_free, p_eq_free], 'g--', linewidth=1, alpha=0.5)
ax4.plot([q_eq_zoning, q_eq_zoning], [0, p_eq_zoning], 
         'r--', linewidth=1, alpha=0.5)
ax4.plot([0, q_eq_zoning], [p_eq_zoning, p_eq_zoning],
         'r--', linewidth=1, alpha=0.5)

ax4.annotate(f'Free Market Eq.\nP*=${p_eq_free:,.0f}  Q*={q_eq_free:,.0f}',
             xy=(q_eq_free, p_eq_free),
             xytext=(q_eq_free * 1.05, p_eq_free - 150),
             fontsize=9, color='green',
             arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

ax4.annotate(f'Zoning Eq.\nP*=${p_eq_zoning:,.0f}  Q*={q_eq_zoning:,.0f}',
             xy=(q_eq_zoning, p_eq_zoning),
             xytext=(q_eq_zoning * 0.4, p_eq_zoning + 100),
             fontsize=9, color='red',
             arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

#dwl triangle
dwl_q= np.linspace(q_eq_zoning, q_eq_free, 300)
dwl_demand=wtp_max-wtp_slope*dwl_q
dwl_supply=wta_min+wta_slope*dwl_q
ax4.fill_between(dwl_q, dwl_supply, dwl_demand,
                 alpha=0.25, color='orange',
                 label='Deadweight Loss')

#tax rectangle
ax4.fill_between([0, q_eq_zoning],
                 [p_eq_free, p_eq_free],
                 [p_eq_zoning, p_eq_zoning],
                 alpha=0.15, color='red',
                 label=f'Zoning Tax (≈${zoning_tax:,.0f}/mo per unit)')

#shift arrow
mid_q=q_eq_zoning*0.6
ax4.annotate('',
             xy=(mid_q, wta_min + wta_slope * mid_q + zoning_tax),
             xytext=(mid_q, wta_min + wta_slope * mid_q),
             arrowprops=dict(arrowstyle='->', color='darkred', lw=2))
ax4.text(mid_q*1.02,
         wta_min + wta_slope * mid_q + zoning_tax / 2,
         f'Zoning shifts\nsupply up\n(+${zoning_tax:,.0f}/mo)',
         fontsize=8, color='darkred')

ax4.set_xlabel('Number of Renter Households', fontsize=12)
ax4.set_ylabel('Monthly Rent ($)', fontsize=12)
ax4.set_title('Effect of Zoning Restrictions on Housing Market\n'
              'Calibrated to Median U.S. Metro Area (2022)',
              fontsize=13, fontweight='bold')
ax4.legend(fontsize=9, loc='upper right')
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax4.grid(True, alpha=0.3)
ax4.set_xlim(0, q_eq_free * 1.3)
ax4.set_ylim(0, wtp_max * 1.1)

plt.tight_layout()
plt.savefig('figures/fig4_supply_demand.png', bbox_inches='tight')
plt.close()
print("Saved fig4_supply_demand.png")
