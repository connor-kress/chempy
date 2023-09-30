from chempy import Equation, BalancingError
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print('Please provide one argument in the form "A + B -> C".')
        return
    
    equation_str = sys.argv[1]
    try:
        equation = Equation.parse_from_string(equation_str)
        equation.balance()
    except (ValueError, BalancingError) as e:
        print(f'[ERROR] {e}')
        sys.exit(1)
    else:
        print(equation)
        sys.exit(0)


if __name__ == '__main__':
    main()
