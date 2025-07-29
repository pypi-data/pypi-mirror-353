from typing import Callable, Awaitable
import base64
import jwt  # https://jwt.io/introduction


pem_private_key = base64.b64decode(
    "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQ0KTUlJRW9nSUJBQUtDQVFFQW5IUkxHRlo5dVh3cHM1eUVMbE42bjlBbjJIUEpQUEI0bU5JM0grR3lWNWgyNzRhZQ0KdUJSVll6cWw1amdjQ0JaeTExdE43Q3EreERzZk5jMmRkNDhZeEZ3TG1lSytGUTUrbVJEYjR6Sm14cDVHeWZuMw0KYnh0SWtBZkg3M3VnaC9iQXRkNmpvbDk1WG9jcFNDZWVsV0w0cjEzdTNla3NLZExweDh4cVF2bEdXTzJQWms1TA0KTHZodmVRc0p1ZEhoNzdXaWp2dUN1aTBBenZGd2sySGV3MDZ1OFFYZnVUWnlLRjVGcEpTNWdlRkpJL29GbzFrNQ0KUk9JMWd3TjloNWlSTXhmOGxEN3ZQa1Q3TVZvcXk4ZUVyeVJoZzVPeWxSQU9uSFJybFdtNStaUDdMZTFlek1TYg0KZ0VWWms1UldhLzVQL3Nkc0dVcWJGRXlFOEFza1BCTStTcm5sVFFJREFRQUJBb0lCQURveS9IaGFQRHlTbG9Tcw0KOVhLeU5ReGNCMlo2YytLS1phSWJtTXZ3VGtKTmdmaktNQ0t6MWF1cTltbTBkNkQra012UnVDUGhKc09pWnBMQw0KSVJDSGw2UDd4WWtDRXNtTWNjV0l3dk02SFlkRyszaEkxeVZxbGN5V1NHYXFxMlhJZ1psbDc2TUlOd0xWN3FKYg0Kc3A5SmlNN2JkMjd2UFRGMXR1ZFBBRHhYdERhQjIyUE8zT2F4OXg5Q0t4RXpmWUhsS1VYMlcvd2s1VGdEa3hTcw0KN2EwbXRWMkhVTVZLejhmSytadVgrTlFjVFp2ZGRhNUtWdXNVeDlVRDQ4SGVYOFVQM0lOM3RnTk1KbVloeWNPNQ0KaGY0MDlLdGpyekhTQkxJdnJqa0tUYkJrTE5Yejk1c0E4UDd2aStzT0ZUM05NRHhJb0ZmSWkzVGVsMERoZWFaRg0KdWxRQ00yRUNnWUVBMGdMc21WakJYVmlPQU1kVnFDTzI1SlQxbStYVjhoQy9pLzMxRFZHNk1RTEdxWndjSklNRA0KbXhFVGwyUnVyeXk2V1JycXE0QkErNHh4alhUTnh2TW4zT1JTTStVVG9vMVlKL0hXR210T1VVbFlxek55RFlxMw0KVXJ1bXN1Q29iYmszYXUwTHdoemZrYXBBSHEwNXR3cGlIandLWlFrbzI2RnV1S0M1bUYwaTRlVUNnWUVBdnJiLw0KUmZvT1R2ZG45TkxmTXdKZk5paFFpczRvQlVCS3YxV25ReHFicUpmVURzSzU5Uk5TVUY0MDRkbFpLOXpjQVRiZg0KSVpBZzlhV1hLMnFMMmc4M3krWEZTODd5amUzeE8xeUorV3BQMG1wM3ZSSnkraEFtS2dodXV0VTdycDNBQnc4cg0KYklHZnNjKzArQ252WGZTN3N0Q21wNkJ6UkZZblNkUUtUdGp0MzBrQ2dZQXczK1ZZT3NPbGlicGlqQUZ2UkFDSQ0KYWZKTytjbzByNWtrWjFIa2E2UzlTendZdFBBSHYwWFRqTUhXZGRVY2gzaEd6SERZd054ZXJteXUwd1Fnek8zMg0KQmx6ckh1RFc3N1lZZGJ1eUlrN3pzL0lpeGJKQlhJc1ZnZjVsbXNzWDNnYjdwM2NaRWNjbUMwMG8xbitjRFpxUQ0KRnNFRWlvRXJ2QUljamFzanZta2owUUtCZ0hQU2ZUdUpQbEZVell5UTJENkpUVHQ5eGxSV0dWWC9FcVlhcGFjSw0KTE1oNTFLNVdNa3NWUGVOVEl6aWFJQjZVVmdSaXg2WUJleExVU3ZkeUVKY1FzT2tpbE95U05ScGZEQ2JwNzExSw0KNUVrOG9aVnc4K1RNRS9GcEI1NXR5MzRqamJCNzFQcGp5cEZaUEdXT1NqRzhaSldYUSs3L2NhRnAxUmh3THdadA0KbGlFSkFvR0FlQVRUUzFlbmtOZUUwYVJxaExmRExWc0ZWbUd0RlpSMEd0VWpFYko5enAwS05qTmdkSGpaMk52eg0KS3BsR0hRWG5DNndmM2g0bDBFd0JmYjdPaEZaYkZwQWoyZ0pIeFloVy9ySDNjVzVtWkRrRnRnNFpQUnRaME5MNg0Kb2NneTUxVjVtK2xYSE5DckFEZTVnRm1tanptMUpDZG5aRERrR29FNU80Z0hZQ1l2U1FJPQ0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0NCg=="
)

pem_public_key = base64.b64decode(
    "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0NCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBbkhSTEdGWjl1WHdwczV5RUxsTjYNCm45QW4ySFBKUFBCNG1OSTNIK0d5VjVoMjc0YWV1QlJWWXpxbDVqZ2NDQlp5MTF0TjdDcSt4RHNmTmMyZGQ0OFkNCnhGd0xtZUsrRlE1K21SRGI0ekpteHA1R3lmbjNieHRJa0FmSDczdWdoL2JBdGQ2am9sOTVYb2NwU0NlZWxXTDQNCnIxM3UzZWtzS2RMcHg4eHFRdmxHV08yUFprNUxMdmh2ZVFzSnVkSGg3N1dpanZ1Q3VpMEF6dkZ3azJIZXcwNnUNCjhRWGZ1VFp5S0Y1RnBKUzVnZUZKSS9vRm8xazVST0kxZ3dOOWg1aVJNeGY4bEQ3dlBrVDdNVm9xeThlRXJ5UmgNCmc1T3lsUkFPbkhScmxXbTUrWlA3TGUxZXpNU2JnRVZaazVSV2EvNVAvc2RzR1VxYkZFeUU4QXNrUEJNK1NybmwNClRRSURBUUFCDQotLS0tLUVORCBQVUJMSUMgS0VZLS0tLS0NCg=="
)


def asJWT(data={}):
    result = jwt.encode(data, pem_private_key, algorithm="RS256")
    return result


import random
import string
import datetime


def randomString(size=32):
    return "".join(
        (random.choice(string.ascii_letters + string.digits) for _ in range(size))
    )


def loginPage(key=None, token=None, suggestedUsers=[]):
    if key is None:
        key = randomString()

    if len(suggestedUsers) == 0:
        userHelp = ""
    else:
        usersStr = (
            ", ".join(suggestedUsers)
            if len(suggestedUsers) < 15
            else ", ".join(suggestedUsers[:15])
        )
        userHelp = "Try to use one of emails: " + usersStr
    if token is None:
        tokenHtml = ""
    else:
        tokenHtml = f"""<div class="alert alert-warning" role="alert">{token}</div>"""

    _loginPage = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Login Page</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>

    <div class="container-fluid p-5 bg-primary text-white text-center">
    <h1>Login Page</h1>
    <p>Enter your email and password</p> 
    </div>
    
    <div class="container mt-5">
    <div class="row">
        <div class="col">
        <form method="post">
            <div class="mb-3">
            <label for="username" class="form-label">Email address</label>
            <input type="email" class="form-control" id="username" name="username" aria-describedby="emailHelp">
            <div id="emailHelp" class="form-text">{userHelp}</div>
            </div>
            <div class="mb-3">
            <label for="password" class="form-label">Password (should be any)</label>
            <input type="password" class="form-control" id="password" name="password">
            <input type="hidden" class="form-control" id="key" name="key" value={key}>
            </div>
            {tokenHtml}
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        </div>
    </div>
    </div>

    </body>
    </html>
    """
    return _loginPage


def createToken(
    client_state="", expires_in=3600, refresh_token_expires_in=24 * 3600, iss=None
):
    code = "C-" + randomString()
    accesstoken = "ACCT-" + randomString()
    refreshtoken = "REFT-" + randomString()
    id_token = "IDT-" + randomString()
    date_of_creation = datetime.datetime.now(tz=datetime.timezone.utc)
    result = {
        "id_token": id_token,
        "access_token": accesstoken,
        "date_of_creation": date_of_creation,
        "expires_in": expires_in,
        "refresh_token": refreshtoken,
        "refresh_token_expires_in": date_of_creation
        + datetime.timedelta(refresh_token_expires_in),
        "code": code,
        "state": client_state,
        "token_type": "Bearer",
        "exp": date_of_creation + datetime.timedelta(seconds=expires_in),
    }
    if iss:
        result["iss"] = iss

    return result


def extractKeys(data={}, keys=[]):
    result = {}
    for key in keys:
        value = data.get(key, None)
        if value is not None:
            result[key] = value
    return result


from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from fastapi import Form, Header, Cookie
from typing import Union, Optional


def createServer(
    iss="http://localhost:8000/publickey",
    db_users=[
        {
            "id": "5563aa07-45c8-4098-af17-f2e8ec21b9df",
            "email": "someone@somewhere.world",
        }
    ],
    passwordValidator: Callable[[str, str], Awaitable[bool]] = None,
    emailMapper: Callable[[str], Awaitable[str]] = None,
):

    async def buildInPasswordValidator(email, password):
        return True

    if passwordValidator is None:
        passwordValidator = buildInPasswordValidator

    async def buildInEmailMapper(email):
        rows = filter(lambda item: item["email"] == email, db_users)
        row = next(rows, None)
        result = row.get("id", None)
        return result

    if emailMapper is None:
        emailMapper = buildInEmailMapper

    db_table_codes = {}
    db_table_params = {}

    db_table_tokens = {}
    db_table_refresh_tokens = {}

    app = FastAPI()

    def tokenFromCode(code):
        storedParams = db_table_codes.get(code, None)
        if storedParams is None:
            return None

        del db_table_codes[code]  # delete code, so it is not possible to use it more?

        token = createToken(iss=iss)

        tokenRow = {**token, **storedParams}
        db_table_tokens[tokenRow["access_token"]] = tokenRow
        db_table_refresh_tokens[tokenRow["refresh_token"]] = tokenRow

        responseJSON = extractKeys(
            tokenRow, ["token_type", "access_token", "expires_in", "refresh_token"]
        )
        return responseJSON

    @app.get("/login")
    async def getLoginPage(
        response_type: Union[str, None] = "code",
        client_id: Union[str, None] = "SomeClientID",
        state: Union[str, None] = "SomeState",
        redirect_uri: Union[str, None] = "redirectURL",
    ):

        # if there is a sign that user is already logged in, then appropriate redirect should be returned (see method postNameAndPassword)

        storedParams = {
            "response_type": response_type,
            "client_id": client_id,
            "state": state,
            "redirect_uri": redirect_uri,
        }

        # here client_id should be checked
        # here redirect_uri should be checked (client should use always same redirect uri)

        # save info into db table
        key = randomString()
        db_table_params[key] = storedParams

        # return login page
        suggestedUsers = [user["email"] for user in db_users]
        return HTMLResponse(loginPage(key, suggestedUsers=suggestedUsers))

    @app.get("/login2")
    async def getLoginPage(
        response_type: Union[str, None] = "code",
        client_id: Union[str, None] = "SomeClientID",
        state: Union[str, None] = "SomeState",
        redirect_uri: Union[str, None] = "redirectURL",
    ):

        # if there is a sign that user is already logged in, then appropriate redirect should be returned (see method postNameAndPassword)

        storedParams = {
            "response_type": response_type,
            "client_id": client_id,
            "state": state,
            "redirect_uri": redirect_uri,
        }

        # here client_id should be checked
        # here redirect_uri should be checked (client should use always same redirect uri)

        # save info into db table
        key = randomString()
        db_table_params[key] = storedParams

        # return login page
        suggestedUsers = [user["email"] for user in db_users]
        return HTMLResponse(loginPage(key, suggestedUsers=suggestedUsers))

    @app.post("/login2")
    async def postNameAndPassword(
        response: Response,
        username: str = Form(None),
        password: str = Form(None),
        key: str = Form(None),
    ):

        storedParams = db_table_params.get(key, None)
        if (storedParams is None) or (key is None):
            # login has not been initiated appropriatelly
            # HTMLResponse(content=f"Bad OAuth Flow, {key} has not been found", status_code=404)
            return RedirectResponse(f"./login2", status_code=status.HTTP_303_SEE_OTHER)

        del db_table_params[key]  # remove key from table

        # username and password must be checked here, if they match eachother
        validpassword = await passwordValidator(username, password)
        if not validpassword:
            # return RedirectResponse(f"./login2", status_code=status.HTTP_403_FORBIDDEN)
            result = RedirectResponse(
                f"./login2?redirect_uri={storedParams['redirect_uri']}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
            return result

        # retrieve previously stored data from db table
        token = createToken()
        # user_ids = map(lambda user: user["id"], filter(lambda user: user["email"] == username, db_users))
        # user_id = next(user_ids, None)
        user_id = await emailMapper(username)

        storedParams["user"] = {"name": username, "email": username, "id": user_id}
        storedParams["user_id"] = user_id
        tokenRow = {**token, **storedParams}

        db_table_tokens[tokenRow["access_token"]] = tokenRow
        db_table_refresh_tokens[tokenRow["refresh_token"]] = tokenRow

        responseJSON = extractKeys(
            tokenRow,
            ["token_type", "access_token", "expires_in", "refresh_token", "user_id"],
        )
        token = asJWT(responseJSON)

        result = RedirectResponse(
            f"{storedParams['redirect_uri']}", status_code=status.HTTP_302_FOUND
        )
        result.set_cookie(key="authorization", value=token)

        return result

    @app.get("/login3")
    async def getLoginPage(
        response_type: Union[str, None] = "code",
        client_id: Union[str, None] = "SomeClientID",
        state: Union[str, None] = "SomeState",
        redirect_uri: Union[str, None] = "redirectURL",
    ):

        # if there is a sign that user is already logged in, then appropriate redirect should be returned (see method postNameAndPassword)

        storedParams = {
            "response_type": response_type,
            "client_id": client_id,
            "state": state,
            "redirect_uri": redirect_uri,
        }

        # here client_id should be checked
        # here redirect_uri should be checked (client should use always same redirect uri)

        # save info into db table
        key = randomString()
        db_table_params[key] = storedParams

        return {"key": key}

    from pydantic import BaseModel

    class NameAndPassword(BaseModel):
        username: str
        password: str
        key: str

    @app.post("/login3")
    async def postNameAndPasswordinJSON(response: Response, item: NameAndPassword):
        key = item.key
        username = item.username

        # retrieve previously stored data from db table
        storedParams = db_table_params.get(key, None)
        if (storedParams is None) or (key is None):
            # login has not been initiated appropriatelly
            # HTMLResponse(content=f"Bad OAuth Flow, {key} has not been found", status_code=404)
            return RedirectResponse(f"./login3", status_code=status.HTTP_303_SEE_OTHER)

        del db_table_params[key]  # remove key from table

        # username and password must be checked here, if they match eachother
        validpassword = await passwordValidator(item.username, item.password)
        if not validpassword:
            # return RedirectResponse(f"./login2", status_code=status.HTTP_403_FORBIDDEN)
            return RedirectResponse(f"./login3", status_code=status.HTTP_303_SEE_OTHER)

        token = createToken()
        # user_ids = map(lambda user: user["id"], filter(lambda user: user["email"] == username, db_users))
        # user_id = next(user_ids, None)

        user_id = await emailMapper(username)

        storedParams["user"] = {"name": username, "email": username, "id": user_id}
        storedParams["user_id"] = user_id
        tokenRow = {**token, **storedParams}

        db_table_tokens[tokenRow["access_token"]] = tokenRow
        db_table_refresh_tokens[tokenRow["refresh_token"]] = tokenRow

        responseJSON = extractKeys(
            tokenRow,
            ["token_type", "access_token", "expires_in", "refresh_token", "user_id"],
        )
        token = asJWT(responseJSON)

        return {"token": token}

    # pip install python-multipart
    @app.post("/login")
    async def postNameAndPassword(
        username: str = Form(None), password: str = Form(None), key: str = Form(None)
    ):

        # retrieve previously stored data from db table
        storedParams = db_table_params.get(key, None)
        if (storedParams is None) or (key is None):
            # login has not been initiated appropriatelly
            return HTMLResponse(
                content=f"Bad OAuth Flow, {key} has not been found", status_code=404
            )

        # remove stored data from table
        del db_table_params[key]  # remove key from table

        # username and password must be checked here, if they match eachother
        validpassword = await passwordValidator(username, password)
        if not validpassword:
            return RedirectResponse(
                f"./login?redirect_uri={storedParams['redirect_uri']}",
                status_code=status.HTTP_302_FOUND,
            )

        # store code and related info into db table
        code = randomString()
        # user_ids = map(lambda user: user["id"], filter(lambda user: user["email"] == username, db_users))
        # user_id = next(user_ids, None)
        user_id = await emailMapper(username)

        storedParams["user"] = {"name": username, "email": username, "id": user_id}
        storedParams["user_id"] = user_id

        db_table_codes[code] = storedParams
        if "?" in storedParams["redirect_uri"]:
            result = RedirectResponse(
                f"{storedParams['redirect_uri']}&code={code}&state={storedParams['state']}",
                status_code=status.HTTP_302_FOUND,
            )
        else:
            result = RedirectResponse(
                f"{storedParams['redirect_uri']}?code={code}&state={storedParams['state']}",
                status_code=status.HTTP_302_FOUND,
            )
        return result

    @app.post("/token")
    async def exchangeCodeForToken(
        response: Response,
        grant_type: str = Form(None),
        code: str = Form(None),
        client_id: str = Form(None),
        client_secret: Optional[str] = Form(None),
        code_verifier: Optional[str] = Form(None),
        refresh_token: Optional[str] = Form(None),
    ):

        # add header Cache-Control: no-store
        response.headers["Cache-Control"] = "no-store"

        # if web app flow is used, client_secret should be checked
        # if PKCE flow is used, code_verifier must be returned

        if grant_type == "authorization_code":
            # retrieve previously stored data from db table

            responseJSON = tokenFromCode(code)

            if responseJSON is None:
                # login has not been initiated appropriatelly
                return JSONResponse(
                    content={
                        "error": "invalid_request",
                        "error_description": f"Bad OAuth Flow, code {code} has not been found",
                    },
                    status_code=404,
                )

            pass

        if grant_type == "refresh_token":
            storedParams = db_table_refresh_tokens.get(refresh_token, None)
            if tokenRow is None:
                # refresh token does not exists
                return JSONResponse(
                    content={
                        "error": "invalid_request",
                        "error_description": f"Bad OAuth Flow, refresh_token {refresh_token} has not been found",
                    },
                    status_code=404,
                )

            # remove token from tables
            del db_table_tokens[tokenRow["access_token"]]
            del db_table_refresh_tokens[tokenRow["refresh_token"]]

            if storedParams["refresh_token_expires_in"] > datetime.datetime.now(
                tz=datetime.timezone.utc
            ):
                # refresh token has expired
                return JSONResponse(
                    content={
                        "error": "invalid_refresh_token",
                        "error_description": f"Bad OAuth Flow, refresh_token {refresh_token} has not been found",
                    },
                    status_code=404,
                )

            token = createToken()

            tokenRow = {**storedParams, **token}
            db_table_tokens[tokenRow["access_token"]] = tokenRow
            db_table_refresh_tokens[tokenRow["refresh_token"]] = tokenRow

            responseJSON = extractKeys(
                tokenRow,
                [
                    "token_type",
                    "access_token",
                    "expires_in",
                    "refresh_token",
                    "user_id",
                ],
            )
            pass

        if code_verifier is not None:
            # PKCE flow
            responseJSON[code_verifier] = code_verifier

        return asJWT(responseJSON)

    @app.get("/userinfo")
    async def getUserInfo(authorization: Union[str, None] = Header(default="Bearer _")):
        print("getUserInfo", authorization)
        [_, token] = authorization.split(" ")

        if token == "_":
            return JSONResponse(
                content={
                    "error": "invalid_request",
                    "error_description": f"Bad OAuth Flow, token {token} has not been found",
                },
                status_code=404,
            )

        print(db_table_tokens)
        tokenRow = db_table_tokens.get(token, None)
        if tokenRow is None:
            # login has not been initiated appropriatelly
            return JSONResponse(
                content={
                    "error": "invalid_request",
                    "error_description": f"Bad OAuth Flow, token {token} has not been found",
                },
                status_code=404,
            )

        responseJSON = extractKeys(tokenRow, ["user"])

        # return asJWT(responseJSON)
        return JSONResponse(content=responseJSON)

    @app.get("/logout")
    async def logout(authorization: Union[str, None] = Cookie(default="")):
        tokenRow = None
        # logout z cookies
        if authorization is not None:
            print("authorization", authorization)
            jwtdecoded = jwt.decode(
                jwt=authorization, key=pem_public_key, algorithms=["RS256"]
            )
            print("jwtdecoded", jwtdecoded)
            token = jwtdecoded["access_token"]
            tokenRow = db_table_refresh_tokens.get(token, None)
            print("tokenRow", tokenRow)
            if not (tokenRow is None):
                # remove token from tables
                del db_table_tokens[tokenRow["access_token"]]
                del db_table_refresh_tokens[tokenRow["refresh_token"]]

        if tokenRow:
            response = RedirectResponse(
                f"./login?redirect_uri={tokenRow['redirect_uri']}"
            )
        else:
            response = RedirectResponse(f"./login?redirect_uri=/")
        response.delete_cookie(key="authorization")
        # where to go?
        return response

    @app.get("/logout2")
    async def logout(authorization: Union[str, None] = Header(default="Bearer _")):
        authorization = authorization.replace("Bearer ")
        tokenRow = None
        # logout z cookies
        if authorization is not None:
            print("authorization", authorization)
            jwtdecoded = jwt.decode(
                jwt=authorization, key=pem_public_key, algorithms=["RS256"]
            )
            print("jwtdecoded", jwtdecoded)
            token = jwtdecoded["access_token"]
            tokenRow = db_table_refresh_tokens.get(token, None)
            print("tokenRow", tokenRow)
            if not (tokenRow is None):
                # remove token from tables
                del db_table_tokens[tokenRow["access_token"]]
                del db_table_refresh_tokens[tokenRow["refresh_token"]]

        if tokenRow:
            response = RedirectResponse(
                f"./login?redirect_uri={tokenRow['redirect_uri']}"
            )
        else:
            response = RedirectResponse(f"./login?redirect_uri=/")
        response.delete_cookie(key="authorization")
        # where to go?
        return response

    @app.get("/publickey")
    async def getPublicKeyPem():
        return pem_public_key.decode("ascii")

    return app
