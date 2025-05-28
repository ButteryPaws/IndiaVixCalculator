import pandas as pd

from calculate_vix import vix_calculator

# Generate data
data = {}
data['option_chain_1'] = pd.read_csv("Data/toy data/near_month_option_chain.csv")
data['option_chain_2'] = pd.read_csv("Data/toy data/next_month_option_chain.csv")
data["fut_1"] = 5129
data["fut_2"] = 5115
data["mte_1"] = 12960
data["mte_2"] = 53280
data["ir_1"] = 0.0390
data["ir_2"] = 0.0465
print(vix_calculator(data))
