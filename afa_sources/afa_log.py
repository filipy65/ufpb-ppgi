import cgi, hashlib, json
from time import sleep
import afa_dlt, merkletools


# Initialize variables
http_request = cgi.FieldStorage()
html_page_head = log_info = ""
page_to_manage = log_title = None
hash_algorithm = "sha256"
page_directory = "pages/"
file_extension = ".json"


def audit_entry(page, entry):
    #global log_info
    entry_consistency = False
    if page['entries']['replacement']['replaced'][entry]:
        replace_page = open_file(page_directory + str(page['entries']['replacement']['replace_page'][entry]) + file_extension)
        replace_entry_parity = bool(page['entries']['global_id'][entry] == replace_page['entries']['global_id'][page['entries']['replacement']['replace_id'][entry]])
        #log_info += str(replace_entry_parity)
        if replace_entry_parity:
            pages_status = audit_page(replace_page['id'])
            entry_consistency = bool((replace_page['id'] not in pages_status['inconsistent_pages']) and audit_entry(replace_page, page['entries']['replacement']['replace_id'][entry]))
    else:
        entry_hash = get_concatenated_hash(hash_algorithm, page['entries']['global_id'][entry], page['entries']['description']['content'][entry], page['entries']['description']['is_file_path'][entry])
        merkle_tools = merkletools.MerkleTools()
        entry_consistency = merkle_tools.validate_proof(page['entries']['fixity']['audit_proof'][entry], entry_hash, page['anchors']['hash'])
    if page['entries']['consistent'][entry] != entry_consistency:
        page['entries']['consistent'][entry] = entry_consistency
        update_file(page_directory + str(page['id']) + file_extension, page)
    return entry_consistency




def audit_page(page_id):
    #global pages_status_file, pages_status
    page_file = page_directory + str(page_id) + file_extension
    page = open_file(page_file)

    page_consistency = afa_dlt.confirm_page_info(page)
    #page_consistency = False
    if page['consistent'] != page_consistency:
        page['consistent'] = page_consistency
        update_file(page_file, page)
        
        
    #page_consistency = check_page_consistency(page)
    #inconsistent_entries = []
    
    #inconsistent_entries.append(entry)
    #if inconsistent_entries or not page_consistency:
    if not page_consistency:
        pages_status['inconsistent_pages'].append(page_id)        
    else:
        if page_id in pages_status['inconsistent_pages']:
            pages_status['inconsistent_pages'].remove(page_id)
        page_id = str(page_id)
        pages_status['inconsistent_entries'][page_id] = []
        for entry in range(len(page['entries']['global_id'])):
            if not audit_entry(page, entry):
                pages_status['inconsistent_entries'][page_id].append(entry)
        if not len(pages_status['inconsistent_entries'][page_id]):
            del pages_status['inconsistent_entries'][page_id]
    
    #update_file(pages_status_file, pages_status)
    return pages_status
                




def check_page_consistency(page):
    sleep(3)
    page_consistency = afa_dlt.confirm_page_info(page)
    #page_consistency = False
    if page['consistent'] != page_consistency:
        page['consistent'] = page_consistency
        update_file(page_directory + str(page['id']) + file_extension, page)
    return page_consistency


# Call to get the SHA-256 hash of the value1 and value2 hashes concatenation.
def get_concatenated_hash(algorithm, value1, value2, value2_is_a_file_path):
    hash1 = hashlib.sha256(bytes(value1, "utf-8")).hexdigest()
    if value2_is_a_file_path:
        hash2 = get_file_hash(value2)
    else:
        hash2 = hashlib.sha256(bytes(value2, "utf-8")).hexdigest()
    return hashlib.sha256(bytes(hash1 + hash2, "utf-8")).hexdigest()
    

# Hash file function implementation from https://stackoverflow.com/a/55542529
# Call to get the SHA-256 hash of the file_path.
def get_file_hash(file_path):
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as file:
            while True:
                # Reading is buffered, so we can read smaller chunks.
                chunk = file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except:
        return ""


# Call to try read files if exists (or create them, if do not).
def open_file(file_path, status_file = False): # Define it if the case is a status file.
    try:
        with open(file_path) as file:
            file_data = json.load(file)
    except FileNotFoundError:
        if status_file: # If status file does not exist (first run?), create it based on the following model...
            file_data = {
                'current_page' : 0,
                'not_registered_closed_pages' : [],
                'registered_pages_awaiting_confirmation' : [],
                'inconsistent_pages' : [],
                'inconsistent_entries' : {}
            }
        
        else: # If the case is not a status file, then, it is about a new page. So, create it based on the following model...
            file_data = {
            'id' : page_to_manage,
            'entries' : {
                'global_id' : [],
                'description' : {
                    'is_file_path' : [],
                    'content' : [],
                },
                'fixity' : {
                    'hash_algorithm' : [],
                    'hash' : [],
                    'audit_proof' : [],
                },
                'replacement' : {
                    'replaced' : [],
                    'replace_page': [],
                    'replace_id': [],
                },
                'consistent' : [],
            },
            'anchors' : {
                'hash_algorithm' : "",
                'hash' : "",
                'network' : "",
                'txid' : "",
                'timestamp' : None,
                'add_info' : "",
            },
            'consistent' : True,
        }
        update_file(file_path, file_data) # Write the new file
        
    return file_data


# Call to write file_data to file_path in pretty JSON format
def update_file(file_path, file_data):
    with open(file_path, "w") as file:
        json.dump(file_data, file, indent = 4)








# Load pages status
pages_status_file = page_directory + "status" + file_extension
pages_status = open_file(pages_status_file, True)


# If previous action creates some information, show it.
if http_request.getvalue('log_info'):
    log_info += http_request.getvalue('log_info')


# Define the operation and page title
try:
    page_to_manage = int(http_request.getvalue('page_to_manage'))
    log_title = f"Edit or audit entries on page {page_to_manage}"
    """try:
        entry_to_audit = int(http_request.getvalue('entry_to_audit'))
        log_page_file = page_directory + str(page_to_manage) + file_extension
        log_page = open_file(log_page_file)
        if entry_to_audit < len(log_page['entries']['global_id']):
            audit
            entry_consistency = bool(audit_page(log_page) and check_entry_consistency(log_page, entry_to_audit))
            log_info += f"<br>The consistency of the entry {entry_to_audit} of the page {page_to_manage} is <span style='font-weight:bold;text-transform:uppercase;'>{str(entry_consistency)}</span>"
        else:
            log_info += "<br>Invalid values. Nothing changed."
    except:"""
    if page_to_manage > pages_status['current_page']:
        html_page_head += f"<meta http-equiv=\"Refresh\" content=\"0; URL=?log_info=Page {page_to_manage} doesn't exist!\""
        page_to_manage = None
    elif page_to_manage in pages_status['not_registered_closed_pages'] or page_to_manage in pages_status['registered_pages_awaiting_confirmation'] or page_to_manage == pages_status['current_page']:
        html_page_head += f"<meta http-equiv=\"Refresh\" content=\"0; URL=?log_info=Page {page_to_manage} still pending!\""
        page_to_manage = None
    elif http_request.getvalue('entry_to_audit') == "all":
        #page_inconsistent_entries = audit_page(page_to_manage)
        #page_consistency = bool(page_to_manage not in pages_status['inconsistent_pages'])
        pages_status = audit_page(page_to_manage)
        update_file(pages_status_file, pages_status)
        page_consistency = bool(page_to_manage not in pages_status['inconsistent_pages'])
        if page_consistency and (str(page_to_manage) in pages_status['inconsistent_entries']):
            log_info += f"<br><span style='font-weight:bold;'>The page {page_to_manage} is consistent, but there are inconsistent entries.</span>"
        elif not page_consistency:
            log_info += f"<br><span style='font-weight:bold;'>The page {page_to_manage} is NOT consistent.</span>"
        else:
            log_info += f"<br><span style='font-weight:bold;'>The page {page_to_manage} is consistent.</span>"
        #if page_inconsistent_entries:
        #    log_info += f"<br>The following entries are marked as inconsistent: {page_inconsistent_entries}"
    #else:
        #log_info += "<br>Invalid values. Nothing changed."
            
except:
    if http_request.getvalue('page_to_manage') == "open" or http_request.getvalue('page_to_manage') == "close":#ALERT
        page_to_manage = pages_status['current_page']
        log_title = "Create new entries"
    else:
        log_title = "Audit full collection"
        if http_request.getvalue('page_to_manage') == http_request.getvalue('entry_to_audit') == "all":
            if pages_status['not_registered_closed_pages'] or pages_status['registered_pages_awaiting_confirmation']:
                html_page_head += f"<meta http-equiv=\"Refresh\" content=\"0; URL=?log_info=There are pages still pending!\""
            else:
                for page_id in range(pages_status['current_page'] - 1, -1, -1):
                    sleep(3) # To avoid be recognized as spamer by blockchain explorer services
                    pages_status = audit_page(page_id)
                    update_file(pages_status_file, pages_status)
                log_info += f"<br>Full audit process has finished and found <span style='font-weight:bold;'>{len(pages_status['inconsistent_pages'])} INCONSISTENT PAGES</span>"
                if len(pages_status['inconsistent_entries']):
                    log_info += "<br>But there are pages with inconsistent entries"


# If a page to manage is defined, open it, manage it as needed and open the updated version.
if isinstance(page_to_manage, int):
    
    log_page_file = page_directory + str(page_to_manage) + file_extension
    log_page = open_file(log_page_file)
    
    if http_request.getvalue('global_id') and http_request.getvalue('description'): # If a new entry was submitted, record the needed attributes.
        log_page['entries']['consistent'].append(True)
        log_page['entries']['global_id'].append(http_request.getvalue('global_id'))
        log_page['entries']['description']['is_file_path'].append(bool(http_request.getvalue('description_is_a_file_path')))
        log_page['entries']['description']['content'].append(http_request.getvalue('description'))
        log_page['entries']['fixity']['hash_algorithm'].append(hash_algorithm)
        log_page['entries']['fixity']['hash'].append(get_concatenated_hash(hash_algorithm, http_request.getvalue('global_id'), http_request.getvalue('description'), bool(http_request.getvalue('description_is_a_file_path'))))
        log_page['entries']['fixity']['audit_proof'].append(None)
        log_page['entries']['replacement']['replace_page'].append(None)
        log_page['entries']['replacement']['replace_id'].append(None)
        log_page['entries']['replacement']['replaced'].append(False)
        update_file(log_page_file, log_page)
        
    elif http_request.getvalue('entry_replaced'): # If a entry was replaced, update the needed attributes.
        try: # Threat invalid replacement values
            log_page['entries']['replacement']['replace_page'][int(http_request.getvalue('local_id'))] = int(http_request.getvalue('replace_page'))
            log_page['entries']['replacement']['replace_id'][int(http_request.getvalue('local_id'))] = int(http_request.getvalue('replace_id'))
            log_page['entries']['replacement']['replaced'][int(http_request.getvalue('local_id'))] = True
            update_file(log_page_file, log_page)
        except:
            log_info += "<br>Invalid values. Nothing changed."
            
    elif http_request.getvalue('page_to_manage') == "close": # If the page must be closed...
        merkle_tools = merkletools.MerkleTools()
        merkle_tools.add_leaf(log_page['entries']['fixity']['hash'])
        merkle_tools.make_tree()
        log_page['anchors']['hash_algorithm'] = hash_algorithm
        log_page['anchors']['hash'] = merkle_tools.get_merkle_root() # ...build the Merkle Tree...
        for entry in range(len(log_page['entries']['global_id'])):
            log_page['entries']['fixity']['audit_proof'][entry] = merkle_tools.get_proof(entry) # ...update the entries Merkle Proof...
        update_file(log_page_file, log_page) # ...update the page file...
        pages_status['not_registered_closed_pages'].append(pages_status['current_page'])
        pages_status['current_page'] += 1
        update_file(pages_status_file, pages_status) # ...update the pages status...
        page_to_manage = pages_status['current_page']
        log_page_file = page_directory + str(page_to_manage) + file_extension
        log_page = open_file(log_page_file) # Load the new page.
        log_info += f"<br>Page {pages_status['current_page'] - 1} was successfully closed."
   
    log_page_total_entries = len(log_page['entries']['global_id']) # Calcule and storage the total entries on the page.





for dlt_page_id in pages_status['registered_pages_awaiting_confirmation']:
    dlt_page_file = page_directory + str(dlt_page_id) + file_extension
    dlt_page = open_file(dlt_page_file)
    sleep(1)
    dlt_page = afa_dlt.confirm_page_register(dlt_page)
    if dlt_page['anchors']['timestamp']:
        update_file(dlt_page_file, dlt_page)
        pages_status['registered_pages_awaiting_confirmation'].remove(dlt_page_id)
        update_file(pages_status_file, pages_status)
        log_info += f"<br>Register of page {dlt_page_id} confirmed."




if http_request.getvalue('register_page'):
    try:
        dlt_page_id = int(http_request.getvalue('register_page'))
        if dlt_page_id in pages_status['not_registered_closed_pages'] or dlt_page_id in pages_status['registered_pages_awaiting_confirmation']:
            dlt_page_file = page_directory + str(dlt_page_id) + file_extension
            dlt_page = open_file(dlt_page_file)
            dlt_register = afa_dlt.register_page(pages_status, dlt_page)
            #log_info += f"<br>313"
            log_info += dlt_register[1]
            if dlt_register[0]:
                #log_info += f"<br>316"
                update_file(dlt_page_file, dlt_register[2])
                #log_info += f"<br>318"
                pages_status = dlt_register[3]
                #log_info += f"<br>320"
                update_file(pages_status_file, pages_status)
        else:
            log_info += f"<br>Page {dlt_page_id} is not pending for register."
    except:
        log_info += "<br>Invalid values. Nothing changed."
            
