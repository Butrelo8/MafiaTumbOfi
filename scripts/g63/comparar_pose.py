import json, math
a = json.load(open('/mnt/e/tmp/mto-live-catchup/pose-blend1.json'))
b = json.load(open('/mnt/e/tmp/mto-g63-nuevo/pose-g63-volcado.json'))
def mul(M, p): return [sum(M[i][j] * (p + [1])[j] for j in range(4)) for i in range(3)]
for q in a['rigs']:
    ra, rb = a['rigs'][q], b['rigs'][q]
    print(q, 'cabeza viejo', ra['cabeza'], 'nuevo', rb['cabeza'], 'mundo trans viejo', [round(ra['mundo'][i][3], 3) for i in range(3)], 'nuevo', [round(rb['mundo'][i][3], 3) for i in range(3)])
    d = []
    for n, A in ra['huesos'].items():
        B = rb['huesos'][n]
        pa = mul(ra['mundo'], [A[0][3], A[1][3], A[2][3]]); pb = mul(rb['mundo'], [B[0][3], B[1][3], B[2][3]])
        d.append((math.dist([pa[0], pa[1], pa[2] - 0.28], pb), n))
    d.sort(reverse=True)
    print('   huesos en el mundo: dif max %.4f m (%s), mediana %.4f' % (d[0][0], d[0][1], d[len(d)//2][0]))
