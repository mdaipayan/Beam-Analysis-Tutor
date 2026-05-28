import numpy as np


def sanitize_loads(length, loads):
    """Validate and normalize load definitions."""
    normalized = []
    for ld in loads:
        if ld["type"] == "point":
            P = max(0.0, float(ld["P"]))
            a = min(length, max(0.0, float(ld["a"])))
            normalized.append({"type": "point", "P": P, "a": a})
        elif ld["type"] == "udl":
            w = max(0.0, float(ld["w"]))
            s = min(length, max(0.0, float(ld["start"])))
            e = min(length, max(0.0, float(ld["end"])))
            if e < s:
                s, e = e, s
            normalized.append({"type": "udl", "w": w, "start": s, "end": e})
    return normalized


def reactions_for_simply_supported(length, loads):
    R1 = 0.0
    R2 = 0.0
    total_vertical = 0.0
    moment_about_left = 0.0

    for ld in loads:
        if ld["type"] == "point":
            total_vertical += ld["P"]
            moment_about_left += ld["P"] * ld["a"]
        elif ld["type"] == "udl":
            L = ld["end"] - ld["start"]
            W = ld["w"] * L
            centroid = ld["start"] + L / 2
            total_vertical += W
            moment_about_left += W * centroid

    if length == 0:
        return 0.0, 0.0

    R2 = moment_about_left / length
    R1 = total_vertical - R2
    return R1, R2


def shear_force(x, length, loads, support):
    if support == "cantilever":
        right_load = 0.0
        for ld in loads:
            if ld["type"] == "point" and ld["a"] >= x:
                right_load += ld["P"]
            elif ld["type"] == "udl":
                s, e, w = ld["start"], ld["end"], ld["w"]
                if x <= s:
                    right_load += w * (e - s)
                elif s < x < e:
                    right_load += w * (e - x)
        return -right_load

    V = 0.0
    R1, _ = reactions_for_simply_supported(length, loads)
    V += R1
    for ld in loads:
        if ld["type"] == "point":
            if ld["a"] <= x:
                V -= ld["P"]
        elif ld["type"] == "udl":
            s, e, w = ld["start"], ld["end"], ld["w"]
            if x <= s:
                continue
            elif x >= e:
                V -= w * (e - s)
            else:
                V -= w * (x - s)
    return V


def bending_moment(x, length, loads, support):
    if support == "cantilever":
        moment = 0.0
        for ld in loads:
            if ld["type"] == "point" and ld["a"] >= x:
                moment += ld["P"] * (ld["a"] - x)
            elif ld["type"] == "udl":
                s, e, w = ld["start"], ld["end"], ld["w"]
                if x <= s:
                    W = w * (e - s)
                    centroid = s + (e - s) / 2
                    moment += W * (centroid - x)
                elif s < x < e:
                    W = w * (e - x)
                    centroid = x + (e - x) / 2
                    moment += W * (centroid - x)
        return -moment

    M = 0.0
    R1, _ = reactions_for_simply_supported(length, loads)
    M += R1 * x
    for ld in loads:
        if ld["type"] == "point":
            if ld["a"] <= x:
                M -= ld["P"] * (x - ld["a"])
        elif ld["type"] == "udl":
            s, e, w = ld["start"], ld["end"], ld["w"]
            if x <= s:
                continue
            elif x >= e:
                load_len = e - s
                W = w * load_len
                centroid = s + load_len / 2
                M -= W * (x - centroid)
            else:
                load_len = x - s
                W = w * load_len
                centroid = s + load_len / 2
                M -= W * (x - centroid)
    return M
