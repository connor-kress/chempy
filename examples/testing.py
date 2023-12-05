from chempy import Equation, Compound

print(Equation('2H -> 3O').extended(Equation('O -> 4Fe')))
print(Equation('2H -> 3O'))
print(Compound(['H20', 'O2', 'CO2'])[2])
