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

def update_tx_code(conn, file, data):
        # for i in glob.glob('/home/nishayadav/Myprojects/lfm_va/*'):
        print(data)
        table_name = None
        cursor = conn.cursor()
        i = file.split("/")[-1]
        print("File under tax code functions:-", file)
        if i.startswith("par"):
            table_name = 'table_par_file'
            cursor.execute(
            f"update {table_name} set tx_cva_rx_w2naf = true where split_part(par_filename, '/', 2) = '{i}'",

        )
            
        
        elif i.startswith("lfm"):
            table_name = 'table_lfm_file'
            cursor.execute(
            f"update {table_name} set tx_cva_rx_w2naf = true where split_part(lfm_file_path, '/', 2) = '{i}'",

        )
            q = f"update table_lfm_file set tx_code_w2naf = array_append(tx_code_w2naf, '{data['tx_code']}') where split_part(lfm_file_path, '/', 2) = '{i}'" 
            
            cursor.execute(q)
        
            print("file is:- ", file)
        

        conn.commit()
        print("Done...")

#getting the folder name
def get_virginia_lfm_ionograms(conn, folder_name):
    print("Folder name", folder_name)
    query = f"select lfm_filename from table_lfm_file tlf where tlf.tx_cva_rx_w2naf is true and lfm_file_path like '%{folder_name}%'"

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
    # print(unfiltered_data)
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
    