ReclistGen_CVVC ver20200621
本程序通过读取presamp文件，自动生成CVVC录音表以及对应的初始oto模板。

用法：
按需求修改配置文件：reclist-gen-cvvc.ini，然后运行reclist-gen-cvvc.exe即可。
（也可以执行reclist-gen-cvvc.py）

配置说明：
input_path=presamp.ini		输入presamp文件的相对路径
reclist_output_path=Reclist.txt		输出录音表文件的相对路径
length=8		每句的字数
include_CV_head=True		是否要求包含句首CV字（True为要求，False为不要求）
include_VV=True		是否要求包含VV字（True为要求，False为不要求）
use_underbar=True		字与字之间是否加入“_”（True为是，False为否）
use_planb=True		是否使用Plan B（另附说明）
oto_output_path=oto.ini		输出oto文件的相对路径
oto_max_of_same_cv=3		oto中相同CV音素最多重复出现的条目数
oto_max_of_same_vc=3		oto中相同VC音素最多重复出现的条目数
oto_preset_blank=1250		oto的前置空白长度
oto_bpm=130		录音的BPM
oto_devide_vccv=False		是否将VC和CV分开排列（True为是，False为否）

如遇到bug或者使用上的问题，请联系sder.colin@gmail.com。


**更新履历**
20200621：
 - 修正了非Plan B时可能出现的一个错误。
 
20200604：
 - 减少了少量不必要的重复输出。

20191215:
 - 修正了presamp文件的读取错误。
 
20191120:
 - 将"oto_max_of_same"参数分为了分别针对CV和VC的两个参数。

20180918：
 - 增加了Plan B。

20180108：
 - 修正了oto文件中R不占位的错误。
 - 修正了部分句中CV缺失的错误。
 - 发布包中增加了源代码文件。