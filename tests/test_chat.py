import sys
sys.path.insert(0, "../src/lambda/Chat")
sys.path.insert(0, "../src/models/")

from CreateChat import lambda_function as create

if __name__ == "__main__":
    create.handler("{}", '')
