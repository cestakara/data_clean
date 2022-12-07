#import library regex, pandas, sqlite
import re
import sqlite3 as sql
import pandas as pd

#import library flask
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

#define app for flask
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

#define description for Swagger 
swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API for Text Data Cleansing by Widhiasta'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'API ini dibuat untuk membersihkan data text dibuat oleh Widhiasta')
        }, 
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers":[],
    "specs":[
        {
        "endpoint":'docs',
        "route":'/docs.json'
        }
     ],
    "static_url_path":"/flasgger_static",
    "swagger_ui":True,
    "specs_route":"/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

#lowercase alphabet
def lowercase(s):
    return s.lower()

#clean unwanted character  
def clean(s):
    #Remove USER, RT, RETWEET, URL, http, https
    s = re.sub('user|rt|retweet|url|http|https',' ', s)
    #Remove text berawalan angka
    s = re.sub('(\d{1,})', ' ', s)
    #Remove emoji
    s = re.sub(r'\\x[a-z0-9]+', ' ', s)
    #Clean non alfanumerik except space,!,?
    s = re.sub('[^a-z0-9\s\!\?]+', ' ', s)
    #Remove enter (\n)
    s = re.sub(r'\n',' ', s)
    #Remove spasi lebih dari 1
    s = re.sub('\s\s+', ' ', s)
    #Replace 'gue - saya'
    s = re.sub('gue','saya', s)
    #Replace 'loe - anda'
    s = re.sub('loe', 'anda', s)
    return s

db = sql.connect('database.db' , check_same_thread=False)
q_kamus_alay= 'select * from kamus_alay'
t_kamus_alay=  pd.read_sql_query(q_kamus_alay, db)
q_abusive = 'select * from abusive'
t_abusive = pd.read_sql_query(q_abusive, db)


def replace_alay(s):
    kamus_alay = dict(zip(t_kamus_alay['anakjakartaasikasik'],t_kamus_alay['anak jakarta asyik asyik']))
    for i in kamus_alay:
        return ' '.join([kamus_alay[i] if i in kamus_alay else i for i in s.split(' ')])


def remove_abusive (s):
    abusive_words = t_abusive['ABUSIVE'].str.lower().tolist()
    word_list = s.split()
    return ' '.join([s for s in word_list if s not in abusive_words ])

#cleansing all#
def text_cleansing (s):
    s = lowercase(s)
    s = clean(s)
    s = replace_alay(s)
    s = remove_abusive(s)
    return s


#POST METHOD#
@swag_from("docs/input_data.yml", methods=['POST'])
@app.route('/input_data', methods=['POST'])
def input ():
    input_text = request.form.get('input_data')
    output_text = text_cleansing(input_text)
    print(output_text)
    db.execute('create table if not exists input_data (input_text varchar(255), output_text varchar(255))')
    query_text = 'insert into input_data (input_text , output_text) values (?,?)'
    val = (input_text,output_text)
    db.execute(query_text,val)
    db.commit()

    return_text = { "input" :input_text, "output" : output_text}
    return jsonify (return_text)

@swag_from("docs/upload_data.yml", methods=['POST'])
@app.route('/upload_data', methods=['POST'])
def upload():
    file = request.files["upload_data"]
    df_csv = (pd.read_csv(file, encoding="latin-1"))

    df_csv['new_tweet'] = df_csv['Tweet'].apply(text_cleansing)
    df_csv.to_sql("clean_tweet", con=db, index=False, if_exists='append')
    db.close()

    cleansed_tweet = df_csv.new_tweet.to_list()

    return_file = {
        'output' : cleansed_tweet}
    return jsonify(return_file)

#GET METHOD#
@swag_from("docs/get_all.yml", methods=['GET'])
@app.route('/get_text', methods=['GET'])
def readAll():
    returnData = getAllTableData()
    return jsonify({'data ' : returnData})
    
@swag_from("docs/get_id.yml", methods=['GET'])
@app.route('/get_text/<string:idText>', methods=['GET'])
def readID(idText):
    dataToReturn = getTableDataByID(idText)
    return jsonify({'data ' : dataToReturn})


if __name__ == '__main__':
    app.run(debug=True)