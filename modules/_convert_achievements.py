from re import compile
from collections import defaultdict


month_p = compile(r"(\d+), playedIn\(Month\.(.*)\)")
normal_day_p = compile(r'(\d+), playedOn\(Month\.(.*), (\d+), "(.*)"\)')
moveable_p = compile(r'(\d+), playedOn\(Month\.(.*), (\d+), DayOfWeek\.(.*), "(.*)"\)')
special_p = compile(r'(\d+), playedOn\((.*)\)')

pattern_list = [month_p, normal_day_p, moveable_p, special_p]
p = compile(r"  case object No_\d+ extends NormalManual\((.*)\)")

MONTHS = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
]
DAY_OF_WEEK = [
    "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
]

# https://github.com/GiganticMinecraft/SeichiAssist/blob/develop/src/main/scala/com/github/unchama/seichiassist/achievement/SeichiAchievement.scala


if __name__ == "__main__":
    row = input()
    res = [defaultdict(list) for _ in range(4)]
    while row:
        content, = p.fullmatch(row).groups()
        for i, pattern in enumerate(pattern_list):
            if pattern.fullmatch(content):
                groups = pattern.fullmatch(content).groups()

                if i == 0:
                    id_, month = groups
                    key = 1+MONTHS.index(month)
                    value = int(id_)
                elif i == 1:
                    id_, month, day, name = groups
                    key = (1+MONTHS.index(month), int(day))
                    value = (int(id_), name)
                elif i == 2:
                    id_, month, week_th, day_of_week, name = groups
                    key = (1+MONTHS.index(month), int(week_th), DAY_OF_WEEK.index(day_of_week))
                    value = (int(id_), name)
                else:
                    id_, internal_name = groups
                    if internal_name == "SpringEquinoxDay":
                        display_name = "春分の日"
                    key = internal_name
                    value = (int(id_), display_name)
                
                res[i][key].append(value)
                break
        else:
            print("Error:", row)

        row = input()
    
    for res_type in res[1:]:
        print("{", end="")
        for i, (key, value) in enumerate(sorted(res_type.items())):
            if i != 0:
                print(", ", end="")
            print(repr(key), ": ", sorted(value), sep="", end="")
        print("}")
    
