def float_gcd(nums, rtol=1e-05, atol=1e-08):
    gcd = nums[0]
    for num in nums[1:]:
        tol = rtol*min(abs(gcd), abs(num)) + atol
        while abs(num) > tol:
            gcd, num = num, gcd % num
    return gcd
