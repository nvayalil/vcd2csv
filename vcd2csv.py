"""
Copyright (C) 2023 Niras C. Vayalil. 

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import re
import csv

def get_field(f, line, field):
    val = line.lstrip(field).rstrip('$end\n').strip()
    while (line.find('$end') < 0):
        val = line.rstrip('$end\n').strip()
        line = f.readline()
    return val


def vcd2csv(infile, outfile, en_scope=False):
    """
    Convert a VCD (Value Change Dump) file into CSV format.

    Parameters
    ----------
    infile : str
        Path to the input VCD file.
    outfile : str
        Path where the CSV file will be written.
    en_scope : bool, optional (default=False)
        If True, include full hierarchical signal scope names in the CSV output.
        If False, only signal names will be used.
    """      
    keys = ['ts']
    ref = ['timestamp']
    scope = ''
    with open(infile) as f:
        header = 0
        print('Writing to file', outfile)
        w = open(outfile, 'w', newline='')
        wcsv = csv.writer(w)
        # w.write('timestamp')
        vd = re.compile(r'^\$var\s+(\w+)\s+(\d+)\s+(\w+)\s+(\w+)\s+\S*\s*\$end\s+$')
        sc = re.compile(r'^\$scope\s+module\s+(\S+)\s+\$end\s+$')
        us = re.compile(r'^\$upscope\s+\$end')
        while True:
            line  = f.readline()
            if line.startswith('$timescale'):
                timescale = get_field(f, line, '$timescale')
                    
            if line.startswith('$date'):
                date = get_field(f, line, '$date')
                
            if line.startswith('$version'):
                version = get_field(f, line, '$version')
            
            
            if line.startswith('$var'):
                # $var vary_type size id_code reference $end
                m = vd.match(line)
                if (m != None):
                    # print('{0}, {1}, {2}, {3}'.format(m.group(1), m.group(2), m.group(3), m.group(4)))
                    keys.append(m.group(3))
                    if en_scope:
                        ref.append(scope + '.' + m.group(4))
                    else:
                        ref.append(m.group(4))
                else:
                    print ('Error on parsing variable declaration')
            
            if line.startswith('$scope'):
                m = sc.match(line)
                if m != None:
                    scope  += '.' + m.group(1)
                else:
                    print('Error in parsing module name')
            if us.match(line):
                scope = scope.rsplit('.', 1)[0]
            
            if line.startswith('$enddefinitions'):
                d = dict.fromkeys(keys, None)
                # w.write('\n')
                wcsv.writerow(ref)
                break
            
        sb = re.compile(r'^(\d)(\S+)\s*$')
        bv = re.compile(r'^b(\d+)\s+(\S+)\s*$')
        bl = re.compile(r'^\s*$')
            
        while not(line.startswith('#')):
            line = f.readline()
            if line == '':
                break
    
        d['ts'] = int(line.strip('#'))
        
        while line != '':
            line = f.readline()
            if line.startswith('#'):
                if (d['clk']) == 1:             # capture on the rising edge
                    wcsv.writerow(d.values())
                d['ts'] = int(line.strip('#'))  # next timestamp
                continue
            
            m = sb.match(line) # single bit
            if m != None:
                # print(m.group(2), ' = ', m.group(1))
                d[m.group(2)] = int(m.group(1), 2)
                continue
            
            m = bv.match(line) # bit vector
            if m != None:
                # print(m.group(2), ' = ', m.group(1))
                d[m.group(2)] = int(m.group(1), 2)
                continue
            
            if (bl.match(line) == None):  # except blank line or end of file, 
                print ('Unable to decode the line', line) # print error message
        w.close()