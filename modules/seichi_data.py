ACHIEVEMENTS = {
    (1, 1): (9001, 'とある始まりの日'), (2, 3): (9006, 'とあるお豆の絨毯爆撃の日'), (2, 11): (9007, '建国記念日'), (2, 14): (9008, 'とあるカカオまみれの日'),
    (3, 3): (9010, 'とある女の子の日'), (3, 14): (9011, '燃え尽きたカカオの日'), (3, 20): (9012, '春分の日'), (4, 1): (9014, 'とある嘘の日'), (4, 15): (9015, 'とある良い子の日'), (4, 22): (9016, 'とある掃除デー'),
    (5, 5): (9019, '端午の節句'), (5, 14): (9020, '母の日'), (6, 12): (9022, 'とある日記の日'), (6, 17): (9023, '父の日'), (6, 29): (9024, 'とある生誕の日'),
    (7, 7): (9026, '七夕'), (7, 17): (9027, 'とある東京の日'), (7, 29): (9028, 'とある肉の日'), (8, 7): (9030, 'とあるバナナの日'), (8, 16): (9031, 'とあるJDの日'), (8, 29): (9032, 'とある焼肉の日'),
    (9, 2): (9034, 'とあるくじの日'), (9, 12): (9035, 'とあるマラソンの日'), (9, 29): (9036, 'とあるふぐの日'),
    (12, 25): (9002, 'とある聖夜の日'), (12, 31): (9003, 'とある終わりの日')
}

BREAK_LEVEL = [
    0, 15, 49, 106, 198, 333, 705, 1265, 2105, 3347, #1-10
    4589, 5831, 7073, 8315, 9557, 11047, 12835, 14980, 17554, 20642, #11-20
    24347, 28793, 34128, 40530, 48212, 57430, 68491, 81764, 97691, 116803, #21-30
    135915, 155027, 174139, 193251, 212363, 235297, 262817, 295841, 335469, 383022, #31-40
    434379, 489844, 549746, 614440, 684309, 759767, 841261, 929274, 1024328, 1126986, #41-50
    1250000, 1375000, 1500000, 1625000, 1750000, 1875000, 2000000, 2125000, 2250000, 2375000, #51-60
    2550000, 2725000, 2900000, 3075000, 3250000, 3425000, 3600000, 3775000, 3950000, 4125000, #61-70
    4345000, 4565000, 4785000, 5005000, 5225000, 5445000, 5665000, 5885000, 6105000, 6325000, #71-80
    6605000, 6885000, 7165000, 7445000, 7725000, 8005000, 8285000, 8565000, 8845000, 9125000, #81-90
    9485000, 9845000, 10205000, 10565000, 10925000, 11285000, 11645000, 12005000, 12365000, 13165000, #91-100
    13615000, 14065000, 14515000, 14965000, 15415000, 15865000, 16315000, 16765000, 17215000, 17665000, #101-110
    18155000, 18645000, 19135000, 19625000, 20115000, 20605000, 21095000, 21585000, 22075000, 22565000, #111-120
    23105000, 23645000, 24185000, 24725000, 25265000, 25805000, 26345000, 26885000, 27425000, 27965000, #121-130
    28555000, 29145000, 29735000, 30325000, 30915000, 31505000, 32095000, 32685000, 33275000, 33865000, #131-140
    34525000, 35185000, 35845000, 36505000, 37165000, 37825000, 38485000, 39145000, 39805000, 40465000, #141-150
    41205000, 41945000, 42685000, 43425000, 44165000, 44905000, 45645000, 46385000, 47125000, 47865000, #151-160
    48685000, 49505000, 50325000, 51145000, 51965000, 52785000, 53605000, 54425000, 55245000, 56065000, #161-170
    56985000, 57905000, 58825000, 59745000, 60665000, 61585000, 62505000, 63425000, 64345000, 65265000, #171-180
    66265000, 67265000, 68265000, 69265000, 70265000, 71265000, 72265000, 73265000, 74265000, 75265000, #181-190
    76415000, 77565000, 78715000, 79865000, 81015000, 82165000, 83315000, 84465000, 85615000, 87115000] #191-200

BUILD_LEVEL = [
    0, 50, 100, 200, 300,450, 600, 900, 1200, 1600, #1-10
    2000, 2500, 3000, 3600, 4300,5100, 6000, 7000, 8200, 9400, #11-20
    10800, 12200, 13800, 15400, 17200,19000, 21000, 23000, 25250, 27500, #21-30
    30000, 32500, 35500, 38500, 42000,45500, 49500, 54000, 59000, 64000, #31-40
    70000, 76000, 83000, 90000, 98000,106000, 115000, 124000, 133000, 143000, #41-50
    153000, 163000, 174000, 185000, 196000,208000, 220000, 232000, 245000, 258000, #51-60
    271000, 285000, 299000, 313000, 328000,343000, 358000, 374000, 390000, 406000, #61-70
    423000, 440000, 457000, 475000, 493000,511000, 530000, 549000, 568000, 588000, #71-80
    608000, 628000, 648000, 668000, 688000,708000, 728000, 748000, 768000, 788000, #81-90
    808000, 828000, 848000, 868000, 888000,908000, 928000, 948000, 968000, 1000000] #91-100

MANA = [ #使う予定はないけどメモ程度に
    0, 0, 0, 0, 0, 0, 0, 0, 0, 100, #1-10
    110, 120, 130, 140, 150, 160, 170, 180, 190, 200, #11-20
    212, 224, 236, 248, 260, 272, 284, 296, 308, 320, #21-30
    336, 352, 368, 384, 400, 416, 432, 448, 464, 480, #31-40
    504, 528, 552, 576, 600, 624, 648, 672, 696, 720, #41-50
    760, 800, 840, 880, 920, 960, 1000, 1040, 1080, 1120, #51-60
    1192, 1264, 1336, 1408, 1480, 1552, 1624, 1696, 1768, 1840, #61-70
    1976, 2112, 2248, 2384, 2520, 2656, 2792, 2928, 3064, 3200, #71-80
    3464, 3728, 3992, 4256, 4520, 4784, 5048, 5312, 5576, 5840, #81-90
    6360, 6880, 7400, 7920, 8440, 8960, 9480, 10000, 10520, 11040, #91-100
    12072, 13104, 14136, 15168, 16200, 17232, 18264, 19296, 20328, 21360, #101-110
    23416, 25472, 27528, 29584, 31640, 33696, 35752, 37808, 39864, 41920, #111-120
    43976, 46032, 48088, 50144, 52200, 54256, 56312, 58368, 60424, 62480, #121-130
    64536, 66592, 68648, 70704, 72760, 74816, 76872, 78928, 80984, 83040, #131-140
    85096, 87152, 89208, 91264, 93320, 95376, 97432, 99488, 101544, 103600, #141-150
    105656, 107712, 109768, 111824, 113880, 115936, 117992, 120048, 122104, 124160, #151-160
    126216, 128272, 130328, 132384, 134440, 136496, 138552, 140608, 142664, 144720, #161-170
    146776, 148832, 150888, 152944, 155000, 157056, 159112, 161168, 163224, 165280, #171-180
    167336, 169392, 171448, 173504, 175560, 177616, 179672, 181728, 183784, 185840, #181-190
    187896, 189952, 192008, 194064, 196120, 198176, 200232, 202288, 204344, 206400] #191-200