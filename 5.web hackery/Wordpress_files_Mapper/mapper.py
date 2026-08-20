import contextlib
import os 
import queue
import requests
import sys
import threading
import time


filtered= [".jpg",".gif",".png",".css"]
target = "https://techcrunch.com/"
threds= 10

answers =queue.Queue()
web_paths=queue.Queue()

def gather_paths():
    for root, _ , files in os.walk("."):
        
        for fname in files:
            if os.path.splitext(fname)[1] in filtered:
                continue
            path =os.path.join(root,fname)
            if path.startswith("."):
                path= path[1:]
            print(path)
            web_paths.put(path)


@contextlib.contextmanager
def chdir(path):
    """
    on enter , change the directory to specifield path 
    on exit change the directory back to original 
    """

    this_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(this_dir)
    

## test the live target 
def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url =f"{target}{path}"
        time.sleep(2)  # your target may have the throattling/lockout
        r=requests.get(url)
        if r.status_code==200:
            answers.put(url)
            sys.stdout.write("+")
        else:
            sys.stdout.write("x")
        sys.stdout.flush()




def run():
    mythreads =list()
    for i in range(threds):
        print(f"swapping threads {i}")
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()

    for thread in mythreads:
        thread.join()
        

if __name__ == '__main__':
    with chdir ("C:/Users/ad828/Downloads/wordpress-6.8.1/wordpress"):
        gather_paths()
    input("press return to continue.")
    run()
    with open("myanswers.txt", "w") as f:
        f.write(f"{answers.get()}\n")
    
    print("done")