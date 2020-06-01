import tensorflow as tf
import redis
import cv2 as cv
import numpy as np
import pymongo
import os
from bson.objectid import ObjectId
import time
from datetime import datetime
import json
import traceback
from util import processing

list_name = os.getenv("LIST_NAME")
DB_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME")
DB_COLLECTION = os.getenv("DB_COLLECTION")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")



print(f"{datetime.now()}: Connecting to Database", flush=True)
client = pymongo.MongoClient(DB_URI)
print(f"{datetime.now()}: Connected to Database", flush=True)

print(f"{datetime.now()}: Loading the Model", flush=True)
generator = tf.keras.models.load_model("./color_generator_100.h5")
print(f"{datetime.now()}: Model Loaded", flush=True)


print(f"{datetime.now()}: Connecting to Queue", flush=True)
redis_client = redis.Redis(host = REDIS_URL, port=REDIS_PORT, password=REDIS_PASSWORD)
finished_list = redis_client
print(f"{datetime.now()}: Connected to Queue", flush=True)



def updateDocument(post_id,original_buffer, color_buffer):
	result = client[DB_NAME][DB_COLLECTION].update_one({'_id': ObjectId(post_id)}, {'$set': {"original":original_buffer, 'color':color_buffer}})
	return result

def insertDocument(message):
	result = client[DB_NAME][DB_COLLECTION].insert_one(message)
	return result


while(True):
	message = redis_client.rpop(list_name)

	if(message):
		# getting the message and message id
		message = json.loads(message)

		# processing the image
		# if there is an error, it will pass an black image 
		try:
			final_image, original_resized_image = processing(generator, message)		
		except Exception as error:
			traceback.print_exc()
			final_image, original_resized_image = np.zeros((256, 256)), np.zeros((256, 256))

		is_success, color_image_buffer = cv.imencode(".jpg", final_image)
		is_success, original_resized_image_buffer = cv.imencode(".jpg", original_resized_image)

		# Updating the database
		result = insertDocument( {**message, "_id":ObjectId(message['_id']) ,"original": original_resized_image_buffer.tostring(), "color": color_image_buffer.tostring() })
		finished_list.set(message["_id"], "true")		

		print(f"{datetime.now()}: Inserted into the database and finished list: {result.inserted_id}", flush=True)

	time.sleep(0.001)

