
from kerri import Kerri

from KerriElektrik import KerriElektrik


kerri1 = Kerri("tesla","2000","sdf")
kerri1.info()

kerri2 = KerriElektrik("byd","2020","plus","85%")

kerri2.mbusheBaterin()
kerri1.rritjeShpejtesise()
kerri2.rritjeShpejtesise()
kerri2.nalu()

