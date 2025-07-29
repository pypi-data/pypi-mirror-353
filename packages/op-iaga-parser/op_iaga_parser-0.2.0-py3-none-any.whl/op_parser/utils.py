def safe_float(val):
    try:
        return float(val)
    except Exception:
        return None


def f_to_c(f):
    if f is None or f == '':
        return ''
    return round((f - 32) * 5.0 / 9.0, 2)


def inch_to_mm(inch):
    if inch is None or inch == '':
        return ''
    return round(inch * 25.4, 2)


def mph_to_mps(mph):
    if mph is None or mph == '':
        return ''
    return round(mph * 0.44704, 2)


def mile_to_km(mile):
    if mile is None or mile == '':
        return ''
    return round(mile * 1.60934, 2)


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def convert_value(val, converters=None, apply_conversion=True):
    """
    Универсальная функция для безопасного преобразования значения.
    :param val: исходное значение
    :param converters: список функций преобразования
    :param apply_conversion: bool, применять ли преобразования
    :return: преобразованное значение или исходное (если apply_conversion=False)
    """
    if not apply_conversion or not converters:
        return val
    res = val
    for conv in converters:
        try:
            res = conv(res)
        except Exception:
            pass
    return res
