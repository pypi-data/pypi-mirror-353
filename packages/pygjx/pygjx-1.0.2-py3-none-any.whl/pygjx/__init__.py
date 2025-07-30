__version__ = "1.0.2"
__author__ = "Zeng Yuye"
import os,re,requests,threading,time,urllib.request,cv2,pygame,pygjx,subprocess,zipfile,base64,io,ctypes,easygui,sys,win32security,ntsecuritycon,win32api,win32con,speedtest,tempfile,hashlib
from queue import Queue
from tqdm import tqdm
from urllib.parse import urlparse
con=ntsecuritycon
del ntsecuritycon
ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join([sys.executable] + sys.argv), None, 1)
pygjx_path=str(pygjx)[22:len(str(pygjx))-13]
ED2K_CHUNK_SIZE = 9728000
def calculate_ed2k_hash(filepath):
    md4 = hashlib.new('md4')
    with open(filepath, 'rb') as f:
        while chunk:
            f.read(ED2K_CHUNK_SIZE)
            if not chunk:break
            md4.update(chunk)
    return md4.hexdigest()
def download_with_progress(url, save_path):
    def progress_hook(count, block_size, total_size):
        pbar.total = total_size
        pbar.update(block_size)
    with tqdm(unit='B', unit_scale=True, miniters=1) as pbar:
        urllib.request.urlretrieve(url, save_path,reporthook=progress_hook)
def dbt(ed2k_link,save_path):
    try:
        print(f"Start downloading: {os.path.basename(save_path)}")
        download_with_progress(ed2k_link, save_path)
        print("Verify files...")
        file_hash = calculate_ed2k_hash(save_path)
        if file_hash in ed2k_link:
            print("Verification is successful! Download is completed")
            return True
        else:
            print("Verification failed!")
            return False
    except Exception as e:
        print(f"Download failed: {str(e)}")
        return False
def xmjc():
    try:
        result = subprocess.run(
            ["powercfg", "/a"],
            capture_output=True,
            text=True,
            check=True
        )
        return "休眠" in result.stdout or "Hibernate" in result.stdout
    except:
        return False
def smjc():
    try:
        result = subprocess.run(
            ["powercfg", "/a"],
            capture_output=True,
            text=True,
            check=True
        )
        return "待机(S3)" in result.stdout or "Standby (S3)" in result.stdout
    except:
        return False
class fn:
    def __init__(self, wjdm):self.filename = self.get_filename(wjdm)
    def __str__(self):
        time.sleep(1)
        return self.filename
    @staticmethod
    def from_url(url):
        path = urlparse(url).path
        return os.path.basename(path)
    @staticmethod 
    def from_headers(url):
        try:
            with requests.head(url, allow_redirects=True) as r:
                if 'Content-Disposition' in r.headers:
                    content = r.headers['Content-Disposition']
                    return re.findall('filename=(.+)', content)[0].strip('"\'')
        except:pass
        return None
    @classmethod
    def get_filename(cls, url, fallback="download"):
        filename = cls.from_headers(url) or cls.from_url(url)
        return filename if filename else f"{fallback}{cls.get_extension(url)}"
    @staticmethod
    def get_extension(url):
        path = urlparse(url).path
        return os.path.splitext(path)[1] or ''
class ddfe:
    def __init__(self, url, num_threads=8, save_path='./download'):
        self.wjm = fn(url)
        self.url = url
        self.num_threads = num_threads
        self.save_path = save_path
        self.file_size = 0
        self.progress = 0
        self.lock = threading.Lock()
        os.makedirs(save_path, exist_ok=True)
        self.run(str(self.wjm))
    def get_file_size(self):
        res = requests.head(self.url)
        self.file_size = int(res.headers.get('content-length', 0))
        return self.file_size
    def download_chunk(self, start, end, chunk_no):
        headers = {'Range': f'bytes={start}-{end}'}
        res = requests.get(self.url, headers=headers, stream=True)
        chunk_file = f"{self.save_path}/chunk_{chunk_no}.tmp"
        with open(chunk_file, 'wb') as f:
            for data in res.iter_content(1024):
                f.write(data)
                with self.lock:self.progress += len(data)
    
    def merge_chunks(self, final_name):
        with open(final_name, 'wb') as f:
            for i in range(self.num_threads):
                chunk_file = f"{self.save_path}/chunk_{i}.tmp"
                with open(chunk_file, 'rb') as cf:f.write(cf.read())
                os.remove(chunk_file)
    def run(self, final_name):
        file_size = self.get_file_size()
        chunk_size = file_size // self.num_threads
        threads = []
        with tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
            for i in range(self.num_threads):
                start = i * chunk_size
                end = start + chunk_size -1 if i < self.num_threads-1 else file_size-1
                thread = threading.Thread(target=self.download_chunk,args=(start, end, i))
                threads.append(thread)
                thread.start()
            while self.progress < file_size:
                pbar.n = self.progress
                pbar.refresh()
                time.sleep(0.1)
            for thread in threads:thread.join()
        self.merge_chunks(final_name)
def dhttp(url):ddfe(url)
def gj():subprocess.run(["shutdown", "/s", "/t", "0"],shell=True,check=True)
def xm():
    if xmjc():ctypes.windll.powrprof.SetSuspendState(1, 1, 0)
    else:easygui.msgbox("Hibernation is not available")
def cq():subprocess.run(["shutdown", "/r", "/t", "0"],shell=True,check=True)
def sm():ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
def cws():
    st = speedtest.Speedtest()
    return [st.download(),st.upload()]
