from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
from imutils import paths
import argparse
import imutils
import cv2
import array


def get_classification_detection(model_path, images_path, output_path):
    print("Model path : " + model_path)
    print("Iamges path : " + images_path)

    i = 0
    output_images = []
    covidFind = False
    total_covid_detected = 0
    # Take images
    imageTabs = sorted(list(paths.list_images(images_path)))

    total_percent_prediction = 0

    # Loop for all images
    for img in imageTabs:
        # load the image
        image = cv2.imread(img)
        orig = image.copy()
        i += 1
        # pre-process the image for classification
        image = cv2.resize(image, (56, 56))
        image = image.astype("float") / 255.0
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)

        # load the trained convolutional neural network
        print("[INFO] loading network...")
        model = load_model(model_path)

        # classify the input image
        (notCovid, covid) = model.predict(image)[0]
        # build the label
        if covid > notCovid:
            print("Image " + str(i) + ": Covid19")
            label = "Covid"
            proba = covid
            label = "{}: {:.2f}%".format(label, proba * 100)
            covidFind = True
            total_covid_detected += 1
            total_percent_prediction += proba * 100
        else:
            print("Image " + str(i) + ": not Covid19")
            label = "Not covid"
            proba = notCovid
            label = "{}: {:.2f}%".format(label, proba * 100)
        # draw the label on the image
        output = imutils.resize(orig, width=400)
        cv2.putText(
            output, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        cv2.imwrite(output_path + "/result" + str(i) + ".png", output)
        output_images.append(output_path + "/result" + str(i) + ".png")

    print("Covid19 in scanner : " + str(covidFind))

    result = {
        "covid_detected": covidFind,
        "total_covid_detected": str(total_covid_detected) + "/" + str(i),
        "percent_prediction": total_percent_prediction / i,
        "output_images_path": output_images,
    }
    return result
