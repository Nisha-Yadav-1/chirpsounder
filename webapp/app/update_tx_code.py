import psycopg2

#Name               :               Nisha Yadav
#Function Name      :               create_db_connection
#Functionality      :               Create database connection

def create_db_connection():
    conn_args = {
            "user": "postgres",
            "password": "Welcome@123",
            "host": "127.0.0.1",
            "port": "5432",
            "database": "h5db",
        }
    conn = psycopg2.connect(**conn_args)
    
    return conn
    
#Name               :               Nisha Yadav
#Function Name      :               update_virginia_tx_code
#Functionality      :               Updating TX_CODE_VA field in DB

def update_tx_code(conn, file, data, flag):
        print(data)
        table_name = None
        cursor = conn.cursor()
        i = file.split("/")[-1]
        print("File under tax code functions:-", file)
        if flag:
            table_name = 'table_lfm_file'
            cursor.execute(
            f"update {table_name} set classification_flag = {flag} where split_part(lfm_file_path, '/', 2) = '{i}'",

        )
            q = f"update table_lfm_file set tx_code_w2naf = array_append(tx_code_w2naf, '{data['tx_code']}') where split_part(lfm_file_path, '/', 2) = '{i}'" 
            
            cursor.execute(q)
        
            print("file is:- ", file)

        else:
            f"update {table_name} set classification_flag = {flag} where split_part(lfm_file_path, '/', 2) = '{i}'",


        conn.commit()
        print("Done...")

def get_virginia_lfm_ionograms_api(conn, folder_name):
    print("Folder name", folder_name)
    query = f"select lfm_filename from table_lfm_file tlf where tlf.classification_flag is true and lfm_file_path like '%{folder_name}%'"

    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    data = [i[0] for i in data]
    return data

#getting the folder name
def get_virginia_lfm_ionograms(conn, folder_name):
    print("Folder name", folder_name)
    query = f"select lfm_filename from table_lfm_file tlf where tlf.classification_flag is true and lfm_file_path like '%{folder_name}%'"

    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    data = [i[0] for i in data]
    data = enumerate(data)
    return data
#All the filtered ionograms
def get_unfiltered_ionograms(conn, folder_name):
    query = f"select lfm_filename, tx_code_w2naf from table_lfm_file tlf where tlf. lfm_file_path like '%{folder_name}%'"
    unfiltered_data = []
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    counter = 1
    for i in data:
        unfiltered_data.append(
             {
             "sr_no": counter,
             "filename": i[0],
             "tx_code": i[1],
             "png_filename": f"{i[0].replace('h5', 'png')}"
             }
             )
        counter = counter + 1

    return unfiltered_data

#By using this function searching functionality is working. User would be able to choose TX-Code , RX-code and data-range to search data related to them. User can user individually these parameters and combination as well.
def get_search_data(conn, tx_code, start_date, end_date):

    if start_date and end_date and tx_code != 'Choose TX Code':
        query = f"select lfm_filename, tx_code_w2naf, split_part(lfm_file_path, '/', 1) from table_lfm_file tlf where '{tx_code}' = any(tx_code_w2naf) and date >= '{start_date}' and date <= '{end_date}'"

    elif start_date and end_date:
        query = f"select lfm_filename, tx_code_w2naf, split_part(lfm_file_path, '/', 1) from table_lfm_file tlf where date >= '{start_date}' and date <= '{end_date}'"
    else:
        query = f"select lfm_filename, tx_code_w2naf, split_part(lfm_file_path, '/', 1) from table_lfm_file tlf where '{tx_code}' = any(tx_code_w2naf)"

    unfiltered_data = []
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    counter = 1
    for i in data:
        
        unfiltered_data.append(
             {
             "sr_no": counter,
             "filename": i[0],
             "tx_code": i[1],
             "png_filename": f"{i[0].replace('h5', 'png')}",
             "selected_date": i[2]
             }
             )
        counter = counter + 1

    return unfiltered_data




def get_folder_date(conn, tx_code):
    folder = []
    cursor = conn.cursor()
    query = f"select split_part(lfm_file_path, '/', 1) from table_lfm_file tlf where '{tx_code}' = any(tx_code_w2naf) group by split_part(lfm_file_path, '/', 1)"
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    for i in data:
        
        folder.append(
             {
             "date": i[0]
             }
             )
    print(folder)
    return folder


def total_no_ionograms(txcode, conn):

    folder = {} 
    # Creating cursor object
    cursor = conn.cursor()
    #  Total no. of ionograms
    cursor.execute("select count(*) from table_lfm_file tlf;")

    cursor1 = conn.cursor()
    # Total filtered ionograms
    cursor1.execute(f"select count(*) from table_lfm_file tlf where '{txcode}' != any(tx_code_w2naf)")

    cursor2 = conn.cursor()
    #  Total unfiltered ionograms
    cursor2.execute(f"select count(*) from table_lfm_file tlf where '{txcode}' = any(tx_code_w2naf)")


    start_date = conn.cursor()
    start_date.execute("select date as start_date from table_lfm_file tlf order by date asc limit 1;")
    end_date = conn.cursor()
    end_date.execute(f"select date as last_date from table_lfm_file tlf2 order by date desc  limit 1;")
    total_filtered_ionograms = cursor2.fetchall()[0][0]
    x = cursor.fetchall()[0][0]
    y = cursor1.fetchall()[0][0]

    st_date = start_date.fetchall()[0][0]
    ed_date = end_date.fetchall()[0][0]
    folder.update(
    {
    "total_ionograns": x,
    "total_unclassified": x - total_filtered_ionograms - y,
    "total_filtered":total_filtered_ionograms,
    "unfiltered": y,
    "start_date":str(st_date),
    "end_date":str(ed_date)
    }
    )
    return folder
    





def get_ionograms_after_summary(conn, flag, tx_code=None):
    print(flag, tx_code)
    if flag == 'total':
        query = f"select lfm_filename from table_lfm_file"
    elif flag == 'unfiltered':
        print('inside')
        query = f"select split_part(lfm_file_path, '/', 1), lfm_filename, tx_code_w2naf, station_name from table_lfm_file tlf where not '{tx_code}' = any(tx_code_w2naf)"
    else:
        query = f"select split_part(lfm_file_path, '/', 1),lfm_filename, tx_code_w2naf, station_name from table_lfm_file tlf where '{flag}' = any(tx_code_w2naf)"

    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    print("Data", data)
    data = [{'filename': i[1], 'date': i[0], 'tx_code': i[2], 'station_name': i[3]} for i in data]
    data = enumerate(data)
    return data




def get_files_for_previous_next(conn, folder_name, tx_code):
    query = f"select lfm_filename from table_lfm_file tlf where '{tx_code}' = any(tx_code_w2naf) and date = '{folder_name}'"
    cursor = conn.cursor()
    cursor.execute(query)
    files = cursor.fetchall()

    return files


def clearClassification(conn):
#     update table_lfm_file set tx_code_w2naf = Null  where lfm_file_path = '2022-05-24/lfm_ionogram-000-1653357033.01.h5' 
#  select * from table_lfm_file tlf where  lfm_file_path = '2022-05-24/lfm_ionogram-000-1653357033.01.h5' 

    query = f"update table_lfm_file set tx_code_w2naf = Null"

    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    
