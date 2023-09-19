import random
import signal

def ran():
    return random.randint(999,99999)
def add():
    question = f"{ran()} + {ran()} = "

    print(question.replace('+','-'))
    answer = eval(question[:-2])
    
    calc = input()
    if calc == str(answer):
        print("Correct.")
    else:
        print("Wrong.")
        exit(0)

def sub():
    question = f"{ran()} - {ran()} = "

    print(question.replace('-','x'))
    answer = eval(question[:-2])
    
    calc = input()
    if calc == str(answer):
        print("Correct.")
    else:
        print("Wrong.")
        exit(0)

def mul():
    question = f"{ran()} x {ran()} = "

    print(question.replace('x','//'))
    answer = eval(question[:-2].replace('x','*'))
    
    calc = input()
    if calc == str(answer):
        print("Correct.")
    else:
        print("Wrong.")
        exit(0)

def div():
    question = f"{ran()} // {ran()} = "

    print(question.replace('//','%'))
    answer = eval(question[:-2])
    
    calc = input()
    if calc == str(answer):
        print("Correct.")
    else:
        print("Wrong.")
        exit(0)

def mod():
    question = f"{ran()} % {ran()} = "

    print(question.replace('%','+'))
    answer = eval(question[:-2])
    
    calc = input()
    if calc == str(answer):
        print("Correct.")
    else:
        print("Wrong.")
        exit(0)



print("  ____ ____   ___  _   _    ____ _____ _____ ")
print(" / ___|  _ \ / _ \| | | |  / ___|_   _|  ___|")
print("| |  _| | | | | | | | | | | |     | | | |_   ")
print("| |_| | |_| | |_| | |_| | | |___  | | |  _|  ")
print(" \____|____/ \___/ \___/   \____| |_| |_|    ")
print("												")
print("Welcome to the calculate challenge. Please try to solve 300 Question in 600 seconds.")
print("ATTENTION: This is an April Fool's game, and the real problem may not be what it seems")
print("")
input("Press Enter to start...")
signal.alarm(600)

for i in range(300):
    print("Round: "+str(i+1))
    random.choice([add,sub,mul,div,mod])()


flag = open('/flag').read()
print("Congratulations on passing the challenge. This is your flag: " + str(flag))

