import re
import codecs

version = "200604"
debug = True


class cv:
    def __init__(self, name, c, v, type):
        self.name = name
        self.c = c
        self.v = v
        self.type = type


class worker():
    cvlist = []
    vclist = []
    vvlist = []
    clist = []
    vlist = []

    def findcv(self, list, c, v, fromindex=0):
        for i in range(fromindex, len(list)):
            cv = list[i]
            if(cv.c == c and cv.v == v):
                return cv
        return None

    def findcv_c(self, list, c, fromindex=0, cyclic=False):
        for i in range(fromindex, len(list)):
            cv = list[i]
            if(cv.c == c):
                return cv

        # 循环搜索
        if cyclic:
            for i in range(0, len(list)):
                cv = list[i]
                if(cv.c == c):
                    return cv
        return None

    def findcv_v(self, list, v, fromindex=0, cyclic=False):
        for i in range(fromindex, len(list)):
            cv = list[i]
            if(cv.v == v):
                return cv
        # 循环搜索
        if cyclic:
            for i in range(0, len(list)):
                cv = list[i]
                if(cv.v == v):
                    return cv
        return None

    def read_presamp(self, filename='presamp.ini'):
        V_list = []
        C_list = []
        CV_V_list = []
        CV_C_list = []
        tag = ''
        for temp in open(filename, 'r', encoding='UTF-8').readlines():
            if (temp.find('[VOWEL]') != -1):
                tag = '[VOWEL]'
            elif (temp.find('[CONSONANT]') != -1):
                tag = '[CONSONANT]'
            elif (temp.find('[') != -1):
                tag = ''
            else:
                if(tag == '[VOWEL]'):
                    temp_list = re.split(r'[,=]+', temp)
                    V_list.append(temp_list[0])
                    CV_V_list.append(temp_list[2:-1])
                elif(tag == '[CONSONANT]'):
                    temp_list = re.split(r'[,=]+', temp)
                    if V_list.count(temp_list[0]) == 0:
                        C_list.append(temp_list[0])
                    else:
                        C_list.append(temp_list[0] + '#')
                    CV_C_list.append(temp_list[1:-1])
        l = -1
        for i in range(0, len(V_list)):
            for j in CV_V_list[i]:
                l = l + 1
                cv_now = cv(j, '', V_list[i], 'cv')
                for k in range(0, len(C_list)):
                    if j in CV_C_list[k]:
                        cv_now.c = C_list[k]
                if cv_now.c == '':
                    cv_now.c = cv_now.v
                self.cvlist.append(cv_now)
                self.clist = C_list[:]
                self.vlist = V_list[:]

        for _c in self.clist:
            for _v in self.vlist:
                vc = cv(_v + ' ' + ''.join(_c).replace('#', ''), _c, _v, 'vc')
                self.vclist.append(vc)

        for _v1 in self.vlist:
            for _v2 in self.vlist:
                if self.findcv_c(self.cvlist, _v1) != None:  # 确保VV作为VC时C部分的元音有存在纯元音
                    vv = cv(_v2 + ' ' + _v1, _v1, _v2, 'vv')
                    self.vvlist.append(vv)
                else:
                    break

        if debug:
            read_result = codecs.open("read_result.txt", "w", encoding="UTF-8")
            read_result.write("clist:\r\n")
            for _c in self.clist:
                read_result.write(_c + " ")
            read_result.write("\r\nvlist:\r\n")
            for _v in self.vlist:
                read_result.write(_v + " ")
            read_result.write("\r\ncvlist:\r\n")
            for _cv in self.cvlist:
                read_result.write(_cv.name + "=" + _cv.c +
                                  " " + _cv.v + "\r\n")
            read_result.write("\r\nvclist:\r\n")
            for _vc in self.vclist:
                read_result.write(_vc.name + "\r\n")
            read_result.write("\r\nvvlist:\r\n")
            for _vv in self.vvlist:
                read_result.write(_vv.name + "\r\n")

    def gen_CVVC(self, path='Reclist.txt', length=8, UsePlanB=True, CV_head=True, IncludeVV=True, UseUnderlineInReclist=True, otopath='oto.ini', OtoMaxOfSameCV=3, OtoMaxOfSameVC=3, preset_blank=float(1250), oto_bpm=float(130), DivideVCCV=True):
        reclist = []  # List<List<cv>> 按行收录
        vc_remained = self.vclist[:]  # 余下的VC部
        vR_remained = self.vlist[:]  # 余下的V_R

        # 如果要求包含VV，则包含VV
        if IncludeVV == True:
            vc_remained.extend(self.vvlist)

        if (not UsePlanB) and CV_head:
            headcv_remained = self.cvlist[:]  # 余下的句首CV

        notheadcv_remained = self.cvlist[:]  # 余下的句中CV

        if not UsePlanB:
            # 遍历CV部(Plan A)
            row_total = int(len(self.cvlist) / length)
            vc_count_inlastrow = len(self.cvlist) % length
            if(vc_count_inlastrow != 0):
                row_total += 1
            for i in range(0, row_total):
                row = []
                v_last = ''
                for j in range(0, length):
                    if(i * length + j == len(self.cvlist)):
                        break
                    cv_now = self.cvlist[i * length + j]
                    row.append(cv_now)
                    if j == 0:
                        if CV_head:
                            headcv_remained.remove(cv_now)  # 删除已经出现的句首CV字
                    elif notheadcv_remained.count(cv_now) > 0:
                        notheadcv_remained.remove(cv_now)  # 删除已经出现的句中CV字
                    if(vc_remained.count(self.findcv(self.vclist, cv_now.c, v_last))):
                        vc_remained.remove(self.findcv(
                            self.vclist, cv_now.c, v_last))  # 删除已经出现的VC部
                    v_last = cv_now.v
                reclist.append(row)
                # 记录句尾V的出现
                if(vR_remained.count(row[len(row) - 1].v) > 0):
                    vR_remained.remove(row[len(row) - 1].v)
        else:
            # 遍历CV部(Plan B)
            for cv_now in self.cvlist:
                row = []
                row.append(cv_now)
                row.append(cv_now)
                row.append(cv_now)
                if(vc_remained.count(self.findcv(self.vclist, cv_now.c, cv_now.v))):
                    vc_remained.remove(self.findcv(
                        self.vclist, cv_now.c, cv_now.v))  # 删除已经出现的VC部
                if(vc_remained.count(self.findcv(self.vvlist, cv_now.c, cv_now.v))):
                    vc_remained.remove(self.findcv(
                        self.vvlist, cv_now.c, cv_now.v))  # 删除已经出现的VV部
                reclist.append(row)

        # 补全VC部
        row = []  # 生成新行
        count = 0  # 该行的字数
        vc_wanted = None
        vc_wanted_next = None
        add_flag = 0  # 用于标记是否出现增字（浪费了一个VC部的机会）
        index_findcv_connective = 0  # 为寻找可接续的CV而设置的搜索指针
        # 为随意取CV时尽量平均而设置的搜索指针
        index_random_findcv_c = []
        for i in range(0, len(self.clist)):
            index_random_findcv_c.append(0)
        index_random_findcv_v = []
        for i in range(0, len(self.vlist)):
            index_random_findcv_v.append(0)

        while len(vc_remained) > 0:  # 主循环
            if vc_wanted != None and count != 0:  # 非句首且不出现增字时
                vc_remained.remove(vc_wanted)  # 取出将要写入的VC部
                if vc_wanted.type != 'vv':
                    index_findcv_connective = index_random_findcv_c[self.clist.index(
                        vc_wanted.c)]
                else:
                    index_findcv_connective = 0
            while True:  # 以CV字为单位的子循环
                # 句首或者出现增字时，需要先写入一个与前文无关的CV字
                if count == 0:  # 句首时
                    vc_wanted = vc_remained[0]  # 随便取出一个VC部
                    vc_remained.remove(vc_wanted)  # 移除
                    cv_now = None
                    if CV_head and not UsePlanB:
                        # 要求句首CV时，首先尝试写入一个以VC部的V结尾，且还未在句首出现过的CV字
                        cv_now = self.findcv_v(headcv_remained, vc_wanted.v)
                        if cv_now != None:
                            headcv_remained.remove(cv_now)  # 删除已经出现句首的CV字
                    if cv_now == None:
                        cv_now = self.findcv_v(self.cvlist, vc_wanted.v, index_random_findcv_v[self.vlist.index(
                            vc_wanted.v)], True)  # 写入一个以VC部的V结尾的CV字
                        index_random_findcv_v[self.vlist.index(
                            vc_wanted.v)] = self.cvlist.index(cv_now) + 1
                    row.append(cv_now)
                    count += 1
                elif add_flag == 1:  # 出现增字的情况
                    if count + 1 == length:  # 如果加入增字会导致超出行长度，则先行换行
                        count = 0
                        reclist.append(row)
                        # 记录句尾V的出现
                        if(vR_remained.count(row[len(row) - 1].v) > 0):
                            vR_remained.remove(row[len(row) - 1].v)
                        row = []
                    cv_now = self.findcv_v(self.cvlist, vc_wanted.v, index_random_findcv_v[self.vlist.index(
                        vc_wanted.v)], True)  # 写入一个以VC部的V结尾的CV字（此字为增字，因为其C和前一个字的V组成的VC部已经不需要）
                    if count != 1:  # 如果前一个字是句首则已经写入过，所以不再写入
                        index_random_findcv_v[self.vlist.index(
                            vc_wanted.v)] = self.cvlist.index(cv_now) + 1
                        row.append(cv_now)
                        if notheadcv_remained.count(cv_now) > 0 and count > 0:
                            notheadcv_remained.remove(cv_now)  # 删除已经出现的句中CV字
                        count += 1
                    add_flag = 0

                # 搜索确定下一个要写入的CV字，使得其C与上一个字凑成所需要的VC部
                if index_findcv_connective < len(self.cvlist):
                    cv_now = self.findcv_c(
                        self.cvlist, vc_wanted.c, index_findcv_connective)  # 从上次搜索到的位置继续向下搜索
                else:
                    cv_now = None  # 若指针越界或已经搜索完所有结果，则置空cv_now，并准备增字

                # 由于搜索不到任何符合条件的VC，则下一个字必须增字，并离开本轮子循环
                if cv_now == None:
                    # 先随意写入一个CV字来完成本轮的VC部，V是什么无所谓，因为没有能够接续下去的V
                    if vc_wanted.type != 'vv':
                        cv_now = self.findcv_c(
                            self.cvlist, vc_wanted.c, index_random_findcv_c[self.clist.index(vc_wanted.c)], True)
                    else:
                        cv_now = self.findcv_c(self.cvlist, vc_wanted.c)
                    add_flag = 1  # 点亮增字标记
                    if(len(vc_remained) > 0):
                        vc_wanted = vc_remained[0]  # 随意取出一个下轮的VC部
                    break  # 离开本轮子循环

                # 检查搜索到的CV字是否符合要求
                # 尝试找到下一个需要的VC部，使得其V与目前检索到的CV字的V相同（即能够接续）
                vc_wanted_next = self.findcv_v(vc_remained, cv_now.v)
                index_findcv_connective = self.cvlist.index(
                    cv_now) + 1  # 记录搜索指针到达的位置
                if vc_wanted_next != None:
                    # 如果找到了符合要求的VC部，则记录该VC部，并离开本轮子循环
                    if vc_wanted.type != 'vv':
                        index_random_findcv_c[self.clist.index(
                            vc_wanted.c)] = index_findcv_connective
                    vc_wanted = vc_wanted_next
                    break

                # VC部用尽时结束工作
                if len(vc_remained) == 0:
                    break

            # 离开上述子循环的条件是：已经找到一个合适的CV字来写入（有可能在其之前还要再写入一个增字）
            if not cv_now == None:
                row.append(cv_now)  # 写入该CV字
                if notheadcv_remained.count(cv_now) > 0 and count > 0:
                    notheadcv_remained.remove(cv_now)  # 删除已经出现的句中CV字
                count += 1

            # 如果字数达到一句的长度，则换行
            if(count == length):
                count = 0
                reclist.append(row)
                # 记录句尾V的出现
                if(vR_remained.count(row[len(row) - 1].v) > 0):
                    vR_remained.remove(row[len(row) - 1].v)
                row = []

        # 全部VC部用尽后，将最后一行未满的字写入
        if len(row) > 0:
            reclist.append(row)
            # 记录句尾V的出现
            if(vR_remained.count(row[len(row) - 1].v) > 0):
                vR_remained.remove(row[len(row) - 1].v)

        if not UsePlanB:
            # 如果要求句首CV，则需要在最后单独补充
            if CV_head:
                while True:
                    row = []
                    i = 0
                    while i < length:
                        if len(headcv_remained) > 0:
                            row.append(headcv_remained[0])
                            # 记录句尾V的出现
                            if(vR_remained.count(headcv_remained[0].v) > 0):
                                vR_remained.remove(headcv_remained[0].v)
                            headcv_remained.remove(headcv_remained[0])
                            i += 1
                        else:
                            break
                        if i < length:  # 隔一个字放置一个空拍
                            if i + 1 < length and len(headcv_remained) > 0:
                                row.append(cv('blank', '', '', 'blank'))
                            i += 1
                    reclist.append(row)
                    if len(headcv_remained) == 0:
                        break

            # 补充句中CV
            while True:
                # print(notheadcv_remained[0].name)
                row = []
                row.append(notheadcv_remained[0])
                i = 1
                while i < length:
                    if len(notheadcv_remained) > 0:
                        row.append(notheadcv_remained[0])
                        notheadcv_remained.remove(notheadcv_remained[0])
                        i += 1
                    else:
                        break
                reclist.append(row)
                # 记录句尾V的出现
                if(vR_remained.count(row[len(row) - 1].v) > 0):
                    vR_remained.remove(row[len(row) - 1].v)
                if len(notheadcv_remained) == 0:
                    break

            # 补充V_R
            for v_R in vR_remained:
                row = []
                row.append(self.findcv_v(self.cvlist, v_R, 0, False))
                reclist.append(row)

        # 写入CVVC录音表文件
        f_reclist = open(path, 'w', encoding='UTF-8')
        reclist_text = []
        for row in reclist:
            text = '_'
            for _cv in row:
                if UseUnderlineInReclist and text != '_':
                    text += '_'
                if _cv.name != 'blank':
                    text += _cv.name
                else:
                    if UseUnderlineInReclist:
                        text += 'R'
                    else:
                        text += '_'
            reclist_text.append(text)
            f_reclist.write(text + "\n")

        # 写入oto文件
        f_oto = open(otopath, 'w', encoding='UTF-8')
        exist_list_cv = []
        exist_list_vc = []
        ticks = float(60) / oto_bpm * float(1000)
        vc_list_temp = []
        repeat_list = []
        for i in range(0, len(reclist)):
            row_text = reclist_text[i] + ".wav="
            row = reclist[i]
            count = 0
            row_count = 0
            cv_last = None
            for _cv in row:
                if _cv.name == 'blank':
                    count = count + 1
                    cv_last = None
                    continue
                # VC
                text = row_text
                if cv_last != None:
                    _name = cv_last.v + ' ' + _cv.c.replace('#', '')
                else:
                    _name = None
                if _name != None:
                    if OtoMaxOfSameVC == -1 or exist_list_vc.count(_name) < OtoMaxOfSameVC:
                        text += _name
                        if exist_list_vc.count(_name) > 0:
                            text += str(exist_list_vc.count(_name) + 1)
                            if exist_list_vc.count(_name) == 1:
                                repeat_list.append(
                                    _name + ',' + str(exist_list_vc.count(_name) + 1) + '\n')
                            else:
                                repeat_list.remove(
                                    _name + ',' + str(exist_list_vc.count(_name)) + '\n')
                                repeat_list.append(
                                    _name + ',' + str(exist_list_vc.count(_name) + 1) + '\n')
                        text += ',' + \
                            "{:.1f}".format(
                                preset_blank - 0.5 * ticks + float(count) * ticks)
                        text += ',' + "{:.1f}".format(0.65 * ticks)
                        text += ',' + "{:.1f}".format(-1 * ticks)
                        text += ',' + "{:.1f}".format(0.5 * ticks)
                        text += ',' + "{:.1f}".format(0.5 * ticks / float(3))
                        if DivideVCCV:
                            vc_list_temp.append(text + '\n')
                        else:
                            f_oto.write(text + "\n")
                        exist_list_vc.append(_name)

                # CV
                text = row_text
                if cv_last:
                    _name = _cv.name
                else:
                    _name = "- " + _cv.name

                if UsePlanB and row_count == 2 and len(row) == 3:
                    _name = _name + "_L"

                if OtoMaxOfSameCV == -1 or exist_list_cv.count(_name) < OtoMaxOfSameCV:
                    text += _name
                    repeat_time = ''
                    if exist_list_cv.count(_name) > 0:
                        repeat_time = str(exist_list_cv.count(_name) + 1)
                        text += repeat_time
                        if exist_list_cv.count(_name) == 1:
                            repeat_list.append(
                                _name + ',' + str(exist_list_cv.count(_name) + 1) + '\n')
                        else:
                            repeat_list.remove(
                                _name + ',' + str(exist_list_cv.count(_name)) + '\n')
                            repeat_list.append(
                                _name + ',' + str(exist_list_cv.count(_name) + 1) + '\n')
                    text += ',' + \
                        "{:.1f}".format(preset_blank - 0.1 *
                                        ticks + float(count) * ticks)
                    text += ',' + "{:.1f}".format(0.3 * ticks)
                    text += ',' + "{:.1f}".format(float(-0.7) * ticks)
                    text += ',' + "{:.1f}".format(0.1 * ticks)
                    text += ',' + "{:.1f}".format(0.1 * ticks / float(3))
                    f_oto.write(text + "\n")
                    exist_list_cv.append(_name)

                cv_last = _cv
                count += 1
                row_count += 1

            # V_R
            text = row_text
            _name = cv_last.v + ' R'
            if OtoMaxOfSameVC == -1 or exist_list_vc.count(_name) < OtoMaxOfSameVC:
                text += _name
                if exist_list_vc.count(_name) > 0:
                    text += str(exist_list_vc.count(_name) + 1)
                    if exist_list_vc.count(_name) == 1:
                        repeat_list.append(
                            _name + ',' + str(exist_list_vc.count(_name) + 1) + '\n')
                    else:
                        repeat_list.remove(
                            _name + ',' + str(exist_list_vc.count(_name)) + '\n')
                        repeat_list.append(
                            _name + ',' + str(exist_list_vc.count(_name) + 1) + '\n')
                text += ',' + \
                    "{:.1f}".format(preset_blank - 0.5 *
                                    ticks + float(count) * ticks)
                text += ',' + "{:.1f}".format(0.65 * ticks)
                text += ',' + "{:.1f}".format(-1 * ticks)
                text += ',' + "{:.1f}".format(0.5 * ticks)
                text += ',' + "{:.1f}".format(0.5 * ticks / float(3))
                if DivideVCCV:
                    vc_list_temp.append(text + '\n')
                else:
                    f_oto.write(text + "\n")
                exist_list_vc.append(_name)

        if DivideVCCV:
            f_oto.writelines(vc_list_temp)

        if debug:
            # 写入repeat文件
            f_repeat = open('repeat.txt', 'w', encoding='UTF-8')
            f_repeat.writelines(repeat_list)
        return


ini = open('reclist-gen-cvvc.ini', 'r', encoding='UTF-8').readlines()
_input_path = ''.join(re.split(r'[,=]+', ini[1])[1]).strip('\n')
_reclist_output_path = ''.join(re.split(r'[,=]+', ini[2])[1]).strip('\n')
_length = int(''.join(re.split(r'[,=]+', ini[3])[1]).strip('\n'))
_include_CV_head = ''.join(re.split(r'[,=]+', ini[4])[1]).strip('\n') == 'True'
_include_VV = ''.join(re.split(r'[,=]+', ini[5])[1]).strip('\n') == 'True'
_use_underbar = ''.join(re.split(r'[,=]+', ini[6])[1]).strip('\n') == 'True'
_use_planb = ''.join(re.split(r'[,=]+', ini[7])[1]).strip('\n') == 'True'
_oto_output_path = ''.join(re.split(r'[,=]+', ini[9])[1]).strip('\n')
_oto_max_of_same_cv = int(''.join(re.split(r'[,=]+', ini[10])[1]).strip('\n'))
_oto_max_of_same_vc = int(''.join(re.split(r'[,=]+', ini[11])[1]).strip('\n'))
_oto_preset_blank = int(''.join(re.split(r'[,=]+', ini[12])[1]).strip('\n'))
_oto_bpm = int(''.join(re.split(r'[,=]+', ini[13])[1]).strip('\n'))
_oto_divide_vccv = ''.join(
    re.split(r'[,=]+', ini[14])[1]).strip('\n') == 'True'

my_worker = worker()
my_worker.read_presamp(_input_path)
my_worker.gen_CVVC(_reclist_output_path, _length, _use_planb, _include_CV_head, _include_VV,
                   _use_underbar, _oto_output_path, _oto_max_of_same_cv, _oto_max_of_same_vc, _oto_preset_blank, _oto_bpm, _oto_divide_vccv)
