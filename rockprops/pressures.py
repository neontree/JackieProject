

def hydsta_pres(mudweight, depth, inclination, inclination_threshold=90):
    """Calculate hydrostatic pressure based on mudweight

    Input unit:
        mudweight: ppg
        depth: ft
        inclination: degree
    Output unit:
        hydrostatic pressure: kPa
    """

    Ph = 0.052 * mudweight * depth

    # below kick-off has same pressure
    kick_off = inclination > inclination_threshold
    Ph[kick_off] = Ph[~kick_off][-1]

    return Ph #Kpa


def conf_pres(hydsta_pres, diff_pres):
    """Calculate confined pressure based on hydrostatic pressure
    and differential pressure

    Input unit:
        hydsta_pres: Kpa
        diff_pres: Kpa
        """
    return hydsta_pres + diff_pres


if __name__ == '__main__':
    import numpy as np
    mudweight = 8
    depth = np.arange(6)

    inclination = np.ones(depth.shape).astype(dtype=np.int)
    inclination[-3:] = 92
    p = hydsta_pres(mudweight, depth, inclination)
    print(inclination)
    print(depth)
    print(p)



