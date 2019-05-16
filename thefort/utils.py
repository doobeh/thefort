def usd_filter(value):
    return "${:,.2f}".format(float(value / 100.0))


def decimal_places(value, places=2):
    return f"{value:.{places}f}"


def zfill(value, places=15):
    return str(value).zfill(places)
