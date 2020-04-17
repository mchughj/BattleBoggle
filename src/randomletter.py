
import numpy as np

f = [
    0.08167,  # a	
    0.01492,  # b	
    0.02202,  # c	
    0.04253,  # d	
    0.12248,  # e	
    0.02228,  # f	
    0.02015,  # g	
    0.06094,  # h	
    0.06966,  # i	
    0.00153,  # j	
    0.01292,  # k	
    0.04025,  # l
    0.02406,  # m
    0.06749,  # n
    0.07507,  # o
    0.01929,  # p
    0.00095,  # q
    0.05987,  # r
    0.06327,  # s
    0.09356,  # t
    0.02758,  # u
    0.00978,  # v
    0.02560,  # w
    0.00150,  # x
    0.01994,  # y
    0.00070,  # z
]

# Normalize a numpy array as probabilities that sum to 1.
probabilities = np.array(f, dtype=np.float64)
probabilities /= probabilities.sum().astype(np.float64)

# Choice of letters
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def randomLetter():
    return np.random.choice(a=list(letters), p=probabilities)
