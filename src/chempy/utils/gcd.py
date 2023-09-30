import numpy as np
import numpy.typing as npt


def float_gcd(nums: npt.NDArray[np.float_], rtol=1e-05, atol=1e-08) -> float:
    gcd = nums[0]
    for num in nums[1:]:
        tol = rtol*min(abs(gcd), abs(num)) + atol
        while abs(num) > tol:
            gcd, num = num, gcd % num
    return gcd
