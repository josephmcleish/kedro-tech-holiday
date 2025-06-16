import os
import subprocess

print("JAVA_HOME =", os.environ.get("JAVA_HOME"))

try:
    output = subprocess.check_output("java -version", stderr=subprocess.STDOUT, shell=True)
    print(output.decode())
except subprocess.CalledProcessError as e:
    print("Java test failed:", e.output.decode())
