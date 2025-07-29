import platform
if platform.system() != "Windows":
    raise EnvironmentError("BetterMt5 only works on Windows due to MetaTrader5 limitations.")
