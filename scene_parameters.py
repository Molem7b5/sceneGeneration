# parameters used to generate scenes

def get_params(argv='1'):
    print(f"SET: {argv}")
    ###  default params for NIGENS dataset ####

    params = dict(
        db_name='NIGENS',  # name of the audio dataset used for data generation
        rirpath='D:\Dan_PC_Stuff\Google_drive\PhD\Rig_IRs/', # path containing Room Impulse Responses (RIRs)
        rirdata='D:\Dan_PC_Stuff\Google_drive\PhD\Rig_IRs/IR_pos.mat',
        mixturepath='D:\Dan_PC_Stuff/NIGENS_scenes', # output path for the generated dataset
        noisepath='D:\Dan_PC_Stuff\Google_drive\PhD\Rig_IRs\Listening_room_ambience', # path containing background noise recordings
        nb_folds=1,  # number of folds (default 2 - training and testing)
        nb_mic_arrays=11,

        # rooms2fold they assign different rooms to each of the folds - good for testing as introduces new environments

        # I'm going to split into test train splits later on so am using all the mic arrays for all the folds
        # I think it's fine because I'm not wanting to predict from mic arrays the network hasn't seen (though this would be interesting )


        rooms2fold=[[10, 6, 1, 4, 3, 8],  # FOLD 1, rooms assigned to each fold (0's are ignored)
                    [9, 5, 2, 0, 0, 0]],  # FOLD 2
        micarrays=[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],

        db_path='D:\Dan_PC_Stuff/NIGENS', # path containing audio events to be utilized during data generation
        max_polyphony=3,  # maximum number of overlapping sound events
        active_classes=[0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13],  # list of sound classes to be used for data generation
        nb_mixtures_per_fold=[300],  # if scalar, same number of mixtures for each fold
        nb_mixtures=[300],
        mixture_duration=60.,  # in seconds
        event_time_per_layer=40.,  # in seconds (should be less than mixture_duration)
        audio_format='foa',  # 'foa' (First Order Ambisonics) or 'mic' (four microphones) or 'both'
        )
    #### user defined parmeters
    if argv == '1':
        print(" USING DEFAULT PARAMETERS FOR NIGENS DATASET\n")

    else:
        print(f"Error: unknown argument {argv}")
        exit()

    for key, value in params.items():
        print(f"\t{key}: {value}")
    return params