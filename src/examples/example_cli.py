import sys


def main() -> None:
    if len(sys.argv) != 2:
        print('Please provide one argument in the form "A + B -> C".')
        return
    equation = sys.argv[1]
    try:
        result = 0  # get_balanced_equation(equation)
    except ValueError as e:
        print(e)
        return
    print(result)


if __name__ == '__main__':
    main()