import unittest
import numpy as np
import tensorflow as tf
from util import preprocessor
from util import postprocessor

class Test_Util(unittest.TestCase):
	def test_preprocessor(self):
		'''
			Testing preprocessor util function
			Output shape should match 
		'''
		shape = 128
		img = np.zeros((256, 256, 3), np.uint8)
		preprocessed_img = preprocessor(img, shape)
		self.assertEqual((1, shape, shape, 1), preprocessed_img.numpy().shape)

	def test_postprocessor(self):
		'''
			Testing post processor util function
			Output shape should match
		'''
		preprocessed_img = tf.zeros((1, 256, 256, 1))
		generated_img = tf.zeros((1, 128, 128, 2))
		final_img = postprocessor(preprocessed_img, generated_img, 256, False)
		self.assertEqual(final_img.shape, (256, 256, 3))	

		

if __name__ == '__main__':
    unittest.main()
