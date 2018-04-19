import os
import re
import pickle

import pandas as pd

INDEX_TYPE = 'sps'


class ascii_:
    def __init__(self, f_path, f_name, is_fam):
        self.file_path = f_path
        self.file_name = f_name
        self.is_fam = is_fam

    def _get_index_path(self):
        return os.path.join(self.file_path, self.file_name + '.' + INDEX_TYPE)

    def _get_data_path(self):
        return os.path.join(self.file_path, self.file_name + '.txt')

    def _get_csv_path(self):
        return os.path.join(self.file_path, self.file_name + '.csv')

    def _get_pickle_path(self):
        return os.path.join(self.file_path, self.file_name + '.pickle')

    def _chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def _export_pickle(self, a):
        with open(self._get_pickle_path(), 'wb') as f:
            pickle.dump(a, f)

    def read_index_file(self):
        """Reads SPS index file using indices stored in 'inds'.
        'inds' is used to parse the PSID raw ascii .txt file,
        which is given in fixed format.
        For more info on ascii file formats,
        refer to: http://wlm.userweb.mwn.de/SPSS/wlmsrrd.htm
        """
        with open(self._get_index_path(), 'r') as f:
            data = []
            raw_data = f.readlines()
            # get locations of 1) indices, 2) data format (int or float),
            # 3) variable labels
            for i, raw_line in enumerate(raw_data):
                line = re.sub('\s+', ' ', raw_line).strip()
                if re.match('^DATA LIST FILE = ', line):
                    i_index = i + 1
                if line == 'FORMATS':
                    i_format = i + 1
                if line == 'VARIABLE LABELS':
                    i_label = i + 1
                data.append(line)
            # create 'inds' variable and list of labels
            inds, headers = [0], []
            for j in range(i_index, i_format):
                line = data[j]
                if line == '.':
                    break
                s = line.split()
                for c in self._chunks(s, 4):
                    inds.append(int(c[3]))
                    headers.append(c[0])
            # create dictionaries for variable labels, formats and names
            lab2format, lab2name, name2lab = {}, {}, {}
            for j in range(i_format, i_label):
                line = data[j]
                if line == '.':
                    break
                s = line.split()
                for c in self._chunks(s, 2):
                    lab2format[c[0]] = c[1]
            if self.is_fam:
                for j in range(i_label, len(data)):
                    line = data[j]
                    if line == '.':
                        break
                    s = line.replace('"', '')
                    s = re.sub('\s+', ' ', s).strip()
                    lab, *name = s.split()
                    name = ' '.join(name)
                    lab2name[lab] = name
                    name2lab[name] = lab
            else:
                for j in range(i_label, len(data)):
                    line = data[j]
                    if line == '.':
                        break
                    s = line.replace('"', '')
                    s = re.sub('\s+', ' ', s).strip()
                    yr = re.findall(' [0-9]{2}$', s)
                    if not yr:
                        lab, *name = s.split()
                        yr = 'NA'
                    else:
                        s = re.sub(' [0-9]{2}$', '', s)
                        lab, *name = s.split()
                        yr = yr[-1].strip()
                    name = ' '.join(name)
                    lab2name[lab] = (name, yr)
                    name2lab[(name, yr)] = lab
            assert headers == list(lab2name.keys())
            print('Exporting pickle file...')
            self._export_pickle((lab2name, name2lab))
        return inds, headers, lab2format, lab2name, name2lab

    def read_data_file(self, inds, headers, lab2format):
        """Reads raw ascii .txt file and exports as csv"""
        with open(self._get_data_path(), 'r') as f:
            print('Opened ascii file and processing...')
            data_table = []
            for line in f:
                split_data = []
                split_line = [
                    line[inds[i]:inds[i + 1]] for i in range(len(inds) - 1)
                ]
                for i, h in enumerate(headers):
                    if split_line[i].strip() == '':
                        split_data.append(None)
                    # checks if data is integer or float
                    elif h in lab2format and '.' in lab2format[h]:
                        split_data.append(float(split_line[i]))
                    else:
                        split_data.append(int(split_line[i]))
                data_table.append(split_data)
            print('Merging to dataframe...')
            df = pd.DataFrame(data_table, columns=headers)
        print('Dimensions of dataframe: {0}'.format(df.shape))
        print('Exporting as csv...')
        csv_path = self._get_csv_path()
        df.to_csv(csv_path)
        print('File available in {0}'.format(csv_path))
        return csv_path
