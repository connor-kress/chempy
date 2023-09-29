from data.elements import ATOMIC_NUMS
from scipy.linalg import null_space
from collections import Counter
from itertools import chain
import numpy as np
import string
import sys

ELEMENTS = ATOMIC_NUMS.keys()
LEFT_DELS = ['(', '[', '{']
RIGHT_DELS = [')', ']', '}']
VALID_CHARS = list(string.ascii_letters + string.digits) + LEFT_DELS + RIGHT_DELS


def get_vector_dict():
    vectors = {}
    for symbol, num in ATOMIC_NUMS.items():
        vec = np.zeros(len(ELEMENTS), dtype=int)
        vec[num-1] = True
        vectors[symbol] = vec
    return vectors


def parse_to_fragments(compound: str) -> list[str | int]:
    frags = []
    num_str = ''
    lower = ''
    for c in reversed(compound):
        if c.isdigit():
            if lower:
                raise ValueError('Invalid input syntax')
            num_str = c + num_str
            continue
        if num_str:
            frags.insert(0, int(num_str))
            num_str = ''
        if c in LEFT_DELS + RIGHT_DELS:
            if lower:
                raise ValueError('Invalid input syntax')
            frags.insert(0, c)
        elif c.islower():
            lower = c + lower
        elif lower:
            frags.insert(0, c + lower)
            lower = ''
        else:
            frags.insert(0, c)
    if num_str or lower:
        raise ValueError('Invalid input syntax')
    return frags


def parse_from_fragments(frags: list[str | int]) -> list[str]:
    def get_closing_index(start: int, l_del: str) -> int:
        r_del = RIGHT_DELS[LEFT_DELS.index(l_del)]
        count = 0
        # print(f'searching for "{r_del}"')
        for i in range(start, len(frags)):
            frag = frags[i]
            if frag == l_del:
                count += 1
            elif frag == r_del:
                if count == 0:
                    # print(f'closing "{r_del}" found at {i=}')
                    return i
                count -= 1
        raise ValueError(f'"{l_del}" opened at i={start-1} was never closed.')

    elements = []
    prev_frag = None
    i = 0
    # print(f'Starting {frags}')
    while i < len(frags):
        frag = frags[i]
        if frag in LEFT_DELS:
            close_idx = get_closing_index(i+1, frag)
            inside = parse_from_fragments(frags[i+1:close_idx])
            if (close_idx + 1 <= len(frags) - 1
                and isinstance(frags[close_idx+1], int)):

                elements.extend(inside * frags[close_idx+1])
                i = close_idx + 2
            else:
                elements.extend(inside)
                i = close_idx + 1
            prev_frag = None
            continue
        if frag in RIGHT_DELS:
            raise ValueError('Invalid equation syntax (delimeters).')
        if isinstance(frag, str):  # element
            elements.append(frag)
            prev_frag = frag
        else:  # number after element
            if prev_frag is None:
                raise ValueError('Invalid equation syntax.')
            elements.extend([prev_frag] * (frag-1))
            prev_frag = None
        i += 1
    # print(f'Returning {elements}')
    return elements


def compound_to_elements(compound: str) -> Counter[str]:
    compound = compound.replace(' ', '')
    if not all(c in VALID_CHARS for c in compound):
        raise ValueError('Invalid character found in input string.')
    if sum(c in LEFT_DELS for c in compound) != sum(c in RIGHT_DELS for c in compound):
        raise ValueError('Unequal left and right delimiters.')
    
    fragments = parse_to_fragments(compound)
    elements = parse_from_fragments(fragments)

    return Counter(elements)


def float_gcd(nums, rtol=1e-05, atol=1e-08):
    gcd = nums[0]
    for num in nums[1:]:
        tol = rtol*min(abs(gcd), abs(num)) + atol
        while abs(num) > tol:
            gcd, num = num, gcd % num
    return gcd


def solve(system):
    results = null_space(system).T

    for result in results:
        if np.any(np.isclose(result, 0)):
            continue
        signs = result / np.abs(result)
        if np.allclose(signs, 1) or np.allclose(signs, -1):
            ratios = result * signs[0]
            break
    else:
        raise Exception('No solution found.')
    
    solution = ratios / float_gcd(ratios)
    
    if not np.allclose(solution, np.round(solution)):
        raise ValueError(f'Unknown error. Found solution {solution}.')
    
    return np.round(solution).astype(int)


def get_equation_with_coefs(reactant_strs: list[str], product_strs: list[str], coefs: list[int]) -> str:
    result_str = ''
    for i in range(len(reactant_strs)):
        coef = coefs[i]
        if i != 0:
            result_str += ' + '
        if coef == 1:
            result_str += reactant_strs[i]
        else:
            result_str += f'{coef}({reactant_strs[i]})'
    result_str += ' -> '
    for i in range(len(product_strs)):
        coef = coefs[len(reactant_strs) + i]
        if i != 0:
            result_str += ' + '
        if coef == 1:
            result_str += product_strs[i]
        else:
            result_str += f'{coef}({product_strs[i]})'
    return result_str


def get_balanced_equation(equation: str) -> str:
    if '->' in equation:
        reactants_str, products_str = equation.split('->')
    elif '→' in equation:
        reactants_str, products_str = equation.split('→')
    else:
        raise ValueError('Seperate reactants and products with "->".')

    reactant_strs = [comp.replace(' ', '') for comp in reactants_str.split('+')]
    product_strs = [comp.replace(' ', '') for comp in products_str.split('+')]

    reactant_parts = [compound_to_elements(comp_str) for comp_str in reactant_strs]
    product_parts = [compound_to_elements(comp_str) for comp_str in product_strs]
    
    for comp in chain(reactant_parts, product_parts):
        for element in comp:
            if element not in ELEMENTS:
                raise ValueError(f'"{element}" is not a valid element.')

    vector_dict = get_vector_dict()

    reactant_vecs = []
    for comp in reactant_parts:
        reactant_vec = np.zeros(len(ELEMENTS), dtype=int)
        for symbol, n in comp.items():
            reactant_vec += vector_dict[symbol] * n
        reactant_vecs.append(reactant_vec)

    product_vecs = []
    for comp in product_parts:
        product_vec = np.zeros(len(ELEMENTS), dtype=int)
        for symbol, n in comp.items():
            product_vec += vector_dict[symbol] * n
        product_vecs.append(product_vec)
    
    reactant_vecs = np.array(reactant_vecs)
    product_vecs = np.array(product_vecs)
    
    system = np.hstack((reactant_vecs.T, -product_vecs.T))
    coefs = list(solve(system))

    return get_equation_with_coefs(reactant_strs, product_strs, coefs)


def main() -> None:
    # if len(sys.argv) != 2:
    #     print('Please provide one argument in the form "A + B -> C".')
    #     return
    # equation = sys.argv[1]
    equation = 'KNO3 + C12H22O11 -> N2 + CO2 + H2O + K2CO3'
    try:
        result = get_balanced_equation(equation)
    except Exception as e:
        print(e)
        return
    print(result)


if __name__ == '__main__':
    main()
