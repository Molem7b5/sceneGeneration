import numpy as np
import scipy.io
import csv
import librosa
import os
import soundfile as sf

class DBConfig(object):
    def __init__(self, params):
        self._rirpath = params['rirpath']
        self._rirdata = params['rirdata']
        self._mixturepath = params['mixturepath']
        self._rirdata = self._load_rir() #- need to load IR at some other point
        self._nb_folds = params['nb_folds']
        self._nb_mic_arrays = params['nb_mic_arrays']
        self._rooms2fold = params['rooms2fold']
        self._db_path = params['db_path']
        self._db_name = params['db_name']


        self._fs = 44100
        self._class_dict = {'alarm': 0, 'baby': 1, 'crash': 2, 'dog': 3, 'engine': 4, 'femaleScream': 5,
                            'femaleSpeech': 6,
                            'fire': 7, 'footsteps': 8, 'knock': 9, 'maleScream': 10, 'maleSpeech': 11,
                            'phone': 12, 'piano': 13, 'general': 14}
        self._class_mobility = [0, 2, 0, 2, 2, 0, 2, 0, 1, 0, 0, 2, 2, 0, 0]
        self._classes = list(self._class_dict.keys())
        self._nb_classes = len(self._classes)
        self._samplelist = self._load_db_fileinfo_nigens()
        self._apply_class_gains = False
        self._class_gaines = []


    def _load_rir(self):
        ir_data = scipy.io.loadmat(self._rirdata)
        ir_data = ir_data['data']
        ## need to see how this works later in the code
        return ir_data

    def _load_db_fileinfo_nigens(self):
        samplelist_per_fold = []

        for nfold in range(self._nb_folds):
            print(f'Preparing sample list for fold {nfold+1}')
            foldlist_file = self._db_path + '/NIGENS_8-foldSplit_fold' + str(nfold + 1) + '_wo_timit.flist'
            filelist = []
            with open(foldlist_file, newline='') as flist:
                flist_reader = csv.reader(flist, delimiter='\t')
                for fline in flist_reader:
                    filelist.append(fline)
            flist_len = len(filelist)

            samplelist = {'class': np.array([]), 'audiofile': np.array([]), 'duration': np.array([]), 'onoffset': [],
                          'nSamples': flist_len,
                          'nSamplesPerClass': np.array([]), 'meanStdDurationPerClass': np.array([]),
                          'minMaxDurationPerClass': np.array([])}
            for file in range(flist_len):
                clsfilename = filelist[file][0].split('/')
                clsname = clsfilename[0]
                filename = clsfilename[1]

                samplelist['class'] = np.append(samplelist['class'], int(self._class_dict[clsname]))
                samplelist['audiofile'] = np.append(samplelist['audiofile'], clsname + '/' + filename)
                audiopath = self._db_path + '/' + clsname + '/' + filename
                # print(audiopath)
                # with contextlib.closing(wave.open(audiopath,'r')) as f:
                audio, sr = sf.read(audiopath)
                samplelist['duration'] = np.append(samplelist['duration'], len(audio) / float(sr))

                if clsname == 'general':
                    onoffsets = []
                    onoffsets.append([0., samplelist['duration'][file]])
                    samplelist['onoffset'].append(np.array(onoffsets))
                else:
                    meta_file = self._db_path + '/' + clsname + '/' + filename + '.txt'
                    onoffsets = []
                    with open(meta_file, newline='') as meta:
                        meta_reader = csv.reader(meta, delimiter='\t')
                        for onoff in meta_reader:
                            onoffsets.append([float(onoff[0]), float(onoff[1])])

                    samplelist['onoffset'].append(np.array(onoffsets))
            samplelist['onoffset'] = np.squeeze(np.array(samplelist['onoffset'], dtype=object))

            for n_class in range(self._nb_classes):
                class_idx = (samplelist['class'] == n_class)
                samplelist['nSamplesPerClass'] = np.append(samplelist['nSamplesPerClass'], np.sum(class_idx))
                if n_class == 0:
                    samplelist['meanStdDurationPerClass'] = np.array(
                        [[np.mean(samplelist['duration'][class_idx]), np.std(samplelist['duration'][class_idx])]])
                    samplelist['minMaxDurationPerClass'] = np.array(
                        [[np.min(samplelist['duration'][class_idx]), np.max(samplelist['duration'][class_idx])]])
                else:
                    samplelist['meanStdDurationPerClass'] = np.vstack((samplelist['meanStdDurationPerClass'], np.array(
                        [np.mean(samplelist['duration'][class_idx]), np.std(samplelist['duration'][class_idx])])))
                    samplelist['minMaxDurationPerClass'] = np.vstack((samplelist['minMaxDurationPerClass'], np.array(
                        [np.min(samplelist['duration'][class_idx]), np.max(samplelist['duration'][class_idx])])))
            samplelist_per_fold.append(samplelist)

        return samplelist_per_fold

    def _make_selected_filelist(self):
        folds = []
        folds_names = ['train', 'test']  # TODO: make it more generic
        nb_folds = len(folds_names)
        class_list = self._classes  # list(self._classes.keys())

        for ntc in range(self._nb_classes):
            classpath = self._db_path + '/' + class_list[ntc]

            per_fold = []
            for nf in range(nb_folds):
                foldpath = classpath + '/' + folds_names[nf]
                foldcont = os.listdir(foldpath)
                nb_subdirs = len(foldcont)
                filelist = []
                for ns in range(nb_subdirs):
                    subfoldcont = os.listdir(foldpath + '/' + foldcont[ns])
                    for nfl in range(len(subfoldcont)):
                        if subfoldcont[nfl][0] != '.' and subfoldcont[nfl].endswith('.wav'):
                            filelist.append(
                                class_list[ntc] + '/' + folds_names[nf] + '/' + foldcont[ns] + '/' + subfoldcont[nfl])
                per_fold.append(filelist)
            folds.append(per_fold)

        return folds