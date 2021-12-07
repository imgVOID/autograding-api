import subprocess

if __name__ == '__main__':
    ''' Main controller to set containers and test values '''
    containerName = "test"
    print("\nGenerating test messages...\n")
    popen = subprocess.Popen(["docker", "run", "-d", "--rm", "--name", "test1", "python:3.9-alpine"],
                             stdout=subprocess.PIPE)
    popen2 = subprocess.Popen(["docker", "run", "-d", "--rm", "--name", "test2", "python:3.9-alpine"],
                             stdout=subprocess.PIPE)
    popen3 = subprocess.Popen(["docker", "run", "-d", "--rm", "--name", "test3", "python:3.9-alpine"],
                             stdout=subprocess.PIPE)
    print(popen.stdout.readline().decode("utf-8"))
    print(popen2.stdout.readline().decode("utf-8"))
    print(popen3.stdout.readline().decode("utf-8"))
