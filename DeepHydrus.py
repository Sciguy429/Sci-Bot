#Compact reimplementaion of DeepDanbooru's evaluator with added features
#By Sciguy429

import math
import tensorflow as tf
import skimage.transform

class DeepHydrus:
    def __init__(self, modelPath, tagsPath, modelHeight, modelWidth):
        #Set vars
        self.modelPath = modelPath
        self.tagsPath = tagsPath
        self.modelHeight = modelHeight
        self.modelWidth = modelWidth

        #Initilze Tensorflow and model
        self.model = tf.keras.models.load_model(modelPath)
        self.tags = self.load_tags(tagsPath)

    def load_tags(self, tags_path):
        with open(tags_path, 'r') as tags_stream:
            tags = [tag for tag in (tag.strip() for tag in tags_stream) if tag]
            return tags


    def transform_and_pad_image(self, image, target_width, target_height, scale=None, rotation=None, shift=None, order=1, mode='edge'):
        """
        Transform image and pad by edge pixles.
        """
        image_width = image.shape[1]
        image_height = image.shape[0]
        image_array = image

        # centerize
        t = skimage.transform.AffineTransform(
            translation=(-image_width * 0.5, -image_height * 0.5))

        if scale:
            t += skimage.transform.AffineTransform(scale=(scale, scale))

        if rotation:
            radian = (rotation / 180.0) * math.pi
            t += skimage.transform.AffineTransform(rotation=radian)

        t += skimage.transform.AffineTransform(
            translation=(target_width * 0.5, target_height * 0.5))

        if shift:
            t += skimage.transform.AffineTransform(
                translation=(target_width * shift[0], target_height * shift[1]))

        warp_shape = (target_height, target_width)

        image_array = skimage.transform.warp(
            image_array, (t).inverse, output_shape=warp_shape, order=order, mode=mode)
        
        image_array = image_array / 255.0

        image_shape = image_array.shape
        image_array = image_array.reshape((1, image_shape[0], image_shape[1], image_shape[2]))

        return image_array

    def evaluate(self, image_path, threshold):
        image_raw = tf.io.read_file(image_path)
        image = tf.io.decode_png(image_raw, channels=3)
        image = tf.image.resize(image, size=(self.modelHeight, self.modelWidth), method=tf.image.ResizeMethod.AREA, preserve_aspect_ratio=True)
        image = image.numpy()

        scaledImage = self.transform_and_pad_image(image, self.modelWidth, self.modelHeight)

        results = self.model.predict(scaledImage)[0]

        result_dict = {}
        for i, tag in enumerate(self.tags):
            result_dict[tag] = results[i]

        culledTags = {}
        if (threshold != 0):
            for tag, certainty in result_dict.items():
                if (certainty >= threshold):
                    culledTags[tag] = certainty
        else:
            culledTags = result_dict
            
        return culledTags
