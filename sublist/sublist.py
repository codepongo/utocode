#coding:utf-8
'''
一个序列啊list=[a1,a2,....,an]
求一个子序列
要求1：子序列元素在原序列中不相邻
要求2：子序列之和最大
'''
import random
debug = False
def create_list(length):
    return create_list_with_limit(length, -length/2, length/2)

def create_list_with_limit(length, minimum, maximum):
    l = []
    i = 0
    for i in range(0, length):
        l.append(random.randint(minimum, maximum))
    if debug:
        print l 
    return l


def get_sub_with_nonadjacent(l):
    #get_count_of_sub_lists
    count_of_sub_list = 2 ** len(l)
    if debug:
        print 'the count of sub list is %d' % (count_of_sub_list)
    max_sum = 0
    for i in range(0, count_of_sub_list):
        #every bit expresses the state of the list item.
        #1 means the list item is belong the sub item or 0 means it not belong
        b = bin(i)[2:]
        current_bit = 0
        ajacent = False
        for current_bit in range(1, len(b)):
            if b[current_bit] == '1' and b[current_bit-1] == b[current_bit]:
                ajacent = True
                break
        if not ajacent:
            sum = 0
            for p in range(0, len(b)):
                if b[p] == '0':
                    continue
                sum += l[p]
            if debug:
                print 'the nonadjacent sub list is %s%s and the total of items is %d' % ('0' * (len(l) - len(b)),b,sum)
            if sum > max_sum:
                max_sum = sum
    return max_sum

if __name__ == '__main__':
    debug = True
    print get_sub_with_nonadjacent(create_list(3))
