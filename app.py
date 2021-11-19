import flask
from flask import request, jsonify, send_from_directory, make_response
from flask_cors import CORS, cross_origin
import os
from configparser import ConfigParser
import json
import pandas
import subprocess
import fnmatch
import shutil
from distutils.dir_util import copy_tree
import requests as req
import gzip


"""
This API server is made according to "Koa cert generation feature_sample" referencing the 4 main api used there:
1. create_group_api = 'https://api.accredible.com/v1/issuer/groups'
2. search_group_api = 'https://api.accredible.com/v1/issuer/groups/search'
3. search_credential_api = 'https://api.accredible.com/v1/credentials/search'
4. create_credential_api = 'https://api.accredible.com/v1/credentials'

Required library are stated above

Some validation haven't been done, some are still hard coded, no authorization token yet, currently works according to the postman usage.
Installation should be as easy: creat venv in the app.py folder, then navigate 1 by 1 to the blockcert app and use pip install -r requirements.txt. for cert-issuer, follow the steps in the cert-issuer github + pip install -r requirements.txt AND pip install -r ethereum_requirements.txt

To-DO:
- manage inputs from openEDX to be written to conf.ini, referencing from accredible API <-- should be done
- manage return to match accredible api output <-- should be done
"""



dir_path=os.path.abspath(os.getcwd())


app = flask.Flask(__name__)

app.config["DEBUG"] = True

@app.route('/issuer_id/<issuer_id>',methods=['GET'])
@cross_origin()
def send_issuerId(issuer_id):
    my_dir = str(dir_path)+"/static"
    print (my_dir)
    return send_from_directory(my_dir,issuer_id)

@app.route('/api/v1/viewer/<transaction_id>',methods=['GET'])
@cross_origin()
def view(transaction_id):
    tx_id = transaction_id
    data_request = request
    print(data_request)
    my_headers = {'Authorization' : ''}
    get_data = req.get(""+tx_id,headers=my_headers)
    #print (get_data.json())
    response = get_data.json()
    #response_obj = response.loads(response)

    '''
    data = {
        "jsonrpc":"2.0",
        "id":1,
        "result":{
            "blockHash":str(response["blockHash"]),
            "blockNumber":str(response["blockNumber"]),
            "from":str(response["from"]),
            "gas":"",
            "gasPrice":str(response["gasProvided"]),
            "maxFeePerGas":"",
            "maxPriorityFeePerGas":"",
            "hash":str(response["hash"]),
            "input":str(response["inputBytes"]),
            "nonce":"",
            "to":str(response["to"]),
            "transactionIndex":str(response["index"]),
            "value":"",
            "type":"",
            "accessList":[

            ],
            "chainId":"0x1",
            "v":"0x0",
            "r":str(response["previousHash"]),
            "s":str(response["nextHash"])
        }
    }
    data_json = json.dumps(data)
    '''

    '''
    #compressed_response = gzip.compress(json.dumps(response).encode('utf8'))
    response_format = make_response(json.dumps(response),mimetype='application/json')
    #response_format.headers['Access-Control-Allow-Origin']=<origin>
    response_format.headers['Access-Control-Allow-headers']='Content-Type'
    response_format.headers['Access-Control-Allow-METHODS']='GET, POST, OPTIONS'
    response_format.headers['connection']='keep-alive'
    #response_format.headers['Vary']='Accept-Encoding'
    #response_format.headers['Content-Encoding']='gzip'
    #response_format.headers['X-Powered-By']='Express'
    response_format.headers['content-type']='application/json'
    '''
    #return response_format
    return jsonify(response)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Testing API for open edx integration with blockcerts</h1><p>This site is a prototype API for open edx integration with blockcerts</p>"


#this api creates groups/templates (DONE, only name formatting needs to be changed and images link)
@app.route('/api/v1/issuer/groups', methods=['POST'])
def create_group():
    """

    THIS API IS NOT CALLED FROM KOA CERT GENERATION FILE. (maybe) groups are created when institute makes their group


    """

    msg=""

    #check if request is json so data is not None
    if request.is_json:
        data = request.json
    else:
        return jsonify({"msg":"data does not have content type application/json!"})

    issuer_id_output = "cert-tools/sample_data/issuer_id/"+str(data["group"]["name"]).replace(" ","_")+".json"
    group_name = str(data['group']['name'])

    #TODO: Change the issuer_id_url and issuer_pubkey according to the insitute issuer
    #issuer_id_url=  "http://localhost:5000/issuer_id/"+group_name+".json"
    issuer_id_url = "http://127.0.0.1:5000/issuer_id/edx.json"
    issuer_pubkey = "0x88D2a0D90B290d7233045E364501F9DD8B3680Cf".lower()
    #pubkey in cert-tools config file needs to be lower as cert-verifier (the python one) will fail to check if not. for the js, havem't tested yet

    #this below might not be needed if the issuer is only 1 organization (generate sendiri nanti sesuai dari website icei + gambar mereka)
    """
    issuer_conf = ConfigParser()
    issuer_conf.read("cert-tools/issuer_conf.ini")
    issuer_conf.set("configurations","issuer_public_key","ecdsa-koblitz-pubkey:"+issuer_pubkey) #blockchain address for issuing
    #issuer_conf.set("configurations","revocation_address",data["credential"]["meta_data"]["issuer_pub_key_revocation"]) #blockchain address for revocation
    issuer_conf.set("configurations","issuer_id",issuer_id_url)
    issuer_conf.set("configurations","issuer_name",str(data["group"]["name"]))
    issuer_conf.set("configurations","output_file",issuer_id_output)
    issuer_conf.set("configurations","issuer_url",str(data["group"]["meta_data"]["issuer_url"]))
    with open('cert-tools/issuer_conf.ini', 'w') as f:
        issuer_conf.write(f)

    try:
        run_create_issuer = subprocess.run(['python3','cert-tools/cert_tools/create_v2_issuer.py','-c','cert-tools/issuer_conf.ini']) #runs the create_v2_issuer.py
    except:
        return jsonify({"msg":"error creating issuer id"})
    """


    #this function writes the data from api call to conf.ini file
    #below is setting config for creating the templates/groups
    #EVERY detailed configuration can be seen in conf.ini file (in cert-tools folder or from github). link to cert-tools github https://github.com/blockchain-certificates/cert-tools

    cert_conf = ConfigParser()
    cert_conf.read("cert-tools/conf.ini")
    cert_conf.set("issuer information","issuer_url",str(data["group"]["course_link"])) #get issuer url
    cert_conf.set("issuer information","issuer_email",str(data["group"]["meta_data"]["email"])) #get issuer email
    cert_conf.set("issuer information","issuer_name",str(data["group"]["name"])) #get issuer name
    cert_conf.set("issuer information","revocation_list","https://www.blockcerts.org/samples/2.0/revocation-list-testnet.json") #get revocation list. Stated as unused in the cert-tools github
    cert_conf.set("issuer information","issuer_signature_lines","""{"fields": [{"job_title": "University Issuer","signature_image": "images/issuer-signature.png","name":"your signature"}]}""") #signature lines Can be inputted if needed
    #if(data["group"]["blockchain"]==True): <-- this probably isn't needed if all credentials are going to be issued to blockchain
    cert_conf.set("issuer information","issuer_public_key","ecdsa-koblitz-pubkey:"+issuer_pubkey) #public key of issuer. Enter information in the metadata section
    cert_conf.set("issuer information","issuer_id",issuer_id_url)
    cert_conf.set("certificate information","certificate_description",str(data["group"]["course_description"]))
    cert_conf.set("certificate information","certificate_title",str(data["group"]["course_name"]))
    cert_conf.set("certificate information","criteria_narrative",str(data["group"]["course_description"])) #currently set equal with certificate description
    #cert_conf.set("certificate information","badge_id",str(data["group"]["department_id"])) #dont know what to input. This is required by cert-tools, currently set to default from the blockcerts github

    #currently, the template_file_name is the group id
    template_file_name = "course-v1:"+str(data["group"]["name"]).replace(" ","_").lower()+"+"+str(data["group"]["course_name"]).replace(" ","_").lower()

    #template file name should look like this group+name_course+name.json. Formatting can be changed
    cert_conf.set("template data","template_file_name",template_file_name+'.json')

    #write the conf in cert-tools/conf.ini
    with open('cert-tools/conf.ini', 'w') as f:
        cert_conf.write(f)

    #run the create-certificate-template
    try:
        run_cert_tools = subprocess.run(['create-certificate-template','-c','cert-tools/conf.ini']) #can add '-c','myconf.ini' after 'create_certificate_template' to the conf file if this failed
        msg="Create template succeeded!"
    except Exception as e:
        msg="error creating template; "
        msg = msg+str(e)
        return jsonify({"msg":msg})

    #open the created certificate
    with open(dir_path+"/cert-tools/"+cert_conf["template data"]["data_dir"]+"/"+cert_conf["template data"]["template_dir"]+"/"+template_file_name+'.json', 'r') as f:
        return_json = json.load(f)
    #format the return data so that it's the same as accredible
    value ={
        "groups": {
            "id": template_file_name,
            "name": template_file_name,
            "course_description": str(return_json["badge"]["description"]),
            "course_name": str(return_json["badge"]["name"]),
            "learning_outcomes": [
            ],
            "attach_pdf": False,
            "course_link": "some url",
            "language": "en",
            "design_name": "test",
            "updated_at": "",
            "created_at": "",
            "design_id": None,
            "blockchain": True,
            "certificate_design_id": None,
            "badge_design_id": str(return_json["badge"]["id"]).split(":")[2],
            "department_id": None,
            "meta_data": {
            }
        }
    }
    return jsonify(value)

#this api finds 1 group
@app.route('/api/v1/groups/search', methods = ['POST'])
def search_group():
    if request.is_json:
        data = request.json
    else:
        return jsonify({"msg":"data does not have content type application/json!"})

    #loads data from cert templates to convert it accordingly to what accredible returns. currently format of name variable is: group name_course name
    cert_id = str(data["name"]).lower()+'.json'
    #print (name)

    group = {
        'groups':[]
        }

    try:
        #with open('cert-tools/sample_data/certificate_templates/'+cert_id+'.json', 'r') as myfile:
            #group_data = myfile.read()
        #group_json=json.loads(group_data)
        folder = dir_path+'/cert-tools/sample_data/certificate_templates/'
        print (folder)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder,filename)
            if cert_id == filename.lower():
                cert_path = file_path
                print (cert_path)
                with open(cert_path, 'r') as f:
                    group_json = json.load(f)
                identity = str(group_json["badge"]["id"])
                name = str(group_json["badge"]["issuer"]["name"])
                course_description=str(group_json["badge"]["description"])
                course_name=str(group_json["badge"]["name"])
                course_link = str(group_json["badge"]["issuer"]["url"])
                groups_list={
                    'id': cert_id.split('.')[0],
                    'name': filename.split('.')[0],
                    'course_description': course_description,
                    'course_name': course_name,
                    'learning_outcomes': None,
                    'attach_pdf': False,
                    'course_link': course_link,
                    'language': "en",
                    'design_name': None,
                    'updated_at': None,
                    'created_at': None,
                    'design_id': None,
                    'blockchain': True,
                    'certificate_design_id': 23,
                    'badge_design_id': identity.split(":")[2],
                    'department_id': None,
                }
                group['groups'].append(groups_list)

    except:
        return jsonify({"msg":"No group data exist!"})



    #this returns 1 result only

    return jsonify(group)

#This api create certificate in cert-tools and issue it automatically to blockchain. Writing the blockchain config is not yet made/not neccessary if issuer is only 1
@app.route('/api/v1/credentials', methods=['POST'])
def create_certificate():
    #Gets data from api call
    if request.is_json:
        data = request.json
    else:
        return jsonify({"msg":"data does not have content type application/json!"})


    """
    #this records the data to write as csv using pandas module. This is for bulk create, commented just in case it's needed
    recipient=[]
    for x in data["credentials"]:
        recipient_name=str(x["recipient"]["name"])
        recipient_email=str(x["recipient"]["email"])
        recipient_id="ecdsa-koblitz-pubkey:"+str(x["recipient"]["pubkey"]) #uses pubkey POSTed in recipient
        recipient_temp=[recipient_name,recipient_id,recipient_email]
        recipient.append(recipient_temp)
    mainnet = pandas.DataFrame(recipient)
    column_name=['name','pubkey','identity']
    mainnet.to_csv('cert-tools/sample_data/rosters/roster_kaleido.csv', index=False, header=column_name)
    """
    #group_id = str(data["group_id"]).lower()+'.json' #this group_id should be the same as the one saved in sample_data/certificate_templates. CURRENTLY not yet implement different group id bulk create


    #below is for creating certificate
    #EVERY detailed configuration can be seen in conf.ini file (in cert-tools folder or from github). link to cert-tools github https://github.com/blockchain-certificates/cert-tools
    if 'name' not in data["credential"]["recipient"] or 'email' not in data["credential"]["recipient"]:
        return jsonify ({"msg":"missing name, email in credential recipient and/or pubkey in credential meta_data"})


    cert_conf = ConfigParser()
    cert_conf.read("cert-tools/conf.ini")
    group_id = str(data["credential"]["group_id"]).lower()
    #cert_conf.set("instantiate batch config","roster","rosters/mainnet.csv")
    cert_conf.set("template data","template_file_name",group_id+'.json')
    #unsigned_dir_temp = os.path.join(dir_path,unsigned_dir)
    with open('cert-tools/conf.ini', 'w') as f:
        cert_conf.write(f)
    #print (unsigned_dir_temp)
    recipient=[]
    recipient_name=str(data["credential"]["recipient"]["name"])
    recipient_email=str(data["credential"]["recipient"]["email"])
    #if 'pubkey' not in data["credential"]["recipient"]["meta_data"]:
    recipient_pubkey = "ecdsa-koblitz-pubkey: 0x88D2a0D90B290d7233045E364501F9DD8B3680Cf"
    #else:
    #    recipient_pubkey="ecdsa-koblitz-pubkey:"+str(data["credential"]["recipient"]["meta_data"]["pubkey"]) #uses pubkey POSTed in recipient

    recipient_temp=[recipient_name,recipient_pubkey,recipient_email]
    recipient.append(recipient_temp)
    recipient_csv = pandas.DataFrame(recipient)
    column_name=['name','pubkey','identity']
    recipient_csv.to_csv('cert-tools/sample_data/rosters/roster_kaleido.csv', index=False, header=column_name)

    #create certificate from csv
    try:

        run_cert_tools = subprocess.run(['instantiate-certificate-batch','-c','cert-tools/conf.ini']) #can add '-c','myconf.ini' after 'instantiate-certificate-batch' to the conf file if this failed
        print("instantiate succeed!")
        unsigned_dir_temp = dir_path+'/cert-tools/'+str(cert_conf["template data"]["data_dir"])+"/"+str(cert_conf["instantiate batch config"]["unsigned_certificates_dir"])
        """
        shutil.copytree(unsigned_dir_temp,dir_path+"/cert-issuer/data/unsigned_certificates",dirs_exist_ok=True) #copy temp file to cert-issuer folder to be proccessed, only in python 3.8+ :(
        shutil.copytree(unsigned_dir_temp,dir_path+"/cert-tools/sample_data/unsigned_certificates",dirs_exist_ok=True) #copy temp file to cert-tools folder for storage, only in python 3.8+
        """
        copy_tree(str(unsigned_dir_temp), str(dir_path)+'/cert-issuer/data/unsigned_certificates')
        copy_tree(str(unsigned_dir_temp),str(dir_path)+"/cert-tools/sample_data/unsigned_certificates")
        print("copy succeed")

        #this function deletes the content of temp folder
        folder = unsigned_dir_temp
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        print("Success creating batch certificate!")

    except:
        return jsonify({"msg":"error creating certificate!"})

    #this function below issues the certificate automatically to cert-issuer
    try:
        run_cert_issuer = subprocess.run(['cert-issuer','-c','cert-issuer/conf.ini'])
        print("success issuing!")
        #this function deletes unsigned certificates in cert-issuer (issue to blockchain from the folder specified in cert-issuer/conf.ini). Because of how cert-issuer read from unsigned_certificates every issuing, this folder needs to be cleaned so previously signed certificate not get issued again
        folder = os.path.join(dir_path,'cert-issuer/data/unsigned_certificates')
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    except:
        return jsonify({"msg":"error issuing certificate to blockchain!"})

    #find the newly created blockchain certificate
    recipient_name_return = recipient_email.replace("@","").replace(".","")
    recipient_name_return_sanitize = ''.join(e for e in recipient_name_return if e.isalnum())
    course_name_return = group_id.split('+')[1].replace("_","")
    #course_name_return = course_name_return.split('_')[1]
    blockchain_file = course_name_return+recipient_name_return_sanitize+".json"
    #blockchain_file = blockchain_file.replace(" ","")
    folder = os.path.join(dir_path,'cert-issuer/data/blockchain_certificates')
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder,filename)
            if blockchain_file.strip() == filename.lower():
                blockchain_link = file_path
                break
        print (blockchain_file)
        with open(blockchain_link, 'r') as f:
            return_json = json.load(f)
    except:
        return jsonify({"msg":"cannot find blockchain certificates / Error when issuing certificate!"})
    return_data = {
        "credential": {
            "id": str(return_json["id"]).split(":")[2],
            "name": str(return_json["badge"]["name"]),
            "description": str(return_json["badge"]["description"]),
            "approve": True,
            "grade": None,
            "complete": True,
            "issued_on": str(return_json["issuedOn"]),
            "course_link": "",
            "custom_attributes": {
                "transaction id":str(return_json["signature"]["anchors"][0]["sourceId"])
            },
            "expired_on": None,
            "group_name": str(return_json["badge"]["name"]),
            "group_id": group_id,
            "url": "",
            "encoded_id": "",
            "private": False,
            "seo_image": "url here",
            "certificate": {
                "image": {
                    "preview": "url here"
                }
            },
            "badge": {
                "image": {
                "preview": "url here"
            }
            },
            "evidence_items": [
            {
                "id": None,
                "description": "",
                "preview_image_url": None,
                "link_url": None,
                "type": "grade",
                "string_object": {
                    "grade": "",
                },
                "supplemental": False,
                "position": 1
            },
            ],
        "references": [
        {
            "id": None,
            "description": str(return_json["badge"]["criteria"]["narrative"]),
            "relationship": "",
            "supplemental": False,
            "approve": True,
            "referee": {
                "id": None,
                "name": "",
                "title": None,
                "url": None,
                "avatar_image_url": "url here"
            }
        }
        ],
        "recipient": {
            "name": str(return_json["recipientProfile"]["name"]),
            "email": str(return_json["recipient"]["identity"]),
            "id": str(return_json["recipientProfile"]["publicKey"]),
            "meta_data": {
            }
        },
        "issuer": {
            "name": str(return_json["badge"]["issuer"]["name"]),
            "description": None,
            "url": str(return_json["badge"]["issuer"]["url"]),
        "id": None
        },
        "meta_data": {
            "foo": "bar"
        }
    }
}

    return jsonify(return_data)

#this api search certificates
@app.route('/api/v1/credentials/search', methods=['POST'])
def search_credential():
    if  request.is_json:
        data=request.json
    else:
        return jsonify({"err": "Content type is not json."})

    if 'email' not in data["recipient"]:
        return jsonify({"msg":"missing email in recipient"})
    recipient_email = str(data["recipient"]["email"]).replace('@','').replace('.','')
    recipient_email_match = '*'+recipient_email+'.json'
    #print (recipient_email)
    if "group_id" in data:
        group_id = str(data["group_id"])
        group_id_match = group_id+'*.json'
        course_name = group_id.split("+")[1]
    else:
        group_id=""
    blockchain_cert_dir = os.path.join(dir_path,"cert-issuer/data/blockchain_certificates") #this can be changed to use the dir path in conf.ini
    print (blockchain_cert_dir)
    blockchain_cert_data={
            "credentials":[]
        }

    cert_id = course_name+recipient_email+'.json'

    for x in os.listdir(blockchain_cert_dir):
        filename=x.lower()
        print(filename)
        if group_id!="":
            if cert_id==filename:
                file_dir = blockchain_cert_dir+"/"+x
                print (file_dir)
                with open(file_dir,'r') as f:
                   data=json.load(f)
                formatting = {
                    "id": str(data["id"]).split(':')[2],
                    "name": str(data["badge"]["name"]),
                    "description": str(data["badge"]["description"]),
                    "grade": None,
                    "complete": True,
                    "issued_on": str(data["issuedOn"]),
                    "allow_supplemental_references": None,
                    "allow_supplemental_evidence": None,
                    "course_link": None,
                    "custom_attributes": None,
                    "expired_on": None,
                    "group_name": str(data["badge"]["issuer"]["name"]),
                    "private": False,
                    "recipient": {
                        "name": str(data["recipientProfile"]["name"]),
                        "email": str(data["recipient"]["identity"]),
                        "id": None,
                        "meta_data": {
                        }
                    },
                    "issuer": {
                        "name": str(data["badge"]["issuer"]["name"]),
                        "description": None,
                        "url": "http://www.accredible.com"
                    },
                    "meta_data": {
                    }
                }
                blockchain_cert_data["credentials"].append(formatting)
        else:
            if fnmatch.fnmatch(filename,recipient_email_match):
                file_dir = blockchain_cert_dir+"/"+x
                print(file_dir)
                with open(file_dir,'r') as f:
                    data=json.load(f)
                formatting = {
                    "id": str(data["id"]).split(':')[2],
                    "name": str(data["badge"]["name"]),
                    "description": str(data["badge"]["description"]),
                    "grade": None,
                    "complete": True,
                    "issued_on": str(data["issuedOn"]),
                    "allow_supplemental_references": None,
                    "allow_supplemental_evidence": None,
                    "course_link": None,
                    "custom_attributes": None,
                    "expired_on": None,
                    "group_name": str(data["issuer"]["name"]),
                    "private": False,
                    "recipient": {
                        "name": str(data["recipientProfile"]["name"]),
                        "email": str(data["recipient"]["identity"]),
                        "id": None,
                        "meta_data": {
                        }
                    },
                    "issuer": {
                        "name": str(data["badge"]["issuer"]["name"]),
                        "description": None,
                        "url": "http://www.accredible.com"
                    },
                    "meta_data": {
                    }
                }
                blockchain_cert_data["credentials"].append(formatting)

    return jsonify(blockchain_cert_data)

#this api shows certificate by json as blockcert doesn't generate pdf
@app.route('/api/v1/credentials/generate_single_pdf/<cert_id>', methods=['POST'])
def generate_pdf(cert_id):
    if  request.is_json:
        #cert_dir = dir_path+'/cert-issuer/data/blockchain_certificates/'+cert_id+'.json'
        return_data = {
            "file":"localhost:80/blockchain_certificates/"+cert_id+'.json'
        }
    else:
        return jsonify({"err": "Content type is not json."})
    return jsonify(return_data)

@app.route('/blockchain_certificates/<path:filename>')
def send_certificates(filename):
    my_dir = str(dir_path)+"/cert-issuer/data/blockchain_certificates"
    print (my_dir)
    return send_from_directory(my_dir,filename,as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
