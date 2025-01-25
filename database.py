from sqlalchemy import create_engine, MetaData

motor = create_engine("mysql+pymysql://root@localhost:3306/fastapi2")

meta = MetaData()

conectar = motor.connect()

