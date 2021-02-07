
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bcolors import bcolors
from bs4 import BeautifulSoup; import string, pyfiglet, socket, sys, re, time

hosts = []

    # Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def displayMessage(msg):
	s = ""
	for i in msg:
	    s += i                      
	    print(s, end='')                                                    
	    time.sleep(0.1)   

# Check https://regex101.com/r/A326u1/5 for reference
DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)" # http basic authentication [optional]
    r"(?:(?:(?=\S{0,253}(?:$|:))" # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+" # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
    r"(?:[a-z0-9]{1,63})))" # check for top level domain, no dashes allowed
    r"|localhost)" # accept also "localhost" only
    r"(:\d{1,5})?", # port [optional]
    re.IGNORECASE
)
SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$", # scheme: http(s) or ftp(s)
    re.IGNORECASE
)

def validate_url(url: str):
    url = url.strip()

    if not url:
        raise Exception("No URL specified")

    if len(url) > 2048:
        raise Exception("URL exceeds its maximum length of 2048 characters (given length={})".format(len(url)))

    result = urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        return False
        #raise Exception("No URL scheme specified")

    if not re.fullmatch(SCHEME_FORMAT, scheme):
        return False
        #raise Exception("URL scheme must either be http(s) or ftp(s) (given scheme={})".format(scheme))

    if not domain:
        return False
        #raise Exception("No URL domain specified")

    if not re.fullmatch(DOMAIN_FORMAT, domain):
        return False
        #raise Exception("URL domain malformed (domain={})".format(domain))

    return True


def search(remoteAddr):

    first = 0
    q = True

    while(q):

        try:
            address = (f"https://www.bing.com/search?q=ip:\"{remoteAddr}\"&first={first}1")
            custom_user_agent = "Mozilla/5.0 (Linux; Android 4.4; Nexus 7 Build/KRT16M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.92 Safari/537.36"
            getRequest = Request(address, headers={"User-Agent": custom_user_agent}); page = urlopen(getRequest)
            soup = BeautifulSoup(page.read(), "lxml"); links = soup.find_all("a", href=True)
            for link in links:
                if(int(soup.select("#b_results > li.b_pag > div > nav > div.sb_center > ul > li > a.sb_pagS.sb_pagS_bp.sb_bp")[0].text) == (first + 1)):
                    pass
                    if(validate_url(link["href"])):

                        domain = urlparse(link["href"])
                        domain = domain.hostname

                        if(domain.startswith("www.")):
                            domain = domain.replace("www.", "")

                        if(domain not in hosts and "microsoft" not in domain):
                            hosts.append(domain)
                            print(bcolors.ok("[+]") + domain)
                            time.sleep(0.3)
            
            
                else:
                    while(q == True):
                        displayMessage("\r{}Found {} sites hosted on a given server\n".format(bcolors.okblue("[i]"), len(hosts)))
                        q = False

            first += 1  
        except KeyboardInterrupt:
            print("{}Found {} sites hosted on a given server".format(bcolors.okblue("[i]"), len(hosts)))
        except IndexError:
            continue    

print(pyfiglet.figlet_format("Reverse IP Lookup") + "\t\t\t\t\twritten by batininhani\n")

try:  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    #print ("Socket successfully created") 
except socket.error as err:  
    #print ("socket creation failed with error %s" %(err))
    sys.exit(1)
  
remoteAddr = input("Remote Address: ")

# default port for socket  
port = 80

try:  
    host_ip = socket.gethostbyname(remoteAddr)
    host = socket.gethostbyaddr(host_ip)

except socket.gaierror:  
  
    # this means could not resolve the host  
    displayMessage("\r%sThere was an error resolving the host" % bcolors.fail("[-]")) 
    sys.exit(1)

except socket.herror:

    displayMessage("\r%sHost could not be found!" % (bcolors.fail("[-]")))
    sys.exit(1)

# connecting to the server  
s.connect((host_ip, port))
displayMessage("\rResolve Host: %s" % host[0]); print('\n')
s.close()
search(host_ip)

if(len(hosts) >= 1):

    file_name = remoteAddr + "_output.txt"
    file_object  = open(file_name, "w+")
    for i in hosts:
        file_object.write(i + '\n')
    displayMessage("\r%sOutput has been successfully written to %s!" % (bcolors.okblue("[i]"), file_name)); print('\n')
    file_object.close()
    

