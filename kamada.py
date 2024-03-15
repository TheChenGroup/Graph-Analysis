import networkx as nx
# import os

def read_input(file, num_of_config):
    with open(file, 'r') as f:
        data = f.readlines()
    i = 0
    while 1:
        if 'Excitation   ExcitLevel   Seniority    Walkers    Amplitude    Init?   Proc' in data[i].strip():
            break
        i += 1
    data_we_need = data[i + 1:i + 1 + num_of_config]
    amplitude, configs = [], []
    # configs添加第1列的数据
    # amplitude添加第5列的数据
    for line in data_we_need:
        line_split = line.split()
        configs.append(line_split[0])
        amplitude.append(float(line_split[4]))
    return amplitude, configs

def get_G(dump_name, fciout_name, num_of_con=100, tol=0):

    ci_lst, configuration_lst = read_input(fciout_name, num_of_con)
    print(fciout_name + ' read complete ')
    print('starting reading ' + dump_name)
    data = read_dump_concise(dump_name, configuration_lst)
    print(dump_name + ' read complete')
    hcore = data['H1']
    eri_dic = data['H2']

    G = nx.Graph()
    for i in range(num_of_con):
        configi = configuration_lst[i]
        configi_ = split_(configi)
        G.add_node(i, config=configi, h_ii=H(configi_, configi_, hcore, eri_dic), ci=ci_lst[i])

    for i in range(num_of_con):
        for j in range(i, num_of_con):
            if i != j:
                con_i = split_(configuration_lst[i])
                con_j = split_(configuration_lst[j])
                h_ij = H(con_i, con_j, hcore, eri_dic)
                # if h_ij != 0:
                #     print('i=',i,' j=',j,' hij=',h_ij)
                G.add_edge(i, j, h_ij=h_ij if abs(h_ij) > tol else 0, weight=1 / abs(h_ij) if h_ij else 1e3)
    return G


def kamada(G, mm=30):
    nx.draw(G,
            pos=nx.kamada_kawai_layout(G),
            node_size=[(G.nodes[node]['ci'] ** 0.7 * 300) for node in list(G.nodes)],
            # with_labels= True,
            edge_color=get_edgecolor(G, mm),
            node_color=[abs(G.nodes[node]['h_ii']) for node in list(G.nodes)],
            width=[float(abs(d['h_ij'] ** 0.4 * 3)) for (u, v, d) in G.edges(data=True)],
            cmap='copper'
            )
    return None


def split_(config):
    orb = []
    for i in range(len(config)):
        if config[i] == '1':
            orb.append((i // 2, i % 2))
    return orb


def get_edgecolor(G, mm):
    edge_color = []
    edge_elem_list = [G.edges[edge]['h_ij'] for edge in list(G.edges)]
    edgemax_p, edgemax_n = max(edge_elem_list), -min(edge_elem_list)
    edgemin_p, edgemin_n = edgemax_p, edgemax_n
    for i in range(len(edge_elem_list)):
        if edge_elem_list[i] > 0 and edge_elem_list[i] < edgemin_p:
            edgemin_p = edge_elem_list[i]
        elif edge_elem_list[i] < 0 and -edge_elem_list[i] < edgemin_n:
            edgemin_n = -edge_elem_list[i]

    fc = lambda x: x ** mm

    for i in range(len(edge_elem_list)):
        if edge_elem_list[i] == 0:
            edge_color.append((1, 1, 1, 1e-6))
        elif edge_elem_list[i] > 0:
            edge_color.append((238 / 255, 154 / 255, 0,
                               0.05 + 0.9 * (fc(edge_elem_list[i]) - fc(edgemin_p)) / (fc(edgemax_p) - fc(edgemin_p))))
            # edge_color.append((113/255,175/255,164/255,0.05+0.9*(fc(edge_elem_list[i])-fc(edgemin_p))/(fc(edgemax_p)-fc(edgemin_p))))
        else:
            edge_color.append((113 / 255, 175 / 255, 164 / 255,
                               0.05 + 0.9 * (fc(-edge_elem_list[i]) - fc(edgemin_n)) / (fc(edgemax_n) - fc(edgemin_n))))
    return edge_color



def get_all_spacial_orb(data):
    def temp_(config, spacial_orb_list):
        num_of_elec = len(config)
        for i in range(num_of_elec):
            if config[i] == '1' and i // 2 + 1 not in spacial_orb_list:
                spacial_orb_list.append(i // 2 + 1)

    spatial_orb_list = []
    for configi in data:
        temp_(configi, spatial_orb_list)
    spatial_orb_list.sort()
    print('spacial orbitals: ', spatial_orb_list)
    return spatial_orb_list


def read_dump_concise(filename, config_lst):
    orbs = get_all_spacial_orb(config_lst)
    orbs.append(0)
    finp = open(filename, 'r')

    for i in range(10):
        line = finp.readline().upper()
        if '&END' in line:
            break
    else:
        raise RuntimeError('Problematic FCIDUMP header')

    result = {}

    h1e_dic = {}
    h2e_dic = {}
    dat = finp.readline().split()
    while dat:
        i, j, k, l = [int(x) for x in dat[1:5]]
        if i in orbs and j in orbs and k in orbs and l in orbs:
            if k != 0:
                h2e_dic[(i - 1, j - 1, k - 1, l - 1)] = float(dat[0])
            elif k == 0:
                if j != 0:
                    h1e_dic[(i - 1, j - 1)] = float(dat[0])
        dat = finp.readline().split()

    result['H1'] = h1e_dic
    result['H2'] = h2e_dic

    finp.close()
    return result


def save_G(G):
    """

    :param G: nx.Graph
    :param sd: save direction
    :return:
    """
    with open('G_data.txt', 'w') as f:
        node_lst = G.nodes(data=True)
        edge_lst = G.edges(data=True)
        f.write('nodes\' data\n')
        f.write('i      configuration       h_ii      ci\n')
        for node in node_lst:
            f.write(str(node[0]) + '  ' + node[1]['config'] + '  ' + str(node[1]['h_ii']) + '  ' + str(
                node[1]['ci']) + '\n')
        f.write('&end nodes\' data\n')
        f.write('\n\n\n')
        f.write('edges\' data\n')
        f.write('i      j     h_ij     weight\n')
        for edge in edge_lst:
            f.write(str(edge[0]) + '  ' + str(edge[1]) + '    ' + str(edge[2]['h_ij']) + '   ' + str(
                edge[2]['weight']) + '\n')
        f.write('&end edges\' data\n')

        f.close()
    return None

def save_G_(dump_name,fciout_name,num_of_con = 100,tol = 0):
    ci_lst, configuration_lst = read_input(fciout_name, num_of_con)
    print(fciout_name + ' read complete ')
    print('starting reading ' + dump_name)
    data = read_dump_concise(dump_name, configuration_lst)
    print(dump_name + ' read complete')
    hcore = data['H1']
    eri_dic = data['H2']

    f = open('G_data.txt','w')

    f.write('nodes\' data\n')
    f.write('i      configuration       h_ii      ci\n')
    for i in range(num_of_con):
        configi = configuration_lst[i]
        configi_ = split_(configi)
        f.write(str(i) + '  ' + configi + '  ' + str(H(configi_, configi_, hcore, eri_dic)) + '  ' + str(
            ci_lst[i]) + '\n')

    f.write('&end nodes\' data\n')
    f.write('\n\n\n')
    f.write('edges\' data\n')
    f.write('i      j     h_ij     weight\n')
    for i in range(num_of_con):
        for j in range(i, num_of_con):
            if i != j:

                con_i = split_(configuration_lst[i])
                con_j = split_(configuration_lst[j])
                h_ij = H(con_i, con_j, hcore, eri_dic)
                f.write(str(i) + '  ' + str(j) + '    ' + str(h_ij if abs(h_ij) > tol else 0) + '   ' + str(
                    1 / abs(h_ij) if h_ij else 1e3) + '\n')
                # if h_ij != 0:
                #     print('i=',i,' j=',j,' hij=',h_ij)

    f.write('&end edges\' data\n')
    f.close()
    return None

def read_Gdata():
    G = nx.Graph()
    with open('G_data.txt', 'r') as f:
        line = f.readline()
        if line == 'nodes\' data\n':
            f.readline()
            line = f.readline()
            while line != '&end nodes\' data\n':
                i, configuration, h_ii, ci = line.split()
                G.add_node(int(i), config=configuration, h_ii=float(h_ii), ci=float(ci))
                line = f.readline()
        else:
            raise ValueError('Wrong G_data file !!!')
        while line != 'i      j     h_ij     weight\n':
            line = f.readline()
        line = f.readline()
        while line != '&end edges\' data\n':
            # print(line.split())
            i, j, h_ij, weight = line.split()
            G.add_edge(int(i), int(j), h_ij=float(h_ij), weight=float(weight))
            line = f.readline()
        f.close()
    return G

def diff_(config1_, config2_):
    config1_c = config1_.copy()
    config2_c = config2_.copy()
    for i in config1_:
        if i in config2_:
            config1_c.remove(i)
            config2_c.remove(i)
    return len(config2_c), config1_c, config2_c


def O_1(orb1, orb2, hcore):
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
    O1 = O_1(a, b, hcore)
    O2 = O_2(a, b, eri)

    # return O_1(a, b, hcore) + O_2(a, b, hcore, eri) + mf.energy_nuc()
    return O1 + O2