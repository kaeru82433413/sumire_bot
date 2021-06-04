from fractions import Fraction
import re
import operator as op
import math
from copy import copy

UNITS = {"tick": Fraction("0.05"), "sec": 1, "min": 60, "hour": 60*60, "day": 60*60*24,
                 "st": 64, "lc": 3456, "chunk": 16**2, "unit": 15**2, "star": 87115000,
                 "k": 1000, "m":1000_000, "g":1000_000_000, "%": Fraction("0.01"),
                 "pi": Fraction(math.pi), "radian": Fraction(math.pi/180), "degree": Fraction(180/math.pi)}
RE_UNITS = "|".join(sorted(UNITS, key=len, reverse=True))
RE_NUMBER = fr'\d(\,?\d)*(\.\d+)?(e[\+\-]?\d+)?'
FUNCTIONS = {"abs": abs, "floor": math.floor, "ceil": math.ceil, "sin": math.sin, "cos": math.cos, "tan": math.tan, "radian": math.radians, "degree": math.degrees}
RE_FUNCTIONS = "|".join(sorted(FUNCTIONS, key=len, reverse=True))
RE_BRACKET = fr'\s*((\s*[\+\-])?((\s*({RE_FUNCTIONS}))?\s*\()?)*(\s*[\+\-])*\s*{RE_NUMBER}({RE_UNITS})?(\s*\)({RE_UNITS})?)*'
RE_EXPRESSION = fr'{RE_BRACKET}(\s*[\+\-\*/\^]{RE_BRACKET})*\s*'
OPERATORS = {"+": op.iadd, "-": op.isub, "*": op.imul, "/": op.itruediv, "^": op.ipow}

class UnionFind(list):
    def __init__(self, n):
        super().__init__(range(n))
    
    def union(self, a, b):
        if not a < b:
            a, b = b, a
        self[self[b]] = self[a]
    
    def __getitem__(self, index):
        chs = set()
        while index != super().__getitem__(index):
            chs.add(index)
            index = super().__getitem__(index)
        for ch in chs:
            self[ch] = index
        return index

class Value:
    def __init__(self, value):
        sign = re.match(r"[+-]*", value)
        self.sign = 1
        if sign.group().count("-")%2:
            self.sign *= -1
        value = value[sign.end():]

        unit = re.search(fr"({RE_UNITS})?$", value)
        value = value[:unit.start()]
        unit = UNITS.get(unit.group(), 1)

        if re.match(fr"({RE_FUNCTIONS})?\(", value):
            function = re.match(fr"({RE_FUNCTIONS})?", value)
            value = value[function.end()+1:-1]
            self.value = Bracket(value, function=FUNCTIONS.get(function.group()), unit=unit)
        else:
            self.value = Fraction(value)
            self.value *= unit
    
    def get(self):
        if isinstance(self.value, Bracket):
            return self.value.calc(True) * self.sign
        else:
            return self.value * self.sign
    
    def __iadd__(self, other):
        self.value += other.get() * self.sign
    
    def __isub__(self, other):
        self.value -= other.get() * self.sign

    def __imul__(self, other):
        self.value *= other.get()

    def __itruediv__(self, other):
        self.value /= other.get()
    
    def __ipow__(self, other):
        if isinstance(self.value, Bracket):
            self.value = self.value.calc()
        other = other.get()
        if self.value < 0 and other.denominator!=1:
            raise ValueError("基数が負の数かつ指数が小数の計算はできません")
        self.value **= other

    def __repr__(self):
        return f"<value={self.value} sign={self.sign}>"

class Bracket:
    def __init__(self, value, function=None, unit=1):
        value = value.lower()
        if not re.fullmatch(RE_EXPRESSION, value):
            raise TypeError("数式のフォーマットが正しくありません")
        brackets = 0
        for t in value:
            if t == "(":
                brackets += 1
            elif t == ")":
                brackets -= 1
                if brackets < 0:
                    raise TypeError("括弧の配置が正しくありません")
        if brackets > 0:
            raise TypeError("括弧の配置が正しくありません")
        value = re.sub(r"[\s\,]", "", value)

        self.function = function
        self.unit = unit
        self.values = []
        self.operators = []

        brackets = 0
        while not re.fullmatch(RE_BRACKET, value):
            number = re.match(rf"[\+\-]*{RE_NUMBER}({RE_UNITS})?", value)
            if number:
                self.values.append(Value(number.group()))
                self.operators.append(OPERATORS.get(value[number.end()]))
                value = value[number.end()+1:]
            else:
                for i, t in enumerate(value):
                    if t in OPERATORS:
                        if brackets == 0 and re.match(fr"[\+\-]*({RE_FUNCTIONS})?\(", value[:i]):
                            self.values.append(Value(value[:i]))
                            self.operators.append(OPERATORS.get(t))
                            value = value[i+1:]
                            break
                    elif t == "(":
                        brackets += 1
                    elif t == ")":
                        brackets -= 1
                else:
                    break
        self.values.append(Value(value))


    def calc(self, fraction=False):
        values = list(map(copy, self.values))
        for i, value in enumerate(values):
            if isinstance(value.value, Bracket):
                value.value = value.value.calc()
        operand = UnionFind(len(values))

        for i, operator in reversed(list(enumerate(self.operators))): # べき乗は右結合なのでreversed
            if operator is op.ipow:
                operator(values[operand[i]], values[operand[i+1]])
                operand.union(i, i+1)

        for i, operator in enumerate(self.operators):
            if operator in (op.imul, op.itruediv):
                operator(values[operand[i]], values[operand[i+1]])
                operand.union(i, i+1)

        for i, operator in enumerate(self.operators):
            if operator in (op.iadd, op.isub):
                operator(values[operand[i]], values[operand[i+1]])
                operand.union(i, i+1)

        value = values[0].get()
        if self.function is not None:
            value = self.function(value)
        if not isinstance(value, Fraction):
            value = Fraction(value)
        value *= self.unit
        
        if fraction: # 戻り値がFractionであることを要求されていれば
            return value
        else:
            if value.denominator == 1: # 整数ならint
                return value.numerator
            else: # 整数にできないのであればfloat
                return float(value)
    
    def __repr__(self):
        return f"<values={self.values} operators={self.operators} function={self.function}>"

def expression(result_type="int"):
    if result_type not in ("natural", "int", "float", "fraction"):
        raise ValueError

    def converter(value):
        result = Bracket(value.replace(r"\*", "*")).calc(fraction=(result_type=="fraction"))

        if result_type == "fraction":
            return result
        elif result_type in ("natural", "int") and not isinstance(result, int):
            raise ValueError
        if result_type == "natural" and result < 1:
            raise ValueError

        return result
    return converter

if __name__ == "__main__":
    try:
        bracket = Bracket(input())
        print(bracket.calc())
    except (TypeError, ValueError) as e:
        print(e)
    except ZeroDivisionError:
        print("ゼロ除算はできません")
