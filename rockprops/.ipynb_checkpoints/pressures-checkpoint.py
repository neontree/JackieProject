

def hydsta_pres(mudweight, depth):
    """Calculate hydrostatic pressure based on mudweight

    Input unit:
        mudweight: ppg
        depth: ft
    Output unit:
        hydrostatic pressure: kPa
    """
    Ph = 0.052 * mudweight * depth #psi
    return Ph * 101.325 / 14.7  #Kpa


def conf_pres(hydsta_pres, diff_pres):
    """Calculate confined pressure based on hydrostatic pressure
    and differential pressure

    Input unit:
        hydsta_pres: Kpa
        diff_pres: Kpa
        """
    return hydsta_pres + diff_pres