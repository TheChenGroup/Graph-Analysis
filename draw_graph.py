import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from kamada import *

"""
wd为文件夹路径,该路径下有FCIDUMP文件和neci输出文件
作图生成的pdf文件和保存的图G数据也都保存在该路径下
"""
wd = '/Users/sunlei/Desktop/可用的脚本/Graph_github/example'
os.chdir(wd)

# 图的大小，如果点重合看不清可以将图调大
plt.figure(figsize=(10, 8))

"""
进行作图，kamada函数运行完后作图完毕,只要 plt.show() 即可输出图像,或是用 Pdfpages 保存图像

G 为 networkx.Graph数据类型
    
    前两个参数分别为 FCIDUMP文件 和 neci输出文件 的文件名
    
    参数
    :param num_of_con 画入图中的组态数目，默认为100
    :param tol 截断，跃迁矩阵元小于该值的边将不被画入图中，默认不截断
    :param mm 控制边的透明程度，该值越大，透明程度变化越快（mm越大，显眼的边越少）
"""
# FCIDUMP 文件由 Pyscf生成
# neci输出文件中第1列，第5列分别为组态、对应的ci系数，是作图需要的数据，
# 若输出文件有不同的格式可在 kamada.py read_input()中进行修改
G = get_G('FCIDUMP', 'fciqmc.out', num_of_con=100, tol=0)

kamada(G, mm=30)

# 选择 保存pdf文件的路径 和 pdf文件的名称

with PdfPages(wd + "/test.pdf") as pdf:
    pdf.savefig()
    plt.close()

# 保存图G的数据，sd即为保存数据的路径，存为'G_data.txt'
save_G(G)

"""
如果保存过图G的数据，可以从 G_data.txt 生成图类型（）
将上文中
G = get_G('FCIDUMP', 'fciqmc.out', num_of_con=100, tol=0)
用下面注释的两行代码替代即可
"""

# os.chdir(cwd)
# G = read_Gdata('test_data')
