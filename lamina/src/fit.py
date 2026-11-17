"""Least-squares cubic fitting of sampled points (Schneider, Graphics Gems 1990)."""
import math


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _mul(a, s):
    return (a[0] * s, a[1] * s)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _len(a):
    return math.hypot(a[0], a[1])


def _unit(a):
    d = _len(a)
    return (a[0] / d, a[1] / d) if d else (0.0, 0.0)


def _q(b, t):
    mt = 1 - t
    return (mt ** 3 * b[0][0] + 3 * mt * mt * t * b[1][0] + 3 * mt * t * t * b[2][0] + t ** 3 * b[3][0],
            mt ** 3 * b[0][1] + 3 * mt * mt * t * b[1][1] + 3 * mt * t * t * b[2][1] + t ** 3 * b[3][1])


def _qprime(b, t):
    mt = 1 - t
    return (3 * mt * mt * (b[1][0] - b[0][0]) + 6 * mt * t * (b[2][0] - b[1][0]) + 3 * t * t * (b[3][0] - b[2][0]),
            3 * mt * mt * (b[1][1] - b[0][1]) + 6 * mt * t * (b[2][1] - b[1][1]) + 3 * t * t * (b[3][1] - b[2][1]))


def _qprimeprime(b, t):
    return (6 * (1 - t) * (b[2][0] - 2 * b[1][0] + b[0][0]) + 6 * t * (b[3][0] - 2 * b[2][0] + b[1][0]),
            6 * (1 - t) * (b[2][1] - 2 * b[1][1] + b[0][1]) + 6 * t * (b[3][1] - 2 * b[2][1] + b[1][1]))


def fit_curve(points, max_error):
    if len(points) < 2:
        return []
    if len(points) == 2:
        return [_line(points[0], points[1])]
    left = _unit(_sub(points[1], points[0]))
    right = _unit(_sub(points[-2], points[-1]))
    # use a few points for a steadier end tangent
    if len(points) > 4:
        left = _unit(_sub(points[2], points[0]))
        right = _unit(_sub(points[-3], points[-1]))
    return _fit_cubic(points, left, right, max_error)


def _line(p0, p1):
    return (p0, _add(p0, _mul(_sub(p1, p0), 1 / 3)), _add(p0, _mul(_sub(p1, p0), 2 / 3)), p1)


def _fit_cubic(points, left_t, right_t, error):
    if len(points) == 2:
        dist = _len(_sub(points[0], points[1])) / 3.0
        return [(points[0], _add(points[0], _mul(left_t, dist)), _add(points[1], _mul(right_t, dist)), points[1])]
    u = _chord_param(points)
    b = _generate(points, u, left_t, right_t)
    max_err, split = _max_error(points, b, u)
    if max_err < error:
        return [b]
    if max_err < error * error * 4 or max_err < 16:
        for _ in range(20):
            u2 = _reparam(b, points, u)
            b = _generate(points, u2, left_t, right_t)
            max_err, split = _max_error(points, b, u2)
            if max_err < error:
                return [b]
            u = u2
    split = max(1, min(len(points) - 2, split))
    center = _unit(_sub(points[split - 1], points[split + 1]))
    return (_fit_cubic(points[:split + 1], left_t, center, error)
            + _fit_cubic(points[split:], _mul(center, -1), right_t, error))


def _generate(points, u, left_t, right_t):
    first, last = points[0], points[-1]
    C = [[0.0, 0.0], [0.0, 0.0]]
    X = [0.0, 0.0]
    for p, t in zip(points, u):
        mt = 1 - t
        a1 = _mul(left_t, 3 * mt * mt * t)
        a2 = _mul(right_t, 3 * mt * t * t)
        C[0][0] += _dot(a1, a1)
        C[0][1] += _dot(a1, a2)
        C[1][0] += _dot(a1, a2)
        C[1][1] += _dot(a2, a2)
        tmp = _sub(p, _q((first, first, last, last), t))
        X[0] += _dot(a1, tmp)
        X[1] += _dot(a2, tmp)
    det_c0_c1 = C[0][0] * C[1][1] - C[1][0] * C[0][1]
    det_c0_x = C[0][0] * X[1] - C[1][0] * X[0]
    det_x_c1 = X[0] * C[1][1] - X[1] * C[0][1]
    alpha_l = 0.0 if det_c0_c1 == 0 else det_x_c1 / det_c0_c1
    alpha_r = 0.0 if det_c0_c1 == 0 else det_c0_x / det_c0_c1
    seg_len = _len(_sub(first, last))
    eps = 1.0e-6 * seg_len
    if alpha_l < eps or alpha_r < eps:
        return (first, _add(first, _mul(left_t, seg_len / 3)), _add(last, _mul(right_t, seg_len / 3)), last)
    return (first, _add(first, _mul(left_t, alpha_l)), _add(last, _mul(right_t, alpha_r)), last)


def _reparam(b, points, u):
    return [_newton(b, p, t) for p, t in zip(points, u)]


def _newton(b, p, t):
    d = _sub(_q(b, t), p)
    q1 = _qprime(b, t)
    q2 = _qprimeprime(b, t)
    num = _dot(d, q1)
    den = _dot(q1, q1) + _dot(d, q2)
    if den == 0:
        return t
    return min(1.0, max(0.0, t - num / den))


def _chord_param(points):
    u = [0.0]
    for i in range(1, len(points)):
        u.append(u[-1] + _len(_sub(points[i], points[i - 1])))
    total = u[-1] or 1
    return [x / total for x in u]


def _max_error(points, b, u):
    max_d, split = 0.0, len(points) // 2
    for i, (p, t) in enumerate(zip(points, u)):
        d = _len(_sub(_q(b, t), p))
        if d > max_d:
            max_d, split = d, i
    return max_d, split
