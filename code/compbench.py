import time

tic = time.time()

N = 100
result = 0
for i in range(N):
    for j in range(N):
        if i > 0 and i % 3 == 0:
            result += 1
print 'Result: %d\n%ss Elapsed' % (result, str(time.time() - tic))
