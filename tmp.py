from sympy import nsimplify

target_ratio = 0.7312
approx = nsimplify(target_ratio, tolerance=0.03, rational=True)
print(approx.numerator, approx.denominator)