import cProfile
import datetime
import os
import pstats
import time
import mysql.connector
import numpy as np
import random
import copy
import threading
import zlib
import base64
import signal

global totalepisode, stop_requested

class DatabaseManager:
	def __init__(self):
		self.db_config = {
			'user': os.getenv('DB_USER'),
			'password': os.getenv('DB_PASSWORD'),
			'host': os.getenv('DB_HOST'),
			'database': os.getenv('DB_NAME')
		}

	def execute_query(self, query, params, retry_attempts=5):
		for attempt in range(retry_attempts):
			try:
				conn = mysql.connector.connect(**self.db_config)
				cursor = conn.cursor()
				cursor.execute(query, params)
				conn.commit()
				cursor.close()
				conn.close()
				return
			except mysql.connector.errors.DatabaseError as e:
				if e.errno == 1205:  # ER_LOCK_WAIT_TIMEOUT
					if attempt < retry_attempts - 1:
						time.sleep(1)  # Attendre avant de réessayer
						continue
					else:
						print(f"Transaction failed after {retry_attempts} attempts due to lock wait timeout.")
						raise
				else:
					raise
			except Exception as e:
				print(f"Error executing query: {e}")
				raise
			finally:
				if 'conn' in locals() and conn.is_connected():
					cursor.close()
					conn.close()

	def execute_many(self, query, params_list, retry_attempts=5):
		for attempt in range(retry_attempts):
			try:
				conn = mysql.connector.connect(**self.db_config)
				cursor = conn.cursor()
				cursor.executemany(query, params_list)
				conn.commit()
				cursor.close()
				conn.close()
				return
			except mysql.connector.errors.DatabaseError as e:
				if e.errno == 1205:  # ER_LOCK_WAIT_TIMEOUT
					if attempt < retry_attempts - 1:
						time.sleep(1)  # Attendre avant de réessayer
						continue
					else:
						print(f"Transaction failed after {retry_attempts} attempts due to lock wait timeout.")
						raise
				else:
					raise
			except Exception as e:
				print(f"Error executing query: {e}")
				raise
			finally:
				if 'conn' in locals() and conn.is_connected():
					cursor.close()
					conn.close()

	def fetch_one(self, query, params):
		try:
			conn = mysql.connector.connect(**self.db_config)
			cursor = conn.cursor()
			cursor.execute(query, params)
			result = cursor.fetchone()
			cursor.close()
			conn.close()
			return result
		except Exception as e:
			print(f"Error fetching data: {e}")
			return None
		finally:
			if 'conn' in locals() and conn.is_connected():
				cursor.close()
				conn.close()

