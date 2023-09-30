from chempy import Equation
import sys

def main() -> None:
    if len(sys.argv) != 2:
        print('Please provide one argument in the form "A + B -> C".')
        return
    
    equation_str = sys.argv[1]
    try:
        equation = Equation.parse_from_string(equation_str)
        equation.balance()
    except Exception as e:
        print(e)
        return
    
    print(equation)


if __name__ == '__main__':
    main()
