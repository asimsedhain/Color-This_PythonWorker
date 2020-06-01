import tensorflow as tf
import cv2 as cv
import numpy as np


# This preprocesses any image so it can be passed into the model
def preprocessor(img, shape):
	# Converint to the 3 channels
	temp_img = cv.cvtColor(img, cv.COLOR_GRAY2RGB) if(len(img.shape)<3) else cv.cvtColor(img, cv.COLOR_BGR2RGB)
	
	# Tensorflow preprocessing
	image = tf.image.convert_image_dtype(temp_img, tf.float32)
	image = tf.image.rgb_to_yuv(image)
	image = tf.image.resize(image, [shape, shape])
	last_dimension_axis = len(image.shape) - 1
	y, u, v = tf.split(image, 3, axis=last_dimension_axis)
	y = tf.subtract(y, 0.5)
	y = tf.reshape(y, (1, shape, shape, 1))

	return y


# This postprocesses the out of the model so it can stroed in the database
def postprocessor(p_img, g_img, shape, scale_preprocessed_image):

	# reversing the normalization
	preprocessed_image = tf.add(p_img, 0.5)

	# scaling the preprocessing image if the flag is set to true
	if(scale_preprocessed_image):
		preprocessed_image = tf.image.resize(preprocessed_image, (shape, shape), tf.image.ResizeMethod.BICUBIC)

	# resizing the generated image to the appropriate size
	generated_image = tf.image.resize(g_img, (shape,shape), tf.image.ResizeMethod.BICUBIC)
	
	# Combining the preprocessed image and generated image. Then converting them to rgb
	last_dimension_axis = len(g_img.shape) - 1
	generated_image = tf.concat([preprocessed_image,generated_image],last_dimension_axis) 
	generated_image = tf.image.yuv_to_rgb(generated_image)

	# RGB to BRG conversion
	channels = tf.unstack (generated_image, axis=-1)
	generated_image = tf.stack   ([channels[2], channels[1], channels[0]], axis=-1)

	# normalizing to 0-255
	generated_image = generated_image.numpy()
	generated_image = cv.normalize(generated_image, generated_image, 0, 255, cv.NORM_MINMAX)

	return generated_image[0]
	

def processing(generator, message):
	# decode the image
	original_image = cv.imdecode(np.frombuffer(bytes(message["original"]["data"]), np.uint8), -1)
	
	# preprocess the image
	preprocessed_image= preprocessor(original_image, 128)

	# preprocessed image of size 256*256
	preprocessed_image_256 = preprocessor(original_image, 256)

	# Generating the colors
	generated_image = generator(preprocessed_image)

	# Postprocessing
	final_image = postprocessor(preprocessed_image_256, generated_image, 256, False)
	
	# original image resized to be saved in the database
	original_resized_image = cv.resize(original_image, (256, 256))


	return final_image, original_resized_image

