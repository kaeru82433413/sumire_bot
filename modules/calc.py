from fractions import Fraction
from operator import add, sub, mul, truediv, pow
import re

UNITS = {"tick": Fraction("0.05"), "sec": 1, "min": 60, "hour": 60*60, "day": 60*60*24, "st": 64, "lc": 3456, "chunk": 16**2, "unit": 15**2, "star": 87115000, "k": 1000, "m":1000_000, "g":1000_000_000, "%": Fraction("0.01")}

class Value:
  def __init__(self, raw, reverse=False):
    self.minus = False
    if isinstance(raw, Fraction):
      self.value = raw
      self.minus = self.minus ^ reverse
    else:
      for i, t in enumerate(raw):
        if t in "+-":
          if t == "-":
            self.minus = not self.minus
        else:
          break
      if "(" in raw:
        self.value = Bracket(raw[i+1:-1])
      else:
        for unit in sorted(UNITS, key=len, reverse=True):
          if raw.endswith(unit):
            self.value = Fraction(raw[i:-len(unit)]) * UNITS[unit]
            break
        else:
          self.value = Fraction(raw[i:])

  def get(self, absolute=False):
    return ((self.minus * (not absolute))*-2+1) * (self.value if isinstance(self.value, Fraction) else self.value.calc(True))

  def __repr__(self):
    return f"{self.minus} {self.value}"

class Bracket:
  def __init__(self, text):
#    if not re.fullmatch(fr'(\(?[\+\-]?)*\d(,?\d)*(\.\d+)?({"|".join(UNITS)})?\)*([\+\-\*/\^](\(?[\+\-]?)*\d(,?\d)*(\.\d+)?({"|".join(UNITS)})?\)*)*', text):
    if not re.fullmatch(fr'( *\(? *[\+\-]?)*\d(,?\d)*(\.\d+)?({"|".join(UNITS)})?( *\))*( *[\+\-\*/\^]( *\(? *[\+\-]?)*\d(,?\d)*(\.\d+)?({"|".join(UNITS)})?( *\))*)* *', text):
      raise TypeError("数式のフォーマットが正しくありません")
    text = text.replace(" ", "").replace(",", "")
    brackets = 0
    for t in text:
      if t == "(":
        brackets += 1
      elif t == ")":
        brackets -= 1
        if brackets < 0:
          raise TypeError("括弧の数が一致しません")
    if brackets > 0:
      raise TypeError("括弧の数が一致しません")

    self.values = []
    self.operators = []
    
    value = ""
    for t in text:
      if brackets == 0:
        if t == "(":
          brackets += 1
          value += t
        elif t in "+-*/^" and value and value[-1] not in "+-":
          self.values.append(Value(value))
          value = ""
          self.operators.append({"+": add, "-": sub, "*": mul, "/": truediv, "^": pow}[t])
        else:
          value += t
      else:
        if t == "(":
          brackets += 1
        elif t == ")":
          brackets -= 1
        value += t
    self.values.append(Value(value))

  def calc(self, fraction=False):
    for i, operator in reversed(list(enumerate(self.operators))):
      if operator == pow:
        if self.values[i].get(absolute=True)<0 and self.values[i+1].value%1:
          raise ValueError("基数が負の数かつ指数が小数のべき乗は計算できません")
        self.values[i] = Value(Fraction(pow(self.values[i].get(absolute=True), self.values[i+1].get())), self.values[i].minus)
        del self.values[i+1], self.operators[i]
    i = 0
    while i < len(self.operators):
      if self.operators[i] in (mul, truediv):
        self.values[i] = Value(self.operators[i](*map(Value.get, self.values[i:i+2])))
        del self.values[i+1], self.operators[i]
      else:
        i += 1
    i = 0
    while i < len(self.operators):
      if self.operators[i] in (add, sub):
        self.values[i] = Value(self.operators[i](*map(Value.get, self.values[i:i+2])))
        del self.values[i+1], self.operators[i]
      else:
        i += 1
    result = self.values[0].get()
    if fraction:
      return result
    else:
      if result.denominator == 1:
        return result.numerator
      else:
        return float(result)
  
  def __str__(self):
    return f"{self.values} {self.operators}"

def expression(allow_decimal=False):
  def converter(text):
    value = Bracket(text).calc()
    if not allow_decimal and isinstance(value, float):
      raise ValueError
    return value
  return converter

if __name__ == "__main__":
  try:
    expr = Bracket(input())
  except TypeError as e:
    print(e)
    exit()
  try:
    print(expr.calc())
  except ValueError as e:
    print(e) 
  except ZeroDivisionError:
    print("ゼロ除算はできません")
