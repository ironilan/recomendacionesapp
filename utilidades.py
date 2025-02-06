import time
from jose import JWTError, jwt
from fastapi import Request, status, HTTPException

def getExtension(content_type):
    if content_type == 'image/jpeg':
        return 'jpg'
    elif content_type == 'image/png':
        return 'png'
    else:
        return 'no'
    
    
def verificar_token(request: Request):
    header = request.headers.get('Authorization')
    if header == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
    else:
        try:
            resuelto = jwt.decode(header, "123456", algorithms=["HS512"])
            if int(resuelto['iat']) < int(time.time()):
                
                return resuelto
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")