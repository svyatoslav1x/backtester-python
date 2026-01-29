import numpy as np
import pandas as pd


def calculate_sharpe_ratio(returns, periods=252):
    return (np.sqrt(periods) * np.mean(returns)) / np.std(returns)


def calculate_drawdowns(equity_curve):
    hwm = [0]
    eq_index = equity_curve.index
    drawdown = pd.Series(index=eq_index)
    duration = pd.Series(index=eq_index)

    # Initialize first values to avoid NaNs if possible, or handle in loop
    drawdown.iloc[0] = 0
    duration.iloc[0] = 0

    for i in range(1, len(eq_index)):
        # FIX: Use .iloc[i] to access value by integer position
        val = equity_curve.iloc[i]

        current_hwm = max(hwm[i - 1], val)
        hwm.append(current_hwm)
        drawdown.iloc[i] = hwm[i] - val
        duration.iloc[i] = 0 if drawdown.iloc[i] == 0 else duration.iloc[i - 1] + 1

    return drawdown.max(), duration.max()
