import scipy, numpy, shutil, os, nibabel
import sys, getopt
import imageio


def niiConvert(inputfile, outputdirectory):
    # print('Input file is ', inputfile)
    # print('Output folder is ', outputdirectory)
    fileNames = []
    # set fn as your 4d nifti file
    image_array = nibabel.load(inputfile).get_data()
    # print(len(image_array.shape))

    # if 4D image inputted
    if len(image_array.shape) == 4:
        # set 4d array dimension values
        nx, ny, nz, nw = image_array.shape

        # set destination folder
        if not os.path.exists(outputdirectory):
            os.makedirs(outputdirectory)
            # print("Created ouput directory: " + outputdirectory)

        # print('Reading NIfTI file...')

        total_volumes = image_array.shape[3]
        total_slices = image_array.shape[2]

        # iterate through volumes
        for current_volume in range(0, total_volumes):
            slice_counter = 0
            # iterate through slices
            for current_slice in range(0, total_slices):
                if (slice_counter % 1) == 0:
                    # rotate or no rotate
                    data = image_array[:, :, current_slice, current_volume]

                    # alternate slices and save as png
                    # print('Saving image...')
                    image_name = (
                        inputfile[:-4]
                        + "_t"
                        + "{:0>3}".format(str(current_volume + 1))
                        + "_z"
                        + "{:0>3}".format(str(current_slice + 1))
                        + ".png"
                    )
                    imageio.imwrite(image_name, data)
                    # print('Saved.')

                    # move images to folder
                    # print('Moving files...')
                    src = image_name
                    shutil.move(src, outputdirectory)
                    fileNames.append(os.path.basename(src))
                    slice_counter += 1
                    # print('Moved.')

        # print('Finished converting images')

    # else if 3D image inputted
    elif len(image_array.shape) == 3:
        # set 4d array dimension values
        nx, ny, nz = image_array.shape

        # set destination folder
        if not os.path.exists(outputdirectory):
            os.makedirs(outputdirectory)
            # print("Created ouput directory: " + outputdirectory)

        # print('Reading NIfTI file...')

        total_slices = image_array.shape[2]

        slice_counter = 0
        # iterate through slices
        for current_slice in range(0, total_slices):
            # alternate slices
            if (slice_counter % 1) == 0:
                # rotate or no rotate
                data = image_array[:, :, current_slice]

                # alternate slices and save as png
                if (slice_counter % 1) == 0:
                    # print('Saving image...')
                    image_name = (
                        inputfile[:-4]
                        + "_z"
                        + "{:0>3}".format(str(current_slice + 1))
                        + ".png"
                    )
                    imageio.imwrite(image_name, data)
                    # print('Saved.')

                    # move images to folder
                    # print('Moving image...')
                    src = image_name
                    src_folder = os.path.dirname(os.path.abspath(src))
                    if not src_folder == outputdirectory:
                        shutil.move(src, outputdirectory)
                    fileNames.append(os.path.basename(src))
                    slice_counter += 1
                    # print('Moved.')

        # print('Finished converting images')
    # else:
    # print('Not a 3D or 4D Image. Please try again.')
    return fileNames
