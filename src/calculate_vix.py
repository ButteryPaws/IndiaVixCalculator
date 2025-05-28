import pandas as pd
from typing import Dict, Any
from scipy.interpolate import CubicSpline
import numpy as np

MINUTES_IN_A_YEAR = 525600
MINUTES_IN_30_DAYS = 43200


def vix_calculator(data: Dict[str, Any]) -> np.float64:
    """
    Calculates the India Vix value at any given point in time. To calculate the India
    Vix value at any point, you require the option chain for the near month and next month options,
    the interest rate and the futures for the corresponding expiries.

    Reference: [NSE Whitepaper on India Vix](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/white_paper_IndiaVIX.pdf)

    :param data: A dictionary with the data required to compute the India Vix at a certain point. This
    is a dictionary with keys as follows
        - option_chain_1: A Pandas dataframe of the option chain with the nearer expiry. This dataframe must contain the columns 'Strike', 'Call Bid', 'Call Ask', 'Put Bid' and 'Put Ask'.
        - mte_1: Minutes to expiry for the first option chain
        - option_chain_2: A Pandas dataframe of the option chain with the next expiry. This dataframe must contain the columns 'Strike', 'Call Bid', 'Call Ask', 'Put Bid' and 'Put Ask'.
        - mte_2: Minutes to expiry for the second option chain
        - fut_1: The **last traded price** for the futures with the same expiry as the first option chain
        - fut_2: The **last traded price** for the futures with the same expiry as the second option chain
        - ir_1: The MIBOR dictated risk-free rate for the first option chain
        - ir_2: The MIBOR dictated risk-free rate for the second option chain
    """
    df_1: pd.DataFrame = data["option_chain_1"]
    df_2: pd.DataFrame = data["option_chain_2"]
    mte_1 = data["mte_1"]
    mte_2 = data["mte_2"]
    sigma_1 = compute_sigma(df_1, mte_1, data["fut_1"], data["ir_1"])
    sigma_2 = compute_sigma(df_2, mte_2, data["fut_2"], data["ir_2"])
    T_1 = mte_1 / MINUTES_IN_A_YEAR
    T_2 = mte_2 / MINUTES_IN_A_YEAR
    sigma = np.sqrt(
        (MINUTES_IN_A_YEAR / MINUTES_IN_30_DAYS)
        * (
            T_1 * sigma_1 * ((mte_2 - MINUTES_IN_30_DAYS) / (mte_2 - mte_1))
            + T_2 * sigma_2 * ((MINUTES_IN_30_DAYS - mte_1) / (mte_2 - mte_1))
        )
    )
    vix = 100 * sigma
    return vix


def compute_sigma(df: pd.DataFrame, mte: int, fut: float, ir: float):
    df["Call Mid"] = (df["Call Ask"] + df["Call Bid"]) / 2
    df["Put Mid"] = (df["Put Ask"] + df["Put Bid"]) / 2
    df["Call Spread"] = (df["Call Ask"] - df["Call Bid"]) / df["Call Mid"]
    df["Put Spread"] = (df["Put Ask"] - df["Put Bid"]) / df["Put Mid"]
    # Need to correct missing strikes or large spreads
    atm = cubic_spline_correction(df, fut)
    df["Q"] = np.where(
        df["Strike"] < atm,
        df["Put Mid"],
        np.where(
            df["Strike"] > atm,
            df["Call Mid"],
            (df["Put Mid"] + df["Call Mid"]) / 2,
        ),
    )
    df["diff_K_upper"] = df["Strike"].diff().abs()
    df["diff_K_lower"] = df["Strike"].diff(-1).abs()
    df["delta_K"] = (df["diff_K_lower"] + df["diff_K_upper"]) / 2
    df.loc[0, "delta_K"] = df.loc[0, "diff_K_lower"]
    df.loc[len(df)-1, "delta_K"] = df.loc[len(df)-1, "diff_K_upper"]
    T = mte / MINUTES_IN_A_YEAR
    df["contribution"] = (
        (df["delta_K"] / (df["Strike"] * df["Strike"])) * np.exp(ir * T) * df["Q"]
    )
    sigma = (2 * df["contribution"].sum() - (fut / atm - 1) ** 2) / T
    return sigma


def cubic_spline_correction(df: pd.DataFrame, fut_price: float):
    """Uses cubic spline interpolation to correct missing option data or large spreads"""
    # Calculate atm price from the index forward
    atm_index = df["Strike"].searchsorted(fut_price) - 1
    atm = df.loc[atm_index, "Strike"]
    call_df = df[df["Strike"] >= atm]
    put_df = df[df["Strike"] <= atm]
    # Find problematic points
    call_knot_points_idx = call_df["Call Spread"] <= 0.3
    if call_knot_points_idx.sum() >= 3:
        call_cs = CubicSpline(
            x=call_df.loc[call_knot_points_idx, "Strike"],
            y=call_df.loc[call_knot_points_idx, "Call Mid"],
            bc_type="natural",
            extrapolate=False,
        )
        df["Call Mid"] = call_cs(df["Strike"])
    else:
        df["Call Mid"] = np.nan
    put_knot_points_idx = put_df["Put Spread"] <= 0.3
    if put_knot_points_idx.sum() >= 3:
        put_cs = CubicSpline(
            x=put_df.loc[put_knot_points_idx, "Strike"],
            y=put_df.loc[put_knot_points_idx, "Put Mid"],
            bc_type="natural",
            extrapolate=False,
        )
        df["Put Mid"] = put_cs(df["Strike"])
    else:
        df["Put Mid"] = np.nan
    return atm
