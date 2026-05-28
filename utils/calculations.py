import numpy as np

def reactions_for_simply_supported(length, loads):
    """
    Compute reactions R1 (left) and R2 (right) for simply supported beam.
    Loads: list of dicts: {"type":"point","P":..,"a":..} or {"type":"udl","w":..,"start":..,"end":..}
    Returns (R1, R2)
    """
    R1 = 0.0
    R2 = 0.0
    total_vertical = 0.0
    moment_about_left = 0.0

    for ld in loads:
        if ld["type"] == "point":
            P = ld["P"]
            a = ld["a"]
            total_vertical += P
            moment_about_left += P * a
        elif ld["type"] == "udl":
            w = ld["w"]
            s = ld["start"]
            e = ld["end"]
            L = e - s
            W = w * L
            centroid = s + L/2
            total_vertical += W
            moment_about_left += W * centroid

    # Solve R1 + R2 = total_vertical and R2*length = moment_about_left
    if length == 0:
        return 0.0, 0.0
    R2 = moment_about_left / length
    R1 = total_vertical - R2
    return R1, R2

def shear_force(x, length, loads, support):
    """
    Returns shear force at position x (kN).
    Positive sign convention: upward positive on left segment.
    For cantilever, reactions at fixed support are included implicitly.
    """
    V = 0.0
    if support == "simply_supported":
        R1, R2 = reactions_for_simply_supported(length, loads)
        V += R1
    elif support == "cantilever":
        # For cantilever, reaction at left support equals sum of vertical loads
        total_vertical = 0.0
        for ld in loads:
            if ld["type"] == "point":
                total_vertical += ld["P"]
            elif ld["type"] == "udl":
                total_vertical += ld["w"] * (ld["end"] - ld["start"])
        V += total_vertical  # upward reaction at fixed support

    # Subtract loads to the left of x
    for ld in loads:
        if ld["type"] == "point":
            if ld["a"] <= x:
                V -= ld["P"]
        elif ld["type"] == "udl":
            s = ld["start"]
            e = ld["end"]
            if x <= s:
                continue
            elif x >= e:
                V -= ld["w"] * (e - s)
            else:
                V -= ld["w"] * (x - s)
    # For cantilever sign convention: make shear negative for downward loads on free end
    if support == "cantilever":
        # convert to conventional sign (downward negative)
        V = -V
    return V

def bending_moment(x, length, loads, support):
    """
    Returns bending moment at position x (kNm).
    Positive sagging convention.
    """
    M = 0.0
    if support == "simply_supported":
        R1, R2 = reactions_for_simply_supported(length, loads)
        M += R1 * x
    elif support == "cantilever":
        # For cantilever, moment at x due to reaction at support is zero (reaction at left)
        M += 0.0

    # Subtract moments from loads to left of x
    for ld in loads:
        if ld["type"] == "point":
            a = ld["a"]
            P = ld["P"]
            if a <= x:
                M -= P * (x - a)
        elif ld["type"] == "udl":
            s = ld["start"]
            e = ld["end"]
            w = ld["w"]
            if x <= s:
                continue
            elif x >= e:
                L = e - s
                W = w * L
                centroid = s + L/2
                M -= W * (x - centroid)
            else:
                L = x - s
                W = w * L
                centroid = s + L/2
                M -= W * (x - centroid)

    # For cantilever, sign convention: positive sagging -> moment due to loads is negative of above
    if support == "cantilever":
        M = -M
    return M
