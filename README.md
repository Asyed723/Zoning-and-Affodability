# Zoning and Rent Burdens

This repo is an analysis of how zoning laws in metropolitan areas in the United States, using Census ACS data, TIGER/Line Shapefiles, HUD Fair Market Rents, and the Wharton Residential Land Use Regulatory Index (WRLURI), affects rent burdens in these areas

## Research Question

Do more restrictive zoning regulations lead to higher rent burdens for renters in metropolitan areas?

## Data Sources

This project uses data from the U.S. Census Bureau, U.S. Department of Housing and Urban Development, and Joeseph Gyourko, professor at the Wharton School at the University of Pennsylvania. Below are links for the data needed.

API for American Community Survey (ACS): <https://api.census.gov/data/key_signup.html>

TIGER/Line Data (Year:2021, Layer Types: Core Based Statistical Area and States (and equivilant): <https://www.census.gov/cgi-bin/geo/shapefiles/index.php>

HUD API (Comprehensive Housing Affordability Strategy (CHAS)): <https://www.huduser.gov/portal/dataset/fmr-api.html>

Wharton Residential Land Use Regulatory Index (WRLURI): <https://www.dropbox.com/scl/fi/ekxan963skmr436rov9j4/WHARTON-LAND-REGULATION-DATA_01_15_2020.dta?rlkey=aqdccswzltbp7w0fxzayh33nz&e=1&st=y45a71ys&dl=0>

## Scripts Used

There are 5 Python scripts used for the analysis: census_data.py, hud_data.py, cleaning_data.py, model.py, and figure.py

The order to run the scripts is:

1.  census_data.py/hud_data.py (Both scripts can be first)

    These scripts use the APIs from the ACS and HUD to get the data needed. The APIs should be in a text files called apitext.txt and hudapitext.txt in the main branch. These scripts create the CSV files needed for the analysis in later scripts.

2.  cleaning_data.py

    This script wrangles the data for easier use. This merges the HUD and ACS data for easier use. Categories are also made and applied to each metro area left after merging describing rent burden. Also, prints some helpful information about some of the most rent burdened cities.

3.  model.py

    This script creates the underlying models used for the next script. The script calculates a 'tax' based on how much prices increase from zoning. It also creates a welfare loss index that measures the welfare loss from zoning regulations. Creates a multivariable regression as well as a proxy for a tax paid by renters as a result from zoning regulations.

4.  figure.py

    Creates all of the figures needed for visual representations. Also merges shapefiles with main CSV for easier use.

## Key Findings

Many metropolitan areas in the U.S. create a 'tax' with their zoning laws. Places like Miami create a huge welfare loss for renters in the metro area as their zoning regulations is associated with more renters being burdened by their rent. This leads to a welfare loss in the renting market. There could be more rent households with lower prices with different zoning regulation. 

Regression analysis shows the variables chosen, WRLURI, log of total renter households, percentage of severely burdened renters, and zoning tax percentage, can can explain their association of higher percentage of renters burdened by their rent. A strong R^2 backs the variables being associated with explaining the change in the percent of people burdened by their rent. 

Using all the data collected, a supply and demand diagram was created. This diagram shows the dead weight loss created by strict zoning laws in metro areas. As well the effect of the 'tax' zoning laws create, shifting the supply curve up. This causes the equilibrium for the price of rent and quantity of renter households to be greater compared to the no zoning tax equilibrium. 

Zoning laws can be helpful tools to help design cities and keep neighborhoods safe from things like pollution. However, restrictive zoning laws can be a big burden on rent prices and cause renters to be more burdened with rent than they would be otherwise.

## Notes

Assumptions were made with how much more renters were willing to overpay or underpay for a fair market value household. More research into this data would help this analysis greatly.

Multi-state metro areas are assigned to the primary (first-listed) state. For example Washington-Arlington-Alexandria is listed in the District of Colombia as opposed to being in Virginia or other states the metro area lies in.

Here is an article about the Wharton Residential Land Use Regulatory Index: <https://www.nber.org/papers/w26573>
