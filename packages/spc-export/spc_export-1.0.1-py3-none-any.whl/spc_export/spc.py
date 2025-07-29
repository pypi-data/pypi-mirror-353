from __future__ import division, absolute_import, unicode_literals, print_function
import struct
import numpy as np
import math
import copy
import zipfile
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

def flag_bits(n):
    return [x == '1' for x in list('{0:08b}'.format(ord(n)))]


def round_to_significant(x, sig=4):
    if x == 0:
        return 0.0
    else:
        return round(x, sig - int(math.floor(math.log10(abs(x))) + 1))


class Data_Block:
    
    def __init__(self, spc_file_type, header, file_content):    
        self.spc_file_type = spc_file_type
        self.header = copy.copy(header)
        y_dat_pos = self.header.subheader(file_content)
        if spc_file_type.isEachFileHasOwnX():
            pts = self.header.subnpts
        else:
            pts = self.header.fnpts
        if not spc_file_type.tmulti:
            exp = self.header.fexp
        else:
            exp = self.header.subexp
        if not (-128 < exp <= 128):
            exp = 0
        if spc_file_type.isEachFileHasOwnX():
            x_str = '<' + 'i' * pts
            x_dat_pos = y_dat_pos
            x_dat_end = x_dat_pos + (4 * pts)

            x_raw = np.array(struct.unpack(x_str, file_content[x_dat_pos:x_dat_end]))
            self.x = (2**(exp - 32)) * x_raw

            y_dat_pos = x_dat_end

        y_dat_str = '<'
        if exp == 128:
            # Floating y-values
            y_dat_str += 'f' * pts
            y_dat_end = y_dat_pos + (4 * pts)
            y_raw = np.array(struct.unpack(y_dat_str, file_content[y_dat_pos:y_dat_end]))
            self.y = y_raw
        else:
            if spc_file_type.tsprec:
                # 16 bit
                y_dat_str += 'h' * pts  # short
                y_dat_end = y_dat_pos + (2 * pts)
                y_raw = np.array(struct.unpack(y_dat_str, file_content[y_dat_pos:y_dat_end]))
                self.y = (2**(exp - 16)) * y_raw
            else:
                y_dat_str += 'i' * pts
                y_dat_end = y_dat_pos + (4 * pts)
                y_raw = np.array(struct.unpack(y_dat_str, file_content[y_dat_pos:y_dat_end]))
                self.y = (2**(exp - 32)) * y_raw
                
    def write(self,zip_archive,name,xlabel,ylabel):
        filename = zipfile.ZipInfo(
            filename=f"{name}.csv",
            date_time=self.header.datetime())
        with zip_archive.open(filename, 'w') as csv_file:
            csv_file.write(str.encode(f"{xlabel}\t{ylabel}\n"))
            for xx, yy in zip(self.x, self.y):
                csv_file.write(str.encode(f"{xx}\t{yy}\n"))
        

class Old_Data_Block:
    def __init__(self,spc_file_type,header,content):
        if header.subnpts > 0:
            pts = header.subnpts
        else:
            pts = self.onpts
        y_dat_pos = 0
        yfloat = False
        if header.subexp == 128:
            yfloat = True
        if header.subexp > 0 and self.subexp < 128:
            exp = header.subexp
        else:
            exp = header.oexp
        if spc_file_type.isEachFileHasOwnX():
            x_str = 'i' * pts
            x_dat_pos = y_dat_pos
            x_dat_end = x_dat_pos + (4 * pts)

            x_raw = np.array(struct.unpack(x_str, content[x_dat_pos:x_dat_end]))
            self.x = (2**(exp - 32)) * x_raw

            y_dat_pos = x_dat_end
        y_dat_end = y_dat_pos + (4 * pts)
        if yfloat:
            y_dat_str = '<' + 'f' * pts
            y_raw = struct.unpack(y_dat_str, content[y_dat_pos:y_dat_end])
            self.y = y_raw
        else:
            y_dat_str = '>' + 'B' * 4 * pts
            y_raw = struct.unpack(y_dat_str, content[y_dat_pos:y_dat_end])

            y_int = []
            for i in range(0, len(y_raw), 4):
                y_int.append((
                    y_raw[i + 1] * (256**3) + y_raw[i] * (256**2) +
                    y_raw[i + 3] * (256) + y_raw[i + 2]))
            y_int = np.int32(y_int) / (2**(32 - exp))

            self.y = y_int


class Log_Block:
    def __init__(self, header, file_content):    
        logstc_str = "<iiiii44s"
        log_siz = struct.calcsize(logstc_str)
        log_head_end = header.flogoff + log_siz
        logsizd, \
            self.logsizm, \
            logtxto, \
            self.logbins, \
            self.logdsks, \
            self.logspar \
            = struct.unpack(logstc_str,
                            file_content[header.flogoff:log_head_end])
        log_pos = header.flogoff + logtxto

        log_end_pos = log_pos + logsizd

        log_content = file_content[log_pos:log_end_pos].replace(b'\r', b'').split(b'\n')
 
        self.log_dict = dict()
        self.log_other = [] 
        for x in log_content:
            if x.find(b'=') >= 0:
                key, value = x.split(b'=')[:2]
                self.log_dict[key.decode('utf-8').strip()] = value.decode('utf-8').strip()
            else:
                self.log_other.append(x.decode('utf-8'))


    def to_xml(self,root):
        log_xml = ET.SubElement(root, "log")
        for attr, val in self.log_dict.items():
            child = ET.SubElement(log_xml, attr.lower().replace(' ','_'))
            child.text = str(val)
            
        for attr in self.log_other:
            ET.SubElement(root, "other").text=attr
        return root

    def generate_filename(self) -> str:
        instrument = self.log_dict.get("INSTRUMENT", "unknown_instrument")
        sample = self.log_dict.get("SAMPLE", "unknown_sample")
        operator = self.log_dict.get("OPERATOR", "unknown_operator")
    
        instrument = instrument.strip().replace(" ", "_")
        sample = sample.strip().replace(" ", "_")
        operator = operator.strip().replace(" ", "_")
    
        filename = f"{instrument}_{operator}_{sample}".lower()
        return filename


class SPC_File_Type:
    
    format = '<cc'
    length = struct.calcsize(format)
    def __init__(self, file_content):    
        
        self.file_type_flag, \
        self.spc_file_version \
        = struct.unpack(self.format, file_content[:self.length])

        self.tsprec, \
            self.tcgram, \
            self.tmulti, \
            self.trandm, \
            self.tordrd, \
            self.talabs, \
            self.txyxys, \
            self.txvals = flag_bits(self.file_type_flag)[::-1]

    def isNewFormat(self):
        return self.spc_file_version == b'\x4b'
    
    def isOldFormat(self):
        return self.spc_file_version == b'\x4d'
    
    def isEachFileHasOwnX(self):
        return self.txyxys
            
class SPC_New_File_Header:
    sub_header_format = "<cchfffiif4s"
    format = "<cciddicccci9s9sh32s130s30siicchf48sfifc187s"    
    offset = 2
    length = struct.calcsize(format)
    def __init__(self, spc_file_type, file_content):
        self.fexper, \
            self.fexp, \
            self.fnpts, \
            self.ffirst, \
            self.flast, \
            self.fnsub, \
            self.fxtype, \
            self.fytype, \
            self.fztype, \
            self.fpost, \
            self.fdate, \
            self.fres, \
            self.fsource, \
            self.fpeakpt, \
            self.fspare, \
            self.fcmnt, \
            self.fcatxt, \
            self.flogoff, \
            self.fmods, \
            self.fprocs, \
            self.flevel, \
            self.fsampin, \
            self.ffactor, \
            self.fmethod, \
            self.fzinc, \
            self.fwplanes, \
            self.fwinc, \
            self.fwtype, \
            self.freserv \
            = struct.unpack(self.format, file_content[self.offset:self.length+self.offset])
        self.extract_header_info(spc_file_type)
        
    def extract_header_info(self, spc_file_type):
        self.fnpts = int(self.fnpts)  
        self.fexp = ord(self.fexp)
        self.ffirst = float(self.ffirst)
        self.flast = float(self.flast)
        self.flogoff = int(self.flogoff) 
        self.fxtype = ord(self.fxtype)
        self.fytype = ord(self.fytype)
        self.fztype = ord(self.fztype)
        self.fexper = ord(self.fexper)
        d = self.fdate
        self.year = (d >> 20) + 1900
        self.month = ((d >> 16) % (2**4)) + 1
        self.day = (d >> 11) % (2**5)
        self.hour = (d >> 6) % (2**5)
        self.minute = d % (2**6)
        try:
            self.cmnt = ' '.join((self.fcmnt.replace('\x00', ' ')).split())
        except:
            self.cmnt = self.fcmnt
        if self.fnsub > 1:
            self.dat_multi = True

        if spc_file_type.isEachFileHasOwnX():
            self.dat_fmt = '-xy'
        elif spc_file_type.txvals:
            self.dat_fmt = 'x-y'
        else:
            self.dat_fmt = 'gx-y'
        self.fpost   = self.fpost  .decode("utf-8").replace('\0',' ').strip() 
        self.fres    = self.fres   .decode("utf-8").replace('\0',' ').strip()  
        self.fsource = self.fsource.decode("utf-8").replace('\0',' ').strip() 
        self.fspare  = self.fspare .decode("utf-8").replace('\0',' ').strip() 
        self.fcmnt   = self.fcmnt  .decode("utf-8").replace('\0',' ').strip() 
        self.fcatxt  = self.fcatxt .decode("utf-8").replace('\0',' ').strip() 
        self.fprocs  = self.fprocs .decode("utf-8").replace('\0',' ').strip() 
        self.flevel  = self.flevel .decode("utf-8").replace('\0',' ').strip() 
        self.fmethod = self.fmethod.decode("utf-8").replace('\0',' ').strip() 
        self.freserv = self.freserv.decode("utf-8").replace('\0',' ').strip() 
        self.cmnt    = self.cmnt   .decode("utf-8").replace('\0',' ').strip() 
            
    def readSS(self,content,index):
        self.ssfposn, \
            self.ssfsize, \
            self.ssftime  \
            = struct.unpack(
                '<iif', content[self.header.fnpts + (index * 12):self.header.fnpts + ((index + 1) * 12)])
        self.fnpts = 0
        self.fexp = 0 

    def subheader(self, subheader):
        header_size = struct.calcsize(self.sub_header_format)
        self.subflgs, \
            self.subexp, \
            self.subindx, \
            self.subtime, \
            self.subnext, \
            self.subnois, \
            self.subnpts, \
            self.subscan, \
            self.subwlevel, \
            self.subresv \
            = struct.unpack(self.sub_header_format, subheader[:header_size])
        self.subflgs = int.from_bytes(self.subflgs, byteorder='little')
        self.subexp = int.from_bytes(self.subexp, byteorder='little')
        self.subresv = self.subresv.decode('utf-8')
        return header_size
            
    def readSubHeader(self,spc_file_type,content,sub_pos):
        if spc_file_type.isEachFileHasOwnX():
            self.subheader(content[sub_pos:(sub_pos + 32)])
            pts = self.subnpts
            return (8 * pts) + 32
        else:
            pts = self.fnpts
            return (4 * pts) + 32
        
    def datetime(self):
        return (self.year,self.month,self.day,self.hour,self.minute,0)
    
    def datetime_str(self):
        return f"{self.year}-{self.month}-{self.day}-{self.hour}-{self.minute}"
    
    def to_xml(self,root):

        for attr, val in self.__dict__.items():
            child = ET.SubElement(root, attr)
            child.text = str(val)
        return root

    def sub_coordinnates(self) -> str:
    
        x_val = round_to_significant(self.subwlevel, 4)
        y_val = round(self.subtime, 2)  # Assuming 2 decimal places for subtime
    
        return f"x_{x_val:.2f}_y_{y_val:.2f}"

        
            
class SPC_Old_File_Header:
    format = "<hfffcchcccc8shh28s130s30s32s"   
    offset = 2
    length = struct.calcsize(format)
    def __init__(self, spc_file_type, file_content):
        self.oftflgs, \
            self.oversn, \
            self.oexp, \
            self.onpts, \
            self.ofirst, \
            self.olast, \
            self.fxtype, \
            self.fytype, \
            self.oyear, \
            self.omonth, \
            self.oday, \
            self.ohour, \
            self.ominute, \
            self.ores, \
            self.opeakpt, \
            self.onscans, \
            self.ospare, \
            self.ocmnt, \
            self.ocatxt, \
            self.osubh1 \
            = struct.unpack(self.old_head_str,
                                        file_content[self.offset:self.length+self.offset])        
        self.extract_header_info(spc_file_type)
        
    def extract_header_info(self, spc_file_type):
        self.oexp = int(self.oexp)
        self.onpts = int(self.onpts)  # can't have floating num of pts
        self.ofirst = float(self.ofirst)
        self.olast = float(self.olast)
        self.omonth = ord(self.omonth)
        self.oday = ord(self.oday)
        self.ohour = ord(self.ohour)
        self.ominute = ord(self.ominute)
        self.onscans = int(self.onscans)
        self.ores = self.ores.split(b'\x00')[0]
        self.ocmnt = self.ocmnt.split(b'\x00')[0]
      
    
class SPC_Record:
    fytype_op = ("Arbitrary Intensity",
             "Interferogram",
             "Absorbance",
             "Kubelka-Munk",
             "Counts",
             "Volts",
             "Degrees",
             "Milliamps",
             "Millimeters",
             "Millivolts",
             "Log(1/R)",
             "Percent",
             "Intensity",
             "Relative Intensity",
             "Energy",
             "",
             "Decibel",
             "",
             "",
             "Temperature (F)",
             "Temperature (C)",
             "Temperature (K)",
             "Index of Refraction [N]",
             "Extinction Coeff. [K]",
             "Real",
             "Imaginary",
             "Complex")

    fytype_op2 = ("Transmission",
                  "Reflectance",
                  "Arbitrary or Single Beam with Valley Peaks",
                  "Emission")
    fxtype_op = ("Arbitrary",
                 "Wavenumber (1/cm)",
                 "Micrometers (um)",
                 "Nanometers (nm)",
                 "Seconds ",
                 "Minutes", "Hertz (Hz)",
                 "Kilohertz (KHz)",
                 "Megahertz (MHz) ",
                 "Mass (M/z)",
                 "Parts per million (PPM)",
                 "Days",
                 "Years",
                 "Raman Shift (1/cm)",
                 "eV",
                 "XYZ text labels in fcatxt (old 0x4D version only)",
                 "Diode Number",
                 "Channel",
                 "Degrees",
                 "Temperature (F)",
                 "Temperature (C)",
                 "Temperature (K)",
                 "Data Points",
                 "Milliseconds (mSec)",
                 "Microseconds (uSec) ",
                 "Nanoseconds (nSec)",
                 "Gigahertz (GHz)",
                 "Centimeters (cm)",
                 "Meters (m)",
                 "Millimeters (mm)",
                 "Hours")
    fexper_op = ("General SPC",
                 "Gas Chromatogram",
                 "General Chromatogram",
                 "HPLC Chromatogram",
                 "FT-IR, FT-NIR, FT-Raman Spectrum or Igram",
                 "NIR Spectrum",
                 "UV-VIS Spectrum",
                 "X-ray Diffraction Spectrum",
                 "Mass Spectrum ",
                 "NMR Spectrum or FID",
                 "Raman Spectrum",
                 "Fluorescence Spectrum",
                 "Atomic Spectrum",
                 "Chromatography Diode Array Spectra")

    def __init__(self, filename):
        with open(filename, "rb") as fin:
            content = fin.read()
        self.length = len(content)
        self.spc_file_type = SPC_File_Type(content)
        if self.spc_file_type.isNewFormat():
            self.header = SPC_New_File_Header(self.spc_file_type,content)
            
            self.head_siz = self.spc_file_type.length + self.header.length
            sub_pos =  self.head_siz
            if not self.spc_file_type.isEachFileHasOwnX():
                sub_pos = self.define_global_x_axis(sub_pos,content)
            self.sub = []
            if self.header.dat_fmt == '-xy' and self.header.fnpts > 0:
                self.directory = True
                for i in range(0, self.header.fnsub):
                    self.spc_file_type.txyxy = True
                    dataheader = copy.copy(self.header)
                    dataheader.readSS(content)
                    data_block = Data_Block(self.spc_file_type,dataheader,content[dataheader.ssfposn:dataheader.ssfposn + dataheader.ssfsize])
                    if not hasattr(data_block, 'x'):
                        data_block.x = self.x
                    self.sub.append(data_block)
            else:
                for i in range(self.header.fnsub):
                    dataheader = copy.copy(self.header)
                    dat_siz = dataheader.readSubHeader(self.spc_file_type,content,sub_pos)
                    data_block = Data_Block(self.spc_file_type, dataheader, content[sub_pos:sub_pos + dat_siz])
                    self.sub.append(data_block)
                    if not hasattr(data_block, 'x'):
                        data_block.x = self.x
                    sub_pos = sub_pos + dat_siz

            if self.header.flogoff:
                self.log_block = Log_Block(self.header,content)

            self.spacing = (self.header.flast - self.header.ffirst) / (self.header.fnpts - 1)

            self.xlabel = self.set_xz_label(self.header.fxtype)
            self.zlabel = self.set_xz_label(self.header.fztype)
            self.ylabel = self.set_y_label(self.header.fytype)
            self.set_exp_type()

        elif self.spc_file_version.isOldFormat():
            self.header = SPC_Old_File_Header(self.spc_file_type, content)
            self.x = np.linspace(self.header.ofirst, self.header.olast, num=self.header.onpts)
            self.sub = []

            self.head_siz = self.spc_file_type.length + self.header.length
            sub_pos =  self.head_siz
            
            subhead_siz = 32
            i = 0
            while True:
                try:
                    dataheader = copy.copy(self.header)
                    header_size = dataheader.subheader(content[sub_pos:sub_pos + subhead_siz])

                    sub_end = sub_pos + subhead_siz + dat_siz

                    data_block = Old_Data_Block(self.spc_file_type,self.header,content[sub_pos+header_size:sub_end])
                    self.sub.append(data_block)
                    sub_pos = sub_end
                    i += 1
                except:
                    self.fnsub = i + 1
                    break

            self.dat_fmt = 'gx-y'

            self.fxtype = ord(self.fxtype)
            self.fytype = ord(self.fytype)
            self.fztype = 0
            self.xlabel = self.set_xz_label(self.header.fxtype)
            self.zlabel = self.set_xz_label(self.header.fztype)
            self.ylabel = self.set_y_label(self.header.fytype)

        else:
            print("File type %s not supported yet. Please add issue. "
                  % hex(ord(self.spc_file_version)))
            self.content = content
        del self.x

    def define_global_x_axis(self,sub_pos, content):
        if self.spc_file_type.txvals:
            x_dat_pos = self.head_siz
            x_dat_end = self.head_siz + (4 * self.header.fnpts)
            self.x = np.array(
                [struct.unpack_from(
                    'f', content[x_dat_pos:x_dat_end], 4 * i)[0]
                    for i in range(0, self.header.fnpts)])
            return x_dat_end
        else:
            self.x = np.linspace(self.header.ffirst, self.header.flast, num=self.header.fnpts)
            return sub_pos
        
    def set_xz_label(self,atype):
        if atype < 30:
            return self.fxtype_op[atype]
        else:
            return  "Unknown"

    def set_y_label(self,atype):

        if atype < 27:
            return self.fytype_op[atype]
        elif type > 127 and type < 132:
            return self.fytype_op2[atype - 128]
        else:
            return "Unknown"

    def set_special_label(self):
        if self.spc_file_type.talabs:
            ll = self.header.fcatxt.split(b'\x00')
            if len(ll) > 2:
                xl, yl, zl = ll[:3]
                if len(xl) > 0:
                    self.xlabel = xl
                if len(yl) > 0:
                    self.ylabel = yl
                if len(zl) > 0:
                    self.zlabel = zl


    def set_exp_type(self):
        self.header.exp_type = self.fexper_op[self.header.fexper]

    def write_zip_file(self):
        archive = BytesIO()
        with ZipFile(archive, 'w') as zip_archive:
            file_name = self.log_block.generate_filename()+"_"+self.header.datetime_str()
            file_info = zipfile.ZipInfo(filename="metadata.xml",
                                        date_time=self.header.datetime())
            root = ET.Element("metadata")  
            self.header.to_xml(root)
            self.log_block.to_xml(root)
            for data_block in self.sub:
                data_block.full_file_name = file_name + "_"+ data_block.header.sub_coordinnates()
                sub_xml = ET.SubElement(root, "sub")
                sub_xml.set("subindx", str(data_block.header.subindx))
                sub_xml.set("subnext", str(data_block.header.subnext))
                sub_xml.set("subwlevel", str(data_block.header.subwlevel))
                sub_xml.set("subtime", str(data_block.header.subtime))
                sub_xml.set("datafile", data_block.full_file_name)
                
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)

            with zip_archive.open(name=file_info, mode='w') as xml_file:
                xml_file.write(ET.tostring(tree.getroot(), encoding='UTF-8'))
    
            count = 1
            for data_block in self.sub:
                data_block.write(zip_archive,data_block.full_file_name ,self.xlabel,self.ylabel)
                count = count + 1

        directory = file_name.replace('_', '/')
        os.makedirs(directory, exist_ok=True)
        with open(f"{directory}/{file_name}.zip", 'wb') as f:
            f.write(archive.getbuffer())

    def write_plot_pdf(self, zip_archive, name, data_blocks, xlabel="X", ylabel="Y"):
        with zip_archive.open(name=name+".pdf", mode='w') as pdf_file:
            with PdfPages(pdf_file) as pdf:
                plt.figure(figsize=(10, 6))
                for i, block in enumerate(self.sub):
                    plt.plot(block.x, block.y, label=f"Sub {i+1}")
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.title("All Sublines")
                plt.legend()
                plt.tight_layout()
                pdf.savefig()
                plt.close()
