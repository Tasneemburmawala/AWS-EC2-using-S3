from flask import Flask, jsonify, request, send_file,render_template,flash,get_flashed_messages
from werkzeug import secure_filename
import config as cfg
import boto3, os, time
from boto3.s3.transfer import S3Transfer
from boto.s3.connection import S3Connection, Bucket, Key


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# upload 
@app.route("/upload", methods=['POST'])
def upload():
    file_name = request.files['file']
    filename = secure_filename(str(time.time()) + file_name.filename)
    dir_name = 'uploads/'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_path = os.path.join(dir_name, filename)
    app.logger.info("Saving file: %s", file_path)
            # save to local
    file_name.save(file_path)
    transfer = S3Transfer(boto3.client('s3', cfg.AWS_REGION, aws_access_key_id=cfg.AWS_APP_ID,
            aws_secret_access_key=cfg.AWS_APP_SECRET))

    transfer.upload_file(file_path, cfg.AWS_BUCKET, file_path)

    flash("FIle uploaded successfully")
    return render_template('index.html')

# display 
@app.route("/display", methods=['POST'])
def display():

    transfer = S3Transfer(boto3.client('s3', cfg.AWS_REGION, aws_access_key_id=cfg.AWS_APP_ID,
                                       aws_secret_access_key=cfg.AWS_APP_SECRET))
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(cfg.AWS_BUCKET)
    
    filenamelist=[]
    for obj in bucket.objects.all():
        key = obj.key
        filename=key.split('/')
        filenamelist.append(filename[1])
        #body = obj.get()['Body'].read()
        print key


    return render_template("download.html",filenamelist=filenamelist)

# download 
@app.route("/download", methods=['POST'])
def download():
    filename=request.form.get("download_file")
    transfer = S3Transfer(boto3.client('s3', cfg.AWS_REGION, aws_access_key_id=cfg.AWS_APP_ID,
                                       aws_secret_access_key=cfg.AWS_APP_SECRET))

    key = 'uploads/' + secure_filename(filename)
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.split(__file__)[0], ''))
    # get file from S3
    transfer = S3Transfer(boto3.client('s3', cfg.AWS_REGION, aws_access_key_id=cfg.AWS_APP_ID,
                                       aws_secret_access_key=cfg.AWS_APP_SECRET))
    # download file from aws
    transfer.download_file(cfg.AWS_BUCKET, key, key)

    return send_file(UPLOAD_DIR + "/" + key,attachment_filename = filename, as_attachment = True)

# delete
@app.route("/delete", methods=['POST'])
def delete():
    file_name1=request.form.get("del_filename")
    print "Filename is "
    print file_name1

    conn = S3Connection(cfg.AWS_APP_ID, cfg.AWS_APP_SECRET)
    bucket = Bucket(conn, cfg.AWS_BUCKET)
    key = 'uploads/' + secure_filename(file_name1)
    k = Key(bucket=bucket, name=key)
    k.delete()
    flash("File Delete successfully")
    return render_template('index.html')

    return file_name1

if (__name__ == "__main__" ):
    app.secret_key = cfg.SECRET_KEY
    app.run("")
