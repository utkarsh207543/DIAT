"""
Cephes Mathematical Functions

Converted from C to Python maintaining exact logic.
Original: cephes.c from NIST Statistical Test Suite
"""

import math

# Constants
MACHEP = 1.11022302462515654042E-16  # 2**-53
MAXLOG = 7.09782712893383996732224E2  # log(MAXNUM)
MAXNUM = 1.7976931348623158E308  # 2**1024*(1-MACHEP)
PI = 3.14159265358979323846

big = 4.503599627370496e15
biginv = 2.22044604925031308085e-16

sgngam = 0

rel_error = 1E-12


def cephes_igamc(a, x):
    """Complementary incomplete gamma function"""
    global sgngam
    
    if x <= 0 or a <= 0:
        return 1.0
    
    if x < 1.0 or x < a:
        return 1.0 - cephes_igam(a, x)
    
    ax = a * math.log(x) - x - cephes_lgam(a)
    
    if ax < -MAXLOG:
        print("igamc: UNDERFLOW")
        return 0.0
    
    ax = math.exp(ax)
    
    # Continued fraction
    y = 1.0 - a
    z = x + y + 1.0
    c = 0.0
    pkm2 = 1.0
    qkm2 = x
    pkm1 = x + 1.0
    qkm1 = z * x
    ans = pkm1 / qkm1
    
    while True:
        c += 1.0
        y += 1.0
        z += 2.0
        yc = y * c
        pk = pkm1 * z - pkm2 * yc
        qk = qkm1 * z - qkm2 * yc
        
        if qk != 0:
            r = pk / qk
            t = abs((ans - r) / r)
            ans = r
        else:
            t = 1.0
        
        pkm2 = pkm1
        pkm1 = pk
        qkm2 = qkm1
        qkm1 = qk
        
        if abs(pk) > big:
            pkm2 *= biginv
            pkm1 *= biginv
            qkm2 *= biginv
            qkm1 *= biginv
        
        if not (t > MACHEP):
            break
    
    return ans * ax


def cephes_igam(a, x):
    """Incomplete gamma function"""
    if x <= 0 or a <= 0:
        return 0.0
    
    if x > 1.0 and x > a:
        return 1.0 - cephes_igamc(a, x)
    
    # Compute x**a * exp(-x) / gamma(a)
    ax = a * math.log(x) - x - cephes_lgam(a)
    if ax < -MAXLOG:
        print("igam: UNDERFLOW")
        return 0.0
    ax = math.exp(ax)
    
    # Power series
    r = a
    c = 1.0
    ans = 1.0
    
    while True:
        r += 1.0
        c *= x / r
        ans += c
        if not (c / ans > MACHEP):
            break
    
    return ans * ax / a


def cephes_lgam(x):
    """Logarithm of gamma function"""
    global sgngam
    
    # Stirling's formula expansion coefficients
    A = [8.11614167470508450300E-4, -5.95061904284301438324E-4,
         7.93650340457716943945E-4, -2.77777777730099687205E-3,
         8.33333333333331927722E-2]
    B = [-1.37825152569120859100E3, -3.88016315134637840924E4,
         -3.31612992738871184744E5, -1.16237097492762307383E6,
         -1.72173700820839662146E6, -8.53555664245765465627E5]
    C = [1.0, -3.51815701436523470549E2, -1.70642106651881159223E4,
         -2.20528590553854454839E5, -1.13933444367982507207E6,
         -2.53252307177582951285E6, -2.01889141433532773231E6]
    
    sgngam = 1
    
    if x < -34.0:
        q = -x
        w = cephes_lgam(q)
        p = math.floor(q)
        
        if p == q:
            return sgngam * MAXNUM
        
        i = int(p)
        if (i & 1) == 0:
            sgngam = -1
        else:
            sgngam = 1
        
        z = q - p
        if z > 0.5:
            p += 1.0
            z = p - q
        z = q * math.sin(PI * z)
        if z == 0.0:
            return sgngam * MAXNUM
        
        z = math.log(PI) - math.log(z) - w
        return z
    
    if x < 13.0:
        z = 1.0
        p = 0.0
        u = x
        
        while u >= 3.0:
            p -= 1.0
            u = x + p
            z *= u
        
        while u < 2.0:
            if u == 0.0:
                return sgngam * MAXNUM
            z /= u
            p += 1.0
            u = x + p
        
        if z < 0.0:
            sgngam = -1
            z = -z
        else:
            sgngam = 1
        
        if u == 2.0:
            return math.log(z)
        
        p -= 2.0
        x = x + p
        p = x * cephes_polevl(x, B, 5) / cephes_p1evl(x, C, 6)
        
        return math.log(z) + p
    
    if x > 2.556348e305:
        print("lgam: OVERFLOW")
        return sgngam * MAXNUM
    
    q = (x - 0.5) * math.log(x) - x + math.log(math.sqrt(2 * PI))
    if x > 1.0e8:
        return q
    
    p = 1.0 / (x * x)
    if x >= 1000.0:
        q += (((7.9365079365079365079365e-4 * p - 2.7777777777777777777778e-3) * p +
               0.0833333333333333333333)) / x
    else:
        q += cephes_polevl(p, A, 4) / x
    
    return q


def cephes_polevl(x, coef, N):
    """Evaluate polynomial"""
    ans = coef[0]
    for i in range(N):
        ans = ans * x + coef[i + 1]
    return ans


def cephes_p1evl(x, coef, N):
    """Evaluate polynomial with leading coefficient 1"""
    ans = x + coef[0]
    for i in range(N - 1):
        ans = ans * x + coef[i + 1]
    return ans


def cephes_erf(x):
    """Error function"""
    two_sqrtpi = 1.128379167095512574
    sum_val = x
    term = x
    xsqr = x * x
    j = 1
    
    if abs(x) > 2.2:
        return 1.0 - cephes_erfc(x)
    
    while True:
        term *= xsqr / j
        sum_val -= term / (2 * j + 1)
        j += 1
        term *= xsqr / j
        sum_val += term / (2 * j + 1)
        j += 1
        
        if not (abs(term) / sum_val > rel_error):
            break
    
    return two_sqrtpi * sum_val


def cephes_erfc(x):
    """Complementary error function"""
    one_sqrtpi = 0.564189583547756287
    
    if abs(x) < 2.2:
        return 1.0 - cephes_erf(x)
    if x < 0:
        return 2.0 - cephes_erfc(-x)
    
    a = 1
    b = x
    c = x
    d = x * x + 0.5
    q2 = b / d
    n = 1.0
    
    while True:
        t = a * n + b * x
        a = b
        b = t
        t = c * n + d * x
        c = d
        d = t
        n += 0.5
        q1 = q2
        q2 = b / d
        
        if not (abs(q1 - q2) / q2 > rel_error):
            break
    
    return one_sqrtpi * math.exp(-x * x) * q2


def cephes_normal(x):
    """Normal distribution"""
    sqrt2 = 1.414213562373095048801688724209698078569672
    
    if x > 0:
        arg = x / sqrt2
        result = 0.5 * (1 + math.erf(arg))
    else:
        arg = -x / sqrt2
        result = 0.5 * (1 - math.erf(arg))
    
    return result
