import streamlit as st
import pandas as pd
import numpy as np
import time
import json
from pathlib import Path

st.set_page_config(page_title="Excel File Uploader")

st.info('Hello - this is a prototype')


# Config

def export_state():
	with open('cache.json', 'w') as fp:
		json.dump(data_out, fp)

my_file = Path("cache.json")
if my_file.is_file():
	with open('cache.json') as json_file:
		cache = json.load(json_file)
		st.session_state['configured'] = cache['configured']
		st.session_state['data'] = cache['data']
		st.session_state['other_data'] = cache['other_data']
else:
	st.session_state['configured'] = False
	st.session_state['data'] = {}
	st.session_state['other_data'] = {}


data_out = {}
columns_data = {}

# Logic
if st.session_state['configured'] is False:

	st.write("# Excel File Uploader")

	st.warning('This form has not been configured.')
	st.write("## Step 1: How many columns do you expect?")
	
	number_cols = st.number_input("", 1, 5)

	list_cols = []
	for i in range(0, number_cols):
		list_cols.append("Column {}".format(i+1))
	list_cols.append("Multi-Column Logic")

	st.write("*You may set the column-specific data validation logic*")
	*tabs, = st.tabs(list_cols)

	for i in range(0, number_cols):
		with tabs[i]:
			columns_data[i] = {}
			columns_data[i]['name'] = st.text_input("What is the name of this column".format(i+1), key = i)
			columns_data[i]['unique'] = st.radio("Are duplicates within this column ok?", ["No", "Yes"], key = 10+i)
			columns_data[i]['data_type'] = st.selectbox("What data do you expect in this column?", ["No - i.e. Free Text", "Y/N", "Date (YYYY/MM/DD)", "Money ($)"], key = 20+i)

	col_names = []
	for i in range(0, number_cols):
		col_names.append(columns_data[i]['name'])

	st.session_state['other_data']['col_names'] = col_names

	with tabs[number_cols]:
		options = st.multiselect('Which combination of columns is unique? (i.e. no more than 1 row can have the same combination of values in these selected columns)', col_names)

	st.session_state['other_data']['col_unique'] = options

	st.write("## Step 2: Is this what you expect")

	if st.button("Generate Preview"):		
		st.dataframe(pd.DataFrame(columns = col_names))

	if st.button("Create"):	
		st.session_state['configured'] = True
		data_out['configured'] = st.session_state['configured']
		data_out['data'] = columns_data
		data_out['other_data'] = {}
		data_out['other_data']['col_names'] = st.session_state['other_data']['col_names']
		data_out['other_data']['col_unique'] = st.session_state['other_data']['col_unique']
		export_state()
		st.experimental_rerun()

else:
	st.title("Please submit your report here.")
	uploaded_file = st.file_uploader("Upload the report.")

	if uploaded_file is not None:
	
		with st.spinner('Checking File'):

			# read file
			df = pd.read_excel(uploaded_file)

			# extract dataframe metadata
			num_rows, num_columns = df.shape
			columns_received = list(df.columns)
			columns_expected = st.session_state['other_data']['col_names']

			# check for duplicates
			dup_rows = df[list(st.session_state['other_data']['col_unique'])].duplicated(keep=False)
			dup_rows_index = np.array(df.index[dup_rows]) + 1
			time.sleep(1)

		# check columns
		if not np.array_equal(columns_received, columns_expected):
			st.error('Do not modify the name and sequence of the columns of the template, and do not add new columns.  \n  \n Expected: {}   \n Received: {}'.format(columns_expected, columns_received), icon = "🚨")

		# check for empty datasets
		elif num_rows == 0:
			st.error('No entries detected.', icon="🚨")

		# for loop


		# check for duplicates
		elif np.sum(dup_rows):
			st.error('Duplicate entries detected.  \n  \n Please check rows {}'.format(np.array2string(dup_rows_index, separator=', ')), icon="🚨")

		# success
		else: 
			st.success("Thank you for submitting the report!", icon = "✅")
			st.balloons()

	if st.button("reset"):
		data_out['configured'] = False
		data_out['data'] = {}
		data_out['other_data'] = {}
		export_state()
		st.experimental_rerun()