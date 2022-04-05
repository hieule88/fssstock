import pandas as pd
import statsmodels.api as sm
from linearmodels.datasets import wage_panel

data = wage_panel.load()
year = pd.Categorical(data.year)
data = data.set_index(["nr", "year"])
data["year"] = year
print(data)
exog_vars = ["black", "hisp", "exper", "expersq", "married", "educ", "union", "year"]
exog = sm.add_constant(data[exog_vars])
from linearmodels.panel import RandomEffects

# print(data.lwage)
# print(data)
mod = RandomEffects(data['lwage'], exog)
re_res = mod.fit()
print(exog)

