class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://u449273699_ProjectTeam:Smsc%402024@193.203.184.150:3306/u449273699_project_status"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10  # Maintain 10 connections in the pool
    SQLALCHEMY_MAX_OVERFLOW = 5  # Allow 5 extra connections if needed
    SQLALCHEMY_POOL_TIMEOUT = 30  # Wait 30 seconds before timeout
    SQLALCHEMY_POOL_RECYCLE = 1800  # Recycle connections every 30 minutes
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # Ensure connection is alive before using
