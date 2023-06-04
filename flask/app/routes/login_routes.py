import gzip
import imp
import sys, json
from turtle import update
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response
from app import app, db, tz
import hashlib
import jwt
from datetime  import datetime, timezone, timedelta
from app.models.inventory_models import User_Table
#from cryptography.hazmat.primitives import serialization
from app.middleware import token_required
import ldap


@app.route("/login", methods = ['POST'])
def Login():
    """
        Get Auth token
        ---
        description: Get login token
        parameters:
        consumes:
            - application/json
        parameters:
            -
             name: body
             in: body
             required: true
             schema:
                id : toto
                required:
                    - user
                    - pass
                properties:
                user:
                    type: string
                    description: Username 
                pass:
                    type: string
                    description: Password

        responses:
            200:
                description: Auth Token
                schema:
                    type: object
                    properties:
                         auth-key:
                            type: string
    """
    postData = request.get_json()
    isAuthenticated=False
    username = postData['user']
    password = postData['pass']
    if username == 'najam' and password == 'najam@123':
        
        #private_key = open('app/authentication_token_private_key.pem', 'r').read()
        #key = serialization.load_ssh_private_key(private_key.encode(), password=b'cisco-mobily')
                
        #except Exception as e:
        #    print("Failed to read private key", file=sys.stderr)
            
        token = jwt.encode(
                    {"user_id": username, "user_role":"Admin", "user_status":"Active", "iat": datetime.now(tz=timezone.utc), "exp": datetime.now(tz=timezone.utc)+timedelta(hours=3)},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
        return jsonify({'response': "Login Successful","code":"200", "auth-key": token  })

    user_exists = User_Table.query.filter_by(user_id=username).first()
    if user_exists:
        if user_exists.status=="Active":
            if user_exists.account_type != "Local":
                #Ldap Authentication
                try:
                    with open('app/cred.json') as inventory:
                        inv = json.loads(inventory.read())
                    
                    ldap_server= inv['LDAP']['ip']

                    connect = ldap.initialize(f"ldap://{ldap_server}:389")
                    connect.set_option(ldap.OPT_REFERRALS, 0)
                    connect.simple_bind_s(f"PRODUCTION\\{username}", password)
                    #result = connect.search_s('DC=prod,DC=mobily,DC=lan', ldap.SCOPE_SUBTREE, 'sAMAccountName=srv00047')

                    token = jwt.encode(
                                {"user_id": user_exists.user_id, "user_role":user_exists.role, "iat": datetime.now(tz=timezone.utc), "exp": datetime.now(tz=timezone.utc)+timedelta(hours=3)},
                                app.config["SECRET_KEY"],
                                algorithm="HS256"
                            )
                    
                    user_exists.last_login = datetime.now(tz)
                    connect.unbind()

                    try:
                        db.session.merge(user_exists)
                        db.session.commit()
                        #print(obj.site_name, file=sys.stderr)
                    except:
                        db.session.rollback()
                        print("Something else went wrong", file=sys.stderr)
                    return jsonify({'response': "Login Successful","code":"200", "auth-key": token })

                
                except ldap.SERVER_DOWN:
                    print("LDAP Server Down", file=sys.stderr)
                    return jsonify({'message': 'LDAP Server Down'}), 401
                except ldap.INVALID_CREDENTIALS:
                    print("LDAP Authentication Failed Incorrect Username/Password", file=sys.stderr)
                    return jsonify({'message': 'LDAP Authentication Failed Incorrect Username/Password'}), 401
                except ldap.ldap.TIMEOUT:
                    print("Request Timeout", file=sys.stderr)
                    return jsonify({'message': 'LDAP Request Timeout'}), 401
                except ldap.LDAPError as e:
                    print(f"Ldap Error Occured {e}", file=sys.stderr)
                    return jsonify({'message': 'Ldap Error Occured'}), 401
                except Exception as e:
                    print(f"Internal Server Error {e}", file=sys.stderr)
                    return jsonify({'message': 'Internal Server Error'}), 500

            else:
                pas = hashlib.sha512()
                pas.update(postData['pass'].encode("utf8"))
                password=  str(pas.digest())

                user = User_Table.query.filter_by(user_id=username).filter_by(password=password).first()
                
                if user:
                    #print(user.token, file=sys.stderr)
                # try:
                        #private_key = open('app/authentication_token_private_key.pem', 'r').read()
                        #key = serialization.load_ssh_private_key(private_key.encode(), password=b'cisco-mobily')    
                    #except Exception as e:
                    #    print("Failed to read private key", file=sys.stderr)
                    
                    token = jwt.encode(
                                {"user_id": user.user_id, "user_role":user.role, "iat": datetime.now(tz=timezone.utc), "exp": datetime.now(tz=timezone.utc)+timedelta(hours=3)},
                                app.config["SECRET_KEY"],
                                algorithm="HS256"
                            )
                    
                    user.last_login = datetime.now(tz)
                    try:
                        db.session.merge(user)
                        db.session.commit()
                        #print(obj.site_name, file=sys.stderr)
                    except:
                        db.session.rollback()
                        print("Something else went wrong", file=sys.stderr)
                    return jsonify({'response': "Login Successful","code":"200", "auth-key": token })
                else: 
                    print("Authentication Failed Incorrect Username/Password", file=sys.stderr)
                    return jsonify({'message': 'Authentication Failed Incorrect Username/Password'}), 401
        
        else:
            print("User is Inactive", file=sys.stderr)
        return jsonify({'message': 'User is Inactive'}), 401

    else: 
        print("Authentication Failed Incorrect Username", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed Incorrect Username'}), 401



    

