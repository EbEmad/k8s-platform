from uptime import models  
from uptime.db import Base, engine


def main() -> None:
    Base.metadata.create_all(engine)
    print("database schema is up to date")


if __name__ == "__main__":
    main()

