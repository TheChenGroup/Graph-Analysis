def diff_(config1_, config2_):
    """
    判断两个组态的轨道差距
    :param config1_:
    :param config2_:
    :return: 所差轨道数目，1中独有的轨道，2中独有的轨道
    """
    config1_c = config1_.copy()
    config2_c = config2_.copy()
    for i in config1_:
        if i in config2_:
            config1_c.remove(i)
            config2_c.remove(i)
    return len(config2_c), config1_c, config2_c


def O_1(orb1, orb2, hcore):
    """
    获得单电子算符O1的本征值
    :param orb1: 轨道的列表，为（i，alpha）的元组
    :param orb2:
    :param hcore:
    :return:
    """
    count, lst1, lst2 = diff_(orb1, orb2)
    if count > 1:
        return 0
    elif count == 1:
        phi1 = lst1[0][0]
        phi2 = lst2[0][0]
        if phi1 < phi2:
            phi1, phi2 = phi2, phi1
        if (phi1, phi2) in hcore:
            return hcore[(phi1, phi2)]
        else:
            return 0

    else:
        res = 0
        for n in orb1:
            phi = n[0]
            res += hcore[(phi, phi)]
        return res


def O_2(orb1, orb2, eri):
    """
    得到双电子算符O2的本征值
    :param orb1: 轨道的列表，为（i，alpha）的元组
    :param orb2:
    :param eri:
    :return:
    """
    count, lst1, lst2 = diff_(orb1, orb2)
    res = 0
    if count > 2:
        return res
    elif count == 2:
        m, n = lst1[0], lst1[1]
        p, q = lst2[0], lst2[1]
        res += (get_eri(m, p, n, q, eri) - get_eri(m, q, n, p, eri))
        return res
    elif count == 1:
        m = lst1[0]
        p = lst2[0]
        for n in orb1:
            if n not in lst1:
                res += (get_eri(m, p, n, n, eri) - get_eri(m, n, n, p, eri))
        return res
    else:
        for i in orb1:
            for j in orb2:
                res += 0.5 * (get_eri(i, i, j, j, eri) - get_eri(i, j, j, i, eri))
        return res


def get_eri(phi1, phi2, phi3, phi4, eri):
    """

    得到双电子积分的值

    :param phi1: 为两个组态中不一样的分子轨道,用元组的形式表示
    :param phi2:
    :param phi3:
    :param phi4:
    :param eri:
    :return:
    """
    i, j, k, l = phi1[0], phi2[0], phi3[0], phi4[0]

    alpha1, beta1 = phi1[1], phi2[1]
    alpha2, beta2 = phi3[1], phi4[1]
    if alpha1 != beta1 or alpha2 != beta2:
        return 0
    else:
        if max(i, j, k, l) == k or max(i, j, k, l) == l:
            i, j, k, l = k, l, i, j
        if i < j:
            i, j = j, i
        if k < l:
            k, l = l, k
        if (i, j, k, l) in eri:
            return eri[(i, j, k, l)]
        else:
            return 0


def H(a, b, hcore, eri):
    """
    得到跃迁矩阵元的值
    :param a: 轨道的列表，为（i，alpha）的元组
    :param b:
    :param mf:
    :param hcore:
    :param eri:
    :return:
    """
    O1 = O_1(a, b, hcore)
    O2 = O_2(a, b, eri)

    # return O_1(a, b, hcore) + O_2(a, b, hcore, eri) + mf.energy_nuc()
    return O1 + O2
