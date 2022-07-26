from functools import reduce
import struct
from const import *


def rotate_left(a, k):
    k %= 32
    high, low = divmod(a, BIT_EACH_32[32 - k])
    return high + low * BIT_EACH_32[k]


T_j = [0x79cc4519] * 16 + [0x7a879d8a] * 48
T_j_rotate_left = [rotate_left(Tj, j) for j, Tj in enumerate(T_j)]


def PUT_UINT32_BE(n):
    return [int((n >> 24) & 0xff), int((n >> 16) & 0xff), int((n >> 8) & 0xff), int(n & 0xff)]


def CF(V_i, B_i):
    W = [(B_i[ind] * BIT_EACH_32[24]) + (B_i[ind + 1] * BIT_EACH_32[16]) + (B_i[ind + 2] * BIT_EACH_32[8]) + (
        B_i[ind + 3]) for ind in range(0, 64, 4)]
    for j in range(16, 68):
        high_W3_15, low_W3_15 = divmod(W[-3], BIT_EACH_32[17])
        high_W13_7, low_W13_7 = divmod(W[-13], BIT_EACH_32[25])
        # P_1
        X = W[- 16] ^ W[- 9] ^ (high_W3_15 + low_W3_15 * BIT_EACH_32[15])
        high_P1_15, low_P1_15 = divmod(X, BIT_EACH_32[17])
        r_l_15 = high_P1_15 + low_P1_15 * BIT_EACH_32[15]
        high_P1_23, low_P1_23 = divmod(X, BIT_EACH_32[9])
        r_l_23 = high_P1_23 + low_P1_23 * BIT_EACH_32[23]
        # return X ^ (rotate_left(X, 15)) ^ (rotate_left(X, 23))
        W.append(X ^ r_l_15 ^ r_l_23 ^ (high_W13_7 + low_W13_7 * BIT_EACH_32[7]) ^ W[- 6])
        # W.append(P_1(W[- 16] ^ W[- 9] ^ (high_W3_15 + low_W3_15 * BIT_EACH_32[15])) ^ (
        #         high_W13_7 + low_W13_7 * BIT_EACH_32[7]) ^ W[- 6])
    W_1 = [W[j] ^ W[j + 4] for j in range(64)]
    A, B, C, D, E, F, G, H = V_i
    for j in range(0, 16):
        high_A12, low_A12 = divmod(A, BIT_EACH_32[20])
        r_l_12 = high_A12 + low_A12 * BIT_EACH_32[12]
        high, low = divmod((r_l_12 + E + T_j_rotate_left[j]) & 0xFFFFFFFF, BIT_EACH_32[25])
        SS1 = high + low * BIT_EACH_32[7]
        SS2 = SS1 ^ r_l_12
        # Wj = (B_i[ind] * BIT_EACH_32[24]) + (B_i[ind + 1] * BIT_EACH_32[16]) + (B_i[ind + 2] * BIT_EACH_32[8]) + (B_i[ind + 3])
        # FF
        TT1 = ((A ^ B ^ C) + D + SS2 + W_1[j]) & 0xFFFFFFFF
        # GG
        TT2 = ((E ^ F ^ G) + H + SS1 + W[j]) & 0xFFFFFFFF
        high_B9, low_B9 = divmod(B, BIT_EACH_32[23])
        high_F19, low_F19 = divmod(F, BIT_EACH_32[13])
        high, low = divmod(TT2, BIT_EACH_32[23])
        r_l_9 = high + low * BIT_EACH_32[9]
        high, low = divmod(TT2, BIT_EACH_32[15])
        r_l_17 = high + low * BIT_EACH_32[17]
        A, B, C, D, E, F, G, H = TT1, A, high_B9 + low_B9 * BIT_EACH_32[9] & 0xffffffff, C, (
                TT2 ^ r_l_9 ^ r_l_17) & 0xffffffff, E, high_F19 + low_F19 * BIT_EACH_32[19] & 0xffffffff, G
    for j in range(16, 64):
        high_A12, low_A12 = divmod(A, BIT_EACH_32[20])
        r_l_12 = high_A12 + low_A12 * BIT_EACH_32[12]
        high, low = divmod((r_l_12 + E + T_j_rotate_left[j]) & 0xFFFFFFFF, BIT_EACH_32[25])
        SS1 = high + low * BIT_EACH_32[7]
        SS2 = SS1 ^ r_l_12
        # FF
        TT1 = (((A & B) | (A & C) | (B & C)) + D + SS2 + W_1[j]) & 0xFFFFFFFF
        # GG
        TT2 = (((E & F) | ((~ E) & G)) + H + SS1 + W[j]) & 0xFFFFFFFF
        high_B9, low_B9 = divmod(B, BIT_EACH_32[23])
        high_F19, low_F19 = divmod(F, BIT_EACH_32[13])
        high, low = divmod(TT2, BIT_EACH_32[23])
        r_l_9 = high + low * BIT_EACH_32[9]
        high, low = divmod(TT2, BIT_EACH_32[15])
        r_l_17 = high + low * BIT_EACH_32[17]
        A, B, C, D, E, F, G, H = TT1, A, high_B9 + low_B9 * BIT_EACH_32[9] & 0xffffffff, C, (
                TT2 ^ r_l_9 ^ r_l_17) & 0xffffffff, E, high_F19 + low_F19 * BIT_EACH_32[19] & 0xffffffff, G
    return [A ^ V_i[0], B ^ V_i[1], C ^ V_i[2],
            D ^ V_i[3], E ^ V_i[4], F ^ V_i[5], G ^ V_i[6], H ^ V_i[7]]


# def CFs(V_i):


def digest(msg, state=(IV, 0)):
    msg = str2bytes(msg)
    cur_v, cur_len = state
    len1 = len(msg) + cur_len
    msg.append(0x80)
    reserve1 = len1 % 64 + 1
    range_end = 56 if reserve1 <= 56 else 120
    msg.extend([0] * (range_end - reserve1))
    bit_length = len1 * 8
    msg.extend(struct.pack(">Q", bit_length))
    B = (msg[i:i + 64] for i in range(0, len(msg), 64))
    y = reduce(CF, B, cur_v)
    b = bytearray()
    [b.extend(PUT_UINT32_BE(each)) for each in y]
    return bytes(b)


def str2bytes(msg: str, encoding='utf-8'):
    """字符串转换成byte数组"""
    msg_bytearray = msg.encode(encoding) if isinstance(msg, str) else msg
    return list(msg_bytearray)


def byte2str(msg, decode='utf-8'):
    """byte数组转字符串"""
    return msg.decode(decode) if isinstance(msg, (bytes, bytearray)) else msg


def hex2byte(msg):
    """16进制字符串转换成byte列表"""
    if not isinstance(msg, str):
        raise ValueError('message must be string')
    ml = len(msg)
    if (ml & 1) != 0:
        msg = '0' + msg
    return list(bytes.fromhex(msg))
